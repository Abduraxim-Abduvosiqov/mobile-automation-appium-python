"""Price helpers."""
import re


def parse_price(text: str) -> float:
    """Extract a number from a price string: "$ 29.99", "$29.99" -> 29.99."""
    match = re.search(r"\d+(?:[.,]\d+)?", text)
    if not match:
        raise ValueError(f"No price found in: {text!r}")
    return float(match.group().replace(",", "."))
