# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pure resource-ID validation shared with the legacy compatibility layer."""
from __future__ import annotations

import re
from typing import Any, Mapping, Optional

_VALID_COSMOS_RESOURCE = re.compile(r"^[^/\\#?\t\r\n]*$")


def validate_resource(resource: Mapping[str, Any]) -> None:
    """Validate an existing nonempty ID without requiring or generating one."""
    id_: Optional[str] = resource.get("id")
    if id_:
        try:
            if _VALID_COSMOS_RESOURCE.match(id_) is None:
                raise ValueError("Id contains illegal chars.")
            if id_[-1] in [" ", "\n"]:
                raise ValueError("Id ends with a space or newline.")
        except TypeError as exc:
            raise TypeError("Id type must be a string.") from exc
