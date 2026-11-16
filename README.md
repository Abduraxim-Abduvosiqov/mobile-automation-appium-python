# Mobile test automation: Appium + Python + pytest

> **Note:** this is a learning project built with the help of [Claude](https://claude.ai) (AI).
> I am learning mobile test automation; the code was written together with AI,
> so I may not know every detail of it yet.

UI tests for Android and iOS apps built with **Appium**, **pytest** and the **Page Object Model**.

Apps under test:
- [Sauce Labs My Demo App](https://github.com/saucelabs/my-demo-app-android) (Android and iOS): login, catalog, cart, gestures, permissions
- Android Settings app: navigation

## Stack

| | |
|---|---|
| Language | Python 3 |
| Automation | Appium 3, UiAutomator2 driver (Android), XCUITest driver (iOS) |
| Test runner | pytest |
| Reporting | Allure |

## Project structure

```
conftest.py      Appium session, capabilities, CLI options, screenshot on failure
pages/           Page objects (base page, demo app screens, system dialogs)
tests/           Test scenarios and assertions
test_data/       Test users and product names
utils/           Helpers
```

## Features

- Page Object Model with per-platform locators: one page class works on Android and iOS
- Positive and negative scenarios, parametrized tests, `smoke` marker
- Gestures: scrolling, swiping, drawing with W3C Actions
- Runtime permission dialogs and mocked GPS location
- One Appium session per test module with a fast app reset between tests
- Known application bugs are kept as `xfail(strict=True)` tests
- Allure report with steps, screenshots and page source on failure

## Setup

1. Android Studio (SDK, emulator) and, for iOS, Xcode with a simulator
2. Appium and drivers:
   ```bash
   npm install -g appium
   appium driver install uiautomator2
   appium driver install xcuitest
   ```
3. Python dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Put the demo app builds into `apps/` (see `APPS` in `conftest.py`):
   - Android: `apps/mda-2.3.0-27.apk`
   - iOS simulator: `apps/ios/MyDemoApp.app`

## Running

Start an emulator (or boot an iPhone simulator) and the Appium server (`appium`), then:

```bash
source env.sh
pytest                                    # all tests on Android
pytest -m smoke                           # smoke tests only
pytest --platform ios                     # iOS (Android-only tests are skipped)
pytest --device emulator-5556             # a specific device
```

Allure report:

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```
