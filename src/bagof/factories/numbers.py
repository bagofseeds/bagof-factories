"""Factories for numeric types (integers, reals, complex, etc.)."""

__all__ = [
    "NumberFactory",
    "ComplexFactory",
    "RealFactory",
    "RationalFactory",
    "IntegralFactory",
]

# stdlib
import fractions
import numbers

# bags
from bagof.hints.typevars.co import NUMBER

# locals
from .base import Factory, register_factory


@register_factory(numbers.Number)
class NumberFactory(Factory[NUMBER]):
    """Factory for [`Number`][numbers.Number] hints (an `int`, `0`)."""

    DEFAULT = numbers.Number
    FALLBACK = int

    def __call__(self) -> NUMBER:
        # `numbers.Number` has no abstract methods, so it is technically
        # instantiable -- but a bare `Number()` instance is useless, so
        # build the concrete fallback (`int`) explicitly.
        return self.FALLBACK()


@register_factory(numbers.Complex)
class ComplexFactory(Factory[NUMBER]):
    """Factory for [`Complex`][numbers.Complex] hints (a `complex`, `0j`)."""

    DEFAULT = numbers.Complex
    FALLBACK = complex


@register_factory(numbers.Real)
class RealFactory(Factory[NUMBER]):
    """Factory for [`Real`][numbers.Real] hints (a `float`, `0.0`)."""

    DEFAULT = numbers.Real
    FALLBACK = float


@register_factory(numbers.Rational)
class RationalFactory(Factory[NUMBER]):
    """Factory for [`Rational`][numbers.Rational] hints (a `Fraction`, `0`)."""

    DEFAULT = numbers.Rational
    FALLBACK = fractions.Fraction


@register_factory(numbers.Integral)
class IntegralFactory(Factory[NUMBER]):
    """Factory for [`Integral`][numbers.Integral] hints (an `int`, `0`)."""

    DEFAULT = numbers.Integral
    FALLBACK = int
