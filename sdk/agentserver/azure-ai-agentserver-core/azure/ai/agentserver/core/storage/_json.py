# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Small JSON helpers shared by Foundry storage serializers."""

# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype

from __future__ import annotations

import json
from typing import Any


def load_json(body: str | None) -> Any:
    """Parse a JSON response body, treating empty/None bodies as an empty object."""
    return json.loads(body or "{}")
