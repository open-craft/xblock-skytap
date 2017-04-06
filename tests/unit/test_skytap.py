"""
Unit tests for the Skytap XBlock.
"""

import unittest

from mock import Mock

from xblock.field_data import DictFieldData

from xblock_skytap.skytap import DEFAULT_KEYBOARD_LAYOUTS, SkytapXBlock


XBLOCK_SETTINGS = {
    "keyboard_layouts": DEFAULT_KEYBOARD_LAYOUTS,
}


class TestSkytap(unittest.TestCase):
    """
    Unit tests for the Skytap XBlock.
    """

    def setUp(self):
        self.service_mock = Mock()
        self.runtime_mock = Mock()
        self.runtime_mock.service = Mock(return_value=self.service_mock)
        self.block = SkytapXBlock(self.runtime_mock, DictFieldData({}), Mock())

    def test_get_keyboard_layouts_no_settings(self):
        """
        Test that `get_keyboard_layouts` returns default value
        if settings service is not available.
        """
        self.runtime_mock.service = Mock(return_value=None)
        self.assertEqual(self.block.get_keyboard_layouts(), DEFAULT_KEYBOARD_LAYOUTS)

    def test_get_keyboard_layouts_no_customizations(self):
        """
        Test that `get_keyboard_layouts` returns default value
        if XBLOCK_SETTINGS do not include customizations for Skytap XBlock.
        """
        self.block.get_xblock_settings = Mock(return_value=None)
        self.assertEqual(self.block.get_keyboard_layouts(), DEFAULT_KEYBOARD_LAYOUTS)
        self.block.get_xblock_settings.assert_called_once_with(default=DEFAULT_KEYBOARD_LAYOUTS)

    def test_get_keyboard_layouts_no_layouts(self):
        """
        Test that `get_keyboard_layouts` returns default value
        if XBLOCK_SETTINGS include customizations for Skytap XBlock,
        but do not specify keyboard layouts.
        """
        xblock_settings = {
            "other": {},
            "options": {},
        }
        self.block.get_xblock_settings = Mock(return_value=xblock_settings)
        self.assertEqual(self.block.get_keyboard_layouts(), DEFAULT_KEYBOARD_LAYOUTS)
        self.block.get_xblock_settings.assert_called_once_with(default=DEFAULT_KEYBOARD_LAYOUTS)

    def test_get_keyboard_layouts(self):
        """
        Test that `get_keyboard_layouts` returns keyboard layouts as defined in XBLOCK_SETTINGS.
        """
        self.block.get_xblock_settings = Mock(return_value=XBLOCK_SETTINGS)
        self.assertEqual(self.block.get_keyboard_layouts(), DEFAULT_KEYBOARD_LAYOUTS)
        self.block.get_xblock_settings.assert_called_once_with(default=DEFAULT_KEYBOARD_LAYOUTS)

    def test_sorted_keyboard_layouts(self):
        """
        Test that `sorted_keyboard_layouts` sorts keyboard layouts by language name.
        """
        expected_keyboard_layouts = [
            ("nl-be", "Dutch-Belgium"),
            ("uk", "English (UK)"),
            ("us", "English (US)"),
            ("fi", "Finnish"),
            ("fr", "French"),
            ("fr-be", "French-Belgium"),
            ("fr-ch", "French-Switzerland"),
            ("de", "German"),
            ("de-ch", "German-Switzerland"),
            ("is", "Icelandic"),
            ("it", "Italian"),
            ("jp", "Japanese"),
            ("no", "Norwegian"),
            ("pt", "Polish"),
            ("es", "Spanish")

        ]
        self.block.get_xblock_settings = Mock(return_value=XBLOCK_SETTINGS)
        self.assertEqual(self.block.sorted_keyboard_layouts, expected_keyboard_layouts)
