"""Tests for the UUID factory."""

# stdlib
import uuid

# locals
from bagof.factories import get_factory


def test_uuid_builds_nil_uuid() -> None:
    """A UUID hint builds the nil UUID (all zeroes)."""
    result = get_factory(uuid.UUID)()
    assert isinstance(result, uuid.UUID)
    assert result == uuid.UUID(int=0)
    assert result.int == 0
