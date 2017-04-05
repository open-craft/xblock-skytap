"""
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


# Classes ###########################################################

@XBlock.wants('settings')
class SkytapXBlock(StudioEditableXBlockMixin, XBlockWithSettingsMixin, XBlock):
    """
    """

    display_name = String(
        display_name=_("Title"),
        help=_("The title of this problem. Displayed to learners as a tooltip in the navigation bar."),
        scope=Scope.settings,
        default=_("Skytap XBlock"),
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
        default = {}
        xblock_settings = self.get_xblock_settings(default=default)
        if xblock_settings:
            return xblock_settings.get("keyboard_layouts", default)
        # Don't make assumptions about available keyboard layouts
        return default

    def student_view(self, context):
        """
        """
        context = context.copy() if context else {}
        fragment = Fragment()
        context['keyboard_layouts'] = self.get_keyboard_layouts()
        fragment.add_content(loader.render_template("templates/skytap.html", context))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/src/skytap.js")
        )
        fragment.initialize_js("SkytapXBlock")
        return fragment
