# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import

from ._version import VERSION

__version__ = VERSION

try:
    from ._patch import __all__ as _patch_all
    from ._patch import *  # type: ignore
except ImportError:
    _patch_all = []
from ._patch import patch_sdk as _patch_sdk

from .models import (  # type: ignore
    DeletedSecret,
    KeyVaultSecret,
    KeyVaultSecretIdentifier,
    SecretProperties,
)

__all__ = [
    "ApiVersion",
    "SecretClient",
    "DeletedSecret",
    "KeyVaultSecret",
    "KeyVaultSecretIdentifier",
    "SecretProperties",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore

_patch_sdk()
