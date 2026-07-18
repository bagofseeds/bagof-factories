"""
A typevar hint must build exactly like the hint it is bound to.

Factories introspect `origin`/`args`/`fallback` to build a value. Since
`MagicHint.UNWRAP` includes `TypeVar`, a typevar resolves to its bound
(or default, or constraints) first, so that building a value directly with
a typevar, with its bound, and via the registry all agree.
"""

# dependencies
import pytest
import typing_extensions as tx

# locals
from bagof.factories import get_factory
from bagof.factories.base import Factory
from bagof.factories.collections import MappingFactory, SequenceFactory

BOUND_TO_LIST = tx.TypeVar("BOUND_TO_LIST", bound=tx.List[int])
BOUND_TO_DICT = tx.TypeVar("BOUND_TO_DICT", bound=tx.Dict[str, int])
BOUND_TO_INT = tx.TypeVar("BOUND_TO_INT", bound=int)
BOUND_TO_STR = tx.TypeVar("BOUND_TO_STR", bound=str)

# (factory, bound hint, typevar bound to it)
EQUIVALENCES = [
    (SequenceFactory, tx.List[int], BOUND_TO_LIST),
    (MappingFactory, tx.Dict[str, int], BOUND_TO_DICT),
    (Factory, int, BOUND_TO_INT),
    (Factory, str, BOUND_TO_STR),
]

IDS = [case[0].__name__ for case in EQUIVALENCES]


@pytest.mark.parametrize("cls,hint,typevar", EQUIVALENCES, ids=IDS)
def test_typevar_builds_like_its_bound(
    cls: tx.Any, hint: tx.Any, typevar: tx.Any
) -> None:
    expected = cls(hint)()
    assert cls(typevar)() == expected
    assert get_factory(typevar)() == expected


@pytest.mark.parametrize("cls,hint,typevar", EQUIVALENCES, ids=IDS)
def test_typevar_builds_the_same_type(
    cls: tx.Any, hint: tx.Any, typevar: tx.Any
) -> None:
    expected = cls(hint)()
    result = cls(typevar)()
    assert type(result) is type(expected)


@pytest.mark.parametrize("cls,hint,typevar", EQUIVALENCES, ids=IDS)
def test_typevar_introspection_matches_its_bound(
    cls: tx.Any, hint: tx.Any, typevar: tx.Any
) -> None:
    assert cls(typevar).origin == cls(hint).origin
    assert cls(typevar).args == cls(hint).args
    assert cls(typevar).unwrapped == cls(hint).unwrapped


def test_typevar_with_default() -> None:
    """A typevar builds like its default when it has no bound."""
    hint = tx.TypeVar("WITH_DEFAULT", default=tx.List[int])
    assert get_factory(hint)() == []
