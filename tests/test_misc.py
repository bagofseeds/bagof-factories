"""Tests for the factories in `bagof.factories.misc`."""

# stdlib
import re
from collections import abc

# dependencies
import pytest
import typing_extensions as tx

# locals
from bagof.factories import get_factory
from bagof.factories.misc import (
    AnyFactory,
    CallableFactory,
    PatternFactory,
    TypeFactory,
)


def test_any_builds_none() -> None:
    assert get_factory(tx.Any)() is None
    assert isinstance(get_factory(tx.Any), AnyFactory)


@pytest.mark.parametrize(
    "hint,expected",
    [(tx.Type[int], int), (tx.Type[str], str), (type, object)],
)
def test_type_builds_the_named_type(hint: tx.Any, expected: type) -> None:
    # `type()` takes 1 or 3 arguments, so the base factory raised.
    assert get_factory(hint)() is expected
    assert isinstance(get_factory(hint), TypeFactory)


def test_callable_builds_a_function_returning_the_return_default() -> None:
    built = get_factory(tx.Callable[[int], str])()
    assert callable(built)
    assert built(1) == ""
    assert built.__annotations__["return"] is str


def test_callable_accepts_any_arguments() -> None:
    built = get_factory(tx.Callable[[int, str], int])()
    assert built(1, "a") == 0
    assert built() == 0
    assert built(whatever=True) == 0


def test_bare_callable_returns_none() -> None:
    built = get_factory(abc.Callable)()
    assert built() is None


def test_callable_is_registered() -> None:
    assert isinstance(get_factory(tx.Callable[[], int]), CallableFactory)


def test_pattern_builds_the_empty_pattern() -> None:
    built = get_factory(re.Pattern)()
    assert isinstance(built, re.Pattern)
    assert built.pattern == ""
    assert built.match("anything") is not None
    assert isinstance(get_factory(re.Pattern), PatternFactory)
