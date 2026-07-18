"""Tests for the collection factories."""

# stdlib
from collections import abc

# dependencies
import typing_extensions as tx

# locals
from bagof.factories import get_factory
from bagof.factories.collections import (
    DictFactory,
    IterableFactory,
    IteratorFactory,
    MappingFactory,
    SequenceFactory,
    SetFactory,
    TupleFactory,
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


def test_dict_hints_dispatch_to_dict_factory() -> None:
    """`dict` and its subclasses match the exact `dict` key."""
    from collections import OrderedDict, defaultdict

    assert isinstance(get_factory(dict), DictFactory)
    assert isinstance(get_factory(tx.Dict[str, int]), DictFactory)
    # subclasses of dict resolve to the dict factory via the MRO
    assert isinstance(get_factory(OrderedDict), DictFactory)
    assert isinstance(get_factory(defaultdict), DictFactory)
    # ... and build their own concrete type
    assert type(get_factory(OrderedDict)()) is OrderedDict


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


def test_fixed_tuple_builds_each_element() -> None:
    """A fixed-length tuple builds a value for each element."""
    assert get_factory(tx.Tuple[int, str])() == (0, "")
    assert get_factory(tx.Tuple[int, str, list])() == (0, "", [])


def test_fixed_tuple_preserves_element_types() -> None:
    """Each built element has its annotated type."""
    result = get_factory(tx.Tuple[int, str])()
    assert [type(x) for x in result] == [int, str]


def test_single_element_tuple() -> None:
    """A one-element tuple builds a one-element value."""
    assert get_factory(tx.Tuple[int])() == (0,)


def test_variadic_tuple_builds_empty() -> None:
    """A variadic tuple has no implied length, so it builds an empty tuple."""
    assert get_factory(tx.Tuple[int, ...])() == ()


def test_unparametrised_tuple_builds_empty() -> None:
    """A bare tuple builds an empty tuple."""
    assert get_factory(tuple)() == ()
    assert get_factory(tx.Tuple)() == ()


def test_empty_tuple_hint_builds_empty() -> None:
    """`Tuple[()]` builds the empty tuple."""
    assert get_factory(tx.Tuple[()])() == ()


def test_empty_tuple_python38_representation_builds_empty() -> None:
    """Python 3.8 spells `Tuple[()]` args as `((),)`; still build ``()``."""
    factory = TupleFactory(tx.Tuple[int])
    factory._args = ((),)  # simulate the Python 3.8 representation
    assert factory() == ()


def test_tuple_factory_directly() -> None:
    """The tuple factory can be used directly."""
    assert TupleFactory(tx.Tuple[int, str])() == (0, "")


def test_nested_tuple() -> None:
    """Nested tuples build recursively."""
    assert get_factory(tx.Tuple[int, tx.Tuple[str, int]])() == (0, ("", 0))
