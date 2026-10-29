"""Tests for the numpy array factories."""

# stdlib
import sys

# dependencies
import pytest
import typing_extensions as tx

# locals
from bagof.factories import get_factory, get_factory_class
from bagof.factories.exceptions import FactoryError

np = pytest.importorskip("numpy")
factories_numpy = pytest.importorskip("bagof.factories.numpy")
hints_numpy = pytest.importorskip("bagof.hints.numpy")
ndarray, NDArray, dtype = (
    hints_numpy.ndarray, hints_numpy.NDArray, hints_numpy.dtype
)
L = tx.Literal


def test_ndarray_is_registered() -> None:
    assert get_factory_class(np.ndarray) is factories_numpy.NDArrayFactory
    assert get_factory_class(NDArray[np.float64]) is (
        factories_numpy.NDArrayFactory
    )
    assert "NDArrayFactory" in factories_numpy.__all__


@pytest.mark.parametrize(
    "hint,shape,expected_dtype",
    [
        # an unconstrained shape builds a 0-d array
        (np.ndarray, (), "float64"),
        (NDArray, (), "float64"),
        (NDArray[np.int32], (), "int32"),
        (NDArray[float], (), "float64"),
        (NDArray[np.number], (), "float64"),
        (ndarray[tx.Any, dtype[tx.Any]], (), "float64"),
        (ndarray[tx.Any, np.dtype], (), "float64"),
        # Literal sizes are used, free sizes are 0
        (ndarray[tx.Tuple[L[2], L[2]], dtype[np.float32]], (2, 2), "float32"),
        (ndarray[tx.Tuple[L[3], int], dtype[complex]], (3, 0), "complex128"),
        (ndarray[tx.Tuple[L[1, 3]], dtype[bool]], (1,), "bool"),
        (ndarray[tx.Tuple[()], dtype[int]], (), np.dtype(int).name),
        # a variadic part builds no dimension
        (ndarray[tx.Tuple[L[3], ...], dtype[np.float64]], (), "float64"),
        (
            ndarray[
                tx.Tuple[tx.Unpack[tx.Tuple[int, ...]], L[3]], dtype[np.int8]
            ],
            (3,),
            "int8",
        ),
    ],
)
def test_ndarray_builds_zeros(
    hint: tx.Any, shape: tx.Tuple[int, ...], expected_dtype: str
) -> None:
    result = get_factory(hint)()
    assert isinstance(result, np.ndarray)
    assert result.shape == shape
    assert result.dtype == np.dtype(expected_dtype)
    assert not result.any()


def test_ndarray_builds_a_new_array_each_time() -> None:
    factory = get_factory(ndarray[tx.Tuple[L[2]], dtype[float]])
    assert factory() is not factory()


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="numpy types subscript from 3.9"
)
def test_ndarray_subclass() -> None:
    class MyArray(np.ndarray):
        pass

    result = get_factory(MyArray[tx.Tuple[L[2]], tx.Any])()
    assert isinstance(result, MyArray)
    assert result.shape == (2,)


def test_ndarray_unbuildable_dtype() -> None:
    # A library that cannot build the dtype (as cupy, for `object`) fails
    # with a factory error.
    class Refusing:
        @staticmethod
        def zeros(shape: tx.Any, dtype: tx.Any = None) -> tx.Any:
            raise TypeError(f"Unsupported dtype {dtype}")

    class RefusingFactory(factories_numpy.NDArrayFactory):
        ARRAY = Refusing

    with pytest.raises(FactoryError, match="Unsupported dtype"):
        RefusingFactory(ndarray[tx.Any, dtype[object]])()
