"""Common factories (none, union, literal, typevar, annotated)."""

__all__ = [
    "NoneFactory",
    "UnionFactory",
    "LiteralFactory",
    "TypeVarFactory",
    "AnnotatedFactory",
]

# dependencies
import typing_extensions as tx  # noqa: I001

# bags
from bagof.core.magic import (
    safe_get_args,
    safe_get_origin,
    safe_isinstance,
    safe_issubclass,
)
from bagof.hints.typevars.co import NONE, T

# locals
from ._compat import NoneType, UnionType
from .base import ClassDecorator, Factory, FactoryRegistry, get_factory


class NoneFactory(Factory[NONE], register=NoneType):
    """Factory for [`None`][] (always returns `None`)."""

    DEFAULT = NoneType

    def __call__(self) -> NONE:
        """Return `None`."""
        return None


class UnionFactory(Factory[T], register=(tx.Union, UnionType)):
    """
    Factory for [`Union`][typing.Union] hints.

    Returns `None` if the union is optional, otherwise builds a value for
    the first member type that can be instantiated.

    !!! example
        ```pycon
        >>> from bagof.factories import get_factory
        >>> factory = get_factory(int | str)
        >>> factory
        UnionFactory(int | str)
        >>> factory()
        0
        >>> get_factory(str | None)()  # optional -> None
        ```
    """

    DEFAULT = tx.Union

    def __call__(self) -> T:
        """Build a value for the first instantiable member of the union."""
        if NoneType in self.args:
            return None
        for arg in self.args:
            try:
                factory = get_factory(arg)
                return factory()
            except TypeError:
                continue
        raise TypeError(
            "Cannot create an instance of any of the union types: "
            f"{' | '.join(str(arg) for arg in self.args)}"
        )


class LiteralFactory(Factory[T], register=tx.Literal):
    """
    Factory for [`Literal`][typing.Literal] hints.

    Returns the first literal value (or `None` if the literal allows it).
    """

    DEFAULT = tx.Literal

    def __call__(self) -> T:
        """Return the first value of the literal."""
        if not self.args:
            raise TypeError("Cannot create an instance of an empty literal")
        if None in self.args:
            return None
        return self.args[0]


class TypeVarFactory(Factory[T], register=tx.TypeVar):
    """
    Factory for [`TypeVar`][typing.TypeVar] hints.

    Builds a value for the type the typevar resolves to (its default, bound
    or constraints).
    """

    DEFAULT = tx.TypeVar("T")

    def __call__(self) -> T:
        """Build a value for the type the typevar resolves to."""
        return get_factory(self.fallback)()


class AnnotatedFactory(Factory[T], register=tx.Annotated):
    """
    Factory for [`Annotated`][typing.Annotated] hints.

    Builds a value using the annotated origin type, unless a more specific
    factory is provided in the annotation metadata.
    """

    _REGISTRY: FactoryRegistry = {}

    @classmethod
    def register(cls, *hints: tx.Unpack[tx.Tuple[tx.Any]]) -> ClassDecorator:
        """Register a factory class for one or more annotation metadata."""

        def decorator(factory_cls: tx.Type[Factory]) -> tx.Type[Factory]:
            for hint in hints:
                cls._REGISTRY[hint] = factory_cls
            return factory_cls

        return decorator

    @classmethod
    def _get_factory(cls, hint: tx.Any) -> tx.Optional[Factory]:
        return Factory.get(hint, registry=cls._REGISTRY, fallback=None)

    @property
    def factories(self) -> tx.Tuple[Factory, ...]:
        """The factories that apply to this annotated hint, in order."""
        origin = safe_get_origin(self.hint, unwrap=tx.Annotated)

        factories = []
        for arg in safe_get_args(self.hint):
            if safe_issubclass(arg, Factory):
                arg = arg(origin)
            if not isinstance(arg, Factory):
                # Look into annotation registry
                arg = self._get_factory(arg)
            if safe_isinstance(arg, Factory):
                factories.append(arg)

        factories.insert(0, get_factory(origin))
        return tuple(factories)

    def __call__(self) -> T:
        """Build a value using the most specific applicable factory."""
        for factory in reversed(self.factories):
            return factory()
        raise TypeError(f"Cannot instantiate value for {self.hint}")
