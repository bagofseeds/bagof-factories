"""Factories for collection types (sequences, mappings)."""

__all__ = [
    "SequenceFactory",
    "MappingFactory",
]

# stdlib
from collections import abc

# bags
from bagof.hints.typevars.co import MAPPING, SEQUENCE

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
