"""Tests for the factory error family."""

# dependencies
import pytest
import typing_extensions as tx

# locals
from bagof.factories import get_factory
from bagof.factories.base import FACTORIES, Factory
from bagof.factories.exceptions import (
    FactoryError,
    TypeFactoryError,
    ValueFactoryError,
)


class _NoDefault:
    def __init__(self, x: int) -> None:
        self.x = x


def test_error_family_inherits_the_builtins() -> None:
    # Additive: every existing `except TypeError` caller keeps working.
    assert issubclass(TypeFactoryError, TypeError)
    assert issubclass(ValueFactoryError, ValueError)
    assert issubclass(TypeFactoryError, FactoryError)
    assert issubclass(ValueFactoryError, FactoryError)


def test_error_carries_this_and_message() -> None:
    factory = Factory(int)
    error = factory.error("boom")
    assert isinstance(error, FactoryError)
    assert error.this is factory
    assert "boom" in str(error)


def test_error_kind_selection() -> None:
    factory = Factory(int)
    assert isinstance(factory.type_error(), TypeFactoryError)
    assert isinstance(factory.value_error(), ValueFactoryError)


def test_unbuildable_type_raises_a_factory_error() -> None:
    # The base factory called `self.fallback()` raw, so a constructor
    # needing arguments raised a bare `TypeError` naming neither the hint
    # nor the factory.
    with pytest.raises(TypeFactoryError) as info:
        get_factory(_NoDefault)()
    assert "_NoDefault" in str(info.value)
    assert isinstance(info.value.__cause__, TypeError)


def test_union_skips_an_unbuildable_member() -> None:
    assert get_factory(tx.Union[_NoDefault, complex])() == 0j


def test_union_reports_every_member_failure_as_a_cause() -> None:

    class _AlsoNoDefault:
        def __init__(self, y: int) -> None:
            self.y = y

    with pytest.raises(FactoryError) as info:
        get_factory(tx.Union[_NoDefault, _AlsoNoDefault])()
    # The member failures used to be collected and then discarded.
    assert len(info.value.causes) == 2


def test_union_surfaces_a_broken_member_factory() -> None:

    class Broken(Factory):
        DEFAULT = complex

        def __call__(self) -> tx.Any:
            raise RuntimeError("this factory is broken")

    Factory.register(Broken, complex)
    try:
        with pytest.raises(RuntimeError, match="this factory is broken"):
            get_factory(tx.Union[complex, str])()
    finally:
        FACTORIES.pop(complex, None)


def test_empty_literal_and_enum_stay_type_errors() -> None:
    # locals
    import enum

    from bagof.factories.common import LiteralFactory
    from bagof.factories.enums import EnumFactory

    class Empty(enum.Enum):
        pass

    with pytest.raises(TypeError):
        LiteralFactory(tx.Literal)()
    with pytest.raises(TypeError):
        EnumFactory(Empty)()
