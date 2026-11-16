"""Product catalog: the home screen of the app."""
import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.mydemo.app_page import AppPage, acc, rid


class CatalogPage(AppPage):
    TITLE = rid("productTV")
    PRODUCT_TITLES = rid("titleTV")
    PRODUCT_LIST = rid("productRV")
    CATALOG_SCREEN = acc("Catalog-screen")   # iOS only

    # On Android the product name is not clickable, only the image is:
    # find the card that contains the name, then tap the image inside it.
    PRODUCT_IMAGE_BY_NAME = (
        '//*[@text="{name}"]'
        '/ancestor::*[.//*[@content-desc="Product Image"]][1]'
        '//*[@content-desc="Product Image"]'
    )

    def is_opened(self) -> bool:
        if self.is_ios:
            return self.is_visible(self.CATALOG_SCREEN)
        return self.is_visible(self.TITLE) and self.get_text(self.TITLE) == "Products"

    def visible_product_names(self) -> list[str]:
        """Names of the products currently on screen."""
        if self.is_ios:
            names = acc("Product Name")
            self.find(names)
            return [el.get_attribute("label") for el in self.find_all(names)]
        self.find(self.PRODUCT_TITLES)
        return [el.text for el in self.find_all(self.PRODUCT_TITLES)]

    def all_product_names(self, max_scrolls=15) -> list[str]:
        """
        Scroll to the end of the list and collect every product name.
        The RecyclerView only renders the visible items, so names are collected
        page by page. max_scrolls prevents an endless loop.
        """
        names = []
        for _ in range(max_scrolls):
            for name in self.visible_product_names():
                if name not in names:
                    names.append(name)
            can_scroll_more = self.scroll_once(self.PRODUCT_LIST, direction="down")
            if not can_scroll_more:
                break
        for name in self.visible_product_names():
            if name not in names:
                names.append(name)
        return names

    @allure.step("Open product '{name}'")
    def open_product(self, name: str):
        from pages.mydemo.product_page import ProductPage
        if self.is_ios:
            # Only products visible on screen (no scrolling yet)
            self.click((AppiumBy.XPATH,
                        f'//XCUIElementTypeOther[@name="ProductItem"]'
                        f'[.//XCUIElementTypeStaticText[@label="{name}"]]'
                        f'//XCUIElementTypeImage[@name="Product Image"]'))
            return ProductPage(self.driver).wait_until_loaded()
        self.scroll_to_text(name)
        self.click((AppiumBy.XPATH, self.PRODUCT_IMAGE_BY_NAME.format(name=name)))
        return ProductPage(self.driver).wait_until_loaded()
