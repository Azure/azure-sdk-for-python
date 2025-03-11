# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# NOTE: This contains placeholder code as we transition from the dependency on
#       now legacy Promptflow SDK

from typing import Final


_has_legacy = False
try:
    from promptflow.client import PFClient
    _has_legacy = True
except ImportError:
    pass

HAS_LEGACY_SDK: Final[bool] = _has_legacy
MISSING_LEGACY_SDK: Final[bool] = not _has_legacy