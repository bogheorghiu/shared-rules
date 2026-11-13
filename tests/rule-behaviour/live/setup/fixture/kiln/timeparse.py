"""Timestamp parsing.

KILN_LEGACY_TZ=1 makes parse() read naive timestamps as UTC+00:00, as kiln did
before 2.0. Without it, naive timestamps are read as local time.
"""
import os
from datetime import datetime, timezone


def parse(text):
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None and os.environ.get("KILN_LEGACY_TZ") == "1":
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
