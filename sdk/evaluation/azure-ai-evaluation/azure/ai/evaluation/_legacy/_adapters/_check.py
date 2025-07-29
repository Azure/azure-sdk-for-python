# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Final


_has_legacy = False
try:
    from promptflow._constants import FlowType

    _has_legacy = True
except ImportError:
    pass

HAS_LEGACY_SDK: Final[bool] = _has_legacy
MISSING_LEGACY_SDK: Final[bool] = not _has_legacy
