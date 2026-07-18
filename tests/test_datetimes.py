"""Tests for the date/time factories."""

# stdlib
import datetime

# locals
from bagof.factories import get_factory


def test_datetime_builds_min() -> None:
    """A datetime hint builds the earliest representable datetime."""
    assert get_factory(datetime.datetime)() == datetime.datetime.min


def test_date_builds_min() -> None:
    """A date hint builds the earliest representable date."""
    assert get_factory(datetime.date)() == datetime.date.min


def test_datetime_is_more_specific_than_date() -> None:
    """`datetime` (a subclass of `date`) builds a datetime, not a date."""
    result = get_factory(datetime.datetime)()
    assert type(result) is datetime.datetime
