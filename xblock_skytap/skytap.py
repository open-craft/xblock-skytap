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

from .utils import _


# Globals ###########################################################

loader = ResourceLoader(__name__)


# Functions #########################################################

def get_vm_images():
    """
    """
    return ('Dummy image A', 'Dummy image B', 'Dummy image C')


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

    vm_image = String(
        display_name=_("VM image"),
        help=_("The name of the VM image to use."),
        scope=Scope.settings,
        values=get_vm_images,
    )

    editable_fields = ("display_name", "vm_image")

    def student_view(self, context):
        """
        """
        context = context.copy() if context else {}
        users = skytap_library.Users()
        context['users'] = users.json()
        fragment = Fragment()
        fragment.add_content(loader.render_template("templates/skytap.html", context))
        return fragment
