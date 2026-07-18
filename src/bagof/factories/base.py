"""Base class for all factories."""

__all__ = [
    "Factory",
    "FactoryRegistry",
    "register_factory",
    "get_factory",
    "get_factory_class",
]

# dependencies
import typing_extensions as tx  # noqa: I001

# bags
from bagof.core.magic import (
    UNSET,
    MagicHint,
    get_from_registry,
    safe_issubclass,
)
from bagof.hints.typevars.co import T

# typing
ClassDecorator: tx.TypeAlias = tx.Callable[[T], T]
"""A class decorator (that takes a class and returns a class)."""

FactoryRegistry = tx.Dict[tx.Hashable, tx.Type["Factory"]]
"""A registry of factories, mapping type hints to factory classes."""

# constants
FACTORIES: FactoryRegistry = {}
"""The global registry of factories."""


class FactoryMetaclass(type(MagicHint)):
    """Metaclass for all factories."""

    def __new__(
        metacls,
        name: str,
        bases: tx.Tuple[type, ...],
        namespace: tx.Mapping[str, tx.Any],
        **kwargs: tx.Any,
    ) -> tx.Self:
        register = kwargs.pop("register", UNSET)
        cls = super().__new__(metacls, name, bases, namespace, **kwargs)
        if register is not UNSET:
            if register is True:
                register = (cls.DEFAULT,)
            if not isinstance(register, tuple):
                register = (register,)
            Factory.register(cls, *register)
        return cls


class Factory(MagicHint[T], metaclass=FactoryMetaclass):
    """
    Base class for magic factories.

    Factories build a default value for a type hint. They are registered in
    a global registry and looked up by type hint. The base factory builds a
    value by instantiating the hint's [`fallback`][bagof.core.magic.MagicHint]
    concrete type.

    A factory class can register itself for one or more type hints directly in
    its class definition with the `register` keyword:

    !!! example
        ```python
        class IntFactory(Factory[int], register=int):
            def __call__(self) -> int:
                return 42
        ```
    """

    def __call__(self) -> T:
        """Build a value for the hint from its fallback type."""
        return self.fallback()

    @tx.overload
    @staticmethod
    def register(
        factory: tx.Type["Factory"],
        *hints: tx.Unpack[tx.Tuple[tx.Any]],
        registry: FactoryRegistry = ...,
    ) -> tx.Type["Factory"]: ...

    @tx.overload
    @staticmethod
    def register(
        *hints: tx.Unpack[tx.Tuple[tx.Any]],
        registry: FactoryRegistry = ...,
    ) -> ClassDecorator: ...

    @staticmethod
    def register(  # type: ignore[misc]
        *hints: tx.Any,
        registry: FactoryRegistry = FACTORIES,
    ) -> tx.Any:
        """
        Register a factory class for one or more type hints.

        Can be used as a decorator or called directly:

        !!! example
            ```python
            @Factory.register(int)
            class IntFactory(Factory[int]):
                def __call__(self) -> int:
                    return 42
            ```

        Parameters
        ----------
        *hints
            One or more type hints to register the factory class for.
            Defaults to the class's `DEFAULT` hint if none are given.
        registry : FactoryRegistry
            The registry to register the factory class in.
            Defaults to the global registry.
        """
        if hints and safe_issubclass(hints[0], Factory):
            factory, *hints = hints
            return Factory.register(*hints, registry=registry)(factory)

        def decorator(cls: tx.Type[Factory]) -> tx.Type[Factory]:
            hints_ = hints or (cls.DEFAULT,)
            for hint in hints_:
                registry[hint] = cls
            return cls

        return decorator

    @staticmethod
    def get(
        hint: tx.Any,
        registry: FactoryRegistry = FACTORIES,
        fallback: tx.Optional[tx.Type["Factory"]] = UNSET,
    ) -> tx.Optional["Factory"]:
        """
        Get the best-matching factory for a given type hint.

        !!! example
            ```pycon
            >>> from bagof.factories import get_factory
            >>> get_factory(dict[str, int])
            DictFactory(dict[str, int])
            >>> get_factory(list[int])
            SequenceFactory(list[int])
            ```

        Parameters
        ----------
        hint
            The type hint for which to get a factory.
        registry : FactoryRegistry
            The registry to look up the factory in.
            Defaults to the global registry.
        fallback : Optional[Type[Factory]]
            The fallback factory class to use if no matching factory is found.
            Defaults to [`Factory`][]. Pass `None` explicitly to get `None`
            instead of a fallback.

        Returns
        -------
        Optional[Factory]
            The best-matching factory for the given type hint, or `None` if
            no matching factory is found and no fallback is provided.
        """
        cls = Factory.get_class(hint, registry, fallback)
        if cls is None:
            return None
        return cls(hint)

    @staticmethod
    def get_class(
        hint: tx.Any,
        registry: FactoryRegistry = FACTORIES,
        fallback: tx.Optional[tx.Type["Factory"]] = UNSET,
    ) -> tx.Optional[tx.Type["Factory"]]:
        """
        Get the best-matching factory class for a given type hint.

        !!! warning
            By default an unmatched hint returns the base
            [`Factory`][] class, never `None`. Pass `fallback=None`
            explicitly to get `None` back instead.

        Parameters
        ----------
        hint
            The type hint for which to get a factory class.
        registry : FactoryRegistry
            The registry to look up the factory class in.
            Defaults to the global registry.
        fallback : Optional[Type[Factory]]
            The fallback factory class to use if no matching factory is found.
            Defaults to [`Factory`][]. Pass `None` explicitly to get `None`
            instead of a fallback.

        Returns
        -------
        Optional[Type[Factory]]
            The best-matching factory class for the given type hint, or `None`
            if no matching factory is found and no fallback is provided.
        """
        if fallback is UNSET:
            fallback = Factory
        return get_from_registry(hint, registry) or fallback


register_factory = Factory.register
"""Backward-compatible alias for [`Factory.register`][]"""

get_factory = Factory.get
"""Backward-compatible alias for [`Factory.get`][]"""

get_factory_class = Factory.get_class
"""Backward-compatible alias for [`Factory.get_class`][]"""
