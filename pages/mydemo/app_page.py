"""
Base page for Sauce Labs My Demo App: navigation shared by every screen.

Android: side menu + cart icon in the header.
iOS: bottom tab bar (Catalog / Cart / More).
"""
import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage

PKG = "com.saucelabs.mydemoapp.android"


def rid(name: str):
    """Android resource-id locator: rid("nameET") -> (ID, "<package>:id/nameET")."""
    return (AppiumBy.ID, f"{PKG}:id/{name}")


def acc(description: str):
    """Accessibility id locator (content-desc on Android, name on iOS)."""
    return (AppiumBy.ACCESSIBILITY_ID, description)


def ios_predicate(condition: str):
    """iOS predicate string locator, e.g. "label == 'Login'"."""
    return (AppiumBy.IOS_PREDICATE, condition)


class AppPage(BasePage):
    MENU_BUTTON = acc("View menu")                                         # Android only
    CART_BUTTON = {"android": acc("View cart"), "ios": acc("Cart-tab-item")}
    MORE_TAB = acc("More-tab-item")                                        # iOS only
    CART_BADGE = rid("cartTV")   # hidden when the cart is empty

    def open_menu_item(self, description: str):
        """Open the side menu and tap an item by accessibility id (scrolling if needed)."""
        self.click(self.MENU_BUTTON)
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            "new UiScrollable(new UiSelector().scrollable(true))"
            f'.scrollIntoView(new UiSelector().description("{description}"))',
        ).click()

    def open_menu_item_by_text(self, text: str):
        """For menu items without an accessibility id (e.g. Drawing, Geo Location)."""
        self.click(self.MENU_BUTTON)
        self.click(BasePage.by_text(text))

    @allure.step("Open Drawing screen from menu")
    def open_drawing(self):
        """Note: a permission dialog may appear first; the test decides how to handle it."""
        from pages.mydemo.drawing_page import DrawingPage
        self.open_menu_item_by_text("Drawing")
        return DrawingPage(self.driver)

    @allure.step("Open Geo Location screen from menu")
    def open_geo_location(self):
        from pages.mydemo.geo_page import GeoLocationPage
        self.open_menu_item_by_text("Geo Location")
        return GeoLocationPage(self.driver)

    @allure.step("Open Login screen from menu")
    def open_login(self):
        from pages.mydemo.login_page import LoginPage  # local import avoids a circular import
        if self.is_ios:
            self.click(self.MORE_TAB)
            self.click(acc("LogOut-menu-item"))   # the app names the login item this way
        else:
            self.open_menu_item("Login Menu Item")
        return LoginPage(self.driver)

    @allure.step("Open cart")
    def open_cart(self):
        from pages.mydemo.cart_page import CartPage
        self.click(self.CART_BUTTON)
        return CartPage(self.driver)

    def cart_count(self) -> int:
        """Number on the cart badge; 0 when the badge is not shown."""
        if not self.is_visible(self.CART_BADGE, timeout=2):
            return 0
        return int(self.get_text(self.CART_BADGE))
