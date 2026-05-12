# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Shared helpers for the azure-mgmt-fileshares hand-written test suite.

Scenario coverage and parameter values are inspired by the PowerShell
``Az.FileShare`` test suite under
``azure-powershell/src/FileShare/FileShare.Autorest/test``. Implementation is
plain ``pytest`` against the Python SDK; no PowerShell idioms are ported.
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Optional

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.mgmt.fileshares import FileSharesMgmtClient
from azure.mgmt.fileshares import models as fs_models

# --- Configuration --------------------------------------------------------

ARM_ENDPOINT = os.environ.get("ARM_ENDPOINT", "https://eastus2euap.management.azure.com")
LOCATION = os.environ.get("FILESHARES_TEST_LOCATION", "eastus2euap")
RESOURCE_GROUP = os.environ.get("FILESHARES_TEST_RG", "mfstest-prod-eastus2euap-crud-2026-06-01-rg")


# --- Name generation ------------------------------------------------------


def make_share_name(prefix: str = "fs-azsdk") -> str:
    """Return a unique lowercase share name, ≤ 63 chars, valid for the RP."""
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def make_snapshot_name(prefix: str = "snap-azsdk") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def var_share(variables: dict, key: str, prefix: str = "fs-azsdk") -> str:
    """Return a stable share name across record/playback via the proxy ``variables`` dict.

    On Live/Record, generates a fresh uuid-based name and stores it under ``key``.
    On Playback, the proxy pre-populates ``variables`` from the recording so the
    same name is returned — letting the URI match the recorded request.
    """
    return variables.setdefault(key, make_share_name(prefix))


def var_snapshot(variables: dict, key: str, prefix: str = "snap-azsdk") -> str:
    return variables.setdefault(key, make_snapshot_name(prefix))


# --- Payload builders -----------------------------------------------------


def build_share_payload(
    *,
    location: str = LOCATION,
    media_tier: str = "SSD",
    redundancy: str = "Local",
    protocol: str = "NFS",
    provisioned_storage_gi_b: int = 100,
    provisioned_io_per_sec: int = 3300,
    provisioned_throughput_mi_b_per_sec: int = 200,
    mount_name: str = "theshare",
    nfs_root_squash: Optional[str] = "RootSquash",
    public_network_access: Optional[str] = None,
    tags: Optional[dict] = None,
) -> fs_models.FileShare:
    """Build a FileShare create/update payload exercising the value matrix from
    the PowerShell test spec."""
    nfs_props = fs_models.NfsProtocolProperties(root_squash=nfs_root_squash) if nfs_root_squash is not None else None
    properties = fs_models.FileShareProperties(
        mount_name=mount_name,
        media_tier=media_tier,
        redundancy=redundancy,
        protocol=protocol,
        provisioned_storage_gi_b=provisioned_storage_gi_b,
        provisioned_io_per_sec=provisioned_io_per_sec,
        provisioned_throughput_mi_b_per_sec=provisioned_throughput_mi_b_per_sec,
        nfs_protocol_properties=nfs_props,
        public_network_access=public_network_access,
    )
    return fs_models.FileShare(
        location=location,
        tags=tags or {"owner": "azsdk-test"},
        properties=properties,
    )


def build_share_update(
    *,
    tags: Optional[dict] = None,
    provisioned_storage_gi_b: Optional[int] = None,
    provisioned_io_per_sec: Optional[int] = None,
    provisioned_throughput_mi_b_per_sec: Optional[int] = None,
    public_network_access: Optional[str] = None,
) -> fs_models.FileShareUpdate:
    """Build a ``FileShareUpdate`` payload for PATCH."""
    props_kwargs: dict[str, Any] = {}
    if provisioned_storage_gi_b is not None:
        props_kwargs["provisioned_storage_gi_b"] = provisioned_storage_gi_b
    if provisioned_io_per_sec is not None:
        props_kwargs["provisioned_io_per_sec"] = provisioned_io_per_sec
    if provisioned_throughput_mi_b_per_sec is not None:
        props_kwargs["provisioned_throughput_mi_b_per_sec"] = provisioned_throughput_mi_b_per_sec
    if public_network_access is not None:
        props_kwargs["public_network_access"] = public_network_access
    properties = fs_models.FileShareUpdateProperties(**props_kwargs) if props_kwargs else None
    return fs_models.FileShareUpdate(tags=tags, properties=properties)


def build_snapshot_payload(metadata: Optional[dict] = None) -> fs_models.FileShareSnapshot:
    return fs_models.FileShareSnapshot(
        properties=fs_models.FileShareSnapshotProperties(metadata=metadata or {}),
    )


# --- Cleanup helpers ------------------------------------------------------


def safe_delete_share(client: FileSharesMgmtClient, resource_group_name: str, resource_name: str) -> None:
    """Best-effort delete; swallow 404 / generic ARM errors so cleanup never fails a test."""
    try:
        client.file_shares.begin_delete(
            resource_group_name=resource_group_name,
            resource_name=resource_name,
        ).result()
    except (ResourceNotFoundError, HttpResponseError):
        pass


def safe_delete_snapshot(
    client: FileSharesMgmtClient,
    resource_group_name: str,
    resource_name: str,
    snapshot_name: str,
) -> None:
    try:
        client.file_share_snapshots.begin_delete_file_share_snapshot(
            resource_group_name=resource_group_name,
            resource_name=resource_name,
            name=snapshot_name,
        ).result()
    except (ResourceNotFoundError, HttpResponseError):
        pass


# --- Test base mixin ------------------------------------------------------


def make_client(test_case) -> FileSharesMgmtClient:
    """Construct a ``FileSharesMgmtClient`` against the canary ARM endpoint, mirroring
    ``test_fileshares_crud.py``."""
    return test_case.create_mgmt_client(
        FileSharesMgmtClient,
        base_url=ARM_ENDPOINT,
        credential_scopes=["https://management.azure.com/.default"],
    )
