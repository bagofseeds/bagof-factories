"""Tests for the numeric factories."""

# stdlib
import decimal
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


def test_number_subclasses_build_themselves() -> None:
    """A `Number` subclass builds *itself*, not the abstract fallback."""
    # `NumberFactory.__call__` returned the `FALLBACK` class attribute
    # (always `int`), ignoring the fallback resolved from the hint -- so
    # every `numbers.Number` subclass without its own registration built
    # an `int` instead of itself.
    result = get_factory(decimal.Decimal)()
    assert result == 0
    assert type(result) is decimal.Decimal


def test_user_defined_number_subclass_builds_itself() -> None:

    class MyNumber(numbers.Number):
        def __init__(self, value: int = 0) -> None:
            self.value = value

    result = get_factory(MyNumber)()
    assert type(result) is MyNumber


def test_number_factory_handles_every_numeric_tower_rung() -> None:
    expected = {
        numbers.Number: int,
        numbers.Complex: complex,
        numbers.Real: float,
        numbers.Rational: fractions.Fraction,
        numbers.Integral: int,
    }
    for hint, want in expected.items():
        assert type(get_factory(hint)()) is want, hint
