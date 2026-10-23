# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Prepare transactional batches and interpret their per-operation results."""

from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import replace
from typing import Any, Optional

from azure.core.utils import CaseInsensitiveDict

from .._backend.capabilities import OperationRouting
from .._backend.contracts import BackendResponse, PreparedRequest
from .._backend.errors import BindingProtocolError
from .._backend.operations import OP_EXECUTE_ITEM_BATCH
from .._base import _format_batch_operations
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosList
from .._operation_deadline import remaining_timeout
from ..exceptions import CosmosBatchOperationError
from ._item_operations import normalize_item_partition_key, validate_rust_item_options
from ._item_prep import prepare_item_deadline
from ._partition_key import normalize_partition_key
from ._request_settings import build_request_headers_and_settings, compose_item_options
from ._response_parse import build_response_headers, parse_response_body
from ._wire_encoding import serialize_body_to_bytes


def prepare_batch(
    proxy: Any, operations: Any, partition_key: Any, kwargs: dict[str, Any]
) -> tuple[PreparedRequest, Optional[float], Any]:
    """Snapshot input and establish a budget before native metadata resolution."""
    started = time.monotonic()
    kwargs = dict(kwargs)
    hook = kwargs.get("response_hook")
    if hook is not None and not callable(hook):
        raise TypeError("execute_item_batch response_hook must be callable.")
    kwargs.pop("etag", None)
    kwargs.pop("match_condition", None)
    if "request_options" not in kwargs:
        kwargs["request_options"] = kwargs.get("feed_options")
    deadline = prepare_item_deadline(kwargs, OP_EXECUTE_ITEM_BATCH, started)
    options = compose_item_options(kwargs)
    validate_rust_item_options({"kwargs": kwargs}, options)
    proxy._item_context.defaults.apply_to_options(options)
    headers, settings = build_request_headers_and_settings(options)
    body = _format_batch_operations(deepcopy(operations))
    prepared = PreparedRequest(
        op=OP_EXECUTE_ITEM_BATCH,
        container_link=proxy.container_link,
        partition_key=normalize_partition_key(normalize_item_partition_key(partition_key, False)),
        body_bytes=serialize_body_to_bytes(
            body,
            ensure_ascii=not proxy._item_context.defaults.enable_compact_utf8_item_writes,
            allow_nan=False,
        ),
        headers=headers,
        settings=settings,
    )
    remaining_timeout(deadline)
    return prepared, deadline, hook


def complete_batch(
    proxy: Any, response: BackendResponse, hook: Any, deadline: Optional[float]
) -> CosmosList:
    """Preserve batch error indices, operation results, response headers and hooks."""
    headers = build_response_headers(response)
    proxy._item_context.response_state.last_response_headers = CaseInsensitiveDict(headers)
    results = parse_response_body(replace(response, headers=headers))
    if not isinstance(results, list) or any(
        not isinstance(result, dict) or "statusCode" not in result for result in results
    ):
        raise BindingProtocolError("Transactional batch response must contain per-operation status codes.")
    failed = [i for i, result in enumerate(results) if int(result["statusCode"]) >= 400]
    if failed:
        causes = [i for i in failed if int(results[i]["statusCode"]) != 424]
        if not causes:
            raise BindingProtocolError("Transactional batch failed without a causal operation status.")
        index = causes[-1]
        status = int(results[index]["statusCode"])
        raise CosmosBatchOperationError(
            index,
            headers=headers,
            status_code=status,
            message="There was an error in the transactional batch on index {}. Error message: {}".format(
                index, Constants.ERROR_TRANSLATIONS.get(status)
            ),
            operation_responses=results,
        )
    remaining_timeout(deadline)
    if hook is not None:
        hook(CaseInsensitiveDict(headers), results)
    return CosmosList(results, response_headers=headers)


def execute_batch(proxy: Any, operations: Any, partition_key: Any, kwargs: dict[str, Any]) -> CosmosList:
    prepared, deadline, hook = prepare_batch(proxy, operations, partition_key, kwargs)
    return proxy._item_context.adapter.run_operation(
        routing=OperationRouting(OP_EXECUTE_ITEM_BATCH),
        build_request=lambda: prepared,
        process_response=lambda response: complete_batch(proxy, response, hook, deadline),
        deadline=deadline,
    )


async def execute_batch_async(
    proxy: Any, operations: Any, partition_key: Any, kwargs: dict[str, Any]
) -> CosmosList:
    prepared, deadline, hook = prepare_batch(proxy, operations, partition_key, kwargs)
    return await proxy._item_context.adapter.run_operation(
        routing=OperationRouting(OP_EXECUTE_ITEM_BATCH),
        build_request=lambda: prepared,
        process_response=lambda response: complete_batch(proxy, response, hook, deadline),
        deadline=deadline,
    )
