"""Tests for the common factories (none, union, literal, etc.)."""

# dependencies
import pytest
import typing_extensions as tx

# locals
from bagof.factories import get_factory
from bagof.factories.common import (
    AnnotatedFactory,
    LiteralFactory,
    NoneFactory,
    UnionFactory,
)


def test_none_factory_builds_none() -> None:
    """The none factory always builds `None`."""
    assert NoneFactory(type(None))() is None
    assert get_factory(type(None))() is None


def test_optional_union_builds_none() -> None:
    """An optional union builds `None`."""
    assert get_factory(tx.Optional[int])() is None
    assert UnionFactory(tx.Optional[int])() is None


def test_union_builds_first_instantiable_member() -> None:
    """A non-optional union builds a value for its first member."""
    assert get_factory(tx.Union[int, str])() == 0
    assert get_factory(tx.Union[str, int])() == ""


def test_union_raises_when_no_member_is_instantiable() -> None:
    """A union of non-instantiable members raises `TypeError`."""
    with pytest.raises(TypeError):
        UnionFactory(tx.Union[tx.Any, tx.Any])()


def test_literal_builds_first_value() -> None:
    """A literal builds its first value."""
    assert get_factory(tx.Literal["a", "b"])() == "a"
    assert get_factory(tx.Literal[1, 2, 3])() == 1


def test_literal_with_none_builds_none() -> None:
    """A literal that allows `None` builds `None`."""
    assert get_factory(tx.Literal[None, 1])() is None


def test_empty_literal_raises() -> None:
    """An empty literal cannot be instantiated."""
    factory = LiteralFactory(tx.Literal["x"])
    factory.hint = tx.Literal  # force an argument-less literal
    factory._args = ()
    with pytest.raises(TypeError):
        factory()


def test_annotated_builds_origin_value() -> None:
    """An annotated hint with plain metadata builds the origin's value."""
    assert get_factory(tx.Annotated[int, "meta"])() == 0
    assert get_factory(tx.Annotated[tx.List[int], "meta"])() == []


def test_annotated_uses_factory_class_in_metadata() -> None:
    """A `Factory` subclass in the metadata overrides the origin factory."""
    assert get_factory(tx.Annotated[int, NoneFactory])() is None


def test_annotated_factories_property_includes_origin() -> None:
    """The annotated factories always include the origin factory first."""
    factory = AnnotatedFactory(tx.Annotated[int, "meta"])
    assert len(factory.factories) >= 1
