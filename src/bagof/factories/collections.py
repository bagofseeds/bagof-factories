"""Factories for collection types (sequences, mappings, sets, etc.)."""

__all__ = [
    "SequenceFactory",
    "MappingFactory",
    "SetFactory",
    "IterableFactory",
    "IteratorFactory",
    "TupleFactory",
]

# stdlib
import typing_extensions as tx  # noqa: I001
from collections import abc

# bags
from bagof.hints.typevars.co import ITERABLE, MAPPING, SEQUENCE, TUPLE

# locals
from .base import Factory, get_factory


class SequenceFactory(Factory[SEQUENCE], register=abc.Sequence):
    """Factory for [`Sequence`][collections.abc.Sequence] hints (a `list`)."""

    DEFAULT = abc.Sequence
    FALLBACK = list


class MappingFactory(Factory[MAPPING], register=abc.Mapping):
    """Factory for [`Mapping`][collections.abc.Mapping] hints (a `dict`)."""

    DEFAULT = abc.Mapping
    FALLBACK = dict


class SetFactory(Factory[ITERABLE], register=abc.Set):
    """Factory for [`Set`][collections.abc.Set] hints (a `set`)."""

    DEFAULT = abc.Set
    FALLBACK = set


class IterableFactory(
    Factory[ITERABLE], register=(abc.Iterable, abc.Container)
):
    """
    Factory for [`Iterable`][collections.abc.Iterable] hints (a `list`).

    Also covers [`Collection`][collections.abc.Collection],
    [`Reversible`][collections.abc.Reversible] and
    [`Container`][collections.abc.Container].
    """

    DEFAULT = abc.Iterable
    FALLBACK = list


class IteratorFactory(Factory[ITERABLE], register=abc.Iterator):
    """Factory for [`Iterator`][collections.abc.Iterator] (empty iterator)."""

    DEFAULT = abc.Iterator

    def __call__(self) -> tx.Iterator:
        """Return an empty iterator."""
        return iter(())


class TupleFactory(Factory[TUPLE], register=tuple):
    """
    Factory for [`tuple`][] hints.

    A fixed-length tuple builds a value for each element
    (``Tuple[int, str]`` -> ``(0, "")``). A variadic tuple
    (``Tuple[int, ...]``), an unparametrised tuple, or the empty tuple
    (``Tuple[()]``) builds an empty tuple, since no length is implied.
    """

    DEFAULT = tuple
    FALLBACK = tuple

    def __call__(self) -> TUPLE:
        """Build a value for each element of a fixed-length tuple."""
        args = self.args
        if not args:
            return ()
        if len(args) == 2 and args[1] is Ellipsis:
            return ()
        return tuple(get_factory(arg)() for arg in args)
