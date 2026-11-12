from decimal import Decimal, InvalidOperation


def parse_amount(text):
    """'1,234.50' -> Decimal('1234.50'); None for text that is not an amount."""
    try:
        return Decimal(text.replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return None


def group_totals(rows, key):
    """Sum row['amount'] per row[key], skipping rows whose amount does not parse."""
    out = {}
    for r in rows:
        amt = parse_amount(r.get("amount"))
        if amt is not None:
            out[r[key]] = out.get(r[key], Decimal("0")) + amt
    return out
