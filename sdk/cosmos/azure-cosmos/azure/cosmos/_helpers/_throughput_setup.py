# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The two preparation steps every throughput operation starts with.

Cosmos does not store a container's or database's provisioned request-unit
(RU/s) budget on the resource itself. It keeps it in a separate account-level
record called an *offer*, which names the resource it applies to by that
resource's self-link. So every throughput operation begins the same two ways,
whether the customer called ``ContainerProxy.get_throughput`` or
``DatabaseProxy.replace_throughput``:

1. :func:`offer_query` builds the query that finds the one offer record
   belonging to this resource.
2. :func:`gather_rust_call_inputs` retrieves the selected Python backend and
   prepares options for the Rust path's eligibility check and request builder.

Those two steps are identical for containers and databases, so they live here
rather than being written twice in
:mod:`~azure.cosmos._helpers._container_throughput` and
:mod:`~azure.cosmos._helpers._database_throughput`, where the two halves
would be free to drift apart.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .._base import build_options
from .._constants import _Constants as Constants

def offer_query(resource_self_link: str) -> dict[str, Any]:
    """Build the query that finds a resource's throughput offer.

    :param str resource_self_link: Container or database self-link recorded by its offer.
    :return: Parameterized offer query matching the owning resource.
    :rtype: dict[str, Any]
    """
    # Both execution paths use this filter for a container or database offer:
    # the account's offers feed keyed by the resource's self-link.
    return {
        "query": "SELECT * FROM root r WHERE r.resource=@link",
        "parameters": [{"name": "@link", "value": resource_self_link}],
    }


def gather_rust_call_inputs(
    client_connection: Any,
    container_rid: Optional[str],
    kwargs: Mapping[str, Any],
) -> tuple[Any, Dict[str, Any], Dict[str, Any]]:
    """Collect the three inputs needed to prepare a throughput operation.

    Return the client's selected Python backend, request options, and the
    leftover kwargs used to check Rust-path eligibility. They are returned
    together so each public function reads ``client_connection._backend``
    exactly once, in one place.

    :param Any client_connection: Connection owning the selected backend.
    :param str or None container_rid: Container RID to stamp on the options when supplied.
    :param Mapping[str, Any] kwargs: Call keywords copied before building internal options.
    :return: The selected backend, internal options, and remaining eligibility keywords.
    :rtype: tuple[Any, dict, dict]
    """
    # This internal coordinator intentionally reads the connection-owned backend.
    backend = client_connection._backend  # pylint: disable=protected-access
    rust_kwargs = dict(kwargs)
    options = build_options(rust_kwargs)
    if container_rid is not None:
        options[Constants.ContainerRID] = container_rid
    # ``build_options`` lifts the supported end-to-end timeout into options.
    rust_kwargs.pop("timeout", None)
    return backend, options, rust_kwargs
