from uuid import uuid4

import pytest
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.storage.blobs import BlobStorage
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._resource import FieldType
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, AzureInfrastructure, export, field, AzureApp

TEST_SUB = "6e441d6a-23ce-4450-a4a6-78f8d4f45ce9"
RG = ResourceSymbol("resourcegroup")
IDENTITY = {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}}


def _get_outputs(suffix="", rg=None):
    return {
        "endpoint": [
            Output(
                f"AZURE_BLOBS_ENDPOINT",
                "properties.primaryEndpoints.blob",
                ResourceSymbol(f"storageaccount{suffix}"),
            )
        ]
    }


def test_storage_blobs_properties():
    r = BlobStorage()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r.identifier == ResourceIdentifiers.blob_storage
    assert isinstance(r.parent, StorageAccount)
    assert r._existing == False
    assert r.resource == "Microsoft.Storage/storageAccounts/blobServices"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 2
    assert list(fields.keys()) == ["storageaccount", "storageaccount.blobservice"]
    assert fields["storageaccount.blobservice"].resource == "Microsoft.Storage/storageAccounts/blobServices"
    assert fields["storageaccount.blobservice"].properties == {
        "parent": ResourceSymbol("storageaccount"),
    }
    assert fields["storageaccount.blobservice"].outputs == _get_outputs()
    assert fields["storageaccount.blobservice"].extensions == {}
    assert fields["storageaccount.blobservice"].existing == False
    assert fields["storageaccount.blobservice"].version
    assert fields["storageaccount.blobservice"].symbol == symbols[0]
    assert fields["storageaccount.blobservice"].resource_group == None
    assert not fields["storageaccount.blobservice"].name
    assert fields["storageaccount.blobservice"].defaults

    r2 = BlobStorage(location="westus", sku="Standard_RAGRS", is_versioning_enabled=True)
    assert r2.properties == {"properties": {"isVersioningEnabled": True}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["storageaccount", "storageaccount.blobservice"]
    assert fields["storageaccount.blobservice"].resource == "Microsoft.Storage/storageAccounts/blobServices"
    assert fields["storageaccount.blobservice"].properties == {
        "properties": {"isVersioningEnabled": True},
        "parent": ResourceSymbol("storageaccount"),
    }
    assert fields["storageaccount.blobservice"].outputs == _get_outputs()
    assert fields["storageaccount.blobservice"].extensions == {}
    assert fields["storageaccount.blobservice"].existing == False
    assert fields["storageaccount.blobservice"].version
    assert fields["storageaccount.blobservice"].symbol == symbols[0]
    assert fields["storageaccount.blobservice"].resource_group == None
    assert not fields["storageaccount.blobservice"].name
    assert fields["storageaccount.blobservice"].defaults

    r3 = StorageAccount(sku="Premium_ZRS")
    assert r3.properties == {"sku": {"name": "Premium_ZRS"}, "properties": {}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r3 = BlobStorage(is_versioning_enabled=False)
    assert r3.properties == {"properties": {"isVersioningEnabled": False}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = BlobStorage(account="foo")
    assert r4.properties == {"properties": {}}
    assert r4.parent == StorageAccount(name="foo")
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "storageaccount",
        "storageaccount.blobservice",
        "storageaccount_foo",
        "storageaccount_foo.blobservice_foo",
    ]
    assert fields["storageaccount_foo.blobservice_foo"].resource == "Microsoft.Storage/storageAccounts/blobServices"
    assert fields["storageaccount_foo.blobservice_foo"].properties == {
        "parent": ResourceSymbol("storageaccount_foo"),
    }
    assert fields["storageaccount_foo.blobservice_foo"].outputs == _get_outputs("_foo")
    assert fields["storageaccount_foo.blobservice_foo"].extensions == {}
    assert fields["storageaccount_foo.blobservice_foo"].existing == False
    assert fields["storageaccount_foo.blobservice_foo"].version
    assert fields["storageaccount_foo.blobservice_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo.blobservice_foo"].resource_group == None
    assert fields["storageaccount_foo.blobservice_foo"].name == None
    assert fields["storageaccount_foo.blobservice_foo"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = BlobStorage(account=param1, is_versioning_enabled=param2, automatic_snapshot_policy_enabled=param3)
    assert r5.properties == {"properties": {"isVersioningEnabled": param2, "automaticSnapshotPolicyEnabled": param3}}
    assert r5.parent == StorageAccount(name=param1)
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["storageaccount_testa", "storageaccount_testa.blobservice_testa"]
    assert fields["storageaccount_testa.blobservice_testa"].resource == "Microsoft.Storage/storageAccounts/blobServices"
    assert fields["storageaccount_testa.blobservice_testa"].properties == {
        "parent": ResourceSymbol("storageaccount_testa"),
        "properties": {"isVersioningEnabled": param2, "automaticSnapshotPolicyEnabled": param3},
    }
    assert fields["storageaccount_testa.blobservice_testa"].outputs == _get_outputs("_testa")
    assert fields["storageaccount_testa.blobservice_testa"].extensions == {}
    assert fields["storageaccount_testa.blobservice_testa"].existing == False
    assert fields["storageaccount_testa.blobservice_testa"].version
    assert fields["storageaccount_testa.blobservice_testa"].symbol == symbols[0]
    assert fields["storageaccount_testa.blobservice_testa"].resource_group == None
    assert fields["storageaccount_testa.blobservice_testa"].name == None
    assert fields["storageaccount_testa.blobservice_testa"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_storage_blobs_reference():
    r = BlobStorage.reference(account="foo")
    assert r.properties == {}
    assert r._existing == True
    assert r.parent == StorageAccount.reference(name="foo")
    assert r.extensions == {}
    assert r._settings["name"]() == "default"
    with pytest.raises(RuntimeError):
        r._settings["resource_group"]()
    with pytest.raises(RuntimeError):
        r._settings["subscription"]()
    with pytest.raises(RuntimeError):
        r._settings["resource_id"]()
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["storageaccount_foo", "storageaccount_foo.blobservice_foo"]
    assert fields["storageaccount_foo.blobservice_foo"].resource == "Microsoft.Storage/storageAccounts/blobServices"
    assert fields["storageaccount_foo.blobservice_foo"].properties == {
        "name": "default",
        "parent": ResourceSymbol("storageaccount_foo"),
    }
    assert fields["storageaccount_foo.blobservice_foo"].outputs == _get_outputs("_foo")
    assert fields["storageaccount_foo.blobservice_foo"].extensions == {}
    assert fields["storageaccount_foo.blobservice_foo"].existing == True
    assert fields["storageaccount_foo.blobservice_foo"].version
    assert fields["storageaccount_foo.blobservice_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo.blobservice_foo"].resource_group == None
    assert fields["storageaccount_foo.blobservice_foo"].name == "default"
    assert not fields["storageaccount_foo.blobservice_foo"].defaults

    rg = ResourceSymbol("resourcegroup_bar")
    r = BlobStorage.reference(account="foo", resource_group="bar")
    assert r.properties == {}
    assert r._settings["resource_group"]() == "bar"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_bar", "storageaccount_foo", "storageaccount_foo.blobservice_foo"]
    assert fields["storageaccount_foo.blobservice_foo"].resource == "Microsoft.Storage/storageAccounts/blobServices"
    assert fields["storageaccount_foo.blobservice_foo"].properties == {
        "name": "default",
        "parent": ResourceSymbol("storageaccount_foo"),
    }
    assert fields["storageaccount_foo.blobservice_foo"].outputs == _get_outputs("_foo", "bar")
    assert fields["storageaccount_foo.blobservice_foo"].extensions == {}
    assert fields["storageaccount_foo.blobservice_foo"].existing == True
    assert fields["storageaccount_foo.blobservice_foo"].version
    assert fields["storageaccount_foo.blobservice_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo.blobservice_foo"].resource_group == None
    assert fields["storageaccount_foo.blobservice_foo"].name == "default"
    assert not fields["storageaccount_foo.blobservice_foo"].defaults

    r = BlobStorage.reference(
        account=StorageAccount.reference(
            name="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB)
        )
    )
    assert r.properties == {}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.Storage/storageAccounts/foo/blobServices/default"
    )


def test_storage_blobs_defaults():
    versioning = Parameter("VersioningEnabled", default=True)
    r = BlobStorage(is_versioning_enabled=versioning)
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    add_defaults(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    assert field.properties == {
        "name": "default",
        "parent": ResourceSymbol("storageaccount"),
        "properties": {
            "isVersioningEnabled": versioning,
        },
    }


def test_storage_blobs_export(export_dir):
    with pytest.raises(ValueError):
        BlobStorage(account="account", resource_group="foo", parent=StorageAccount())

    class test(AzureInfrastructure):
        r: BlobStorage = BlobStorage()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_blobs_export_existing(export_dir):
    with pytest.raises(ValueError):
        BlobStorage.reference(account=StorageAccount(), resource_group="foo")

    class test(AzureInfrastructure):
        r: BlobStorage = field(default=BlobStorage.reference(account=StorageAccount.reference(name="storagetest")))

    infra = test(resource_group=ResourceGroup.reference(name="rgtest"), identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_blobs_export_existing_new_rg(export_dir):
    class test(AzureInfrastructure):
        r: BlobStorage = field(default=BlobStorage.reference(account="storagetest", resource_group="rgtest"))

    infra = test(identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_blobs_export_with_properties(export_dir):
    with pytest.raises(TypeError):
        BlobStorage(account=StorageAccount(), location="westus", sku="Premium_LRS")

    class test(AzureInfrastructure):
        r: BlobStorage = field(
            default=BlobStorage(
                {"properties": {}},
                account=StorageAccount(),
                is_versioning_enabled=True,
                cors_rules=[{"allowedMethods": ["GET", "HEAD"], "maxAgeInSeconds": 5}],
                automatic_snapshot_policy_enabled=True,
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_blobs_export_with_role_assignments(export_dir):
    class test(AzureInfrastructure):
        r: BlobStorage = field(default=BlobStorage(roles=[], user_roles=[]))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_blobs_export_with_no_user_access(export_dir):
    class test(AzureInfrastructure):
        r: BlobStorage = field(
            default=BlobStorage(roles=["Storage Blob Data Owner"], user_roles=["Storage Blob Data Contributor"])
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2], user_access=False)


def test_storage_blobs_client():
    from azure.storage.blob import BlobServiceClient
    from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient

    r = BlobStorage()
    with pytest.raises(RuntimeError):
        r.get_client(BlobServiceClient)

    r = BlobStorage.reference(account="foo")
    assert r._settings["endpoint"]() == "https://foo.blob.core.windows.net/"
    client = r.get_client()
    assert isinstance(client, BlobServiceClient)
    client = r.get_client(use_async=True)
    assert isinstance(client, AsyncBlobServiceClient)
    client = r.get_client(BlobServiceClient)
    assert isinstance(client, BlobServiceClient)
    client = r.get_client(AsyncBlobServiceClient)
    assert isinstance(client, AsyncBlobServiceClient)


def test_storage_blobs_infra():
    class TestInfra(AzureInfrastructure):
        data: BlobStorage = BlobStorage()

    assert isinstance(TestInfra.data, BlobStorage)
    infra = TestInfra()
    assert isinstance(infra.data, BlobStorage)
    assert infra.data.properties == {"properties": {}}

    infra = TestInfra(data=BlobStorage(account="foo"))
    assert infra.data._settings["name"]() == "default"
    assert infra.data.parent._settings["name"]() == "foo"

    class TestInfra(AzureInfrastructure):
        data: BlobStorage = field(default=BlobStorage.reference(account="teststorage"))

    infra = TestInfra()
    assert infra.data._settings["name"]() == "default"
    assert infra.data.parent._settings["name"]() == "teststorage"


def test_storage_blobs_app():
    from azure.storage.blob import BlobServiceClient

    r = BlobStorage.reference(account="test", resource_group="test")

    class TestApp(AzureApp):
        client: BlobServiceClient

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(client=r)
    assert isinstance(app.client, BlobServiceClient)
