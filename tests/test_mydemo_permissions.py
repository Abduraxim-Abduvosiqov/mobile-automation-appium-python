"""
My Demo App (Android): runtime permission dialogs.

Each test starts with a clean app, so the permission dialog always appears.
"""
import allure
import pytest

from pages.mydemo.catalog_page import CatalogPage
from pages.system.permission_dialog import PermissionDialog

TASHKENT = (41.2995, 69.2401)

pytestmark = [allure.epic("My Demo App"), allure.feature("Permissions"), pytest.mark.android_only]


@pytest.fixture(scope="module")
def app():
    return "mydemo"


@pytest.fixture
def catalog(driver):
    return CatalogPage(driver)


@pytest.fixture
def permission(driver):
    return PermissionDialog(driver)


def test_drawing_asks_for_media_permission(catalog, permission):
    catalog.open_drawing()

    assert permission.is_shown(), "Permission dialog did not appear"
    assert "photos" in permission.message()


def test_drawing_allowed_permission_opens_pad(catalog, permission):
    drawing = catalog.open_drawing()

    permission.allow()

    assert drawing.is_opened()


def test_drawing_still_opens_when_permission_denied(catalog, permission):
    """The app must keep working when the user denies the permission."""
    drawing = catalog.open_drawing()

    permission.deny()

    assert drawing.is_opened(), "Drawing screen did not open after denying the permission"


def test_geo_location_shows_mocked_gps(driver, catalog, permission):
    latitude, longitude = TASHKENT
    driver.set_location(latitude, longitude, 0)

    geo = catalog.open_geo_location()
    permission.allow_while_using_app()

    # Floats are compared with a tolerance (the app shows e.g. 69.2400983)
    assert geo.latitude() == pytest.approx(latitude, abs=0.001)
    assert geo.longitude() == pytest.approx(longitude, abs=0.001)
