"""My Demo App (Android): login tests."""
import allure
import pytest

from pages.mydemo.catalog_page import CatalogPage
from test_data.users import LOCKED_USER, VALID_USER

pytestmark = [allure.epic("My Demo App"), allure.feature("Login"), pytest.mark.android_only]


@pytest.fixture(scope="module")
def app():
    return "mydemo"


@pytest.fixture
def login_page(driver):
    return CatalogPage(driver).open_login()


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_login_with_valid_user(login_page):
    catalog = login_page.login_as(VALID_USER)

    assert catalog.is_opened(), "Catalog did not open after login"


@pytest.mark.parametrize(
    "username, password, field, expected_error",
    [
        (LOCKED_USER.username, LOCKED_USER.password, "password", "Sorry this user has been locked out."),
        ("",                   VALID_USER.password,  "username", "Username is required"),
        (VALID_USER.username,  "",                   "password", "Enter Password"),
        ("",                   "",                   "username", "Username is required"),
    ],
    ids=["locked-user", "empty-username", "empty-password", "both-empty"],
)
def test_login_shows_error(login_page, username, password, field, expected_error):
    login_page.login(username, password)

    assert login_page.error_under(field) == expected_error


@pytest.mark.xfail(
    reason="Known bug: login succeeds with a wrong password",
    strict=True,
)
def test_login_with_wrong_password_is_rejected(login_page):
    login_page.login(VALID_USER.username, "wrong-password")

    assert login_page.is_opened(), "Wrong password was accepted"
