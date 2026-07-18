"""Factory for TypedDict types."""

__all__ = [
    "TypedDictFactory",
]

# dependencies
import typing_extensions as tx  # noqa: I001

# bags
from bagof.core.magic import safe_get_origin

# locals
from .base import get_factory
from .collections import MappingFactory


class TypedDictFactory(MappingFactory, register=tx.TypedDict):
    """
    Factory for [`TypedDict`][typing.TypedDict] subclasses.

    Builds a dict populated with a value for each **required** key, built
    recursively from the key's annotation. Optional keys (from
    ``total=False`` or [`NotRequired`][typing.NotRequired]) are omitted, so
    the result is the minimal valid instance.

    A plain [`dict`][] is not a TypedDict, so it keeps using
    [`DictFactory`][bagof.factories.collections.DictFactory]: the registry
    matches `dict` to its exact key, which wins over the `TypedDict` entry.

    !!! example
        ```pycon
        >>> import typing_extensions as tx
        >>> from bagof.factories import get_factory
        >>> class Movie(tx.TypedDict):
        ...     title: str
        ...     year: int
        >>> factory = get_factory(Movie)
        >>> factory
        TypedDictFactory(<class '__main__.Movie'>)
        >>> factory()
        {'title': '', 'year': 0}
        ```
    """

    DEFAULT = tx.TypedDict

    def __call__(self) -> tx.Any:
        """Build a dict of the required keys, each from its annotation."""
        cls = safe_get_origin(self.hint)
        hints = tx.get_type_hints(cls)
        required = getattr(cls, "__required_keys__", frozenset(hints))
        return {
            key: get_factory(hint)()
            for key, hint in hints.items()
            if key in required
        }
