"""Tests for the dask array factories."""

# dependencies
import pytest
import typing_extensions as tx

# locals
from bagof.factories import get_factory, get_factory_class

np = pytest.importorskip("numpy")
da = pytest.importorskip("dask.array")
factories_dask = pytest.importorskip("bagof.factories.dask")
hints_dask = pytest.importorskip("bagof.hints.dask")
L = tx.Literal


def test_dask_is_registered() -> None:
    assert get_factory_class(da.Array) is factories_dask.DaskArrayFactory
    assert get_factory_class(hints_dask.NDArray[np.float64]) is (
        factories_dask.DaskArrayFactory
    )


def test_dask_builds_zeros() -> None:
    hint = hints_dask.Array[
        tx.Tuple[L[2], L[3]], hints_dask.dtype[np.float32]
    ]
    result = get_factory(hint)()
    assert isinstance(result, da.Array)
    assert result.shape == (2, 3)
    assert result.dtype == np.dtype("float32")
    assert result.compute().tolist() == [[0.0] * 3] * 2


def test_dask_unconstrained() -> None:
    result = get_factory(da.Array)()
    assert isinstance(result, da.Array)
    assert result.shape == ()
