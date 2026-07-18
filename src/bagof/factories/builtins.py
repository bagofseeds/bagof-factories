"""Factories for builtin types whose constructor requires arguments."""

__all__ = [
    "RangeFactory",
    "SliceFactory",
    "MemoryViewFactory",
]

# bags
from bagof.hints.typevars.co import T

# locals
from .base import Factory


class RangeFactory(Factory[T], register=range):
    """Factory for [`range`][] hints (an empty `range`)."""

    DEFAULT = range

    def __call__(self) -> range:
        """Return an empty range."""
        return range(0)


class SliceFactory(Factory[T], register=slice):
    """Factory for [`slice`][] hints (the full slice ``[:]``)."""

    DEFAULT = slice

    def __call__(self) -> slice:
        """Return the full slice (equivalent to ``[:]``)."""
        return slice(None)


class MemoryViewFactory(Factory[T], register=memoryview):
    """Factory for [`memoryview`][] hints (a view over empty bytes)."""

    DEFAULT = memoryview

    def __call__(self) -> memoryview:
        """Return a memoryview over empty bytes."""
        return memoryview(b"")
