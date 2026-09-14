# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async legacy item parity, separate from Rust execution."""
from __future__ import annotations

import logging
from typing import Any, Dict

from ..._constants import _Constants as Constants
from ..._helpers.legacy_item_helper import LegacyItemHelper, legacy_item_call, prepare_legacy_item_arguments


class AsyncLegacyItemHelper(LegacyItemHelper):
    """Inherited operation methods return this runner's coroutine."""

    async def _run(self, op: str, arguments: Dict[str, Any]) -> Any:
        args, options = prepare_legacy_item_arguments(op, arguments)
        link = args["container_link"]
        try:
            if self._ensure_container_cached is not None:
                await self._ensure_container_cached(options)
            elif link not in self.client_connection._container_properties_cache:
                await self.client_connection._refresh_container_properties_cache(link)
            rid = self.client_connection._container_properties_cache[link].get("_rid")
            if isinstance(rid, str):
                options[Constants.ContainerRID] = rid
        except (AttributeError, KeyError, TypeError) as exc:
            logging.getLogger(__name__).warning("Could not resolve legacy container rid for %r: %s", link, exc)
        return await legacy_item_call(self.client_connection, op, args, options)
