"""
Automatic type-based factories.

Modules
-------
base
    Base class for magic factories.
builtins
    Factories for builtin types that need constructor arguments.
collections
    Factories for collection types (list, dict, set, etc.).
common
    Common factories (none, union, literal, typevar, annotated).
datetimes
    Factories for date and time types.
enums
    Factories for enumeration types.
numbers
    Factories for numeric types (int, float, complex, etc.).
typeddicts
    Factory for TypedDict types.
uuids
    Factories for UUID types.
"""

__all__ = [
    "__version__",
    "base",
    "builtins",
    "collections",
    "common",
    "datetimes",
    "enums",
    "numbers",
    "typeddicts",
    "uuids",
]

try:
    from ._version import __version__
except ImportError:  # pragma: no cover
    __version__ = "0+unknown"

from . import (
    base,
    builtins,
    collections,
    common,
    datetimes,
    enums,
    numbers,
    typeddicts,
    uuids,
)
from .base import *  # noqa: F401, F403
from .base import __all__ as __all_base
from .builtins import *  # noqa: F401, F403
from .builtins import __all__ as __all_builtins
from .collections import *  # noqa: F401, F403
from .collections import __all__ as __all_collections
from .common import *  # noqa: F401, F403
from .common import __all__ as __all_common
from .datetimes import *  # noqa: F401, F403
from .datetimes import __all__ as __all_datetimes
from .enums import *  # noqa: F401, F403
from .enums import __all__ as __all_enums
from .numbers import *  # noqa: F401, F403
from .numbers import __all__ as __all_numbers
from .typeddicts import *  # noqa: F401, F403
from .typeddicts import __all__ as __all_typeddicts
from .uuids import *  # noqa: F401, F403
from .uuids import __all__ as __all_uuids

__all__ += __all_base
__all__ += __all_builtins
__all__ += __all_collections
__all__ += __all_common
__all__ += __all_datetimes
__all__ += __all_enums
__all__ += __all_numbers
__all__ += __all_typeddicts
__all__ += __all_uuids
