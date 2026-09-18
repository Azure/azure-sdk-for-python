# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for online/batch endpoint entities.

Endpoints serialize via a location-bound method (``_to_rest_online_endpoint(location)`` /
``_to_rest_batch_endpoint(location)``) that returns an ``arm_ml_service`` hybrid model, so each builder
returns a small ``_RestAdapter`` exposing the suite's uniform no-arg ``_to_rest_object()`` contract.

DEPLOYMENTS are intentionally NOT covered here. ``OnlineDeployment._to_rest_object(location)`` returns
a per-version msrest envelope (v2023_04) while its nested children (e.g. ``ProbeSettings``) already
serialize to ``arm_ml_service`` hybrid models — a mixed tree that the operations layer resolves at
send time, not a clean offline ``_to_rest_object`` -> wire path. (#47554 did not touch
``deployment_settings.py``; this is pre-existing.) Cover deployments when the online/batch deployment
migration lands and the envelope + children are unified on one generator.
"""
from azure.ai.ml.entities import (
    BatchEndpoint,
    IdentityConfiguration,
    ManagedOnlineEndpoint,
)

_LOCATION = "westus"


class _RestAdapter:
    """Expose a location-bound rest method as the suite's no-arg ``_to_rest_object()`` contract.

    :param entity: The endpoint/deployment entity.
    :param method: Name of the location-taking rest method on the entity.
    :param location: The location string to pass.
    """

    def __init__(self, entity, method, location=_LOCATION):
        self._entity = entity
        self._method = method
        self._location = location

    def _to_rest_object(self):
        """Call the bound rest method with the fixed location.

        :return: The rest object for the bound entity.
        :rtype: Any
        """
        return getattr(self._entity, self._method)(self._location)


def build_managed_online_endpoint():
    """ManagedOnlineEndpoint with traffic, identity and tags."""
    endpoint = ManagedOnlineEndpoint(
        name="smoke-online-endpoint",
        description="smoke online endpoint",
        auth_mode="key",
        tags={"tag1": "value1"},
        traffic={"blue": 100},
        identity=IdentityConfiguration(type="system_assigned"),
    )
    return _RestAdapter(endpoint, "_to_rest_online_endpoint")


def build_batch_endpoint():
    """BatchEndpoint with defaults and tags."""
    endpoint = BatchEndpoint(
        name="smoke-batch-endpoint",
        description="smoke batch endpoint",
        auth_mode="aad_token",
        tags={"tag1": "value1"},
        defaults={"deployment_name": "smoke-batch-deployment"},
    )
    return _RestAdapter(endpoint, "_to_rest_batch_endpoint")


ONLINE_ENDPOINT_BUILDERS = {
    "managed_online_endpoint": build_managed_online_endpoint,
}

BATCH_ENDPOINT_BUILDERS = {
    "batch_endpoint": build_batch_endpoint,
}
