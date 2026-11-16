"""
My Demo App (Android): cart tests.

Every test starts with a clean app (empty cart), so tests are independent.
"""
import allure
import pytest

from pages.mydemo.catalog_page import CatalogPage

PRODUCT = "Sauce Labs Backpack"

pytestmark = [allure.epic("My Demo App"), allure.feature("Cart"), pytest.mark.android_only]

CRASH_BUG = pytest.mark.xfail(
    reason="Known bug: the app crashes when opening the 7th or a later product",
    strict=True,
)


@pytest.fixture(scope="module")
def app():
    return "mydemo"


@pytest.fixture
def catalog(driver):
    return CatalogPage(driver)


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_catalog_shows_products(catalog):
    assert catalog.is_opened()
    assert PRODUCT in catalog.visible_product_names()


# Products from the start, the boundary and the end of the list
@pytest.mark.parametrize("product_name", [
    pytest.param(PRODUCT, marks=pytest.mark.smoke),
    pytest.param("Sauce Labs Backpack (yellow)", id="6th-product-boundary"),
    pytest.param("Sauce Labs Bike Light", marks=CRASH_BUG, id="7th-product-boundary"),
    pytest.param("Test.allTheThings() T-Shirt (yellow)", marks=CRASH_BUG, id="last-product"),
])
def test_add_product_to_cart(catalog, product_name):
    assert catalog.cart_count() == 0, "Cart should be empty at the start"

    product = catalog.open_product(product_name)
    price = product.price()
    product.add_to_cart()

    assert product.cart_count() == 1

    cart = product.open_cart()
    assert cart.is_opened()
    assert cart.item_names() == [product_name]
    assert cart.items_count_text() == "1 Items"
    assert cart.total_price() == price


def test_quantity_changes_total_price(catalog):
    product = catalog.open_product(PRODUCT)
    product.set_quantity(2)
    assert product.quantity() == 2

    product.add_to_cart()
    cart = product.open_cart()

    assert cart.items_count_text() == "2 Items"
    assert cart.total_price() == "$ 59.98"   # 2 x $ 29.99


def test_remove_item_empties_cart(catalog):
    catalog.open_product(PRODUCT).add_to_cart()
    cart = catalog.open_cart()

    cart.remove_first_item()

    assert cart.is_empty(), "Cart should be empty after removing the only item"
    assert cart.cart_count() == 0
