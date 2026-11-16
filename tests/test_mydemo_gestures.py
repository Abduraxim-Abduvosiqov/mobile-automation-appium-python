"""
My Demo App (Android): gestures — scrolling and drawing.

Permissions are granted automatically here (autoGrantPermissions) because
these tests are about gestures; permission dialogs are covered separately.
"""
import allure
import pytest

from pages.mydemo.catalog_page import CatalogPage

pytestmark = [allure.epic("My Demo App"), allure.feature("Gestures"), pytest.mark.android_only]


@pytest.fixture(scope="module")
def app():
    return "mydemo"


@pytest.fixture(scope="module")
def extra_caps():
    return {"autoGrantPermissions": True}


@pytest.fixture
def catalog(driver):
    return CatalogPage(driver)


def test_scroll_through_catalog_shows_all_products(catalog):
    names = catalog.all_product_names()

    assert len(names) == 24, f"Expected 24 products, found {len(names)}: {names}"
    assert names[0] == "Sauce Labs Backpack"
    assert names[-1] == "Test.allTheThings() T-Shirt (yellow)"
    # Default sort order: name A-Z
    assert names == sorted(names), "Products are not sorted by name"


@pytest.fixture
def drawing(catalog):
    page = catalog.open_drawing()
    assert page.is_opened(), "Drawing screen did not open"
    return page


def test_drawing_changes_pad(drawing):
    empty = drawing.pad_snapshot()

    drawing.draw_square()

    assert drawing.pad_snapshot() != empty, "Pad did not change after drawing"


def test_clear_removes_drawing(drawing):
    empty = drawing.pad_snapshot()
    drawing.draw_square()

    drawing.clear()

    assert drawing.pad_snapshot() == empty, "Pad is not empty after Clear"


def test_save_drawing_shows_success_message(drawing):
    drawing.draw_square()

    message = drawing.save()

    assert message == "Drawing saved successfully to gallery"
    drawing.close_dialog()
