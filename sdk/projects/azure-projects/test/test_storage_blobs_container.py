from uuid import uuid4

import pytest
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.storage.blobs import BlobStorage
from azure.projects.resources.storage.blobs.container import BlobContainer
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._resource import FieldType
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, AzureInfrastructure, export, field, AzureApp

TEST_SUB = "6e441d6a-23ce-4450-a4a6-78f8d4f45ce9"
RG = ResourceSymbol("resourcegroup")
IDENTITY = {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"].format(): {}}}


def _get_outputs(suffix="", parent="", rg=None):
    outputs = {
        "resource_id": Output(f"AZURE_BLOB_CONTAINER_ID{suffix.upper()}", "id", ResourceSymbol(f"container{suffix}")),
        "name": Output(f"AZURE_BLOB_CONTAINER_NAME{suffix.upper()}", "name", ResourceSymbol(f"container{suffix}")),
        "resource_group": Output(
            f"AZURE_BLOB_CONTAINER_RESOURCE_GROUP{suffix.upper()}", rg if rg else DefaultResourceGroup().name
        ),
    }
    outputs.update(
        {
            "endpoint": Output(
                f"AZURE_BLOB_CONTAINER_ENDPOINT{suffix.upper()}",
                Output("", "properties.primaryEndpoints.blob", ResourceSymbol(f"storageaccount{parent}")).format()
                + outputs["name"].format(),
            )
        }
    )
    return outputs


def test_storage_blobs_container_properties():
    r = BlobContainer()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r.identifier == ResourceIdentifiers.blob_container
    assert r.parent == BlobStorage()
    assert r.parent.parent == StorageAccount()
    assert r._existing == False
    assert r.resource == "Microsoft.Storage/storageAccounts/blobServices/containers"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 3
    assert list(fields.keys()) == [
        "storageaccount",
        "storageaccount.blobservice",
        "storageaccount.blobservice.container",
    ]
    assert (
        fields["storageaccount.blobservice.container"].resource
        == "Microsoft.Storage/storageAccounts/blobServices/containers"
    )
    assert fields["storageaccount.blobservice.container"].properties == {
        "properties": {},
        "parent": ResourceSymbol("blobservice"),
    }
    assert fields["storageaccount.blobservice.container"].outputs == _get_outputs()
    assert fields["storageaccount.blobservice.container"].extensions == {}
    assert fields["storageaccount.blobservice.container"].existing == False
    assert fields["storageaccount.blobservice.container"].version
    assert fields["storageaccount.blobservice.container"].symbol == symbols[0]
    assert fields["storageaccount.blobservice.container"].resource_group == None
    assert not fields["storageaccount.blobservice.container"].name
    assert fields["storageaccount.blobservice.container"].add_defaults

    r2 = BlobContainer(default_encryption_scope="test")
    assert r2.properties == {"properties": {"defaultEncryptionScope": "test"}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "storageaccount",
        "storageaccount.blobservice",
        "storageaccount.blobservice.container",
    ]
    assert (
        fields["storageaccount.blobservice.container"].resource
        == "Microsoft.Storage/storageAccounts/blobServices/containers"
    )
    assert fields["storageaccount.blobservice.container"].properties == {
        "properties": {"defaultEncryptionScope": "test"},
        "parent": ResourceSymbol("blobservice"),
    }
    assert fields["storageaccount.blobservice.container"].outputs == _get_outputs()
    assert fields["storageaccount.blobservice.container"].extensions == {}
    assert fields["storageaccount.blobservice.container"].existing == False
    assert fields["storageaccount.blobservice.container"].version
    assert fields["storageaccount.blobservice.container"].symbol == symbols[0]
    assert fields["storageaccount.blobservice.container"].resource_group == None
    assert not fields["storageaccount.blobservice.container"].name
    assert fields["storageaccount.blobservice.container"].add_defaults

    r3 = BlobContainer(default_encryption_scope="foo")
    assert r3.properties == {"properties": {"defaultEncryptionScope": "foo"}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = BlobContainer(name="foo")
    assert r4.properties == {"name": "foo", "properties": {}}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "storageaccount",
        "storageaccount.blobservice",
        "storageaccount.blobservice.container",
        "storageaccount.blobservice.container_foo",
    ]
    assert (
        fields["storageaccount.blobservice.container_foo"].resource
        == "Microsoft.Storage/storageAccounts/blobServices/containers"
    )
    assert fields["storageaccount.blobservice.container_foo"].properties == {
        "parent": ResourceSymbol("blobservice"),
        "name": "foo",
        "properties": {},
    }
    assert fields["storageaccount.blobservice.container_foo"].outputs == _get_outputs("_foo")
    assert fields["storageaccount.blobservice.container_foo"].extensions == {}
    assert fields["storageaccount.blobservice.container_foo"].existing == False
    assert fields["storageaccount.blobservice.container_foo"].version
    assert fields["storageaccount.blobservice.container_foo"].symbol == symbols[0]
    assert fields["storageaccount.blobservice.container_foo"].resource_group == None
    assert fields["storageaccount.blobservice.container_foo"].name == "foo"
    assert fields["storageaccount.blobservice.container_foo"].add_defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = BlobContainer(account=param1, name=param2, default_encryption_scope=param3)
    assert r5.properties == {"name": param2, "properties": {"defaultEncryptionScope": param3}}
    assert r5.parent.parent == StorageAccount(name=param1)
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == [
        "storageaccount_testa",
        "storageaccount_testa.blobservice_testa",
        "storageaccount_testa.blobservice_testa.container_testa_testb",
    ]
    assert (
        fields["storageaccount_testa.blobservice_testa.container_testa_testb"].resource
        == "Microsoft.Storage/storageAccounts/blobServices/containers"
    )
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].properties == {
        "parent": ResourceSymbol("blobservice_testa"),
        "properties": {"defaultEncryptionScope": param3},
        "name": param2,
    }
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].outputs == _get_outputs(
        "_testa_testb", "_testa"
    )
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].extensions == {}
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].existing == False
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].version
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].symbol == symbols[0]
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].resource_group == None
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].name == param2
    assert fields["storageaccount_testa.blobservice_testa.container_testa_testb"].add_defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_storage_blobs_container_reference():
    r = BlobContainer.reference(name="foo", account="bar")
    assert r.properties == {"name": "foo"}
    assert r._existing == True
    assert r.parent.parent == StorageAccount.reference(name="bar")
    assert r.extensions == {}
    assert r._settings["name"]() == "foo"
    with pytest.raises(RuntimeError):
        r._settings["resource_group"]()
    with pytest.raises(RuntimeError):
        r._settings["subscription"]()
    with pytest.raises(RuntimeError):
        r._settings["resource_id"]()
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "storageaccount_bar",
        "storageaccount_bar.blobservice_bar",
        "storageaccount_bar.blobservice_bar.container_bar_foo",
    ]
    assert (
        fields["storageaccount_bar.blobservice_bar.container_bar_foo"].resource
        == "Microsoft.Storage/storageAccounts/blobServices/containers"
    )
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].properties == {
        "name": "foo",
        "parent": ResourceSymbol("blobservice_bar"),
    }
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].outputs == _get_outputs("_bar_foo", "_bar")
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].extensions == {}
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].existing == True
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].version
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].symbol == symbols[0]
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].resource_group == None
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].name == "foo"
    assert not fields["storageaccount_bar.blobservice_bar.container_bar_foo"].add_defaults

    rg = ResourceSymbol("resourcegroup_baz")
    r = BlobContainer.reference(name="foo", account="bar", resource_group="baz")
    assert r.properties == {"name": "foo"}
    assert r._settings["resource_group"]() == "baz"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "resourcegroup_baz",
        "storageaccount_bar",
        "storageaccount_bar.blobservice_bar",
        "storageaccount_bar.blobservice_bar.container_bar_foo",
    ]
    assert (
        fields["storageaccount_bar.blobservice_bar.container_bar_foo"].resource
        == "Microsoft.Storage/storageAccounts/blobServices/containers"
    )
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].properties == {
        "name": "foo",
        "parent": ResourceSymbol("blobservice_bar"),
    }
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].outputs == _get_outputs(
        "_bar_foo", "_bar", "baz"
    )
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].extensions == {}
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].existing == True
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].version
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].symbol == symbols[0]
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].resource_group == None
    assert fields["storageaccount_bar.blobservice_bar.container_bar_foo"].name == "foo"
    assert not fields["storageaccount_bar.blobservice_bar.container_bar_foo"].add_defaults

    account = BlobStorage.reference(
        account="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB)
    )
    assert account._settings["subscription"]() == TEST_SUB
    r = BlobContainer.reference(name="foo", account=account)
    assert r.properties == {"name": "foo"}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.Storage/storageAccounts/foo/blobServices/default/containers/foo"
    )


