"""Factories for enumeration types."""

__all__ = [
    "EnumFactory",
]

# stdlib
import enum

# bags
from bagof.hints.typevars.co import T

# locals
from .base import Factory


class EnumFactory(Factory[T], register=enum.Enum):
    """Factory for [`Enum`][enum.Enum] subclasses (the first member)."""

    DEFAULT = enum.Enum

    def __call__(self) -> T:
        """Return the first member of the enumeration."""
        for member in self.origin:
            return member
        raise TypeError(f"Cannot instantiate empty enum {self.origin}")
