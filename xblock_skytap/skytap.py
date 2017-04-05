"""
"""

# Imports ###########################################################

from __future__ import absolute_import

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import _


# Globals ###########################################################

loader = ResourceLoader(__name__)


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

    editable_fields = ("display_name",)

    def student_view(self, context):
        """
        """
        context = context.copy() if context else {}
        fragment = Fragment()
        fragment.add_content(loader.render_template("templates/skytap.html", context))
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/src/skytap.js")
        )
        fragment.initialize_js("SkytapXBlock")
        return fragment
