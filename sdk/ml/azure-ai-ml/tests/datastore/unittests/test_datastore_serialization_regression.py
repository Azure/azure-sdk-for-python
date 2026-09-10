# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regression test for the datastore create_or_update mixed-tree serialization bug.

Context (production regression, azure-ai-ml 1.34.0/1.35.0):
``DatastoreOperations.create_or_update`` was migrated to the arm_ml_service client (its operation
serializes the request body with ``json.dumps(body, cls=SdkJSONEncoder, ...)``), but the datastore
ENTITIES still returned an old per-version msrest ``Datastore`` model. ``SdkJSONEncoder``
can only serialize arm hybrid models, so a msrest datastore body raised
``TypeError: Object of type Datastore is not JSON serializable`` on every create/update — a hard
failure for customers, invisible to the mocked unit tests and the (skipped/live-only) e2e tests.

This test freezes the fix: every datastore entity's ``_to_rest_object()`` must serialize cleanly
through the arm operation's encoder. It is the offline Class-A (mixed-tree) guard the original
migration lacked.
"""
import json

import pytest

from azure.ai.ml._restclient.arm_ml_service._utils.model_base import SdkJSONEncoder
from azure.ai.ml.entities._credentials import (
    AccountKeyConfiguration,
    CertificateConfiguration,
    ServicePrincipalConfiguration,
)
from azure.ai.ml.entities._datastore.adls_gen1 import AzureDataLakeGen1Datastore
from azure.ai.ml.entities._datastore.azure_storage import (
    AzureBlobDatastore,
    AzureDataLakeGen2Datastore,
    AzureFileDatastore,
)
from azure.ai.ml.entities._datastore.one_lake import OneLakeDatastore


def _serializes_via_arm_operation(rest_obj) -> dict:
    """Serialize exactly the way ``DatastoreOperations.create_or_update`` does on the arm client."""
    return json.loads(json.dumps(rest_obj, cls=SdkJSONEncoder, exclude_readonly=True))


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestDatastoreSerializationRegression:
    def test_blob_datastore_body_serializes(self) -> None:
        ds = AzureBlobDatastore(
            name="ds",
            account_name="acct",
            container_name="container",
            credentials=AccountKeyConfiguration(account_key="fake"),
        )
        wire = _serializes_via_arm_operation(ds._to_rest_object())
        assert wire["properties"]["datastoreType"] == "AzureBlob"
        assert wire["properties"]["accountName"] == "acct"

    def test_file_datastore_body_serializes(self) -> None:
        ds = AzureFileDatastore(
            name="ds",
            account_name="acct",
            file_share_name="share",
            credentials=AccountKeyConfiguration(account_key="fake"),
        )
        wire = _serializes_via_arm_operation(ds._to_rest_object())
        assert wire["properties"]["datastoreType"] == "AzureFile"

    def test_adls_gen2_datastore_body_serializes(self) -> None:
        ds = AzureDataLakeGen2Datastore(
            name="ds",
            account_name="acct",
            filesystem="fs",
            credentials=ServicePrincipalConfiguration(tenant_id="t", client_id="c", client_secret="s"),
        )
        wire = _serializes_via_arm_operation(ds._to_rest_object())
        assert wire["properties"]["datastoreType"] == "AzureDataLakeGen2"

    def test_adls_gen1_datastore_body_serializes(self) -> None:
        ds = AzureDataLakeGen1Datastore(
            name="ds",
            store_name="store",
            credentials=ServicePrincipalConfiguration(tenant_id="t", client_id="c", client_secret="s"),
        )
        wire = _serializes_via_arm_operation(ds._to_rest_object())
        assert wire["properties"]["datastoreType"] == "AzureDataLakeGen1"

    def test_adls_gen2_certificate_datastore_body_serializes(self) -> None:
        # Certificate credentials exercise CertificateConfiguration._to_datastore_rest_object, whose
        # ``resource_url`` field is a distinct arm wire name (the old msrest model called it
        # ``resource_uri``). Guards the cert-auth create/update path.
        ds = AzureDataLakeGen2Datastore(
            name="ds",
            account_name="acct",
            filesystem="fs",
            credentials=CertificateConfiguration(
                tenant_id="t",
                client_id="c",
                thumbprint="tp",
                certificate="cert",
                authority_url="https://login.microsoftonline.com",
                resource_url="https://storage.azure.com/",
            ),
        )
        wire = _serializes_via_arm_operation(ds._to_rest_object())
        creds = wire["properties"]["credentials"]
        assert creds["credentialsType"] == "Certificate"
        assert creds["resourceUrl"] == "https://storage.azure.com/"

    def test_adls_gen1_certificate_datastore_body_serializes(self) -> None:
        ds = AzureDataLakeGen1Datastore(
            name="ds",
            store_name="store",
            credentials=CertificateConfiguration(
                tenant_id="t",
                client_id="c",
                thumbprint="tp",
                certificate="cert",
                authority_url="https://login.microsoftonline.com",
                resource_url="https://datalake.azure.net/",
            ),
        )
        wire = _serializes_via_arm_operation(ds._to_rest_object())
        creds = wire["properties"]["credentials"]
        assert creds["credentialsType"] == "Certificate"
        assert creds["resourceUrl"] == "https://datalake.azure.net/"

    def test_one_lake_datastore_body_serializes(self) -> None:
        from azure.ai.ml.entities._datastore.one_lake import LakeHouseArtifact

        ds = OneLakeDatastore(
            name="ds",
            one_lake_workspace_name="ws",
            endpoint="onelake.dfs.fabric.microsoft.com",
            artifact=LakeHouseArtifact(name="artifact"),
            credentials=ServicePrincipalConfiguration(tenant_id="t", client_id="c", client_secret="s"),
        )
        wire = _serializes_via_arm_operation(ds._to_rest_object())
        assert wire["properties"]["datastoreType"] == "OneLake"
