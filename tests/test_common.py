"""Tests for the common factories (none, union, literal, etc.)."""

# dependencies
import pytest
import typing_extensions as tx

# locals
from bagof.core.magic import UNSET

from bagof.factories import get_factory
from bagof.factories.base import Factory
from bagof.factories.common import (
    AnnotatedFactory,
    LiteralFactory,
    NoneFactory,
    UnionFactory,
)


def test_none_factory_builds_none() -> None:
    """The none factory always builds `None`."""
    assert NoneFactory(type(None))() is None
    assert get_factory(type(None))() is None


def test_optional_union_builds_none() -> None:
    """An optional union builds `None`."""
    assert get_factory(tx.Optional[int])() is None
    assert UnionFactory(tx.Optional[int])() is None


def test_union_builds_first_instantiable_member() -> None:
    """A non-optional union builds a value for its first member."""
    assert get_factory(tx.Union[int, str])() == 0
    assert get_factory(tx.Union[str, int])() == ""


def test_union_raises_when_no_member_is_instantiable() -> None:
    """A union of non-instantiable members raises `TypeError`."""
    with pytest.raises(TypeError):
        UnionFactory(tx.Union[tx.Any, tx.Any])()


def test_literal_builds_first_value() -> None:
    """A literal builds its first value."""
    assert get_factory(tx.Literal["a", "b"])() == "a"
    assert get_factory(tx.Literal[1, 2, 3])() == 1


def test_literal_with_none_builds_none() -> None:
    """A literal that allows `None` builds `None`."""
    assert get_factory(tx.Literal[None, 1])() is None


def test_empty_literal_raises() -> None:
    """An empty literal cannot be instantiated."""
    factory = LiteralFactory(tx.Literal)  # an argument-less literal
    assert factory.args == ()
    with pytest.raises(TypeError):
        factory()


def test_annotated_builds_origin_value() -> None:
    """An annotated hint with plain metadata builds the origin's value."""
    assert get_factory(tx.Annotated[int, "meta"])() == 0
    assert get_factory(tx.Annotated[tx.List[int], "meta"])() == []


def test_annotated_uses_factory_class_in_metadata() -> None:
    """A `Factory` subclass in the metadata overrides the origin factory."""
    assert get_factory(tx.Annotated[int, NoneFactory])() is None


def test_annotated_factories_property_includes_origin() -> None:
    """The annotated factories always include the origin factory first."""
    factory = AnnotatedFactory(tx.Annotated[int, "meta"])
    assert len(factory.factories) >= 1


# ----------------------------------------------------------------------
# AnnotatedFactory
# ----------------------------------------------------------------------


def test_annotated_factories_are_cached() -> None:
    # Both sibling packages memoise their metadata chain; this one walked
    # the registry again on every access.
    factory = get_factory(tx.Annotated[int, "meta"])
    assert factory.factories is factory.factories


def test_annotated_uses_the_most_specific_factory() -> None:
    factory = get_factory(tx.Annotated[int, "meta"])
    assert factory.factories[-1] is not None
    assert factory() == 0


def test_annotated_resolves_a_metadata_instance() -> None:

    class Marker:
        pass

    @AnnotatedFactory.register_metadata(Marker)
    class MarkedFactory(Factory):
        DEFAULT = int

        def __init__(
            self, marker: tx.Any = None, hint: tx.Any = None
        ) -> None:
            super().__init__(int)
            self.marker = marker

        def __call__(self) -> int:
            return 42

    try:
        # Metadata is usually an instance and the registry is keyed by
        # its type, so without a `type(hint)` fallback only metadata
        # registered by identity could ever be found.
        assert get_factory(tx.Annotated[int, Marker()])() == 42
        # A bare class key still resolves directly.
        assert get_factory(tx.Annotated[int, Marker])() == 42
    finally:
        AnnotatedFactory._REGISTRY.pop(Marker, None)


def test_annotated_without_metadata_falls_back_to_the_origin() -> None:
    assert get_factory(tx.Annotated[str, "meta"])() == ""
    assert get_factory(tx.Annotated[tx.List[int], "meta"])() == []


def test_register_metadata_is_distinct_from_register() -> None:
    # locals
    from bagof.factories.base import FACTORIES

    class Marker:
        pass

    @AnnotatedFactory.register_metadata(Marker)
    class MarkedFactory(Factory):
        DEFAULT = int

        def __init__(
            self, marker: tx.Any = None, hint: tx.Any = None
        ) -> None:
            super().__init__(int)
            self.marker = marker

        def __call__(self) -> int:
            return 7

    try:
        assert AnnotatedFactory._REGISTRY[Marker] is MarkedFactory
        assert Marker not in FACTORIES
        assert get_factory(tx.Annotated[int, Marker()])() == 7
    finally:
        AnnotatedFactory._REGISTRY.pop(Marker, None)


def test_register_alias_still_works() -> None:
    assert (
        AnnotatedFactory.register.__func__
        is AnnotatedFactory.register_metadata.__func__
    )


def test_annotated_metadata_factory_adopts_the_annotated_type() -> None:
    # locals
    from bagof.factories.base import Factory

    class Marker:
        pass

    class MarkedFactory(Factory):
        DEFAULT = int

        def __init__(
            self, marker: tx.Any = None, hint: tx.Any = UNSET
        ) -> None:
            super().__init__(hint)
            self.marker = marker

    AnnotatedFactory.register_metadata(Marker)(MarkedFactory)
    try:
        # The metadata factory is used in preference to the origin one,
        # so keeping its class `DEFAULT` would build the wrong type.
        factory = get_factory(tx.Annotated[str, Marker()])
        assert factory.factories[-1].hint is str
        assert factory() == ""
        # ... and it keeps its own configuration.
        assert isinstance(factory.factories[-1].marker, Marker)
    finally:
        AnnotatedFactory._REGISTRY.pop(Marker, None)


def test_annotated_metadata_factory_explicit_hint_is_respected() -> None:
    # locals
    from bagof.factories.base import Factory

    class Marker:
        pass

    class PinnedFactory(Factory):
        DEFAULT = int

        def __init__(self, marker: tx.Any = None) -> None:
            super().__init__(int)  # explicit, always
            self.marker = marker

    AnnotatedFactory.register_metadata(Marker)(PinnedFactory)
    try:
        factory = get_factory(tx.Annotated[str, Marker()])
        assert factory.factories[-1].hint is int
        assert factory() == 0
    finally:
        AnnotatedFactory._REGISTRY.pop(Marker, None)
