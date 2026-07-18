"""Smoke tests for importing the package."""

import importlib


def test_package_is_importable() -> None:
    """The package should be importable after installation."""
    module = importlib.import_module("bagof.factories")
    assert module is not None


def test_package_exposes_version() -> None:
    """The package should expose a ``__version__`` string."""
    import bagof.factories

    assert isinstance(bagof.factories.__version__, str)


def test_public_api_is_exported() -> None:
    """The documented public names should be importable from the package."""
    import bagof.factories as factories

    for name in (
        "Factory",
        "FactoryRegistry",
        "register_factory",
        "get_factory",
        "get_factory_class",
        "NoneFactory",
        "UnionFactory",
        "LiteralFactory",
        "TypeVarFactory",
        "SequenceFactory",
        "MappingFactory",
        "AnnotatedFactory",
        "SetFactory",
        "IterableFactory",
        "IteratorFactory",
        "NumberFactory",
        "IntegralFactory",
        "RealFactory",
        "ComplexFactory",
        "RationalFactory",
        "EnumFactory",
        "RangeFactory",
        "SliceFactory",
        "MemoryViewFactory",
        "DateFactory",
        "DateTimeFactory",
        "UUIDFactory",
        "DictFactory",
        "TypedDictFactory",
    ):
        assert name in factories.__all__
        assert hasattr(factories, name)


def test_namespace_package_coexists_with_bagof_hints() -> None:
    """`bagof.factories` and `bagof.hints` share the `bagof` namespace."""
    import bagof.hints  # noqa: F401

    import bagof.factories  # noqa: F401
