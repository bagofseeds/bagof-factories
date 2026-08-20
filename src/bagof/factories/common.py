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
    MultipleCauses,
    safe_get_args,
    safe_get_origin,
    safe_isinstance,
    safe_issubclass,
)
from bagof.hints.typevars.co import NONE, T

# locals
from ._compat import NoneType, UnionType
from .base import ClassDecorator, Factory, FactoryRegistry, get_factory
from .exceptions import FactoryError


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
        errors = []
        for arg in self.args:
            factory = get_factory(arg)
            try:
                return factory()
            except FactoryError as e:
                # Only a factory failure means "this member cannot be
                # built". Catching bare `TypeError` swallowed genuine bugs
                # in a member factory, and missed a member that failed with
                # a `ValueError` -- which killed the whole union.
                errors.append(e)
                continue
        raise self.type_error(
            "Cannot create an instance of any of the union types: "
            f"{' | '.join(str(arg) for arg in self.args)}"
        ) from MultipleCauses(errors)


class LiteralFactory(Factory[T], register=tx.Literal):
    """
    Factory for [`Literal`][typing.Literal] hints.

    Returns the first literal value (or `None` if the literal allows it).
    """

    DEFAULT = tx.Literal

    def __call__(self) -> T:
        """Return the first value of the literal."""
        if not self.args:
            raise self.type_error(
                "Cannot create an instance of an empty literal"
            )
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
    def register_metadata(
        cls, *hints: tx.Unpack[tx.Tuple[tx.Any, ...]]
    ) -> ClassDecorator:
        """
        Register a factory class for one or more pieces of annotation
        metadata.

        Distinct from [`Factory.register`][], which registers a factory
        for a *type hint* in the global registry; this one registers it
        for a piece of `Annotated` **metadata**.
        """

        def decorator(factory_cls: tx.Type[Factory]) -> tx.Type[Factory]:
            for hint in hints:
                cls._REGISTRY[hint] = factory_cls
            return factory_cls

        return decorator

    # Deprecated alias. `register` means "register for a type hint"
    # everywhere else, and a bare `@AnnotatedFactory.register` used to
    # silently register the decorated class as a metadata *key*.
    register = register_metadata

    @classmethod
    def _get_factory(cls, hint: tx.Any) -> tx.Optional[Factory]:
        factory = Factory.get(hint, registry=cls._REGISTRY, fallback=None)
        if factory is not None:
            return factory
        # Metadata is usually an *instance* (e.g. `re.compile(...)`),
        # whereas the registry is keyed by its type (e.g. `re.Pattern`),
        # so fall back to a lookup by type and pass the metadata itself
        # to the factory's constructor. Both sibling packages do this;
        # without it, only metadata registered by identity is ever found.
        if not isinstance(hint, type):
            factory_cls = Factory.get_class(
                type(hint), registry=cls._REGISTRY, fallback=None
            )
            if factory_cls is not None:
                return factory_cls(hint)
        return None

    @property
    def factories(self) -> tx.Tuple[Factory, ...]:
        """
        The factories that apply to this annotated hint, ordered from
        the origin type (least specific) to the last matching metadata
        entry (most specific, used first by `__call__`).
        """
        if getattr(self, "_factories", None) is None:
            self._factories = self._get_factories()
        return self._factories

    def _get_factories(self) -> tx.Tuple[Factory, ...]:
        origin = safe_get_origin(self.hint, unwrap=tx.Annotated)

        factories = []
        for arg in safe_get_args(self.hint):
            if safe_issubclass(arg, Factory):
                # Bind by keyword, so a factory class that needs its own
                # configuration fails with a `TypeError` naming what it
                # is missing rather than silently taking the annotated
                # type as that argument.
                arg = arg(hint=origin)
            if not safe_isinstance(arg, Factory):
                # Look into annotation registry
                arg = self._get_factory(arg)
            if safe_isinstance(arg, Factory):
                factories.append(arg)

        factories.insert(0, get_factory(origin))
        return tuple(factories)

    def __call__(self) -> T:
        """Build a value using the most specific applicable factory."""
        # The last entry wins: `factories` is ordered least- to
        # most-specific, and the origin factory is always at index 0, so
        # there is always at least one.
        return self.factories[-1]()
