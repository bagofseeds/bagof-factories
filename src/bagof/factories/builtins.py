"""Factories for builtin types whose constructor requires arguments."""

__all__ = [
    "RangeFactory",
    "SliceFactory",
    "MemoryViewFactory",
]

# bags
from bagof.hints.typevars.co import T

# locals
from .base import Factory, register_factory


@register_factory(range)
class RangeFactory(Factory[T]):
    """Factory for [`range`][] hints (an empty `range`)."""

    DEFAULT = range

    def __call__(self) -> range:
        """Return an empty range."""
        return range(0)


@register_factory(slice)
class SliceFactory(Factory[T]):
    """Factory for [`slice`][] hints (the full slice ``[:]``)."""

    DEFAULT = slice

    def __call__(self) -> slice:
        """Return the full slice (equivalent to ``[:]``)."""
        return slice(None)


@register_factory(memoryview)
class MemoryViewFactory(Factory[T]):
    """Factory for [`memoryview`][] hints (a view over empty bytes)."""

    DEFAULT = memoryview

    def __call__(self) -> memoryview:
        """Return a memoryview over empty bytes."""
        return memoryview(b"")
