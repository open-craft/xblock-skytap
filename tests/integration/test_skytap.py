"""
Integration tests for the Skytap XBlock.
"""

# Imports ###########################################################

import time

from mock import Mock, patch

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable_test import StudioEditableBaseTest


# Globals ###########################################################

loader = ResourceLoader(__name__)


# Classes ###########################################################

class TestSkytap(StudioEditableBaseTest):
    """
    Integration tests for the Skytap XBlock.
    """

    module_name = __name__
    default_css_selector = "div.skytap-block"

    def load_scenario(self, path, params=None):
        scenario = loader.render_template(path, params)
        self.set_scenario_xml(scenario)
        self.element = self.go_to_view("student_view")

    def refresh_page(self):
        """
        Refresh the current page.
        """
        self.browser.execute_script("$(document).html(' ');")

    def find_menu(self):
        """
        Locate menu for selecting keyboard layout and return it.
        """
        return Select(self.element.find_element_by_tag_name("select"))

    def find_launch_button(self):
        """
        Locate button for launching exercise environment and return it.
        """
        return self.element.find_element_by_css_selector(".skytap-launch")

    def find_spinner(self):
        """
        Locate spinner that indicates that exercise environment is being launched and return it.
        """
        return self.element.find_element_by_css_selector(".skytap-spinner")

    def wait_until_number_of_tabs(self, expected_number_of_tabs):
        """
        Wait until browser shows `expected_number_of_tabs`.
        """
        wait = WebDriverWait(self.driver, self.timeout)
        wait.until(lambda driver: len(driver.window_handles) == expected_number_of_tabs)

    def switch_to_tab(self, index):
        """
        Make sure Selenium web driver looks at tab that sits at `index` in list of tabs.
        """
        tab = self.driver.window_handles[index]
        self.driver.switch_to.window(tab)

    def assert_selected_option(self, menu, expected_value, expected_text):
        """
        Assert that selected option from `menu` matches `expected_value` and `expected_text`.
        """
        selected_option = menu.first_selected_option
        selected_option_value = selected_option.get_attribute("value")
        selected_option_text = selected_option.text.strip()
        self.assertEqual(selected_option_value, expected_value)
        self.assertEqual(selected_option_text, expected_text)

    def test_keyboard_layouts(self):
        """
        Test that menu for selecting keyboard layout defaults to appropriate value.

        - When accessing Skytap XBlock instance for the first time,
          menu should default to "English (US)".
        - On subsequent visits, menu should default to keyboard layout that
          was selected when learner last clicked button for launching exercise environment.
        """
        self.load_scenario("xml/skytap_defaults.xml")

        menu = self.find_menu()
        self.assert_selected_option(menu, "us", "English (US)")

        menu.select_by_visible_text("Norwegian")

        launch_button = self.find_launch_button()
        launch_button.click()

        self.refresh_page()

        menu = self.find_menu()
        self.assert_selected_option(menu, "no", "Norwegian")

    @patch('xblock_skytap.SkytapXBlock.get_boomi_url')
    @patch('xblock_skytap.SkytapXBlock.get_current_course')
    def test_launch(self, _, patched_get_boomi_url):
        """
        Test that successful launch opens sharing portal URL in new tab.
        """
        sharing_portal_url = "http://example.com/"
        patched_get_boomi_url.return_value = "https://not.boomi.com"

        self.load_scenario("xml/skytap_defaults.xml")

        launch_button = self.find_launch_button()
        spinner = self.find_spinner()

        def mock_post(*args, **kwargs):
            """
            Function to use for patching `requests.post`.

            Sleeps for a second before returning a mock response.

            This is necessary because we'd like to verify that the Skytap XBlock:

            - Disables the button for launching an exercise environment when clicked.
            - Shows a spinner while processing the launch request.

            If the new tab opens too quickly, the corresponding checks will fail.
            """
            time.sleep(1)
            mock_response = Mock()
            mock_response.json.return_value = {
                "ErrorExists": "false",
                "SkytapURL": sharing_portal_url,
            }
            return mock_response

        with patch('xblock_skytap.skytap.requests.post', new=mock_post):
            launch_button.click()

            # Verify that button for launching exercise environment is disabled
            # and spinner is visible:
            self.wait_until_disabled(launch_button)
            self.wait_until_visible(spinner)
            # Verify that browser opened a new tab:
            self.wait_until_number_of_tabs(2)

            # Sharing portal is already visible, but we need to make sure
            # that Selenium is looking at the new tab as well:
            self.switch_to_tab(1)

            # Verify that new tab is showing sharing portal:
            self.assertEqual(self.driver.current_url, sharing_portal_url)

            # Go back to original tab
            self.switch_to_tab(0)

            # Verify that button for launching exercise environment is clickable
            # and spinner is hidden:
            self.wait_until_clickable(launch_button)
            self.wait_until_hidden(spinner)
