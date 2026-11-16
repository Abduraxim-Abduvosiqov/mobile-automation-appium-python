"""Android Settings: 'Network & internet' screen."""
from pages.base_page import BasePage


class NetworkPage(BasePage):
    INTERNET_ITEM = BasePage.by_text("Internet")
    AIRPLANE_ITEM = BasePage.by_text("Airplane mode")

    def is_opened(self) -> bool:
        return self.is_visible(self.INTERNET_ITEM)

    def has_item(self, title: str) -> bool:
        return self.is_visible(BasePage.by_text(title), timeout=5)
