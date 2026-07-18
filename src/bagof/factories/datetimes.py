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
from .base import Factory, register_factory


@register_factory(datetime.datetime)
class DateTimeFactory(Factory[T]):
    """Factory for [`datetime`][datetime.datetime] hints (`datetime.min`)."""

    DEFAULT = datetime.datetime

    def __call__(self) -> datetime.datetime:
        """Return the earliest representable datetime."""
        return datetime.datetime.min


@register_factory(datetime.date)
class DateFactory(Factory[T]):
    """Factory for [`date`][datetime.date] hints (`date.min`)."""

    DEFAULT = datetime.date

    def __call__(self) -> datetime.date:
        """Return the earliest representable date."""
        return datetime.date.min
