"""Tests for the numeric factories."""

# stdlib
import fractions
import numbers

# locals
from bagof.factories import get_factory


def test_integral_builds_zero_int() -> None:
    """An integral hint builds ``0``."""
    result = get_factory(numbers.Integral)()
    assert result == 0
    assert type(result) is int


def test_real_builds_zero_float() -> None:
    """A real hint builds ``0.0``."""
    result = get_factory(numbers.Real)()
    assert result == 0.0
    assert type(result) is float


def test_complex_builds_zero_complex() -> None:
    """A complex hint builds ``0j``."""
    result = get_factory(numbers.Complex)()
    assert result == 0j
    assert type(result) is complex


def test_rational_builds_zero_fraction() -> None:
    """A rational hint builds ``Fraction(0, 1)``."""
    result = get_factory(numbers.Rational)()
    assert result == 0
    assert type(result) is fractions.Fraction


def test_number_builds_zero_int() -> None:
    """A bare `Number` hint builds ``0`` rather than a useless instance."""
    result = get_factory(numbers.Number)()
    assert result == 0
    assert type(result) is int


def test_concrete_numeric_types_are_unaffected() -> None:
    """Concrete numeric types still build via their own constructor."""
    assert get_factory(int)() == 0
    assert get_factory(float)() == 0.0
    assert get_factory(complex)() == 0j
    assert get_factory(bool)() is False
