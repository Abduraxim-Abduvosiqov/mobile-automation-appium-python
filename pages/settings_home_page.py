"""Android Settings: home screen."""
import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.about_page import AboutPage
from pages.base_page import BasePage
from pages.network_page import NetworkPage


class SettingsHomePage(BasePage):
    SEARCH_BAR = (AppiumBy.ID, "com.android.settings:id/search_bar_title")
    NETWORK_MENU = BasePage.by_text("Network & internet")

    def is_opened(self) -> bool:
        return self.is_visible(self.SEARCH_BAR)

    def search_bar_text(self) -> str:
        return self.get_text(self.SEARCH_BAR)

    @allure.step("Open 'Network & internet'")
    def open_network_and_internet(self) -> NetworkPage:
        self.click(self.NETWORK_MENU)
        return NetworkPage(self.driver)

    @allure.step("Open 'About device'")
    def open_about_device(self) -> AboutPage:
        # "About emulated device" on emulators, "About phone" on real devices
        self.scroll_to_text("About", exact=False).click()
        return AboutPage(self.driver)
