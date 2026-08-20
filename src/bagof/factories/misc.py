"""Factories for hints with no useful zero-argument constructor."""

__all__ = [
    "AnyFactory",
    "TypeFactory",
    "CallableFactory",
    "PatternFactory",
]

# stdlib
import re
from collections import abc

# dependencies
import typing_extensions as tx

# bags
from bagof.hints.typevars.co import T

# locals
from .base import Factory, get_factory


class AnyFactory(Factory[T], register=tx.Any):
    """
    Factory for [`Any`][typing.Any] (`None`).

    `Any` carries no information about what to build, and `None` is both
    the conventional stand-in for "no value" and itself a valid `Any`.
    """

    DEFAULT = tx.Any

    def __call__(self) -> T:
        """Return `None`."""
        return None


class TypeFactory(Factory[T], register=type):
    """
    Factory for [`type`][] and [`Type[T]`][typing.Type] hints.

    A parametrised hint builds the type it names (`Type[int]` builds
    `int`); a bare `type` builds [`object`][].
    """

    DEFAULT = type

    def __call__(self) -> T:
        """Return the parametrised type, or `object`."""
        args = self.args
        return args[0] if args else object


class CallableFactory(Factory[T], register=abc.Callable):
    """
    Factory for [`Callable`][collections.abc.Callable] hints.

    Builds a function that accepts anything and returns a value built for
    the annotated return type, so the result satisfies the hint rather
    than merely being callable.
    """

    DEFAULT = abc.Callable

    def __call__(self) -> T:
        """Return a function returning the return type's own default."""
        args = self.args
        returns = args[-1] if args else None

        if returns is None:
            def call(*args: tx.Any, **kwargs: tx.Any) -> tx.Any:
                return None
        else:
            def call(*args: tx.Any, **kwargs: tx.Any) -> tx.Any:
                return get_factory(returns)()

            call.__annotations__["return"] = returns

        return call


class PatternFactory(Factory[T], register=re.Pattern):
    """
    Factory for [`re.Pattern`][] hints (the empty pattern).

    `re.Pattern` cannot be instantiated directly; the empty pattern is
    the one that matches everywhere, so it is the neutral default.
    """

    DEFAULT = re.Pattern

    def __call__(self) -> T:
        """Return the compiled empty pattern."""
        return re.compile("")
