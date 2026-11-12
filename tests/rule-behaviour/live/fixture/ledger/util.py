"""Formatting helpers shared by the report and the generated bindings."""


def fmt_amt(cents, currency="EUR"):
    """Format an integer amount of cents for display: 123456 -> '1,234.56 EUR'."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100:,}.{cents % 100:02d} {currency}"


def pad(text, width):
    return str(text).ljust(width)
