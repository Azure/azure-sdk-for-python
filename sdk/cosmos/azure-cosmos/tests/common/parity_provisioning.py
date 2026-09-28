# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Provision test-owned resources without replaying an ambiguous write blindly.

A fixture may lose the response after the service creates its database. Before
trying that create again, read the same resource and verify the requested
settings. Only a missing resource permits another create. Three attempts bound
recovery; transport failures and successful reconciliation are logged.

These helpers are for setup only, never the operation being compared. Callers
must supply a unique, test-owned ID and register its cleanup before calling.
An initial conflict is not permission to adopt an existing resource.
"""
from __future__ import annotations

import logging
import time
from typing import Callable, Optional, TypeVar, Union

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties, exceptions
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy

_LOGGER = logging.getLogger(__name__)
_T = TypeVar("_T")


def _create_or_reconcile(
    resource_name: str, create: Callable[[], _T], read_and_verify: Callable[[], _T],
) -> _T:
    remaining = 3
    reconcile = False
    while True:
        try:
            if reconcile:
                try:
                    resource = read_and_verify()
                except exceptions.CosmosResourceNotFoundError as error:
                    if error.status_code != 404:
                        raise
                else:
                    _LOGGER.warning("Fixture provisioning recovered verified resource %s", resource_name)
                    return resource
            return create()
        except (ServiceRequestError, ServiceResponseError) as error:
            remaining -= 1
            if not remaining:
                _LOGGER.error(
                    "Fixture provisioning exhausted three attempts for %s: %s",
                    resource_name, type(error).__name__,
                )
                raise
            _LOGGER.warning(
                "Fixture provisioning transport failure for %s: %s; "
                "will read and verify before another create (%s attempts remaining)",
                resource_name, type(error).__name__, remaining,
            )
            reconcile = True
            time.sleep(3 - remaining)


def _verify_database_throughput(
    database: DatabaseProxy, expected: Optional[Union[int, ThroughputProperties]],
) -> None:
    try:
        actual = database.get_throughput()
    except exceptions.CosmosResourceNotFoundError as error:
        if error.status_code != 404:
            raise
        assert expected is None, "Recovered database has no requested throughput offer"
        return
    assert expected is not None, "Recovered database unexpectedly has a throughput offer"
    requested = ThroughputProperties(offer_throughput=expected) if isinstance(expected, int) else expected
    assert actual.auto_scale_max_throughput == requested.auto_scale_max_throughput, (
        "Recovered database has different throughput mode or autoscale maximum"
    )
    if requested.auto_scale_max_throughput is None:
        assert actual.offer_throughput == requested.offer_throughput, (
            "Recovered database has different fixed throughput"
        )
    if requested.auto_scale_increment_percent is not None:
        assert actual.auto_scale_increment_percent == requested.auto_scale_increment_percent, (
            "Recovered database has a different autoscale increment"
        )


def create_owned_database(
    client: CosmosClient, *, id: str,
    offer_throughput: Optional[Union[int, ThroughputProperties]] = None,
) -> DatabaseProxy:
    """Create a unique fixture database, verifying any ambiguously completed create."""
    def recover() -> DatabaseProxy:
        database = client.get_database_client(id)
        properties = database.read()
        assert properties["id"] == id, "Recovered database has a different ID"
        _verify_database_throughput(database, offer_throughput)
        return database

    return _create_or_reconcile(
        "database " + id,
        lambda: client.create_database(id=id, offer_throughput=offer_throughput),
        recover,
    )


def create_owned_container(
    database: DatabaseProxy, *, id: str, partition_key: PartitionKey,
) -> ContainerProxy:
    """Create a unique fixture container, checking its key definition on recovery."""
    def recover() -> ContainerProxy:
        container = database.get_container_client(id)
        properties = container.read()
        assert properties["id"] == id, "Recovered container has a different ID"
        for name, expected in partition_key.items():
            assert properties["partitionKey"].get(name) == expected, (
                f"Recovered container has a different partition-key {name}"
            )
        return container

    return _create_or_reconcile(
        "container " + id,
        lambda: database.create_container(id=id, partition_key=partition_key),
        recover,
    )
