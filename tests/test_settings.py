"""Android Settings app: navigation tests."""
import allure
import pytest

from pages.settings_home_page import SettingsHomePage

pytestmark = [allure.epic("Android Settings"), allure.feature("Settings navigation"), pytest.mark.android_only]


@pytest.fixture
def home(driver):
    return SettingsHomePage(driver)


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_settings_home_screen_opens(home):
    assert home.is_opened(), "Settings home screen did not open"
    assert home.search_bar_text() == "Search Settings"


def test_open_network_and_internet(home):
    network = home.open_network_and_internet()

    assert network.is_opened(), "'Network & internet' screen did not open"
    assert network.has_item("Airplane mode")


def test_about_shows_device_android_version(home, driver):
    about = home.open_about_device()

    # Expected value comes from the device itself, so the test works on any Android version
    expected = driver.capabilities["platformVersion"]
    assert about.android_version() == expected
