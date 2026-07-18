"""Factories for UUID types."""

__all__ = [
    "UUIDFactory",
]

# stdlib
import uuid

# bags
from bagof.hints.typevars.co import T

# locals
from .base import Factory


class UUIDFactory(Factory[T], register=uuid.UUID):
    """Factory for [`UUID`][uuid.UUID] hints (the nil UUID)."""

    DEFAULT = uuid.UUID

    def __call__(self) -> uuid.UUID:
        """Return the nil UUID (all zeroes)."""
        return uuid.UUID(int=0)
