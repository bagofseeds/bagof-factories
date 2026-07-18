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
from bagof.core.magic import MagicHint, get_from_registry
from bagof.hints.typevars.co import T

# typing
ClassDecorator: tx.TypeAlias = tx.Callable[[T], T]
"""A class decorator (that takes a class and returns a class)."""

FactoryRegistry = tx.Dict[tx.Hashable, tx.Type["Factory"]]
"""A registry of factories, mapping type hints to factory classes."""

# constants
FACTORIES: FactoryRegistry = {}
"""The global registry of factories."""


class Factory(MagicHint[T]):
    """
    Base class for magic factories.

    Factories build a default value for a type hint. They are registered in
    a global registry and looked up by type hint. The base factory builds a
    value by instantiating the hint's [`fallback`][bagof.core.magic.MagicHint]
    concrete type.
    """

    def __call__(self) -> T:
        """Build a value for the hint from its fallback type."""
        return self.fallback()


def register_factory(
    *hints: tx.Unpack[tx.Tuple[tx.Any]],
    registry: FactoryRegistry = FACTORIES,
) -> ClassDecorator:
    """
    Decorator to register a factory class for one or more type hints.

    Parameters
    ----------
    *hints
        One or more type hints to register the factory class for.
    registry : FactoryRegistry
        The registry to register the factory class in.
        Defaults to the global registry.

    !!! example
        ```python
        @register_factory(int)
        class IntFactory(Factory[int]):
            def __call__(self) -> int:
                return 42
        ```
    """

    def decorator(cls: tx.Type[Factory]) -> tx.Type[Factory]:
        for hint in hints:
            registry[hint] = cls
        return cls

    return decorator


def get_factory(
    hint: tx.Any,
    registry: FactoryRegistry = FACTORIES,
    fallback: tx.Optional[tx.Type[Factory]] = Factory,
) -> Factory:
    """
    Get the best-matching factory for a given type hint.

    Parameters
    ----------
    hint
        The type hint for which to get a factory.
    registry : FactoryRegistry
        The registry to look up the factory in.
        Defaults to the global registry.
    fallback : Optional[Type[Factory]]
        The fallback factory class to use if no matching factory is found.

    Returns
    -------
    Factory
        The best-matching factory for the given type hint.
    """
    factory_cls = get_factory_class(hint, registry, fallback)
    return factory_cls(hint)


def get_factory_class(
    hint: tx.Any,
    registry: FactoryRegistry = FACTORIES,
    fallback: tx.Optional[tx.Type[Factory]] = Factory,
) -> tx.Type[Factory]:
    """
    Get the best-matching factory class for a given type hint.

    Parameters
    ----------
    hint
        The type hint for which to get a factory class.
    registry : FactoryRegistry
        The registry to look up the factory class in.
        Defaults to the global registry.
    fallback : Optional[Type[Factory]]
        The fallback factory class to use if no matching factory is found.

    Returns
    -------
    Type[Factory]
        The best-matching factory class for the given type hint.
    """
    factory_cls = get_from_registry(hint, registry) or fallback
    # Parametrise the factory class with the hint, but only when it still
    # has free type parameters -- a factory that already binds a concrete
    # type (e.g. ``Factory[int]``) is not subscriptable.
    if getattr(factory_cls, "__parameters__", None):
        factory_cls = factory_cls[hint]
    return factory_cls
