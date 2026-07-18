"""Tests for the base factory machinery."""

# dependencies
import pytest
import typing_extensions as tx

# locals
from bagof.factories.base import (
    Factory,
    FactoryRegistry,
    get_factory,
    get_factory_class,
    register_factory,
)


def test_base_factory_builds_from_fallback() -> None:
    """The base factory instantiates the concrete fallback of a hint."""
    assert get_factory(int)() == 0
    assert get_factory(str)() == ""
    assert get_factory(float)() == 0.0
    assert get_factory(bool)() is False


def test_base_factory_preserves_type() -> None:
    """The built value has exactly the hint's type."""
    assert type(get_factory(int)()) is int
    assert type(get_factory(str)()) is str


def test_get_factory_returns_factory_instance() -> None:
    """`get_factory` returns a `Factory` instance bound to the hint."""
    factory = get_factory(int)
    assert isinstance(factory, Factory)


def test_get_factory_class_falls_back_to_base() -> None:
    """An unregistered hint falls back to the base `Factory` class."""

    class Unregistered:
        pass

    cls = get_factory_class(Unregistered)
    assert isinstance(cls(Unregistered), Factory)


def test_get_factory_class_uses_custom_fallback() -> None:
    """A custom fallback is honoured when the hint is unregistered."""
    assert get_factory_class(int, {}, fallback=None) is None


def test_register_factory_into_custom_registry() -> None:
    """`register_factory` registers a class into the given registry."""
    registry: FactoryRegistry = {}

    @register_factory(int, registry=registry)
    class FortyTwoFactory(Factory[int]):
        def __call__(self) -> int:
            return 42

    assert registry[int] is FortyTwoFactory
    assert get_factory(int, registry)() == 42


def test_register_factory_as_decorator_returns_class() -> None:
    """The decorator returns the class unchanged."""
    registry: FactoryRegistry = {}

    @register_factory(str, registry=registry)
    class MyFactory(Factory[str]):
        pass

    assert issubclass(MyFactory, Factory)


def test_unregistered_registry_uses_fallback_base() -> None:
    """Looking up in an empty registry falls back to the base factory."""
    assert get_factory(int, {})() == 0


def test_base_factory_cannot_build_any() -> None:
    """The base factory cannot instantiate a pure `Any` hint."""
    with pytest.raises(TypeError):
        get_factory(tx.Any)()


def test_module_functions_are_aliases_of_static_methods() -> None:
    """The module-level helpers alias the `Factory` static methods."""
    assert register_factory is Factory.register
    assert get_factory is Factory.get
    assert get_factory_class is Factory.get_class


def test_register_keyword_registers_in_class_definition() -> None:
    """A factory can register itself via the `register` class keyword."""
    from bagof.factories.base import FACTORIES

    class _Marker:
        pass

    class MarkerFactory(Factory[int], register=_Marker):
        def __call__(self) -> int:
            return 42

    try:
        assert FACTORIES[_Marker] is MarkerFactory
        assert get_factory(_Marker)() == 42
    finally:
        FACTORIES.pop(_Marker, None)


def test_register_with_no_hints_uses_default() -> None:
    """Registering with no explicit hints uses the class's `DEFAULT` hint."""
    registry: FactoryRegistry = {}

    @register_factory(registry=registry)
    class DefaultingFactory(Factory[int]):
        DEFAULT = int

    assert registry[int] is DefaultingFactory


def test_register_called_directly_with_class() -> None:
    """`Factory.register(cls, *hints)` registers and returns the class."""
    registry: FactoryRegistry = {}

    class MyFactory(Factory[int]):
        def __call__(self) -> int:
            return 7

    returned = Factory.register(MyFactory, int, registry=registry)
    assert returned is MyFactory
    assert registry[int] is MyFactory


def test_get_returns_none_when_fallback_is_none() -> None:
    """`Factory.get` returns `None` when nothing matches and fallback=None."""
    assert Factory.get(int, {}, fallback=None) is None
