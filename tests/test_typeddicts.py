"""Tests for the TypedDict factory."""

# stdlib
import typing as std_typing

# dependencies
import pytest
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


def test_annotated_field_metadata_reaches_its_factory() -> None:
    # locals
    from bagof.factories.base import Factory
    from bagof.factories.common import AnnotatedFactory

    class Marker:
        pass

    @AnnotatedFactory.register_metadata(Marker)
    class MarkedFactory(Factory):
        DEFAULT = int

        def __init__(
            self, marker: tx.Any = None, hint: tx.Any = None
        ) -> None:
            super().__init__(int)
            self.marker = marker

        def __call__(self) -> int:
            return 42

    class Config(tx.TypedDict):
        retries: tx.Annotated[int, Marker()]
        name: str

    try:
        # `get_type_hints` without `include_extras=True` stripped the
        # metadata before `get_factory` ever saw the field.
        assert get_factory(Config)() == {"retries": 42, "name": ""}
    finally:
        AnnotatedFactory._REGISTRY.pop(Marker, None)


def test_annotated_field_without_metadata_factory_uses_the_type() -> None:
    class Config(tx.TypedDict):
        retries: tx.Annotated[int, "just a note"]

    assert get_factory(Config)() == {"retries": 0}


@pytest.mark.parametrize("TD", [tx.TypedDict, std_typing.TypedDict])
def test_typeddict_works_in_either_spelling(TD: tx.Any) -> None:
    # `typing.TypedDict` and `typing_extensions.TypedDict` are distinct
    # objects, so the `tx.TypedDict` registry key used to miss the
    # `typing` one, which fell through to `DictFactory` and built an
    # empty dict with every required key missing.
    class Film(TD):
        title: str
        year: int

    assert get_factory(Film)() == {"title": "", "year": 0}


@pytest.mark.parametrize("TD", [tx.TypedDict, std_typing.TypedDict])
def test_inherited_typeddict_builds_every_required_key(TD: tx.Any) -> None:
    class Film(TD):
        title: str

    class Extended(Film):
        rating: int

    assert get_factory(Extended)() == {"title": "", "rating": 0}


def _tracks_mixed_totality(TD: tx.Any) -> bool:
    """Whether this runtime records requiredness across a `total=` change.

    A capability probe rather than a version check. An older
    `typing.TypedDict` cannot express it -- it records neither which
    class declared a key nor a link back to the base -- so every
    inherited key is reported required.
    """

    class Base(TD, total=False):
        probe_optional: int

    class Child(Base):
        probe_required: int

    return set(getattr(Child, "__required_keys__", ())) == {"probe_required"}


@pytest.mark.parametrize("TD", [tx.TypedDict, std_typing.TypedDict])
def test_inherited_totality_in_either_spelling(TD: tx.Any) -> None:
    class Base(TD, total=False):
        optional_key: int

    class Child(Base):
        required_key: int

    if not _tracks_mixed_totality(TD):
        pytest.skip(
            "this runtime's TypedDict does not record requiredness across "
            "a total= change, so every inherited key reads as required"
        )

    # Only the child's own key is required, so only it is built.
    assert get_factory(Child)() == {"required_key": 0}
