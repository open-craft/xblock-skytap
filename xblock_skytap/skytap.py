"""
An XBlock that allows learners to access a Skytap (https://www.skytap.com/) environment for a given course.

Note that the current implementation does not take care of provisioning the environment.
Instead, it sends relevant data to a Boomi (https://boomi.com/) Listener
which will identify the environment to use, add relevant VMs to it, and configure them
according to the learner's preferences. Upon success, the Boomi Listener responds with a link
to the sharing portal that lets the learner access the environment. The Skytap XBlock is responsible
for opening the sharing portal link in a new browser tab.
"""

# Imports ###########################################################

from __future__ import absolute_import

import base64
import logging
from urllib.parse import urljoin

import requests
from simplejson import JSONDecodeError
from xblock.core import XBlock
from xblock.exceptions import JsonHandlerError
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.settings import XBlockWithSettingsMixin
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .exceptions import (BoomiConfigurationInvalidError,
                         BoomiConfigurationMissingError)
from .utils import _  # pylint: disable=unused-import

# Globals ###########################################################

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)

# Classes ###########################################################


@XBlock.wants("settings")
@XBlock.wants("user")
@XBlock.needs("i18n")
class SkytapXBlock(StudioEditableXBlockMixin, XBlockWithSettingsMixin, XBlock):
    """
    An XBlock that allows learners to access a Skytap (https://www.skytap.com/) environment for a given course.
    """

    # Settings

    display_name = String(
        display_name=_("Title"),
        help=_("The title of this block. Learners currently don't see this."),
        scope=Scope.settings,
        default=_("Skytap XBlock"),
    )

    # User state

    editable_fields = ("display_name",)

    block_settings_key = "skytap"

    def _(self, text):
        """ Translate text. """
        return self.runtime.service(self, "i18n").ugettext(text)

    def student_view(self, context):
        """
        View shown to students.
        """
        context = context.copy() if context else {}
        fragment = Fragment()
        context["display_name"] = self.display_name
        fragment.add_content(loader.render_template("templates/skytap.html", context))
        fragment.add_css_url(
            self.runtime.local_resource_url(self, "public/css/skytap.css")
        )
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/src/skytap.js")
        )
        fragment.initialize_js("SkytapXBlock")
        return fragment

    def get_current_user(self):
        """
        Get current user from user service, and return it.
        """
        user_service = self.runtime.service(self, 'user')
        if user_service:
            return user_service.get_current_user()
        return None

    def get_current_course(self):
        """
        Get the current course, and return it.
        """
        try:
            return self.scope_ids.usage_id.course_key
        except AttributeError:  # We are not in an edx-platform runtime
            return None

    def get_boomi_configuration(self):
        """
        Get Boomi configuration from settings service, and return it.

        Raise an exception if configuration is missing one or more relevant entries.
        """
        xblock_settings = self.get_xblock_settings(default={})
        if not xblock_settings or "boomi_configuration" not in xblock_settings:
            raise BoomiConfigurationMissingError(
                "XBLOCK_SETTINGS for Skytap XBlock are missing Boomi configuration."
            )
        boomi_configuration = xblock_settings["boomi_configuration"]
        relevant_settings = ("base_url", "endpoint", "username", "token")
        missing_settings = [
            setting for setting in relevant_settings if setting not in boomi_configuration
        ]
        if missing_settings:
            raise BoomiConfigurationInvalidError(
                "Boomi configuration is missing the following settings: {missing_settings}".format(
                    missing_settings=", ".join(missing_settings)
                )
            )
        return boomi_configuration

    def get_boomi_url(self):
        """
        Using the "boomi_configuration" in the XBLOCK_SETTINGS, construct the authenticated Boomi endpoint URL.
        """
        boomi_configuration = self.get_boomi_configuration()

        auth_string = "{}:{}".format(boomi_configuration['username'], boomi_configuration['token']).encode('ascii')
        base64_auth_string = base64.b64encode(auth_string)

        return "{base_url};boomi_auth={base64_auth_string}".format(
            base_url=urljoin(boomi_configuration['base_url'], boomi_configuration['endpoint']),
            base64_auth_string=base64_auth_string.decode('ascii')
        )

    @staticmethod
    def raise_error(message='An unknown error occurred.', exception=False):
        """
        Given an error message, log the error and raise a JsonHandlerError to invoke an error response.
        """
        if exception:
            log.exception(message)
        else:
            log.error(message)

        raise JsonHandlerError(500, message)

    @XBlock.json_handler
    def launch(self, data, suffix=""):  # pylint: disable=unused-argument
        """
        Launch Skytap environment and return the resulting sharing portal URL.
        """

        # Gather information from the runtime and settings
        current_user = self.get_current_user()
        current_course = self.get_current_course()
        if current_user is None:
            self.raise_error(self._('Unable to fetch the current user from the runtime.'))
        if current_course is None:
            self.raise_error(self._('This block usage is not associated with a course.'))
        current_user_email = current_user.emails.pop()
        current_course_name = current_course.course
        current_course_run = current_course.run
        try:
            boomi_url = self.get_boomi_url()
        except (BoomiConfigurationInvalidError, BoomiConfigurationMissingError):
            self.raise_error(self._('The Skytap XBlock is improperly configured.'), exception=True)

        # Fetch the sharing portal URL from Boomi
        response = requests.post(
            boomi_url,
            json={
                'email': current_user_email,
                'course_name': current_course_name,
                'course_run': current_course_run,
            },
            headers={'Accept': 'application/json'},
        )

        # Handle response errors
        try:
            response_json = response.json()
        except JSONDecodeError:
            log.error(
                self._('The Boomi endpoint returned the following non-JSON response content: %s'),
                response.content
            )
            self.raise_error(self._('The Skytap launch service returned a malformed response.'), exception=True)

        # Check if Boomi encountered an error while processing the request,
        # and pass it back to the client.
        # Note that Boomi does not support Boolean values in JSON responses,
        # so the check needs to compare string values.
        if response_json['ErrorExists'].lower() == 'true':
            self.raise_error(response_json['ErrorMessage'])

        return {
            'sharing_portal_url': response_json['SkytapURL']
        }
