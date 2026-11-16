"""Android Settings: 'About phone' / 'About emulated device' screen."""
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class AboutPage(BasePage):
    # Each row has a title and a summary (value) as siblings
    SUMMARY_OF = (
        "//*[@resource-id='android:id/title' and @text='{title}']"
        "/following-sibling::*[@resource-id='android:id/summary']"
    )

    def get_value(self, title: str) -> str:
        """Value of a row, e.g. get_value("Android version") -> "16"."""
        self.scroll_to_text(title)
        locator = (AppiumBy.XPATH, self.SUMMARY_OF.format(title=title))
        return self.get_text(locator)

    def android_version(self) -> str:
        return self.get_value("Android version")
