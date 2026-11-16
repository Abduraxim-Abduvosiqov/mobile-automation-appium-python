"""
Drawing screen: a pad to draw on, Clear and Save buttons.

Drawing is verified by comparing screenshots of the pad element
before and after an action.
"""
import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.mydemo.app_page import AppPage, acc, rid


class DrawingPage(AppPage):
    TITLE = rid("drawingTV")
    PAD = acc("Pad to draw on")
    CLEAR_BUTTON = acc("Removes anything drawn on pad")
    SAVE_BUTTON = acc("Save anything drawn on pad")
    DIALOG_TITLE = (AppiumBy.ID, "android:id/alertTitle")
    DIALOG_MESSAGE = (AppiumBy.ID, "android:id/message")
    DIALOG_OK = (AppiumBy.ID, "android:id/button1")

    def is_opened(self) -> bool:
        return self.is_visible(self.PAD)

    def pad_snapshot(self) -> bytes:
        """PNG screenshot of the pad element only."""
        return self.find(self.PAD).screenshot_as_png

    @allure.step("Draw a square ({size}px) on the pad")
    def draw_square(self, size=300):
        """Draw a square in the center of the pad (coordinates come from the pad size)."""
        rect = self.find(self.PAD).rect
        cx = rect["x"] + rect["width"] // 2
        cy = rect["y"] + rect["height"] // 2
        half = size // 2
        self.draw_path([
            (cx - half, cy - half),
            (cx + half, cy - half),
            (cx + half, cy + half),
            (cx - half, cy + half),
            (cx - half, cy - half),
        ])

    @allure.step("Tap Clear")
    def clear(self):
        self.click(self.CLEAR_BUTTON)

    @allure.step("Tap Save")
    def save(self) -> str:
        """Tap Save and return the message of the dialog that appears."""
        self.click(self.SAVE_BUTTON)
        return self.get_text(self.DIALOG_MESSAGE)

    def close_dialog(self):
        self.click(self.DIALOG_OK)