def test_storage_blobs_container_defaults():
    scope = Parameter("EncryptionScope", default="foobar")
    r = BlobContainer(default_encryption_scope=scope)
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    field.add_defaults(field, parameters=dict(GLOBAL_PARAMS))
    assert field.properties == {
        "name": GLOBAL_PARAMS["defaultName"],
        "parent": ResourceSymbol("blobservice"),
        "properties": {
            "defaultEncryptionScope": scope,
        },
    }


def test_storage_blobs_container_export(export_dir):
    class TestInfra(AzureInfrastructure):
        r: BlobContainer = BlobContainer()

    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_blobs_container_export_existing(export_dir):
    class TestInfra(AzureInfrastructure):
        r: BlobContainer = field(default=BlobContainer.reference(name="test", account="storagetest"))

    infra = TestInfra(resource_group=ResourceGroup.reference(name="testrg"), identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_blobs_container_export_existing_new_rg(export_dir):
    class TestInfra(AzureInfrastructure):
        r: BlobContainer = field(
            default=BlobContainer.reference(name="test", account="storagetest", resource_group="testrg")
        )

    infra = TestInfra(identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_blobs_container_export_with_properties(export_dir):
    class TestInfra(AzureInfrastructure):
        r: BlobContainer = field(
            default=BlobContainer(name="foo", default_encryption_scope="test", deny_encryption_scope_override=True)
        )

    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_blobs_container_export_with_role_assignments(export_dir):
    class TestInfra(AzureInfrastructure):
        r: BlobContainer = field(default=BlobContainer(roles=["Owner"], user_roles=["Contributor"]))

    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


# TODO: Test roles with parameters and field references


def test_storage_blobs_container_export_with_no_user_access(export_dir):
    class TestInfra(AzureInfrastructure):
        r: BlobContainer = field(
            default=BlobContainer(roles=["Storage Blob Data Owner"], user_roles=["Storage Blob Data Contributor"])
        )

    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test", user_access=False)


def test_storage_blobs_container_export_with_field_reference_with_default_str(export_dir):
    class TestInfra(AzureInfrastructure):
        name: str = field(default="foo")
        r: BlobContainer = BlobContainer(name=name)

    export(TestInfra(), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_blobs_container_export_with_field_reference_str_no_default(export_dir):
    class TestInfra(AzureInfrastructure):
        name: str = field()
        r: BlobContainer = BlobContainer(name=name)

    export(TestInfra(name="foo"), output_dir=export_dir[0], infra_dir=export_dir[2], name="test")


def test_storage_blobs_container_export_with_field_reference_resource_no_default(export_dir):
    class TestInfra(AzureInfrastructure):
        storage: BlobStorage = field()
        r: BlobContainer = BlobContainer(account=storage)

    export(
        TestInfra(storage=BlobStorage(account="teststorage")),
        output_dir=export_dir[0],
        infra_dir=export_dir[2],
        name="test",
    )


def test_storage_blobs_container_client():
    from azure.storage.blob import ContainerClient
    from azure.storage.blob.aio import ContainerClient as AsyncContainerClient

    r = BlobContainer()
    with pytest.raises(RuntimeError):
        r.get_client()

    r = BlobContainer.reference(name="foo", account="bar")
    assert r._settings["endpoint"]() == "https://bar.blob.core.windows.net/foo"
    client = r.get_client()
    assert isinstance(client, ContainerClient)
    client = r.get_client(use_async=True)
    assert isinstance(client, AsyncContainerClient)
    client = r.get_client(ContainerClient)
    assert isinstance(client, ContainerClient)
    client = r.get_client(AsyncContainerClient)
    assert isinstance(client, AsyncContainerClient)


def test_storage_blobs_container_infra():
    class TestInfra(AzureInfrastructure):
        data: BlobContainer = BlobContainer()

    assert isinstance(TestInfra.data, BlobContainer)
    infra = TestInfra()
    assert isinstance(infra.data, BlobContainer)
    assert infra.data.properties == {"properties": {}}

    infra = TestInfra(data=BlobContainer(name="foo", account="bar"))
    assert infra.data._settings["name"]() == "foo"
    assert infra.data.parent.parent._settings["name"]() == "bar"

    class TestInfra(AzureInfrastructure):
        data: BlobContainer = field(default=BlobContainer.reference(name="testdata", account="teststorage"))

    infra = TestInfra()
    assert infra.data._settings["name"]() == "testdata"
    assert infra.data.parent.parent._settings["name"]() == "teststorage"


def test_storage_blobs_container_app():
    from azure.storage.blob import ContainerClient
    from azure.storage.blob.aio import ContainerClient as AsyncContainerClient

    r = BlobContainer.reference(name="test", account="test", resource_group="test")

    class TestApp(AzureApp):
        sclient: ContainerClient
        aclient: AsyncContainerClient

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(sclient=r, aclient=r)
    assert isinstance(app.sclient, ContainerClient)
    assert isinstance(app.aclient, AsyncContainerClient)

    class TestInfra(AzureInfrastructure):
        data: BlobContainer = field(default=r)

    app = TestApp.load(TestInfra())
    assert isinstance(app.sclient, ContainerClient)
    assert isinstance(app.aclient, AsyncContainerClient)
