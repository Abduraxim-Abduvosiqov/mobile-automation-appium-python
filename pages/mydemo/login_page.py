"""Login screen."""
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.mydemo.app_page import AppPage, acc, ios_predicate, rid
from pages.mydemo.catalog_page import CatalogPage


class LoginPage(AppPage):
    USERNAME_FIELD = {"android": rid("nameET"),
                      "ios": (AppiumBy.CLASS_NAME, "XCUIElementTypeTextField")}
    PASSWORD_FIELD = {"android": rid("passwordET"),
                      "ios": (AppiumBy.CLASS_NAME, "XCUIElementTypeSecureTextField")}
    # iOS has both a "Login" title and a "Login" button: match the button only
    LOGIN_BUTTON = {"android": acc("Tap to login with given credentials"),
                    "ios": ios_predicate("type == 'XCUIElementTypeButton' AND name == 'Login'")}
    USERNAME_ERROR = rid("nameErrorTV")
    PASSWORD_ERROR = rid("passwordErrorTV")

    def is_opened(self) -> bool:
        return self.is_visible(self.USERNAME_FIELD)

    @allure.step("Log in with username '{username}'")
    def login(self, username: str, password: str):
        """Fill in the form and tap Login. The outcome is checked by the test."""
        self.type_text(self.USERNAME_FIELD, username)
        self.type_text(self.PASSWORD_FIELD, password)
        self.click(self.LOGIN_BUTTON)

    def login_as(self, user) -> CatalogPage:
        """Successful login shortcut."""
        self.login(user.username, user.password)
        if self.is_ios:
            self.dismiss_system_alert()
        return CatalogPage(self.driver)

    @allure.step("Dismiss iOS system alert (e.g. 'Save Password?') if shown")
    def dismiss_system_alert(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present()).dismiss()
        except TimeoutException:
            pass

    def error_under(self, field: str) -> str:
        """Error text under a field: "username" or "password"."""
        locators = {"username": self.USERNAME_ERROR, "password": self.PASSWORD_ERROR}
        return self.get_text(locators[field])

    def username_error(self) -> str:
        return self.get_text(self.USERNAME_ERROR)

    def password_error(self) -> str:
        return self.get_text(self.PASSWORD_ERROR)
