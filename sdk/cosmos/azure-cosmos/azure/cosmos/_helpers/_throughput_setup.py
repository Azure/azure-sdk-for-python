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
2. :func:`gather_rust_call_inputs` reads, once, everything the rust dispatch
   needs out of the client and the call's keyword arguments.

Those two steps are identical for containers and databases, so they live here
rather than being written twice in
:mod:`~azure.cosmos._helpers.container_throughput_helper` and
:mod:`~azure.cosmos._helpers.database_throughput_helper`, where the two halves
would be free to drift apart.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .._base import build_options
from .._constants import _Constants as Constants

def offer_query(resource_self_link: str) -> dict[str, Any]:
    """Build the query that finds a resource's throughput offer."""
    # The filter both engines send to find this container's single offer record:
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
    """Collect the three things the rust path needs from one public call.

    Returns the client's selected backend, the rust request options, and the
    leftover kwargs used only to decide rust-eligibility. They are returned
    together so each public function reads ``client_connection._backend``
    exactly once, in one place.
    """
    backend = getattr(client_connection, "_backend", None)
    rust_kwargs = dict(kwargs)
    options = build_options(rust_kwargs)
    if container_rid is not None:
        options[Constants.ContainerRID] = container_rid
    # ``build_options`` lifts the supported end-to-end timeout into options.
    rust_kwargs.pop("timeout", None)
    return backend, options, rust_kwargs
