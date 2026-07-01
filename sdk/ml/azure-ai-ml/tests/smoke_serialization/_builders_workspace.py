# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for workspace / registry entities.

WorkspaceConnection is intentionally NOT covered: its ``_to_rest_object`` embeds a credential child
(e.g. ``WorkspaceConnectionPersonalAccessToken``) that already serializes to an ``arm_ml_service``
hybrid model inside a v2022_10 msrest envelope — a mixed tree resolved by the operations layer at send
time, not a clean offline path (same situation as online/batch deployments). Cover connections when
their migration unifies envelope + children on one generator.
"""
from azure.ai.ml.entities import (
    IdentityConfiguration,
    Registry,
    Workspace,
)
from azure.ai.ml.entities._registry.registry_support_classes import RegistryRegionDetails


def build_workspace_full():
    """Workspace with location, identity and tags."""
    return Workspace(
        name="smoke-workspace",
        description="smoke workspace",
        location="westus",
        display_name="Smoke Workspace",
        tags={"tag1": "value1"},
        hbi_workspace=False,
        public_network_access="Enabled",
        identity=IdentityConfiguration(type="system_assigned"),
        enable_data_isolation=False,
    )


def build_workspace_minimal():
    """Workspace with only required fields."""
    return Workspace(name="smoke-workspace-minimal", location="westus")


def build_registry_full():
    """Registry with a single replication region."""
    return Registry(
        name="smoke-registry",
        location="westus",
        tags={"tag1": "value1"},
        public_network_access="Enabled",
        replication_locations=[RegistryRegionDetails(location="westus")],
        identity=IdentityConfiguration(type="system_assigned"),
    )


WORKSPACE_BUILDERS = {
    "workspace_full": build_workspace_full,
    "workspace_minimal": build_workspace_minimal,
}

REGISTRY_BUILDERS = {
    "registry_full": build_registry_full,
}
