"""Factories for date and time types."""

__all__ = [
    "DateFactory",
    "DateTimeFactory",
]

# stdlib
import datetime

# bags
from bagof.hints.typevars.co import T

# locals
from .base import Factory


class DateTimeFactory(Factory[T], register=datetime.datetime):
    """Factory for [`datetime`][datetime.datetime] hints (`datetime.min`)."""

    DEFAULT = datetime.datetime

    def __call__(self) -> datetime.datetime:
        """Return the earliest representable datetime."""
        return datetime.datetime.min


class DateFactory(Factory[T], register=datetime.date):
    """Factory for [`date`][datetime.date] hints (`date.min`)."""

    DEFAULT = datetime.date

    def __call__(self) -> datetime.date:
        """Return the earliest representable date."""
        return datetime.date.min
