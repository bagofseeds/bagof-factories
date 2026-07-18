"""Tests for the enum factory."""

# stdlib
import enum

# dependencies
import pytest

# locals
from bagof.factories import get_factory
from bagof.factories.enums import EnumFactory


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Grade(enum.IntEnum):
    A = 90
    B = 80


def test_enum_builds_first_member() -> None:
    """An enum hint builds its first member."""
    assert get_factory(Color)() is Color.RED


def test_int_enum_builds_first_member() -> None:
    """An `IntEnum` hint builds its first member."""
    assert get_factory(Grade)() is Grade.A


def test_enum_factory_directly() -> None:
    """The enum factory can be used directly on the enum class."""
    assert EnumFactory(Color)() is Color.RED


def test_empty_enum_raises() -> None:
    """An empty enum cannot be instantiated."""

    class Empty(enum.Enum):
        pass

    with pytest.raises(TypeError):
        EnumFactory(Empty)()
