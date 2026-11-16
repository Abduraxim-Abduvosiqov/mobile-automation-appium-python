"""
Shared pytest configuration: command-line options, Appium capabilities and fixtures.

One Appium session is opened per test module; between tests the app is reset
(cleared and relaunched), which is much faster than creating a new session.
"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import allure
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"


# ----------------------------------------------------------------------
# Command-line options
#   --platform ios                         run on an iPhone simulator (default: android)
#   --device emulator-5556                 target a specific device
#   --appium-url http://host:4723          use a remote Appium server
#   --fresh-session                        new Appium session for every test
# Priority: command line > environment variable > default.
# ----------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--platform",
        choices=["android", "ios"],
        default=os.getenv("PLATFORM", "android"),
        help="Platform to run on: android or ios",
    )
    parser.addoption(
        "--device",
        default=os.getenv("DEVICE_NAME"),
        help="Device UDID. Default: emulator-5554 on Android, the booted iPhone simulator on iOS",
    )
    parser.addoption(
        "--appium-url",
        default=os.getenv("APPIUM_URL", "http://127.0.0.1:4723"),
        help="Appium server URL",
    )
    parser.addoption(
        "--fresh-session",
        action="store_true",
        help="Create a new Appium session for every test (slower)",
    )


@pytest.fixture(scope="session")
def settings(pytestconfig):
    platform = pytestconfig.getoption("--platform")
    device = pytestconfig.getoption("--device")
    if device is None:
        device = "emulator-5554" if platform == "android" else booted_ios_simulator()
    return {
        "platform": platform,
        "device": device,
        "appium_url": pytestconfig.getoption("--appium-url"),
        "fresh_session": pytestconfig.getoption("--fresh-session"),
    }


def booted_ios_simulator() -> str:
    """UDID of the currently booted iPhone simulator."""
    output = subprocess.run(
        ["xcrun", "simctl", "list", "devices", "booted", "--json"],
        capture_output=True, text=True, check=True,
    ).stdout
    for devices in json.loads(output)["devices"].values():
        for device in devices:
            if device["state"] == "Booted" and "iPhone" in device["name"]:
                return device["udid"]
    pytest.exit("No booted iPhone simulator found. Boot one in the Simulator app.")


def pytest_collection_modifyitems(config, items):
    """Skip tests marked android_only when running with --platform ios."""
    if config.getoption("--platform") != "ios":
        return
    skip = pytest.mark.skip(reason="Android-only test")
    for item in items:
        if "android_only" in item.keywords:
            item.add_marker(skip)


# ----------------------------------------------------------------------
# Apps and capabilities: APPS[app][platform]
# ----------------------------------------------------------------------

APPS = {
    # Built-in Android Settings app
    "settings": {"android": {
        "appPackage": "com.android.settings",
        "appActivity": ".Settings",
        "noReset": True,
        # Relaunch the app even if it is already running in the background
        "forceAppLaunch": True,
    }},
    # Sauce Labs "My Demo App"
    "mydemo": {"android": {
        "app": str(Path(__file__).parent / "apps" / "mda-2.3.0-27.apk"),
        "appPackage": "com.saucelabs.mydemoapp.android",
        "appActivity": ".view.activities.SplashActivity",
        "appWaitActivity": "*.MainActivity",
        # Clean app state for every test: empty cart, logged out
        "noReset": False,
    }, "ios": {
        "app": str(Path(__file__).parent / "apps" / "ios" / "MyDemoApp.app"),
        "bundleId": "com.saucelabs.mydemo.app.ios",
        "noReset": False,
        # The first WebDriverAgent build can take several minutes
        "wdaLaunchTimeout": 600000,
        "wdaConnectionTimeout": 600000,
    }},
}


def app_caps(app_name: str, platform: str) -> dict:
    if platform not in APPS[app_name]:
        pytest.skip(f"'{app_name}' is not available on {platform}")
    return APPS[app_name][platform]


def build_options(app_name: str, platform: str, device: str, extra_caps: dict | None = None):
    if platform == "ios":
        options = XCUITestOptions()
        options.platform_name = "iOS"
        options.automation_name = "XCUITest"
    else:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.automation_name = "UiAutomator2"
    options.device_name = device
    options.udid = device
    options.new_command_timeout = 60

    # set_capability() is used for every capability: not all of them have
    # a typed property in the Python client (e.g. forceAppLaunch).
    for name, value in (app_caps(app_name, platform) | (extra_caps or {})).items():
        options.set_capability(f"appium:{name}", value)
    return options


def create_driver(settings, app_name, extra_caps):
    return webdriver.Remote(
        settings["appium_url"],
        options=build_options(app_name, settings["platform"], settings["device"], extra_caps),
    )


def reset_ios_app(drv, caps):
    bundle_id = caps["bundleId"]
    drv.terminate_app(bundle_id)
    if not caps.get("noReset"):
        drv.execute_script("mobile: clearApp", {"bundleId": bundle_id})
    drv.activate_app(bundle_id)


def reset_app(drv, platform, app_name, extra_caps):
    """Bring the app back to a clean state without closing the Appium session."""
    caps = app_caps(app_name, platform) | (extra_caps or {})
    if platform == "ios":
        reset_ios_app(drv, caps)
        return
    package = caps["appPackage"]

    # Go to the home screen first: a system dialog left open by the previous
    # test could otherwise close the relaunched app (race condition).
    drv.press_keycode(3)   # KEYCODE_HOME
    drv.terminate_app(package)
    if not caps.get("noReset"):
        drv.execute_script("mobile: clearApp", {"appId": package})
        if caps.get("autoGrantPermissions"):
            # Clearing app data also revokes runtime permissions
            drv.execute_script("mobile: changePermissions", {
                "permissions": "all", "appPackage": package, "action": "grant",
            })
    drv.execute_script("mobile: startActivity", {
        "intent": f"{package}/{caps['appActivity']}",
        "wait": False,   # wait=True could hang; we wait explicitly below
    })
    running_in_foreground = 4
    try:
        WebDriverWait(drv, 10, poll_frequency=0.5).until(
            lambda d: d.query_app_state(package) == running_in_foreground
        )
    except TimeoutException:
        drv.activate_app(package)


# ----------------------------------------------------------------------
# Fixtures
# app / extra_caps are module-scoped so test modules can override them
# and the module-scoped appium_session can depend on them.
# ----------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    """App under test. Override in a test module to test another app."""
    return "settings"


@pytest.fixture(scope="module")
def extra_caps():
    """Additional capabilities. Override in a test module if needed."""
    return {}


@pytest.fixture(scope="module")
def appium_session(settings, app, extra_caps):
    """One Appium session per test module (none with --fresh-session)."""
    if settings["fresh_session"]:
        yield None
        return
    drv = create_driver(settings, app, extra_caps)
    yield drv
    drv.quit()


@pytest.fixture
def driver(request, settings, appium_session, app, extra_caps):
    """Driver with a clean app for each test. Saves evidence when a test fails."""
    if appium_session is None:
        drv = create_driver(settings, app, extra_caps)
    else:
        drv = appium_session
        reset_app(drv, settings["platform"], app, extra_caps)

    yield drv

    report = getattr(request.node, "rep_call", None)
    # Also collect evidence for expected failures (known bugs)
    if report is not None and (report.failed or hasattr(report, "wasxfail")):
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOTS_DIR / f"{request.node.name}_{stamp}.png"
        drv.save_screenshot(str(path))
        print(f"\nScreenshot saved: {path}")
        allure.attach.file(str(path), name="Screenshot", attachment_type=allure.attachment_type.PNG)
        allure.attach(drv.page_source, name="Page source (XML)", attachment_type=allure.attachment_type.XML)
    if appium_session is None:
        drv.quit()


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Store each phase's report on the test item so fixtures can see the result."""
    report = yield
    setattr(item, f"rep_{report.when}", report)
    return report
