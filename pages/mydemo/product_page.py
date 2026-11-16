"""Product details screen: price, quantity and "Add to cart"."""
import allure

from pages.mydemo.app_page import AppPage, acc, rid


class ProductPage(AppPage):
    TITLE = rid("productTV")
    PRICE = {"android": rid("priceTV"), "ios": acc("Price")}
    QUANTITY = rid("noTV")
    PLUS_BUTTON = acc("Increase item quantity")
    MINUS_BUTTON = acc("Decrease item quantity")
    ADD_TO_CART_BUTTON = {"android": acc("Tap to add product to cart"), "ios": acc("AddToCart")}
    # Present only on the details screen (the catalog image has a different name)
    PRODUCT_IMAGE = {"android": acc("Displays selected product"), "ios": acc("ProductDetails-screen")}

    def wait_until_loaded(self):
        """Wait for the screen; otherwise the next action could run on the catalog."""
        self.find(self.PRODUCT_IMAGE)
        return self

    def title(self) -> str:
        return self.get_text(self.TITLE)

    def price(self) -> str:
        """Price as displayed, e.g. "$ 29.99"."""
        if self.is_ios:
            return self.get_text(self.PRICE)
        # On small screens the price is below the image
        return self.scroll_to_id(self.PRICE["android"][1]).text

    def _scroll_to_controls(self):
        if not self.is_ios:
            self.scroll_to_text("Add to cart")

    @allure.step("Set quantity to {quantity}")
    def set_quantity(self, quantity: int):
        """Tap "+" until the quantity is reached (starts at 1)."""
        self._scroll_to_controls()
        for _ in range(quantity - 1):
            self.click(self.PLUS_BUTTON)

    def quantity(self) -> int:
        return int(self.get_text(self.QUANTITY))

    @allure.step("Add product to cart")
    def add_to_cart(self):
        self._scroll_to_controls()
        self.click(self.ADD_TO_CART_BUTTON)
        return self
