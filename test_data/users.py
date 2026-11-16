"""
Test users of the Sauce Labs demo app.

These are public demo credentials shown on the app's login screen.
Real projects should load credentials from environment variables or a secret store.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    username: str
    password: str


VALID_USER = User("bod@example.com", "10203040")
LOCKED_USER = User("alice@example.com", "10203040")

# The iOS build of the app uses different demo users
VALID_USERS = {
    "android": VALID_USER,
    "ios": User("bob@example.com", "10203040"),
}
