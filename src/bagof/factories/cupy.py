"""Factories for cupy array types."""

__all__: list = []

# dependencies
import typing_extensions as tx

# bags
from bagof.core.magic import has_module, lazy_import

# locals
from ._arrays import ArrayFactory

if tx.TYPE_CHECKING:
    # Import the bare module so mkdocstrings resolves the `cupy.*`
    # cross-references in the docstrings below. Type-checking only.
    import cupy  # noqa: F401


# cupy is only imported once a cupy factory is actually used: the
# registry keys are forward references, resolved once `cupy` (or the hint
# module) has been imported by the caller -- see `Factory.register`.
if tx.TYPE_CHECKING or has_module("cupy"):  # pragma: no cover
    # cupy needs a CUDA toolchain and cannot be installed on a CPU runner,
    # so this factory is only ever type-checked, never exercised in CI.

    class CupyArrayFactory(
        ArrayFactory,
        register=(
            tx.ForwardRef("cupy.ndarray"),
            tx.ForwardRef("bagof.hints.cupy.ndarray"),
        ),
    ):
        """
        Factory for [`cupy.ndarray`][] hints (an array of zeros, on the
        current device).
        """

        DEFAULT = lazy_import("cupy.ndarray")
        ARRAY = SCALARS = lazy_import("cupy")
        ARRAY_TYPE = lazy_import("cupy.ndarray")
        HINT_TYPE = lazy_import("bagof.hints.cupy.ndarray")

    __all__ += ["CupyArrayFactory"]
