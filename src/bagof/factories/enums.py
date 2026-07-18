"""Factories for enumeration types."""

__all__ = [
    "EnumFactory",
]

# stdlib
import enum

# bags
from bagof.hints.typevars.co import T

# locals
from .base import Factory, register_factory


@register_factory(enum.Enum)
class EnumFactory(Factory[T]):
    """Factory for [`Enum`][enum.Enum] subclasses (the first member)."""

    DEFAULT = enum.Enum

    def __call__(self) -> T:
        """Return the first member of the enumeration."""
        for member in self.origin:
            return member
        raise TypeError(f"Cannot instantiate empty enum {self.origin}")
