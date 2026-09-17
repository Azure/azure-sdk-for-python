# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async legacy item parity, separate from Rust execution."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..._constants import _Constants as Constants
from ..._base import _build_properties_cache
from ..._helpers.legacy_item_helper import (
    LegacyItemHelper, legacy_item_call, prepare_legacy_item_arguments,
    prepare_legacy_item_metadata, set_legacy_item_timeout, legacy_item_metadata_options,
)


class AsyncLegacyItemHelper(LegacyItemHelper):
    """Inherited operation methods return this runner's coroutine."""

    async def _run(
        self, op: str, arguments: Dict[str, Any], *, deadline: Optional[float] = None
    ) -> Any:
        args, options = prepare_legacy_item_arguments(
            op, arguments, compact_utf8=getattr(self.client_connection, "_enable_compact_utf8_item_writes", False) is True,
            deadline=deadline,
        )
        link = args["container_link"]
        if op in ("read_item", "create_item"):
            set_legacy_item_timeout(args, options)
            if self._ensure_container_cached is not None:
                await self._ensure_container_cached(options)
            elif link not in self.client_connection._container_properties_cache and args["deadline"] is None:
                await self.client_connection._refresh_container_properties_cache(link)
            elif link not in self.client_connection._container_properties_cache:
                metadata_options = legacy_item_metadata_options(options)
                properties = await self.client_connection.ReadContainer(
                    link, options=metadata_options,
                    **{key: metadata_options[key] for key in ("timeout", "read_timeout") if key in metadata_options},
                )
                self.client_connection._set_container_properties_cache(
                    link, _build_properties_cache(properties, link)
                )
            prepare_legacy_item_metadata(op, args, options, self.client_connection._container_properties_cache[link])
            return await legacy_item_call(self.client_connection, op, args, options)
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
