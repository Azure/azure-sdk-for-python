# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# NOTE: This contains adapters that make the Promptflow dependency optional. In the first phase,
#       Promptflow will still be installed as part of the azure-ai-evaluation dependencies. This
#       will be removed in the future once the code migration is complete.

from typing import Final


_has_legacy = False
try:
    from promptflow.client import PFClient

    _has_legacy = True
except ImportError:
    pass

HAS_LEGACY_SDK: Final[bool] = _has_legacy
MISSING_LEGACY_SDK: Final[bool] = not _has_legacy
