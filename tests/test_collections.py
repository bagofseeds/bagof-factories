"""Tests for the collection factories."""

# stdlib
from collections import abc

# dependencies
import typing_extensions as tx

# locals
from bagof.factories import get_factory
from bagof.factories.collections import (
    IterableFactory,
    IteratorFactory,
    MappingFactory,
    SequenceFactory,
    SetFactory,
)


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


def test_set_factory_builds_empty_set() -> None:
    """A set hint builds an empty set."""
    assert SetFactory(abc.Set)() == set()
    assert type(SetFactory(abc.Set)()) is set


def test_get_factory_dispatches_sets() -> None:
    """Abstract and mutable set hints dispatch to the set factory."""
    assert get_factory(tx.AbstractSet[int])() == set()
    assert get_factory(tx.MutableSet[int])() == set()


def test_iterable_factory_builds_empty_list() -> None:
    """An iterable hint builds an empty list."""
    assert IterableFactory(abc.Iterable)() == []
    assert type(IterableFactory(abc.Iterable)()) is list


def test_get_factory_dispatches_iterables() -> None:
    """Iterable, Collection, Reversible and Container dispatch to a list."""
    assert get_factory(tx.Iterable[int])() == []
    assert get_factory(tx.Collection[int])() == []
    assert get_factory(tx.Reversible[int])() == []
    assert get_factory(tx.Container[int])() == []


def test_iterator_factory_builds_empty_iterator() -> None:
    """An iterator hint builds an empty iterator."""
    result = get_factory(tx.Iterator[int])()
    assert iter(result) is result
    assert list(result) == []


def test_iterator_is_more_specific_than_iterable() -> None:
    """`Iterator` dispatches to the iterator factory, not the iterable one."""
    assert isinstance(get_factory(abc.Iterator), IteratorFactory)
    assert isinstance(get_factory(abc.Iterable), IterableFactory)
