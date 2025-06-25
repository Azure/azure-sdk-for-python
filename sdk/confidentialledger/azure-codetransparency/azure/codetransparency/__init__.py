# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION

__version__ = VERSION


from ._client import CodeTransparencyClient
from ._patch import patch_sdk

__all__ = ["CodeTransparencyClient"]


patch_sdk()