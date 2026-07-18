"""Tests for the TypedDict factory."""

# dependencies
import typing_extensions as tx

# locals
from bagof.factories import get_factory
from bagof.factories.collections import DictFactory
from bagof.factories.typeddicts import TypedDictFactory


class Movie(tx.TypedDict):
    name: str
    year: int
    tags: tx.List[str]


class Partial(tx.TypedDict, total=False):
    a: int
    b: str


class Mixed(tx.TypedDict):
    required: int
    optional: tx.NotRequired[str]


class Nested(tx.TypedDict):
    movie: Movie
    count: int


def test_typeddict_builds_required_fields() -> None:
    """A total TypedDict builds a value for every field."""
    assert get_factory(Movie)() == {"name": "", "year": 0, "tags": []}


def test_typeddict_preserves_field_types() -> None:
    """Each built field has its annotated type."""
    result = get_factory(Movie)()
    assert type(result["name"]) is str
    assert type(result["year"]) is int
    assert type(result["tags"]) is list


def test_total_false_builds_empty() -> None:
    """A `total=False` TypedDict has no required keys, so it builds ``{}``."""
    assert get_factory(Partial)() == {}


def test_not_required_keys_are_omitted() -> None:
    """`NotRequired` keys are omitted from the built dict."""
    assert get_factory(Mixed)() == {"required": 0}


def test_nested_typeddict() -> None:
    """A TypedDict field that is itself a TypedDict builds recursively."""
    assert get_factory(Nested)() == {
        "movie": {"name": "", "year": 0, "tags": []},
        "count": 0,
    }


def test_typeddict_factory_directly() -> None:
    """The TypedDict factory can be used directly on the class."""
    assert TypedDictFactory(Movie)() == {"name": "", "year": 0, "tags": []}


def test_plain_dict_is_not_hijacked() -> None:
    """A plain dict is unaffected: its exact key beats the TypedDict entry."""
    assert get_factory(dict)() == {}
    assert get_factory(tx.Dict[str, int])() == {}
    assert isinstance(get_factory(dict), DictFactory)
    assert not isinstance(get_factory(dict), TypedDictFactory)


def test_typeddict_dispatches_to_typeddict_factory() -> None:
    """A TypedDict hint dispatches to the TypedDict factory, not to dict."""
    assert isinstance(get_factory(Movie), TypedDictFactory)
