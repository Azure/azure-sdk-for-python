# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Explicit core-Python parity adapter. Never constructed as a Rust fallback."""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from .._constants import _Constants as Constants
from .._backend.constants import BACKEND_NAME_CORE_PYTHON
from ._item_dispatch import (
    build_create_item_request_options, build_delete_item_request_options,
    build_patch_item_request_options, build_read_item_request_options,
    build_upsert_item_request_options,
)

_LegacyItemHelperT = TypeVar("_LegacyItemHelperT", bound="LegacyItemHelper")


def require_legacy_item_connection(connection: Any) -> None:
    """Allow context-free proxy compatibility only for explicitly selected legacy.

    This check never constructs an item context or recovers a Rust runtime.
    Missing or Rust selection requires the independently supplied client context.
    """
    attributes = getattr(connection, "__dict__", None)
    backend = attributes.get("_backend") if isinstance(attributes, dict) else getattr(connection, "_backend", None)
    if backend is None or backend.name != BACKEND_NAME_CORE_PYTHON:
        raise RuntimeError(
            "Rust item operations require the context supplied by CosmosClient; "
            "direct proxy construction without context supports only explicit core-python parity"
        )


def prepare_legacy_item_arguments(op: str, arguments: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Keep legacy build_options, mutations and pipeline bookkeeping in parity only."""
    kwargs = dict(arguments)
    args = {
        "container_link": kwargs.pop("container_link"),
        "document_link": kwargs.pop("document_link", None),
        "item_id": kwargs.pop("item_id", None),
        "body": kwargs.pop("body", None),
        "patch_operations": kwargs.pop("patch_operations", None),
        "filter_predicate": kwargs.pop("filter_predicate", None),
        "indexing_directive": kwargs.pop("indexing_directive", None),
        "enable_automatic_id_generation": kwargs.pop("enable_automatic_id_generation", False),
    }
    populate_query_metrics = kwargs.pop("populate_query_metrics", None)
    if op == "create_item":
        options = build_create_item_request_options(
            kwargs,
            enable_automatic_id_generation=args["enable_automatic_id_generation"],
            indexing_directive=args["indexing_directive"],
            populate_query_metrics=populate_query_metrics,
        )
    elif op in ("upsert_item", "replace_item"):
        options = build_upsert_item_request_options(kwargs, populate_query_metrics=populate_query_metrics)
    elif op == "patch_item":
        options = build_patch_item_request_options(kwargs)
        if args["filter_predicate"] is not None:
            options["filterPredicate"] = args["filter_predicate"]
    elif op == "read_item":
        options = build_read_item_request_options(kwargs)
    else:
        options = build_delete_item_request_options(kwargs)
    args["kwargs"] = kwargs
    return args, options


def legacy_item_call(connection: Any, op: str, args: Dict[str, Any], options: Dict[str, Any]) -> Any:
    """Retain the six original legacy signatures and option shapes."""
    kwargs = args["kwargs"]
    if op in ("create_item", "upsert_item"):
        method = connection.CreateItem if op == "create_item" else connection.UpsertItem
        return method(
            database_or_container_link=args["container_link"], document=args["body"], options=options, **kwargs
        )
    if op == "replace_item":
        return connection.ReplaceItem(
            document_link=args["document_link"], new_document=args["body"], options=options, **kwargs
        )
    if op == "patch_item":
        return connection.PatchItem(
            document_link=args["document_link"], operations=args["patch_operations"], options=options, **kwargs
        )
    method = connection.ReadItem if op == "read_item" else connection.DeleteItem
    return method(document_link=args["document_link"], options=options, **kwargs)


class LegacyItemHelper:
    """Separate parity execution retaining the existing Python cache and transport."""

    def __init__(
        self, client_connection: Any,
        ensure_container_cached: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.client_connection = client_connection
        self._ensure_container_cached = ensure_container_cached

    @classmethod
    def from_legacy_connection(
        cls: Type[_LegacyItemHelperT], client_connection: Any,
        ensure_container_cached: Optional[Callable[..., Any]] = None,
    ) -> _LegacyItemHelperT:
        """Direct-proxy compatibility factory; never a Rust fallback."""
        require_legacy_item_connection(client_connection)
        return cls(client_connection, ensure_container_cached)

    def _run(self, op: str, arguments: Dict[str, Any]) -> Any:
        args, options = prepare_legacy_item_arguments(op, arguments)
        link = args["container_link"]
        try:
            if self._ensure_container_cached is not None:
                self._ensure_container_cached(options)
            elif link not in self.client_connection._container_properties_cache:
                self.client_connection._refresh_container_properties_cache(link)
            rid = self.client_connection._container_properties_cache[link].get("_rid")
            if isinstance(rid, str):
                options[Constants.ContainerRID] = rid
        except (AttributeError, KeyError, TypeError) as exc:
            logging.getLogger(__name__).warning("Could not resolve legacy container rid for %r: %s", link, exc)
        return legacy_item_call(self.client_connection, op, args, options)

    def create_item(self, **kwargs: Any) -> Any:
        return self._run("create_item", kwargs)

    def read_item(self, **kwargs: Any) -> Any:
        return self._run("read_item", kwargs)

    def delete_item(self, **kwargs: Any) -> Any:
        return self._run("delete_item", kwargs)

    def upsert_item(self, **kwargs: Any) -> Any:
        return self._run("upsert_item", kwargs)

    def replace_item(self, **kwargs: Any) -> Any:
        return self._run("replace_item", kwargs)

    def patch_item(self, **kwargs: Any) -> Any:
        return self._run("patch_item", kwargs)
