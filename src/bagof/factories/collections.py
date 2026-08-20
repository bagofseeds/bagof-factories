"""Factories for collection types (sequences, mappings, sets, etc.)."""

__all__ = [
    "SequenceFactory",
    "MappingFactory",
    "DictFactory",
    "SetFactory",
    "MutableSetFactory",
    "IterableFactory",
    "IteratorFactory",
    "TupleFactory",
    "NamedTupleFactory",
]

# stdlib
import typing_extensions as tx  # noqa: I001
from collections import abc

# bags
from bagof.hints.typevars.co import ITERABLE, MAPPING, SEQUENCE, TUPLE

# locals
from .base import Factory, get_factory


class SequenceFactory(Factory[SEQUENCE], register=abc.Sequence):
    """Factory for [`Sequence`][collections.abc.Sequence] hints (a `list`)."""

    DEFAULT = abc.Sequence
    FALLBACK = list


class MappingFactory(Factory[MAPPING], register=abc.Mapping):
    """Factory for [`Mapping`][collections.abc.Mapping] hints (a `dict`)."""

    DEFAULT = abc.Mapping
    FALLBACK = dict


class DictFactory(MappingFactory, register=dict):
    """Factory for [`dict`][] hints (an empty `dict`)."""

    DEFAULT = dict
    FALLBACK = dict


class SetFactory(Factory[ITERABLE], register=abc.Set):
    """
    Factory for [`Set`][collections.abc.Set] hints (a `frozenset`).

    [`Set`][collections.abc.Set] is the immutable interface, so it builds
    a [`frozenset`][]; [`MutableSet`][collections.abc.MutableSet] builds
    a [`set`][].
    """

    DEFAULT = abc.Set
    FALLBACK = frozenset


class MutableSetFactory(SetFactory, register=(abc.MutableSet, set)):
    """Factory for [`MutableSet`][collections.abc.MutableSet] (a `set`)."""

    DEFAULT = abc.MutableSet
    FALLBACK = set


class IterableFactory(
    Factory[ITERABLE], register=(abc.Iterable, abc.Container)
):
    """
    Factory for [`Iterable`][collections.abc.Iterable] hints (a `list`).

    Also covers [`Collection`][collections.abc.Collection],
    [`Reversible`][collections.abc.Reversible] and
    [`Container`][collections.abc.Container].
    """

    DEFAULT = abc.Iterable
    FALLBACK = list


class IteratorFactory(Factory[ITERABLE], register=abc.Iterator):
    """
    Factory for [`Iterator`][collections.abc.Iterator] (an empty
    iterator).
    """

    DEFAULT = abc.Iterator

    def __call__(self) -> tx.Iterator:
        """Return an empty iterator."""
        return iter(())


class TupleFactory(Factory[TUPLE], register=tuple):
    """
    Factory for [`tuple`][] hints.

    A fixed-length tuple builds a value for each element
    (``Tuple[int, str]`` -> ``(0, "")``).

    !!! note
        A variadic tuple (``Tuple[int, ...]``), an unparametrised
        tuple, or the empty tuple (``Tuple[()]``) builds an empty
        tuple, since no length is implied.
    """

    DEFAULT = tuple
    FALLBACK = tuple

    def __call__(self) -> TUPLE:
        """Build a value for each element of a fixed-length tuple."""
        origin = self.origin
        if _is_namedtuple(origin):
            # A NamedTuple is a `tuple` subclass with no `__args__`, so it
            # would otherwise look variadic and build a bare `()` -- a
            # value of the wrong type. Its fields are in `__annotations__`.
            return NamedTupleFactory(self.hint)()
        args = self.args
        # `Tuple[()]` is the empty tuple. Python 3.9+ represents it as `()`,
        # but Python 3.8 represents it as `((),)` -- normalise both.
        if not args or args == ((),):
            return ()
        if len(args) == 2 and args[1] is Ellipsis:
            return ()
        return tuple(get_factory(arg)() for arg in args)


def _is_namedtuple(origin: tx.Any) -> bool:
    """Whether `origin` is a NamedTuple class rather than a plain tuple."""
    return (
        isinstance(origin, type)
        and issubclass(origin, tuple)
        and hasattr(origin, "_fields")
        and hasattr(origin, "_field_defaults")
    )


class NamedTupleFactory(Factory[TUPLE]):
    """
    Factory for [`NamedTuple`][typing.NamedTuple] subclasses.

    Builds a real instance, taking each field's declared default where
    there is one and otherwise building a value from the field's
    annotation -- the same shape
    [`TypedDictFactory`][bagof.factories.typeddicts.TypedDictFactory]
    has for dicts.

    !!! note
        A NamedTuple is a plain `tuple` subclass at runtime, so it cannot
        be a registry key of its own;
        [`TupleFactory`][bagof.factories.collections.TupleFactory]
        recognises one and delegates here.

    !!! example
        ```pycon
        >>> import typing_extensions as tx
        >>> from bagof.factories import get_factory
        >>> class Point(tx.NamedTuple):
        ...     x: int
        ...     y: str = "origin"
        >>> get_factory(Point)()
        Point(x=0, y='origin')
        ```
    """

    DEFAULT = tuple

    def __call__(self) -> TUPLE:
        """Build an instance, field by field."""
        cls = self.origin
        defaults = cls._field_defaults
        hints = tx.get_type_hints(cls, include_extras=True)
        values = {}
        for name in cls._fields:
            if name in defaults:
                values[name] = defaults[name]
            else:
                values[name] = get_factory(hints.get(name, tx.Any))()
        return cls(**values)
