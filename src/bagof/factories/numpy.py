"""Factories for numpy array types."""

__all__: list = []

# dependencies
import typing_extensions as tx

# locals
from ._arrays import ArrayFactory

if tx.TYPE_CHECKING:
    # Import the bare module so mkdocstrings resolves the `numpy.*`
    # cross-references in the docstrings below. Type-checking only.
    import numpy  # noqa: F401
    import numpy as np
    from bagof.hints.numpy import ndarray as _hint_ndarray
else:
    try:
        import numpy as np
        from bagof.hints.numpy import ndarray as _hint_ndarray
    except ImportError:  # pragma: no cover
        np = _hint_ndarray = None

if tx.TYPE_CHECKING or np is not None:

    class NDArrayFactory(
        ArrayFactory, register=(np.ndarray, _hint_ndarray)
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

        DEFAULT = np.ndarray
        ARRAY = SCALARS = np
        ARRAY_TYPE = np.ndarray
        HINT_TYPE = _hint_ndarray

    __all__ += ["NDArrayFactory"]
