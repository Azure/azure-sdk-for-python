from uuid import uuid4

import pytest
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.storage.tables import TableStorage
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
                f"AZURE_TABLES_ENDPOINT",
                "properties.primaryEndpoints.table",
                ResourceSymbol(f"storageaccount{suffix}"),
            )
        ]
    }


def test_storage_tables_properties():
    r = TableStorage()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r.identifier == ResourceIdentifiers.table_storage
    assert isinstance(r.parent, StorageAccount)
    assert r._existing == False
    assert r.resource == "Microsoft.Storage/storageAccounts/tableServices"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 2
    assert list(fields.keys()) == ["storageaccount", "storageaccount.tableservice"]
    assert fields["storageaccount.tableservice"].resource == "Microsoft.Storage/storageAccounts/tableServices"
    assert fields["storageaccount.tableservice"].properties == {
        "parent": ResourceSymbol("storageaccount"),
    }
    assert fields["storageaccount.tableservice"].outputs == _get_outputs()
    assert fields["storageaccount.tableservice"].extensions == {}
    assert fields["storageaccount.tableservice"].existing == False
    assert fields["storageaccount.tableservice"].version
    assert fields["storageaccount.tableservice"].symbol == symbols[0]
    assert fields["storageaccount.tableservice"].resource_group == None
    assert not fields["storageaccount.tableservice"].name
    assert fields["storageaccount.tableservice"].defaults

    r2 = TableStorage(location="westus", sku="Standard_RAGRS", cors_rules=[])
    assert r2.properties == {"properties": {"cors": {"corsRules": []}}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["storageaccount", "storageaccount.tableservice"]
    assert fields["storageaccount.tableservice"].resource == "Microsoft.Storage/storageAccounts/tableServices"
    assert fields["storageaccount.tableservice"].properties == {
        "properties": {"cors": {"corsRules": []}},
        "parent": ResourceSymbol("storageaccount"),
    }
    assert fields["storageaccount.tableservice"].outputs == _get_outputs()
    assert fields["storageaccount.tableservice"].extensions == {}
    assert fields["storageaccount.tableservice"].existing == False
    assert fields["storageaccount.tableservice"].version
    assert fields["storageaccount.tableservice"].symbol == symbols[0]
    assert fields["storageaccount.tableservice"].resource_group == None
    assert not fields["storageaccount.tableservice"].name
    assert fields["storageaccount.tableservice"].defaults

    r3 = StorageAccount(sku="Premium_ZRS")
    assert r3.properties == {"sku": {"name": "Premium_ZRS"}, "properties": {}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r3 = TableStorage(cors_rules=["foo"])
    assert r3.properties == {"properties": {"cors": {"corsRules": ["foo"]}}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = TableStorage(account="foo")
    assert r4.properties == {"properties": {}}
    assert r4.parent == StorageAccount(name="foo")
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "storageaccount",
        "storageaccount.tableservice",
        "storageaccount_foo",
        "storageaccount_foo.tableservice_foo",
    ]
    assert fields["storageaccount_foo.tableservice_foo"].resource == "Microsoft.Storage/storageAccounts/tableServices"
    assert fields["storageaccount_foo.tableservice_foo"].properties == {
        "parent": ResourceSymbol("storageaccount_foo"),
    }
    assert fields["storageaccount_foo.tableservice_foo"].outputs == _get_outputs("_foo")
    assert fields["storageaccount_foo.tableservice_foo"].extensions == {}
    assert fields["storageaccount_foo.tableservice_foo"].existing == False
    assert fields["storageaccount_foo.tableservice_foo"].version
    assert fields["storageaccount_foo.tableservice_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo.tableservice_foo"].resource_group == None
    assert fields["storageaccount_foo.tableservice_foo"].name == None
    assert fields["storageaccount_foo.tableservice_foo"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    r5 = TableStorage(account=param1, cors_rules=[param2])
    assert r5.properties == {"properties": {"cors": {"corsRules": [param2]}}}
    assert r5.parent == StorageAccount(name=param1)
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["storageaccount_testa", "storageaccount_testa.tableservice_testa"]
    assert (
        fields["storageaccount_testa.tableservice_testa"].resource == "Microsoft.Storage/storageAccounts/tableServices"
    )
    assert fields["storageaccount_testa.tableservice_testa"].properties == {
        "parent": ResourceSymbol("storageaccount_testa"),
        "properties": {"cors": {"corsRules": [param2]}},
    }
    assert fields["storageaccount_testa.tableservice_testa"].outputs == _get_outputs("_testa")
    assert fields["storageaccount_testa.tableservice_testa"].extensions == {}
    assert fields["storageaccount_testa.tableservice_testa"].existing == False
    assert fields["storageaccount_testa.tableservice_testa"].version
    assert fields["storageaccount_testa.tableservice_testa"].symbol == symbols[0]
    assert fields["storageaccount_testa.tableservice_testa"].resource_group == None
    assert fields["storageaccount_testa.tableservice_testa"].name == None
    assert fields["storageaccount_testa.tableservice_testa"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2


def test_storage_tables_reference():
    r = TableStorage.reference(account="foo")
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
    assert list(fields.keys()) == ["storageaccount_foo", "storageaccount_foo.tableservice_foo"]
    assert fields["storageaccount_foo.tableservice_foo"].resource == "Microsoft.Storage/storageAccounts/tableServices"
    assert fields["storageaccount_foo.tableservice_foo"].properties == {
        "name": "default",
        "parent": ResourceSymbol("storageaccount_foo"),
    }
    assert fields["storageaccount_foo.tableservice_foo"].outputs == _get_outputs("_foo")
    assert fields["storageaccount_foo.tableservice_foo"].extensions == {}
    assert fields["storageaccount_foo.tableservice_foo"].existing == True
    assert fields["storageaccount_foo.tableservice_foo"].version
    assert fields["storageaccount_foo.tableservice_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo.tableservice_foo"].resource_group == None
    assert fields["storageaccount_foo.tableservice_foo"].name == "default"
    assert not fields["storageaccount_foo.tableservice_foo"].defaults

    rg = ResourceSymbol("resourcegroup_bar")
    r = TableStorage.reference(account="foo", resource_group="bar")
    assert r.properties == {}
    assert r._settings["resource_group"]() == "bar"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_bar", "storageaccount_foo", "storageaccount_foo.tableservice_foo"]
    assert fields["storageaccount_foo.tableservice_foo"].resource == "Microsoft.Storage/storageAccounts/tableServices"
    assert fields["storageaccount_foo.tableservice_foo"].properties == {
        "name": "default",
        "parent": ResourceSymbol("storageaccount_foo"),
    }
    assert fields["storageaccount_foo.tableservice_foo"].outputs == _get_outputs("_foo", "bar")
    assert fields["storageaccount_foo.tableservice_foo"].extensions == {}
    assert fields["storageaccount_foo.tableservice_foo"].existing == True
    assert fields["storageaccount_foo.tableservice_foo"].version
    assert fields["storageaccount_foo.tableservice_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo.tableservice_foo"].resource_group == None
    assert fields["storageaccount_foo.tableservice_foo"].name == "default"
    assert not fields["storageaccount_foo.tableservice_foo"].defaults

    r = TableStorage.reference(
        account=StorageAccount.reference(
            name="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB)
        )
    )
    assert r.properties == {}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.Storage/storageAccounts/foo/tableServices/default"
    )


def test_storage_tables_defaults():
    rules = Parameter("CorsRules", default=[])
    r = TableStorage(cors_rules=rules)
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    add_defaults(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    assert field.properties == {
        "name": "default",
        "parent": ResourceSymbol("storageaccount"),
        "properties": {
            "cors": {"corsRules": rules},
        },
    }


def test_storage_tables_export(export_dir):
    with pytest.raises(ValueError):
        TableStorage(account="account", resource_group="foo", parent=StorageAccount())

    class test(AzureInfrastructure):
        r: TableStorage = TableStorage()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_tables_export_existing(export_dir):
    with pytest.raises(ValueError):
        TableStorage.reference(account=StorageAccount(), resource_group="foo")

    class test(AzureInfrastructure):
        r: TableStorage = field(default=TableStorage.reference(account=StorageAccount.reference(name="storagetest")))

    infra = test(resource_group=ResourceGroup.reference(name="rgtest"), identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_tables_export_existing_new_rg(export_dir):
    class test(AzureInfrastructure):
        r: TableStorage = field(default=TableStorage.reference(account="storagetest", resource_group="rgtest"))

    infra = test(identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_tables_export_with_properties(export_dir):
    with pytest.raises(TypeError):
        TableStorage(account=StorageAccount(), location="westus", sku="Premium_LRS")

    class test(AzureInfrastructure):
        r: TableStorage = field(
            default=TableStorage(
                {"properties": {}}, account=StorageAccount(), cors_rules=[{"allowedMethods": ["GET", "HEAD"]}]
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_tables_export_with_role_assignments(export_dir):
    class test(AzureInfrastructure):
        r: TableStorage = field(default=TableStorage(roles=[], user_roles=[]))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_tables_export_with_no_user_access(export_dir):
    class test(AzureInfrastructure):
        r: TableStorage = field(
            default=TableStorage(roles=["Storage Table Data Owner"], user_roles=["Storage Table Data Contributor"])
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2], user_access=False)


def test_storage_tables_client():
    from azure.data.tables import TableServiceClient
    from azure.data.tables.aio import TableServiceClient as AsyncTableServiceClient
    from azure.identity import DefaultAzureCredential

    r = TableStorage()
    with pytest.raises(RuntimeError):
        r.get_client(TableServiceClient)

    r = TableStorage.reference(account="foo")
    assert r._settings["endpoint"]() == "https://foo.table.core.windows.net/"
    client = r.get_client()
    assert isinstance(client, TableServiceClient)
    client = r.get_client(use_async=True)
    assert isinstance(client, AsyncTableServiceClient)
    client = r.get_client(TableServiceClient)
    assert isinstance(client, TableServiceClient)
    client = r.get_client(AsyncTableServiceClient)
    assert isinstance(client, AsyncTableServiceClient)
    client, credential = r.get_client(TableServiceClient, return_credential=True)
    assert isinstance(client, TableServiceClient)
    assert isinstance(credential, DefaultAzureCredential)


def test_storage_tables_infra():
    class TestInfra(AzureInfrastructure):
        data: TableStorage = TableStorage()

    assert isinstance(TestInfra.data, TableStorage)
    infra = TestInfra()
    assert isinstance(infra.data, TableStorage)
    assert infra.data.properties == {"properties": {}}

    infra = TestInfra(data=TableStorage(account="foo"))
    assert infra.data._settings["name"]() == "default"
    assert infra.data.parent._settings["name"]() == "foo"

    class TestInfra(AzureInfrastructure):
        data: TableStorage = field(default=TableStorage.reference(account="teststorage"))

    infra = TestInfra()
    assert infra.data._settings["name"]() == "default"
    assert infra.data.parent._settings["name"]() == "teststorage"


def test_storage_tables_app():
    from azure.data.tables import TableServiceClient

    r = TableStorage.reference(account="test", resource_group="test")

    class TestApp(AzureApp):
        client: TableServiceClient

    # with pytest.raises(TypeError):
    #     app = TestApp()

    app = TestApp(client=r)
    assert isinstance(app.client, TableServiceClient)
