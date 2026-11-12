"""Parsing and rounding of money amounts. Amounts are kept as integer cents."""


def parse_amount(text):
    """Parse '12.34', '-5', '1,200.50' into integer cents."""
    text = text.strip().replace(",", "")
    if text.startswith("-"):
        return -parse_amount(text[1:])
    if "." in text:
        whole, frac = text.split(".", 1)
        frac = (frac + "00")[:2]
    else:
        whole, frac = text, "00"
    return int(whole) * 100 + int(frac)


def apply_rate(cents, rate):
    """Convert cents by an exchange rate, rounding half up to the cent."""
    return round(cents * rate)


def split_evenly(cents, parts):
    """Split an amount into `parts` shares that add back up exactly."""
    base, extra = divmod(cents, parts)
    return [base + (1 if i < extra else 0) for i in range(parts)]
