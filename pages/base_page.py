"""Base page object: waits, actions, scrolling and gestures shared by all pages."""
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    DEFAULT_TIMEOUT = 10

    def __init__(self, driver):
        self.driver = driver

    # ---------- Platform ----------

    @property
    def platform(self) -> str:
        """Current session platform: "android" or "ios"."""
        return self.driver.capabilities["platformName"].lower()

    @property
    def is_ios(self) -> bool:
        return self.platform == "ios"

    def resolve(self, locator):
        """
        A locator is either a plain tuple (same on both platforms) or a dict
        {"android": (...), "ios": (...)} resolved for the current platform.
        """
        if isinstance(locator, dict):
            if self.platform not in locator:
                raise NotImplementedError(f"No {self.platform} locator defined: {locator}")
            return locator[self.platform]
        return locator

    # ---------- Finding elements ----------

    def find(self, locator, timeout=DEFAULT_TIMEOUT):
        """Wait until the element is visible and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.resolve(locator))
        )

    def is_visible(self, locator, timeout=DEFAULT_TIMEOUT) -> bool:
        try:
            self.find(locator, timeout)
            return True
        except TimeoutException:
            return False

    def find_all(self, locator):
        return self.driver.find_elements(*self.resolve(locator))

    # ---------- Actions ----------

    def click(self, locator, timeout=DEFAULT_TIMEOUT):
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.resolve(locator))
        ).click()

    def type_text(self, locator, text, timeout=DEFAULT_TIMEOUT):
        field = self.find(locator, timeout)
        field.clear()
        field.send_keys(text)

    def get_text(self, locator, timeout=DEFAULT_TIMEOUT) -> str:
        """Element text. On iOS the `label` attribute is more reliable than `.text`."""
        element = self.find(locator, timeout)
        return element.get_attribute("label") if self.is_ios else element.text

    # ---------- Android scrolling (UiScrollable) ----------

    def scroll_into_view(self, ui_selector: str):
        """Scroll until an element matching the UiSelector condition is visible."""
        uiautomator = (
            "new UiScrollable(new UiSelector().scrollable(true))"
            f".scrollIntoView(new UiSelector().{ui_selector})"
        )
        try:
            return self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, uiautomator)
        except NoSuchElementException:
            raise NoSuchElementException(f"Scrolled, but {ui_selector} was not found")

    def scroll_to_text(self, text, exact=True):
        selector = "text" if exact else "textStartsWith"
        return self.scroll_into_view(f'{selector}("{text}")')

    def scroll_to_id(self, resource_id):
        return self.scroll_into_view(f'resourceId("{resource_id}")')

    @staticmethod
    def by_text(text):
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')

    # ---------- Gestures ----------

    def swipe(self, locator, direction="up", percent=0.75):
        """Fast swipe (fling) over an element."""
        element = self.find(locator)
        self.driver.execute_script("mobile: swipeGesture", {
            "elementId": element.id,
            "direction": direction,
            "percent": percent,
        })

    def scroll_once(self, locator, direction="down", percent=0.75) -> bool:
        """Controlled scroll. Returns False when the end of the list is reached."""
        element = self.find(locator)
        return self.driver.execute_script("mobile: scrollGesture", {
            "elementId": element.id,
            "direction": direction,
            "percent": percent,
        })

    def long_press(self, locator, duration_ms=1500):
        element = self.find(locator)
        self.driver.execute_script("mobile: longClickGesture", {
            "elementId": element.id,
            "duration": duration_ms,
        })

    def draw_path(self, points, step_pause=0.05):
        """Drag one finger through a list of (x, y) screen points using W3C Actions."""
        finger = PointerInput(interaction.POINTER_TOUCH, "finger")
        actions = ActionBuilder(self.driver, mouse=finger)
        first_x, first_y = points[0]
        actions.pointer_action.move_to_location(first_x, first_y)
        actions.pointer_action.pointer_down()
        for x, y in points[1:]:
            actions.pointer_action.pause(step_pause)
            actions.pointer_action.move_to_location(x, y)
        actions.pointer_action.release()
        actions.perform()
