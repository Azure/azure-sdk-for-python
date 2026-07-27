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
    CertificateConfiguration,
    NoneCredentialConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
)
from azure.ai.ml.entities._datastore.one_lake import LakeHouseArtifact, OneLakeDatastore
from azure.ai.ml.entities._datastore._on_prem import HdfsDatastore
from azure.ai.ml.entities._datastore._on_prem_credentials import KerberosPasswordCredentials


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


def build_adls_gen2_datastore_certificate():
    """AzureDataLakeGen2Datastore with a certificate credential.

    NOTE: ``resource_url``/``authority_url`` are intentionally NOT set. Pre-migration the entity passed
    ``resource_uri`` to the msrest ``CertificateDatastoreCredentials``, which silently dropped it (not a
    known attribute), so it never reached the wire. The migration fixed this to the correct ``resource_url``
    (wire key ``resourceUrl``) so it is now honored -- a latent bug-fix that changes the wire only when the
    value is set. Omitting it here keeps the guard on the substantive cert wire (tenant/client/cert/thumbprint).
    """
    return AzureDataLakeGen2Datastore(
        name="smoke-gen2-cert-ds",
        account_name="smokeaccount",
        filesystem="smoke-filesystem",
        credentials=CertificateConfiguration(
            tenant_id="00000000-0000-0000-0000-000000000000",
            client_id="11111111-1111-1111-1111-111111111111",
            certificate="smoke-certificate-pem",
            thumbprint="SMOKE-THUMBPRINT",
        ),
    )


def build_blob_datastore_none_credential():
    """AzureBlobDatastore with no credential (credential-less / identity-based access)."""
    return AzureBlobDatastore(
        name="smoke-blob-none-ds",
        account_name="smokeaccount",
        container_name="smoke-container",
        credentials=NoneCredentialConfiguration(),
    )


def build_hdfs_datastore_kerberos_password():
    """HdfsDatastore (arm-absent, hand-built JSON-direct wire) with Kerberos password credentials."""
    return HdfsDatastore(
        name="smoke-hdfs-ds",
        name_node_address="hdfs-namenode.smoke.local",
        protocol="https",
        credentials=KerberosPasswordCredentials(
            kerberos_realm="SMOKE.LOCAL",
            kerberos_kdc_address="kdc.smoke.local",
            kerberos_principal="smoke@SMOKE.LOCAL",
            kerberos_password="smoke-kerberos-password",
        ),
    )


DATASTORE_BUILDERS = {
    "blob_datastore_account_key": build_blob_datastore_account_key,
    "blob_datastore_sas": build_blob_datastore_sas,
    "blob_datastore_none_credential": build_blob_datastore_none_credential,
    "file_datastore": build_file_datastore,
    "adls_gen1_datastore": build_adls_gen1_datastore,
    "adls_gen2_datastore": build_adls_gen2_datastore,
    "adls_gen2_datastore_certificate": build_adls_gen2_datastore_certificate,
    "one_lake_datastore": build_one_lake_datastore,
    "hdfs_datastore_kerberos_password": build_hdfs_datastore_kerberos_password,
}
