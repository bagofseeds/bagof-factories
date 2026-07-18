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
from .base import Factory, register_factory


@register_factory(abc.Sequence)
class SequenceFactory(Factory[SEQUENCE]):
    """Factory for [`Sequence`][collections.abc.Sequence] hints (a `list`)."""

    DEFAULT = abc.Sequence
    FALLBACK = list


@register_factory(abc.Mapping)
class MappingFactory(Factory[MAPPING]):
    """Factory for [`Mapping`][collections.abc.Mapping] hints (a `dict`)."""

    DEFAULT = abc.Mapping
    FALLBACK = dict


@register_factory(abc.Set)
class SetFactory(Factory[ITERABLE]):
    """Factory for [`Set`][collections.abc.Set] hints (a `set`)."""

    DEFAULT = abc.Set
    FALLBACK = set


@register_factory(abc.Iterable, abc.Container)
class IterableFactory(Factory[ITERABLE]):
    """
    Factory for [`Iterable`][collections.abc.Iterable] hints (a `list`).

    Also covers [`Collection`][collections.abc.Collection],
    [`Reversible`][collections.abc.Reversible] and
    [`Container`][collections.abc.Container].
    """

    DEFAULT = abc.Iterable
    FALLBACK = list


@register_factory(abc.Iterator)
class IteratorFactory(Factory[ITERABLE]):
    """Factory for [`Iterator`][collections.abc.Iterator] (empty iterator)."""

    DEFAULT = abc.Iterator

    def __call__(self) -> tx.Iterator:
        """Return an empty iterator."""
        return iter(())
