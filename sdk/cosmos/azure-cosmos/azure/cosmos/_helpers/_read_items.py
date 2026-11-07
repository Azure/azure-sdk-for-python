# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Validate read_items inputs and combine their results in the Python wrapper.

Each requested item is identified by its id and partition key. Result indexing
restores the request order, including duplicates. ResponseHeaderAccumulator is
also reused by feed helpers to combine headers across their fetches.
"""
from __future__ import annotations

import math
import time
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, Optional

from azure.core.utils import CaseInsensitiveDict

from .._cosmos_responses import CosmosList
from .._operation_deadline import remaining_timeout
from ..exceptions import CosmosHttpResponseError
from ..partition_key import _Empty, _Undefined, NonePartitionKeyValue, NullPartitionKeyValue
from ._item_prep import prepare_item_deadline
from ._paths import parse_paths
from ._pk_extract import _retrieve_partition_key
from ._resource_validation import validate_resource


def validate_concurrency(value: Optional[int]) -> None:
    if value is not None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("read_items max_concurrency must be a positive integer or None.")
        if value <= 0:
            raise ValueError("read_items max_concurrency must be positive.")


def partition_key_components(value: Any) -> list[Any]:
    values = list(value) if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) else [value]
    components: list[Any] = []
    for component in values:
        if component is NonePartitionKeyValue or isinstance(component, (_Undefined, _Empty)):
            components.append(_Undefined())
        elif isinstance(component, Mapping) and not component:
            components.append(_Undefined())
        elif component is NullPartitionKeyValue or component is None:
            components.append(None)
        elif isinstance(component, (str, bool)):
            components.append(component)
        elif isinstance(component, (int, float)):
            try:
                finite = math.isfinite(component)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError("read_items partition key numbers must be finite.")
            components.append(component)
        else:
            raise TypeError("read_items partition key components must be scalar values or missing-key sentinels.")
    if not components:
        raise ValueError("read_items requires a full partition key, not an empty component list.")
    return components


def partition_key_identity(value: Any) -> tuple:
    return tuple(
        ("undefined",) if isinstance(component, _Undefined)
        else ("null",) if component is None
        else ("bool", component) if isinstance(component, bool)
        else ("number", float(component)) if isinstance(component, (int, float))
        else ("string", component)
        for component in partition_key_components(value)
    )


def prepare_read_items(
    items: Any, max_concurrency: Optional[int], kwargs: dict[str, Any]
) -> tuple[list[tuple[str, Any]], Optional[float]]:
    started = time.monotonic()
    validate_concurrency(max_concurrency)
    hook = kwargs.get("response_hook")
    if hook is not None and not callable(hook):
        raise TypeError("read_items response_hook must be callable or None.")
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes, bytearray)):
        raise TypeError("read_items items must be a sequence of (ID, partition key) pairs.")
    snapshot = []
    for pair in items:
        if not isinstance(pair, Sequence) or isinstance(pair, (str, bytes, bytearray)) or len(pair) != 2:
            raise TypeError("read_items requires (ID, partition key) pairs.")
        item_id, key = pair
        if not isinstance(item_id, str):
            raise TypeError("read_items item IDs must be strings.")
        if not item_id:
            raise ValueError("read_items item IDs must not be empty.")
        validate_resource({"id": item_id})
        partition_key_components(key)
        snapshot.append((item_id, deepcopy(key)))
    if "request_options" not in kwargs and "feed_options" in kwargs:
        kwargs["request_options"] = kwargs.pop("feed_options")
    deadline = prepare_item_deadline(kwargs, "read_items", started)
    if deadline is not None:
        kwargs["_item_operation_deadline"] = deadline
    remaining_timeout(deadline)
    return snapshot, deadline


def normalize_read_items(items: Sequence, definition: Mapping[str, Any]) -> list[tuple[str, Any]]:
    paths = definition.get("paths", [])
    if not paths:
        raise ValueError("read_items requires a partition key definition.")
    normalized = []
    for item_id, key in items:
        components = partition_key_components(key)
        if len(components) != len(paths):
            raise ValueError("read_items requires every component of the container's partition key.")
        if len(paths) == 1 and definition.get("kind") != "MultiHash":
            key = components[0]
            if definition.get("systemKey") and isinstance(key, _Undefined):
                key = _Empty()
        else:
            key = components
        normalized.append((item_id, key))
    return normalized


def index_requested_items(items: Sequence) -> dict[tuple, list[int]]:
    indices: dict[tuple, list[int]] = {}
    for index, item_id, key in items:
        indices.setdefault((item_id, partition_key_identity(key)), []).append(index)
    return indices


def index_query_results(results: Sequence, indices: dict[tuple, list[int]], definition: Mapping) -> list:
    indexed: list[tuple[int, Any]] = []
    seen = set()
    for item in results:
        components = [
            _retrieve_partition_key(parse_paths([path]), item, definition.get("systemKey", False))
            for path in definition["paths"]
        ]
        identity = (item.get("id"), partition_key_identity(components))
        if identity not in indices:
            raise CosmosHttpResponseError(message="read_items received an item outside the requested ID/partition keys.")
        if identity not in seen:
            seen.add(identity)
            indexed.extend((index, deepcopy(item)) for index in indices[identity])
    return indexed


class ResponseHeaderAccumulator:
    """Combine response headers without fetching or advancing a feed.

    Request charges "1.0" and "2.0" become "3.0". Diagnostic strings are joined;
    other headers keep their latest value. Empty pages still contribute their
    available headers.
    """

    def __init__(self) -> None:
        self.headers = CaseInsensitiveDict()
        self.charge = 0.0
        self.diagnostics: list[str] = []

    def __call__(self, headers: Mapping, _: Any) -> None:
        headers = CaseInsensitiveDict(headers)
        charge = headers.get("x-ms-request-charge")
        if charge is not None:
            self.charge += float(charge)
            if not math.isfinite(self.charge):
                raise ValueError("read_items received a non-finite request charge.")
        diagnostic = headers.get("x-ms-cosmos-sdk-diagnostics")
        if diagnostic is not None:
            self.diagnostics.append(diagnostic)
        self.headers.update(headers)
        self.headers["x-ms-request-charge"] = str(self.charge)
        if self.diagnostics:
            self.headers["x-ms-cosmos-sdk-diagnostics"] = "; ".join(self.diagnostics)


def complete_read_items_response(result: CosmosList, hook: Any, deadline: Optional[float]) -> CosmosList:
    remaining_timeout(deadline)
    if hook is not None:
        headers = result.get_response_headers()
        body = CosmosList(deepcopy(list(result)), response_headers=CaseInsensitiveDict(headers))
        hook(CaseInsensitiveDict(headers), body)
    return result
