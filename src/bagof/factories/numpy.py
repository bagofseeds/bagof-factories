"""Factories for numpy array types."""

__all__: list = []

# dependencies
import typing_extensions as tx

# bags
from bagof.core.magic import has_module, lazy_import

# locals
from ._arrays import ArrayFactory

if tx.TYPE_CHECKING:
    # Import the bare module so mkdocstrings resolves the `numpy.*`
    # cross-references in the docstrings below. Type-checking only.
    import numpy  # noqa: F401


# numpy is only imported once a numpy factory is actually used: the
# registry keys are forward references, resolved once `numpy` (or the hint
# module) has been imported by the caller -- see `Factory.register`.
if tx.TYPE_CHECKING or has_module("numpy"):

    class NDArrayFactory(
        ArrayFactory,
        register=(
            tx.ForwardRef("numpy.ndarray"),
            tx.ForwardRef("bagof.hints.numpy.ndarray"),
        ),
    ):
        """
        Factory for [`numpy.ndarray`][] hints (an array of zeros).

        !!! example
            ```pycon
            >>> import numpy as np
            >>> import typing_extensions as tx
            >>> from bagof.factories import get_factory
            >>> from bagof.hints.numpy import ndarray, dtype
            >>> L = tx.Literal
            >>> get_factory(ndarray[tx.Tuple[L[2], L[2]], dtype[int]])()
            array([[0, 0],
                   [0, 0]])
            ```
        """

        DEFAULT = lazy_import("numpy.ndarray")
        ARRAY = SCALARS = lazy_import("numpy")
        ARRAY_TYPE = lazy_import("numpy.ndarray")
        HINT_TYPE = lazy_import("bagof.hints.numpy.ndarray")

    __all__ += ["NDArrayFactory"]
