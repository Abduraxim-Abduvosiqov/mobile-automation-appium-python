# Local environment for running the tests (macOS). Usage: source env.sh
#   JAVA_HOME: required by the UiAutomator2 driver (uses the JDK bundled with Android Studio)
#   PATH:      adds adb and emulator
#   .venv:     activates the Python virtual environment

export ANDROID_HOME="$HOME/Library/Android/sdk"
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools"

source "$(dirname "$0")/.venv/bin/activate" 2>/dev/null || source .venv/bin/activate
