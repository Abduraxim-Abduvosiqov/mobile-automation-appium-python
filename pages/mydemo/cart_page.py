"""Cart ("My Cart") screen."""
import allure

from appium.webdriver.common.appiumby import AppiumBy

from pages.mydemo.app_page import AppPage, acc, ios_predicate, rid


class CartPage(AppPage):
    TITLE = rid("productTV")
    ITEM_TITLES = rid("titleTV")
    CART_SCREEN = acc("Cart-screen")   # iOS only
    # iOS has no stable ids here: 1st and 2nd text after the "Total:" label
    ITEMS_COUNT = {"android": rid("itemsTV"),
                   "ios": (AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Total:"]'
                                           '/following-sibling::XCUIElementTypeStaticText[1]')}
    TOTAL_PRICE = {"android": rid("totalPriceTV"),
                   "ios": (AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Total:"]'
                                           '/following-sibling::XCUIElementTypeStaticText[2]')}
    REMOVE_BUTTON = {"android": acc("Removes product from cart"), "ios": acc("Remove Item")}
    # On iOS "No Items" exists (hidden) even when the cart is not empty: check visibility
    EMPTY_TITLE = {"android": rid("noItemTitleTV"), "ios": acc("No Items")}

    def is_opened(self) -> bool:
        if self.is_ios:
            return self.is_visible(self.CART_SCREEN)
        return self.is_visible(self.TITLE) and self.get_text(self.TITLE) == "My Cart"

    def contains_item(self, name: str) -> bool:
        if self.is_ios:
            return self.is_visible(ios_predicate(f"type == 'XCUIElementTypeStaticText' AND label == '{name}'"))
        return name in self.item_names()

    def item_names(self) -> list[str]:
        self.find(self.ITEM_TITLES)
        return [el.text for el in self.driver.find_elements(*self.ITEM_TITLES)]

    def items_count_text(self) -> str:
        return self.get_text(self.ITEMS_COUNT)

    def total_price(self) -> str:
        return self.get_text(self.TOTAL_PRICE)

    @allure.step("Remove first item from cart")
    def remove_first_item(self):
        self.click(self.REMOVE_BUTTON)
        return self

    def is_empty(self) -> bool:
        return self.is_visible(self.EMPTY_TITLE, timeout=5)
