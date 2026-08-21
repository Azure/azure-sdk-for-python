# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""SDK hook contract for Cosmos SDK integration."""

from __future__ import annotations

from .contract import MirroredQueryRequest, run_mirrored_query

__all__ = ["MirroredQueryRequest", "run_mirrored_query"]
