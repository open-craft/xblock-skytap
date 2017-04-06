"""
Integration tests for the Skytap XBlock.
"""

from selenium.webdriver.support.select import Select

from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable_test import StudioEditableBaseTest


loader = ResourceLoader(__name__)


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
        Locate "Launch" button and return it.
        """
        return self.element.find_element_by_css_selector(".skytap-launch")

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
          was selected when learner last clicked "Launch" button.
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
