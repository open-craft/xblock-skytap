"""
Unit tests for the Skytap XBlock.
"""

# Imports ###########################################################

import json

import ddt
import httpretty
from mock import Mock

from xblock.field_data import DictFieldData

from xblock_skytap.exceptions import BoomiConfigurationInvalidError, BoomiConfigurationMissingError
from xblock_skytap.skytap import DEFAULT_KEYBOARD_LAYOUTS, SkytapXBlock

from .mixins.boomi import BOOMI_CONFIGURATION, CreateVmMockMixin


# Globals ###########################################################

XBLOCK_SETTINGS = {
    "boomi_configuration": BOOMI_CONFIGURATION,
    "keyboard_layouts": {
        "de": "German",
        "de-ch": "German-Switzerland",
        "es": "Spanish",
        "fi": "Finnish",
        "fr": "French",
    },
}


# Classes ###########################################################

@ddt.ddt
class TestSkytap(CreateVmMockMixin):
    """
    Unit tests for the Skytap XBlock.
    """

    def setUp(self):
        # Simulate an edx-platform environment by mocking the runtime
        self.current_user_mock = Mock()
        self.current_user_mock.emails = ['testuser@example.com']

        self.service_mock = Mock()
        self.service_mock.get_current_user = Mock(return_value=self.current_user_mock)
        self.service_mock.ugettext = lambda text: text

        self.runtime_mock = Mock()
        self.runtime_mock.service = Mock(return_value=self.service_mock)

        self.scope_ids_mock = Mock()
        self.scope_ids_mock.usage_id.course_key.course = "TestCourse"
        self.scope_ids_mock.usage_id.course_key.run = "201704"

        self.block = SkytapXBlock(self.runtime_mock, DictFieldData({}), self.scope_ids_mock)

    def assert_launch_response(self, expected, code=500):
        """
        Helper method for calling the launch method and asserting an expected response dict.
        """
        response = self.block.launch(request=Mock(method='POST', body=json.dumps('de')))

        self.assertEqual(response.status_code, code)
        self.assertDictEqual(response.json, expected)

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
        self.block.get_xblock_settings.assert_called_once_with(default={})

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
        self.block.get_xblock_settings.assert_called_once_with(default={})

    def test_get_keyboard_layouts(self):
        """
        Test that `get_keyboard_layouts` returns keyboard layouts as defined in XBLOCK_SETTINGS.
        """
        self.block.get_xblock_settings = Mock(return_value=XBLOCK_SETTINGS)
        self.assertEqual(self.block.get_keyboard_layouts(), XBLOCK_SETTINGS["keyboard_layouts"])
        self.block.get_xblock_settings.assert_called_once_with(default={})

    def test_sorted_keyboard_layouts(self):
        """
        Test that `sorted_keyboard_layouts` sorts keyboard layouts by language name.
        """
        expected_keyboard_layouts = [
            ("fi", "Finnish"),
            ("fr", "French"),
            ("de", "German"),
            ("de-ch", "German-Switzerland"),
            ("es", "Spanish"),
        ]
        self.block.get_xblock_settings = Mock(return_value=XBLOCK_SETTINGS)
        self.assertEqual(self.block.sorted_keyboard_layouts, expected_keyboard_layouts)

    @ddt.unpack
    @ddt.data(
        (BoomiConfigurationMissingError, {}),
        (BoomiConfigurationInvalidError, {'boomi_configuration': {}})
    )
    def test_boomi_configuration_exceptions(self, exception, settings):
        """
        Test that the correct exceptions are raised when the 'boomi_configuration' setting is missing or invalid.
        """
        self.block.get_xblock_settings = Mock(return_value=settings)
        with self.assertRaises(exception):
            self.block.get_boomi_configuration()

    def test_get_boomi_url(self):
        """
        Test constructing the Boomi endpoint URL.
        """
        self.block.get_xblock_settings = Mock(return_value=XBLOCK_SETTINGS)

        expected_url = (
            "https://connect.boomi.example.com/ws/simple/createVm"
            ";boomi_auth=Zm9vOmI4ZWFhZGQ3OC00ZWJkLTQ0MDQtYTI2MS02OTBjODE1MWU1NTY="
        )
        returned = self.block.get_boomi_url()
        self.assertEqual(
            returned,
            expected_url,
        )

    @httpretty.activate
    def test_launch(self):
        """
        Test launching the Skytap xblock environment.
        """
        self.block.get_xblock_settings = Mock(return_value=XBLOCK_SETTINGS)
        sharing_portal_url = u'https://skytap.example.com/sharing/portal/url'
        self.mock_createvm(self.block.get_boomi_url(), sharing_portal_url)
        self.assert_launch_response({u'sharing_portal_url': sharing_portal_url}, code=200)

    @httpretty.activate
    def test_launch_handled_error(self):
        """
        Test that handled errors on the Boomi service are properly passed back to the client.
        """
        self.block.get_xblock_settings = Mock(return_value=XBLOCK_SETTINGS)
        error = u'A handled error.'
        self.mock_createvm_error(self.block.get_boomi_url(), error)
        self.assert_launch_response({u'error': error})

    @httpretty.activate
    def test_launch_malformed_response(self):
        """
        Test that a malformed response from Boomi will result in a generic error message being returned to the client.
        """
        self.block.get_xblock_settings = Mock(return_value=XBLOCK_SETTINGS)
        self.mock_createvm_malformed(self.block.get_boomi_url())
        self.assert_launch_response({u'error': u'The Skytap launch service returned a malformed response.'})

    def test_launch_improperly_configured(self):
        """
        Test that a malformed response from Boomi will result in a generic error message being returned to the client.
        """
        self.block.get_xblock_settings = Mock(return_value={})
        self.assert_launch_response({u'error': u'The Skytap XBlock is improperly configured.'}, code=500)

    def test_launch_no_runtime_user(self):
        """
        Test that the launch method gracefully fails when there is no runtime user.
        """
        self.service_mock.get_current_user = Mock(return_value=None)
        self.assert_launch_response({u'error': u'Unable to fetch the current user from the runtime.'})

    def test_launch_no_runtime_course(self):
        """
        Test that the launch method gracefully fails when there is no runtime course.
        """
        self.scope_ids_mock.usage_id.course_key = None
        self.assert_launch_response({u'error': u'This block usage is not associated with a course.'})
