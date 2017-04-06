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

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.settings import XBlockWithSettingsMixin
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import _


# Globals ###########################################################

loader = ResourceLoader(__name__)

DEFAULT_KEYBOARD_LAYOUTS = {  # Sorted by language code
    "de": "German",
    "de-ch": "German-Switzerland",
    "es": "Spanish",
    "fi": "Finnish",
    "fr": "French",
    "fr-be": "French-Belgium",
    "fr-ch": "French-Switzerland",
    "is": "Icelandic",
    "it": "Italian",
    "jp": "Japanese",
    "nl-be": "Dutch-Belgium",
    "no": "Norwegian",
    "pt": "Polish",
    "uk": "English (UK)",
    "us": "English (US)",
}


# Classes ###########################################################

@XBlock.wants("settings")
class SkytapXBlock(StudioEditableXBlockMixin, XBlockWithSettingsMixin, XBlock):
    """
    An XBlock that allows learners to access a Skytap (https://www.skytap.com/) environment for a given course.
    """

    # Settings

    display_name = String(
        display_name=_("Title"),
        help=_("The title of this block. Displayed above the controls for launching the exercise environment."),
        scope=Scope.settings,
        default=_("Skytap XBlock"),
    )

    # User state

    preferred_keyboard_layout = String(
        scope=Scope.user_state,
        default="us",
    )

    editable_fields = ("display_name",)

    block_settings_key = "skytap"

    def get_keyboard_layouts(self):
        """
        Get available keyboard layouts from settings service, and return them.

        When launching an exercise environment a learner can choose their preferred keyboard layout
        from the list of available keyboard layouts.

        Settings must specify information about available keyboard layouts
        as a mapping from language codes to language names.

        Example:

        XBLOCK_SETTINGS: {
            "skytap": {
                "keyboard_layouts": {
                    "nl-be": "Dutch-Belgium",
                    "uk": "English (UK)",
                    "us": "English (US)",
                    ...
                }
            }
        }
        """
        xblock_settings = self.get_xblock_settings(default=DEFAULT_KEYBOARD_LAYOUTS)
        if xblock_settings:
            return xblock_settings.get("keyboard_layouts", DEFAULT_KEYBOARD_LAYOUTS)
        return DEFAULT_KEYBOARD_LAYOUTS

    @property
    def sorted_keyboard_layouts(self):
        """
        Return list of available keyboard layouts, sorted by language name.
        """
        keyboard_layouts = self.get_keyboard_layouts()
        return sorted(keyboard_layouts.items(), key=lambda i: i[1])

    def student_view(self, context):
        """
        View shown to students.
        """
        context = context.copy() if context else {}
        fragment = Fragment()
        context["display_name"] = self.display_name
        context["keyboard_layouts"] = self.sorted_keyboard_layouts
        context["preferred_keyboard_layout"] = self.preferred_keyboard_layout
        fragment.add_content(loader.render_template("templates/skytap.html", context))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/src/skytap.js")
        )
        fragment.initialize_js("SkytapXBlock")
        return fragment

    @XBlock.json_handler
    def launch(self, keyboard_layout, suffix=""):
        """
        Launch Skytap environment.
        """
        self.preferred_keyboard_layout = keyboard_layout
        return {}
