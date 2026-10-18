# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared validation and result ownership for throughput replacements."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping, Optional, Union

from .._base import _deserialize_throughput
from .._cosmos_responses import CosmosDict
from .._throughput_rust_routing import offer_response_headers
from ..offer import ThroughputProperties
from ._response_parse import with_response_header_snapshot


def validate_replacement_throughput(
    throughput: Union[int, ThroughputProperties],
) -> None:
    """Reject invalid types and mixed throughput modes before reading metadata."""
    if not isinstance(throughput, (int, ThroughputProperties)):
        raise TypeError(
            "offer_throughput must be int or an instance of ThroughputProperties"
        )
    if isinstance(throughput, ThroughputProperties):
        if throughput.offer_throughput is not None and (
            throughput.auto_scale_max_throughput is not None
            or throughput.auto_scale_increment_percent is not None
        ):
            raise KeyError(
                "Manual and autoscale throughput settings cannot be combined"
            )


def finish_replacement(
    updated_offer: Mapping[str, Any],
    client_connection: Any,
    response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]],
) -> ThroughputProperties:
    """Return owned settings and invoke the callback with a separate offer copy."""
    headers = offer_response_headers(updated_offer, client_connection)
    result = _deserialize_throughput(
        [CosmosDict(deepcopy(dict(updated_offer)), response_headers=headers)]
    )
    hook = with_response_header_snapshot(response_hook, copy_body=True)
    if hook is not None:
        hook(headers, CosmosDict(dict(updated_offer), response_headers=headers))
    return result
