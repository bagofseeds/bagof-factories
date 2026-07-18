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
from .base import Factory


class NumberFactory(Factory[NUMBER], register=numbers.Number):
    """Factory for [`Number`][numbers.Number] hints (an `int`, `0`)."""

    DEFAULT = numbers.Number
    FALLBACK = int

    def __call__(self) -> NUMBER:
        # `numbers.Number` has no abstract methods, so it is technically
        # instantiable -- but a bare `Number()` instance is useless, so
        # build the concrete fallback (`int`) explicitly.
        return self.FALLBACK()


class ComplexFactory(Factory[NUMBER], register=numbers.Complex):
    """Factory for [`Complex`][numbers.Complex] hints (a `complex`, `0j`)."""

    DEFAULT = numbers.Complex
    FALLBACK = complex


class RealFactory(Factory[NUMBER], register=numbers.Real):
    """Factory for [`Real`][numbers.Real] hints (a `float`, `0.0`)."""

    DEFAULT = numbers.Real
    FALLBACK = float


class RationalFactory(Factory[NUMBER], register=numbers.Rational):
    """Factory for [`Rational`][numbers.Rational] hints (a `Fraction`, `0`)."""

    DEFAULT = numbers.Rational
    FALLBACK = fractions.Fraction


class IntegralFactory(Factory[NUMBER], register=numbers.Integral):
    """Factory for [`Integral`][numbers.Integral] hints (an `int`, `0`)."""

    DEFAULT = numbers.Integral
    FALLBACK = int
