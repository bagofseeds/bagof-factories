"""Smoke tests for importing the package."""

import importlib
import pathlib
import subprocess
import sys
import textwrap


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


# --- lazy registry keys (bagof-core-magic#75) -------------------------


def _run(code: str, *path: str) -> str:
    """Run `code` in a fresh interpreter, with `path` prepended."""
    prelude = f"import sys; sys.path[:0] = {list(map(str, path))!r}\n"
    result = subprocess.run(
        [sys.executable, "-c", prelude + textwrap.dedent(code)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_import_does_not_import_backends() -> None:
    """Importing the package must not import any optional backend."""
    out = _run("""
        import sys
        import bagof.factories
        backends = ("dask", "cupy", "pandas")
        print(sorted(m for m in sys.modules if m.split(".")[0] in backends))
    """)
    assert out.strip() == "[]"


def test_forward_ref_key_resolves_after_import(tmp_path: pathlib.Path) -> None:
    """A ForwardRef key stays pending until its module is imported."""
    (tmp_path / "_bagof_lazybackend.py").write_text("class Array:\n    pass\n")
    out = _run(
        """
        import sys
        from typing import ForwardRef
        from bagof.core.magic import pending
        from bagof.factories import Factory, get_factory_class

        @Factory.register(ForwardRef("_bagof_lazybackend.Array"))
        class ArrayFactory(Factory):
            pass

        print("_bagof_lazybackend" in sys.modules)
        print(len(pending()))
        import _bagof_lazybackend
        print(get_factory_class(_bagof_lazybackend.Array) is ArrayFactory)
        print(len(pending()))
        """,
        tmp_path,
    )
    assert out.split() == ["False", "1", "True", "0"]


def test_plain_key_after_forward_ref_wins(tmp_path: pathlib.Path) -> None:
    """A newer plain key beats an older, already-resolvable ForwardRef."""
    (tmp_path / "_bagof_lazybackend2.py").write_text(
        "class Array:\n    pass\n"
    )
    out = _run(
        """
        from typing import ForwardRef
        from bagof.factories import Factory, get_factory_class

        @Factory.register(ForwardRef("_bagof_lazybackend2.Array"))
        class Old(Factory):
            pass

        import _bagof_lazybackend2

        @Factory.register(_bagof_lazybackend2.Array)
        class New(Factory):
            pass

        print(get_factory_class(_bagof_lazybackend2.Array) is New)
        """,
        tmp_path,
    )
    assert out.split() == ["True"]
