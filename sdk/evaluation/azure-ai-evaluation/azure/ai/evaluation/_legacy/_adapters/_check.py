# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from importlib.util import find_spec
from typing import Final

HAS_LEGACY_SDK: Final[bool] = find_spec("promptflow") is not None
MISSING_LEGACY_SDK: Final[bool] = not HAS_LEGACY_SDK
