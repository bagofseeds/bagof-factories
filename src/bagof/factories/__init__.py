"""
Automatic type-based factories.

Modules
-------
base
    Base class for magic factories.
collections
    Factories for collection types (list, dict, etc.).
common
    Common factories (none, union, literal, typevar, annotated).
"""

__all__ = [
    "__version__",
    "base",
    "collections",
    "common",
]

try:
    from ._version import __version__
except ImportError:  # pragma: no cover
    __version__ = "0+unknown"

from . import (
    base,
    collections,
    common,
)
from .base import *  # noqa: F401, F403
from .base import __all__ as __all_base
from .collections import *  # noqa: F401, F403
from .collections import __all__ as __all_collections
from .common import *  # noqa: F401, F403
from .common import __all__ as __all_common

__all__ += __all_base
__all__ += __all_collections
__all__ += __all_common
