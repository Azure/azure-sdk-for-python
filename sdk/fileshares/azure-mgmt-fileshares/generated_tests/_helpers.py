# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Shared helpers for FileShares generated_tests.

Tests target the canary ARM endpoint while creating resources in the public
East US region, against a pre-existing resource group named via env var.
"""
import os
import uuid

from azure.mgmt.fileshares import models as fs_models


ARM_ENDPOINT = os.environ.get("ARM_ENDPOINT", "https://eastus2euap.management.azure.com")
AZURE_LOCATION = os.environ.get("FILESHARES_TEST_LOCATION", "eastus")
RESOURCE_GROUP = os.environ.get(
    "FILESHARES_TEST_RG", "sdk-python-eastus-fileshares-crud-rg"
)


def _get_or_set(variables, key, factory):
    """Return variables[key] if present, else generate via factory and store.

    The variables dict is persisted by @recorded_by_proxy across record/playback,
    ensuring deterministic resource names for proxy URI matching.
    """
    if variables is None:
        return factory()
    if key not in variables:
        variables[key] = factory()
    return variables[key]


def random_share_name(variables=None, key="share_name") -> str:
    return _get_or_set(variables, key, lambda: f"fs-gen-{uuid.uuid4().hex[:10]}")


def random_snapshot_name(variables=None, key="snapshot_name") -> str:
    return _get_or_set(variables, key, lambda: f"snap-{uuid.uuid4().hex[:8]}")


def build_share_payload(location: str = AZURE_LOCATION) -> fs_models.FileShare:
    """Build a minimal-but-valid FileShare payload (mirrors PowerShell CRUD test)."""
    return fs_models.FileShare(
        location=location,
        tags={"lifecycle": "crud", "test": "nfs", "owner": "azsdk-generated-test"},
        properties=fs_models.FileShareProperties(
            mount_name="theshare",
            media_tier="SSD",
            redundancy="Local",
            protocol="NFS",
            provisioned_storage_gi_b=1024,
            provisioned_io_per_sec=4024,
            provisioned_throughput_mi_b_per_sec=228,
            nfs_protocol_properties=fs_models.NfsProtocolProperties(root_squash="NoRootSquash"),
        ),
    )


def create_share(client, variables=None, key="share_name", share_name=None):
    """Create a real file share and return (name, share).

    Pass `variables` (the dict supplied by @recorded_by_proxy) so the share name
    is persisted across record/playback. `key` lets a single test create multiple
    shares with distinct stable names.
    """
    name = share_name or random_share_name(variables, key)
    share = client.file_shares.begin_create_or_update(
        resource_group_name=RESOURCE_GROUP,
        resource_name=name,
        resource=build_share_payload(),
    ).result()
    return name, share


def delete_share(client, share_name: str) -> None:
    try:
        client.file_shares.begin_delete(
            resource_group_name=RESOURCE_GROUP,
            resource_name=share_name,
        ).result()
    except Exception:
        pass


async def create_share_async(client, variables=None, key="share_name", share_name=None):
    name = share_name or random_share_name(variables, key)
    poller = await client.file_shares.begin_create_or_update(
        resource_group_name=RESOURCE_GROUP,
        resource_name=name,
        resource=build_share_payload(),
    )
    share = await poller.result()
    return name, share


async def delete_share_async(client, share_name: str) -> None:
    try:
        poller = await client.file_shares.begin_delete(
            resource_group_name=RESOURCE_GROUP,
            resource_name=share_name,
        )
        await poller.result()
    except Exception:
        pass
