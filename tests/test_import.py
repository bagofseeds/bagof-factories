"""Smoke tests for importing the package."""

import importlib
import subprocess
import sys
import textwrap

import pytest


def _run(code: str) -> str:
    # In a fresh interpreter: this test session has imported numpy already.
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


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


def test_import_does_not_import_optional_libraries() -> None:
    out = _run("""
        import sys
        import bagof.factories
        libs = {"numpy", "cupy", "dask", "pandas"}
        print(sorted(libs & {m.partition(".")[0] for m in sys.modules}))
    """)
    assert out == "[]"


@pytest.mark.parametrize("numpy_first", [False, True])
def test_numpy_factories_resolve_whenever_numpy_is_imported(
    numpy_first: bool,
) -> None:
    pytest.importorskip("numpy")
    first, then = "import numpy as np", "from bagof.factories import *"
    if not numpy_first:
        first, then = then, first
    out = _run(f"""
        {first}
        {then}
        from bagof.hints.numpy import NDArray
        assert get_factory_class(np.ndarray) is NDArrayFactory
        assert get_factory_class(NDArray[np.float64]) is NDArrayFactory
        assert NDArrayFactory.DEFAULT is np.ndarray
        print(repr(get_factory(NDArray[np.float64])()))
    """)
    assert out == "array(0.)"
