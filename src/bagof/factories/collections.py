"""Factories for collection types (sequences, mappings, sets, etc.)."""

__all__ = [
    "SequenceFactory",
    "MappingFactory",
    "SetFactory",
    "IterableFactory",
    "IteratorFactory",
]

# stdlib
import typing_extensions as tx  # noqa: I001
from collections import abc

# bags
from bagof.hints.typevars.co import ITERABLE, MAPPING, SEQUENCE

# locals
from .base import Factory


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
