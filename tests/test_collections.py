"""Tests for the collection factories."""

# stdlib
from collections import abc

# dependencies
import typing_extensions as tx

# locals
from bagof.factories import get_factory
from bagof.factories.collections import MappingFactory, SequenceFactory


def test_sequence_factory_builds_empty_list() -> None:
    """A sequence hint builds an empty list."""
    assert SequenceFactory(abc.Sequence)() == []
    assert type(SequenceFactory(abc.Sequence)()) is list


def test_mapping_factory_builds_empty_dict() -> None:
    """A mapping hint builds an empty dict."""
    assert MappingFactory(abc.Mapping)() == {}
    assert type(MappingFactory(abc.Mapping)()) is dict


def test_get_factory_dispatches_sequences() -> None:
    """Parametrised sequence hints dispatch to the sequence factory."""
    assert get_factory(tx.List[int])() == []
    assert get_factory(tx.Sequence[str])() == []


def test_get_factory_dispatches_mappings() -> None:
    """Parametrised mapping hints dispatch to the mapping factory."""
    assert get_factory(tx.Dict[str, int])() == {}
    assert get_factory(tx.Mapping[str, int])() == {}
