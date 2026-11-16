"""
My Demo App: tests that run on both Android and iOS.

Platform differences live in the page objects (locators), test_data (users,
product names) and conftest.py (capabilities); the tests themselves have none.

    pytest tests/test_mydemo_cross_platform.py                  # Android
    pytest tests/test_mydemo_cross_platform.py --platform ios   # iOS
"""
import allure
import pytest

from pages.mydemo.catalog_page import CatalogPage
from test_data.products import FIRST_PRODUCT
from test_data.users import VALID_USERS
from utils.prices import parse_price

pytestmark = [allure.epic("My Demo App"), allure.feature("Cross-platform")]


@pytest.fixture(scope="module")
def app():
    return "mydemo"


@pytest.fixture
def catalog(driver):
    return CatalogPage(driver)


@pytest.fixture
def platform(settings):
    return settings["platform"]


@pytest.mark.smoke
def test_catalog_opens_with_products(catalog, platform):
    assert catalog.is_opened(), "Catalog screen did not open"
    assert FIRST_PRODUCT[platform] in catalog.visible_product_names()


@pytest.mark.smoke
def test_login_with_valid_user(catalog, platform):
    login_page = catalog.open_login()

    home = login_page.login_as(VALID_USERS[platform])

    assert home.is_opened(), "Catalog did not open after login"


def test_add_first_product_to_cart(catalog, platform):
    product_name = FIRST_PRODUCT[platform]

    product = catalog.open_product(product_name)
    price = product.price()
    product.add_to_cart()
    cart = product.open_cart()

    assert cart.is_opened()
    assert cart.contains_item(product_name)
    assert cart.items_count_text() == "1 Items"
    # Compare numbers, not text: iOS shows "$ 29.99" and "$29.99" in different places
    assert parse_price(cart.total_price()) == parse_price(price)


def test_remove_item_empties_cart(catalog, platform):
    catalog.open_product(FIRST_PRODUCT[platform]).add_to_cart()
    cart = catalog.open_cart()

    cart.remove_first_item()

    assert cart.is_empty(), "Cart should be empty after removing the only item"
