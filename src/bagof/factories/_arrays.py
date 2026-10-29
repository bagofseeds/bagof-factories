"""
Shared base for the array factories (numpy / cupy / dask).

The three array libraries build a default array identically: an array of
zeros of the dtype and shape named in the hint, reinterpreted as the
requested subclass. This module factors that out so the per-library
modules stay a few lines each.
"""

__all__ = ["ArrayFactory", "scalar_maps"]

# stdlib
import numbers

# dependencies
import typing_extensions as tx

# bags
from bagof.core.magic import get_args_uw, safe_isinstance

# locals
from ._shapes import ShapeSpec, shape_spec
from .base import Factory


def scalar_maps(xp: tx.Any) -> tx.Tuple[dict, dict]:
    """
    Build the dtype lookup tables for an array/scalar namespace ``xp``.

    Returns
    -------
    py_to_scalar : dict
        Maps Python (and [`numbers`][]) types to the namespace's scalar
        type, e.g. ``float -> xp.floating``.
    abstract_to_py : dict
        Maps abstract scalar types (which cannot be passed to ``zeros``)
        to a concrete Python type, e.g. ``xp.floating -> float``.
    """
    py_to_scalar = {
        object: xp.object_,
        str: xp.str_,
        bool: xp.bool_,
        int: xp.integer,
        float: xp.floating,
        complex: xp.complexfloating,
        numbers.Number: xp.number,
        numbers.Complex: xp.complexfloating,
        numbers.Real: xp.floating,
        numbers.Rational: xp.floating,
        numbers.Integral: xp.integer,
    }
    abstract_to_py = {
        xp.generic: None,
        xp.number: None,
        xp.complexfloating: complex,
        xp.floating: float,
        xp.integer: int,
    }
    return py_to_scalar, abstract_to_py


class ArrayFactory(Factory[tx.Any]):
    """
    Base for array factories.

    A subclass sets the class attributes below; it does not override
    ``__call__``. An optional library's namespaces may be given lazily
    (see [`lazy_import`][bagof.core.magic.lazy_import]) so the class body
    never imports it.

    !!! note
        The concrete factories (``NDArrayFactory``, ``DaskArrayFactory``,
        ``CupyArrayFactory``) are only defined and registered when their
        backing library (numpy, dask or cupy) is installed.
    """

    #: The array namespace (numpy / cupy / dask.array) -- provides
    #: ``zeros`` and the concrete array type.
    ARRAY: tx.Any = None
    #: The scalar-type namespace (numpy, or cupy for cupy arrays) used to
    #: build the dtype tables. dask reuses numpy's, since dask arrays hold
    #: numpy dtypes.
    SCALARS: tx.Any = None
    #: The concrete array type (``numpy.ndarray`` / ``cupy.ndarray`` /
    #: ``dask.array.Array``).
    ARRAY_TYPE: tx.Any = None
    #: The ``bagof.hints`` stub for the array type. On Python 3.8 (where the
    #: real type is not subscriptable) a parametrised hint carries the stub
    #: as its origin, so it is mapped back to ``ARRAY_TYPE``.
    HINT_TYPE: tx.Any = None
    #: Whether the library supports ``array.view(cls)`` to reinterpret as a
    #: subclass. dask does not, and uses the subclass constructor instead.
    CAN_VIEW: bool = True

    @property
    def _array_origin(self) -> tx.Any:
        # Map the hint stub back to the real array type (see HINT_TYPE).
        origin = self.origin
        if origin is self.HINT_TYPE:
            return self.ARRAY_TYPE
        return origin

    @property
    def _target_dtype(self) -> tx.Any:
        # The concrete dtype named by ``ndarray[shape, dtype[X]]``, or
        # None for the library's default.
        args = self.args
        if len(args) < 2:
            return None
        dtype_args = get_args_uw(args[1])
        if not dtype_args:
            return None
        scalar = dtype_args[0]
        if scalar is tx.Any or not isinstance(scalar, type):
            # `Any` or a `TypeVar` (as in the bare `NDArray` alias).
            return None
        py_to_scalar, abstract_to_py = scalar_maps(self.SCALARS)
        scalar = py_to_scalar.get(scalar, scalar)
        return abstract_to_py.get(scalar, scalar)

    @property
    def _target_shape(self) -> tx.Optional[ShapeSpec]:
        # The shapes named by ``ndarray[shape, dtype]``, or None for any.
        args = self.args
        if not args:
            return None
        return shape_spec(args[0])

    def __call__(self) -> tx.Any:
        """
        Build an array of zeros of the dtype and shape named in the hint.

        The shape is the smallest one the hint accepts: each dimension
        constrained by a `Literal` takes its (first) size, each free
        dimension has size 0, and a variadic part has no dimension. An
        unconstrained shape therefore builds a 0-d array.
        """
        shape = self._target_shape
        shape_ = () if shape is None else shape.default_shape()
        try:
            value = self.ARRAY.zeros(shape_, dtype=self._target_dtype)
        except (TypeError, ValueError) as e:
            raise self.type_error(
                f"Cannot build a value for {self.hint}: {e}"
            ) from e
        origin = self._array_origin
        if not safe_isinstance(value, origin):
            value = value.view(origin) if self.CAN_VIEW else origin(value)
        return value
