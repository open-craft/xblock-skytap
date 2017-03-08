"""
"""

# Imports ###########################################################

from __future__ import absolute_import

import skytap as skytap_library

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .default_data import DEFAULT_DATA
from .utils import _


# Globals ###########################################################

loader = ResourceLoader(__name__)


# Functions #########################################################

def get_projects():
    """
    """
    return ('Dummy project A', 'Dummy project B', 'Dummy project C')


def get_vm_images():
    """
    """
    return ('Dummy image A', 'Dummy image B', 'Dummy image C')


def get_vms():
    """
    """
    return ('Dummy VM A', 'Dummy VM B', 'Dummy VM C')


def get_subscription_types():
    """
    """
    return ('All', 'Dummy subscription A', 'Dummy subscription B', 'Dummy subscription C')


# Classes ###########################################################

class SkytapXBlock(StudioEditableXBlockMixin, XBlock):
    """
    """

    display_name = String(
        display_name=_("Title"),
        help=_("The title of this problem. Displayed to learners as a tooltip in the navigation bar."),
        scope=Scope.settings,
        default=_("Skytap XBlock"),
    )

    project = String(
        display_name=_("Project"),
        help=_("Skytap project to pull VM images/templates from."),
        scope=Scope.settings,
        values=get_projects,
    )

    vm_images = String(
        display_name=_("VM images/Templates"),
        help=_("List of VM images/templates belonging to this exercise environment."),
        scope=Scope.settings,
        values=get_vm_images,
    )

    vms = String(
        display_name=_("VMs"),
        help=_("List of VMs to start for selected template."),
        scope=Scope.settings,
        values=get_vms,
    )

    subscription_types = String(
        display_name=_("Subscription types"),
        help=_("List of subscription types that may access this exercise environment."),
        scope=Scope.settings,
        values=get_subscription_types,
    )

    organization_rules = String(
        display_name=_("Organization rules"),
        help=_(
            "Rules that define custom behavior for specific organizations. "
            "To apply a rule to an organization, add one or more identifiers below the rule name."
        ),
        scope=Scope.settings,
        default=DEFAULT_DATA,
        multiline_editor=True,
    )

    editable_fields = ("display_name", "project", "vm_images", "subscription_types", "organization_rules")

    def student_view(self, context):
        """
        """
        context = context.copy() if context else {}
        users = skytap_library.Users()
        context['users'] = users.json()
        fragment = Fragment()
        fragment.add_content(loader.render_template("templates/skytap.html", context))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/src/skytap.js")
        )
        fragment.initialize_js("SkytapXBlock")
        return fragment
