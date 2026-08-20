"""Exceptions raised by factories when a value cannot be built."""

__all__ = ["FactoryError", "ValueFactoryError", "TypeFactoryError"]

# bags
from bagof.core.magic import MagicError


class FactoryError(MagicError):
    """
    Base class for all factory errors.

    !!! note
        The concrete [`ValueFactoryError`][] and [`TypeFactoryError`][]
        subclasses also inherit from the built-in [`ValueError`][] and
        [`TypeError`][], so they can be caught as either.
    """

    def __init__(self, *args, **kwargs) -> None:
        if "factory" in kwargs:
            kwargs["this"] = kwargs.pop("factory")
        super().__init__(*args, **kwargs)


class ValueFactoryError(FactoryError, ValueError):
    """Raised when a value cannot be built for a hint's arguments."""
    ...


class TypeFactoryError(FactoryError, TypeError):
    """Raised when a value cannot be built for a hint's type."""
    ...
