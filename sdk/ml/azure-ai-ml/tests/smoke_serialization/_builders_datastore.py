# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for datastore entities (smoke serialization suite).

Datastores are part of the control-plane surface the upcoming migrations touch. Each builder is fully
deterministic so the request wire is byte-stable across runs.
"""
from azure.ai.ml.entities import (
    AccountKeyConfiguration,
    AzureBlobDatastore,
    AzureDataLakeGen1Datastore,
    AzureDataLakeGen2Datastore,
    AzureFileDatastore,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
)
from azure.ai.ml.entities._datastore.one_lake import LakeHouseArtifact, OneLakeDatastore


def build_blob_datastore_account_key():
    """AzureBlobDatastore with an account-key credential."""
    return AzureBlobDatastore(
        name="smoke-blob-ds",
        description="smoke blob datastore",
        account_name="smokeaccount",
        container_name="smoke-container",
        tags={"tag1": "value1"},
        credentials=AccountKeyConfiguration(account_key="smoke-account-key"),
    )


def build_blob_datastore_sas():
    """AzureBlobDatastore with a SAS-token credential and explicit endpoint/protocol."""
    return AzureBlobDatastore(
        name="smoke-blob-ds-sas",
        account_name="smokeaccount",
        container_name="smoke-container",
        endpoint="core.windows.net",
        protocol="https",
        credentials=SasTokenConfiguration(sas_token="?sv=smoke-sas-token"),
    )


def build_file_datastore():
    """AzureFileDatastore with an account-key credential."""
    return AzureFileDatastore(
        name="smoke-file-ds",
        account_name="smokeaccount",
        file_share_name="smoke-share",
        tags={"tag1": "value1"},
        credentials=AccountKeyConfiguration(account_key="smoke-account-key"),
    )


def build_adls_gen1_datastore():
    """AzureDataLakeGen1Datastore with a service-principal credential."""
    return AzureDataLakeGen1Datastore(
        name="smoke-gen1-ds",
        store_name="smoke-store",
        tags={"tag1": "value1"},
        credentials=ServicePrincipalConfiguration(
            tenant_id="00000000-0000-0000-0000-000000000000",
            client_id="11111111-1111-1111-1111-111111111111",
            client_secret="smoke-secret",
        ),
    )


def build_adls_gen2_datastore():
    """AzureDataLakeGen2Datastore with a service-principal credential."""
    return AzureDataLakeGen2Datastore(
        name="smoke-gen2-ds",
        account_name="smokeaccount",
        filesystem="smoke-filesystem",
        endpoint="core.windows.net",
        protocol="https",
        credentials=ServicePrincipalConfiguration(
            tenant_id="00000000-0000-0000-0000-000000000000",
            client_id="11111111-1111-1111-1111-111111111111",
            client_secret="smoke-secret",
        ),
    )


def build_one_lake_datastore():
    """OneLakeDatastore with a LakeHouse artifact and a service-principal credential."""
    return OneLakeDatastore(
        name="smoke-onelake-ds",
        one_lake_workspace_name="smoke-onelake-workspace",
        endpoint="onelake.dfs.fabric.microsoft.com",
        artifact=LakeHouseArtifact(name="smoke-lakehouse"),
        credentials=ServicePrincipalConfiguration(
            tenant_id="00000000-0000-0000-0000-000000000000",
            client_id="11111111-1111-1111-1111-111111111111",
            client_secret="smoke-secret",
        ),
    )


DATASTORE_BUILDERS = {
    "blob_datastore_account_key": build_blob_datastore_account_key,
    "blob_datastore_sas": build_blob_datastore_sas,
    "file_datastore": build_file_datastore,
    "adls_gen1_datastore": build_adls_gen1_datastore,
    "adls_gen2_datastore": build_adls_gen2_datastore,
    "one_lake_datastore": build_one_lake_datastore,
}
