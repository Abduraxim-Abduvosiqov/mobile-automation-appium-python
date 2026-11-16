"""
Android system permission dialog (com.android.permissioncontroller).

Two ways to deal with permissions:
  - autoGrantPermissions capability, when permissions are not under test;
  - this page object, when the allow/deny behaviour itself is tested.
"""
import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage

PC = "com.android.permissioncontroller:id/"


def pc_id(name):
    return (AppiumBy.ID, PC + name)


class PermissionDialog(BasePage):
    MESSAGE = pc_id("permission_message")
    ALLOW = pc_id("permission_allow_button")
    ALLOW_WHILE_USING = pc_id("permission_allow_foreground_only_button")
    ALLOW_ONCE = pc_id("permission_allow_one_time_button")
    DENY = pc_id("permission_deny_button")

    def is_shown(self, timeout=5) -> bool:
        return self.is_visible(self.MESSAGE, timeout)

    def message(self) -> str:
        return self.get_text(self.MESSAGE)

    @allure.step("Permission dialog: Allow")
    def allow(self):
        self.click(self.ALLOW)

    @allure.step("Permission dialog: While using the app")
    def allow_while_using_app(self):
        """Location permissions show this button instead of "Allow"."""
        self.click(self.ALLOW_WHILE_USING)

    @allure.step("Permission dialog: Don't allow")
    def deny(self):
        self.click(self.DENY)
