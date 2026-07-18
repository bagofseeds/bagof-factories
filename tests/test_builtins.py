"""Tests for the builtin-type factories (range, slice, memoryview)."""

# locals
from bagof.factories import get_factory


def test_range_builds_empty_range() -> None:
    """A range hint builds an empty range."""
    result = get_factory(range)()
    assert isinstance(result, range)
    assert list(result) == []


def test_slice_builds_full_slice() -> None:
    """A slice hint builds the full slice ``[:]``."""
    result = get_factory(slice)()
    assert result == slice(None)


def test_memoryview_builds_empty_view() -> None:
    """A memoryview hint builds a view over empty bytes."""
    result = get_factory(memoryview)()
    assert isinstance(result, memoryview)
    assert result.tobytes() == b""
