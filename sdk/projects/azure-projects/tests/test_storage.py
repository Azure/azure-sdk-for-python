from uuid import uuid4

import pytest
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._resource import FieldType
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, AzureInfrastructure, export, field, AzureApp

TEST_SUB = "6e441d6a-23ce-4450-a4a6-78f8d4f45ce9"
RG = ResourceSymbol("resourcegroup")
IDENTITY = {"type": "UserAssigned", "userAssignedIdentities": {"identity": {}}}


def _get_outputs(suffix="", rg=None):
    return {
        "resource_id": [Output(f"AZURE_STORAGE_ID", "id", ResourceSymbol(f"storageaccount{suffix}"))],
        "name": [Output(f"AZURE_STORAGE_NAME", "name", ResourceSymbol(f"storageaccount{suffix}"))],
        "resource_group": [Output(f"AZURE_STORAGE_RESOURCE_GROUP", rg if rg else DefaultResourceGroup().name)],
    }


def test_storage_properties():
    r = StorageAccount()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.Storage/storageAccounts"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 1
    assert list(fields.keys()) == ["storageaccount"]
    assert fields["storageaccount"].resource == "Microsoft.Storage/storageAccounts"
    assert fields["storageaccount"].properties == {}
    assert fields["storageaccount"].outputs == _get_outputs()
    assert fields["storageaccount"].extensions == {}
    assert fields["storageaccount"].existing == False
    assert fields["storageaccount"].version
    assert fields["storageaccount"].symbol == symbols[0]
    assert fields["storageaccount"].resource_group == None
    assert not fields["storageaccount"].name
    assert fields["storageaccount"].defaults

    r2 = StorageAccount(location="westus", sku="Standard_RAGRS")
    assert r2.properties == {"location": "westus", "sku": {"name": "Standard_RAGRS"}, "properties": {}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["storageaccount"]
    assert fields["storageaccount"].resource == "Microsoft.Storage/storageAccounts"
    assert fields["storageaccount"].properties == {
        "location": "westus",
        "sku": {"name": "Standard_RAGRS"},
    }
    assert fields["storageaccount"].outputs == _get_outputs()
    assert fields["storageaccount"].extensions == {}
    assert fields["storageaccount"].existing == False
    assert fields["storageaccount"].version
    assert fields["storageaccount"].symbol == symbols[0]
    assert fields["storageaccount"].resource_group == None
    assert not fields["storageaccount"].name
    assert fields["storageaccount"].defaults

    r3 = StorageAccount(sku="Premium_ZRS")
    assert r3.properties == {"sku": {"name": "Premium_ZRS"}, "properties": {}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = StorageAccount(name="foo", tags={"test": "value"}, access_tier="Cool")
    assert r4.properties == {"name": "foo", "tags": {"test": "value"}, "properties": {"accessTier": "Cool"}}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["storageaccount", "storageaccount_foo"]
    assert fields["storageaccount_foo"].resource == "Microsoft.Storage/storageAccounts"
    assert fields["storageaccount_foo"].properties == {
        "name": "foo",
        "tags": {"test": "value"},
        "properties": {"accessTier": "Cool"},
    }
    assert fields["storageaccount_foo"].outputs == _get_outputs("_foo")
    assert fields["storageaccount_foo"].extensions == {}
    assert fields["storageaccount_foo"].existing == False
    assert fields["storageaccount_foo"].version
    assert fields["storageaccount_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo"].resource_group == None
    assert fields["storageaccount_foo"].name == "foo"
    assert fields["storageaccount_foo"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = StorageAccount(name=param1, sku=param2, access_tier=param3)
    assert r5.properties == {"name": param1, "sku": {"name": param2}, "properties": {"accessTier": param3}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["storageaccount_testa"]
    assert fields["storageaccount_testa"].resource == "Microsoft.Storage/storageAccounts"
    assert fields["storageaccount_testa"].properties == {
        "name": param1,
        "sku": {"name": param2},
        "properties": {"accessTier": param3},
    }
    assert fields["storageaccount_testa"].outputs == _get_outputs("_testa")
    assert fields["storageaccount_testa"].extensions == {}
    assert fields["storageaccount_testa"].existing == False
    assert fields["storageaccount_testa"].version
    assert fields["storageaccount_testa"].symbol == symbols[0]
    assert fields["storageaccount_testa"].resource_group == None
    assert fields["storageaccount_testa"].name == param1
    assert fields["storageaccount_testa"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_storage_reference():
    r = StorageAccount.reference(name="foo")
    assert r.properties == {"name": "foo"}
    assert r._existing == True
    assert not r.parent
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
    assert list(fields.keys()) == ["storageaccount_foo"]
    assert fields["storageaccount_foo"].resource == "Microsoft.Storage/storageAccounts"
    assert fields["storageaccount_foo"].properties == {"name": "foo"}
    assert fields["storageaccount_foo"].outputs == _get_outputs("_foo")
    assert fields["storageaccount_foo"].extensions == {}
    assert fields["storageaccount_foo"].existing == True
    assert fields["storageaccount_foo"].version
    assert fields["storageaccount_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo"].resource_group == None
    assert fields["storageaccount_foo"].name == "foo"
    assert not fields["storageaccount_foo"].defaults

    rg = ResourceSymbol("resourcegroup_bar")
    r = StorageAccount.reference(name="foo", resource_group="bar")
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar")}
    assert r._settings["resource_group"]() == "bar"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_bar", "storageaccount_foo"]
    assert fields["storageaccount_foo"].resource == "Microsoft.Storage/storageAccounts"
    assert fields["storageaccount_foo"].properties == {"name": "foo", "scope": rg}
    assert fields["storageaccount_foo"].outputs == _get_outputs("_foo", "bar")
    assert fields["storageaccount_foo"].extensions == {}
    assert fields["storageaccount_foo"].existing == True
    assert fields["storageaccount_foo"].version
    assert fields["storageaccount_foo"].symbol == symbols[0]
    assert fields["storageaccount_foo"].resource_group == rg
    assert fields["storageaccount_foo"].name == "foo"
    assert not fields["storageaccount_foo"].defaults

    r = StorageAccount.reference(name="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB))
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar")}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.Storage/storageAccounts/foo"
    )


def test_storage_defaults():
    access_tier = Parameter("myAccessTier", default="Premium")
    r = StorageAccount(location="westus", sku="Premium_ZRS", access_tier=access_tier)
    fields = {}
    params = dict(GLOBAL_PARAMS)
    params["managedIdentityId"] = "identity"
    r.__bicep__(fields, parameters=params)
    add_defaults(fields, parameters=params)
    field = fields.popitem()[1]
    assert field.properties == {
        "name": GLOBAL_PARAMS["defaultName"],
        "location": "westus",
        "sku": {"name": "Premium_ZRS"},
        "kind": "StorageV2",
        "properties": {
            "accessTier": access_tier,
            "allowCrossTenantReplication": False,
            "allowSharedKeyAccess": False,
        },
        "identity": IDENTITY,
        "tags": GLOBAL_PARAMS["azdTags"],
    }


def test_storage_export(export_dir):
    class test(AzureInfrastructure):
        r: StorageAccount = StorageAccount()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_export_existing(export_dir):
    class test(AzureInfrastructure):
        r: StorageAccount = field(default=StorageAccount.reference(name="storagetest"))

    infra = test(resource_group=ResourceGroup.reference(name="rgtest"), identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_export_with_properties(export_dir):
    with pytest.raises(ValueError):
        StorageAccount(custom_domain_use_subdomain_name=True)
    with pytest.raises(ValueError):
        StorageAccount({"properties": {"customDomain": Parameter("custom")}}, custom_domain_use_subdomain_name=False)
    StorageAccount(custom_domain_name="foo", custom_domain_use_subdomain_name=True)

    class test(AzureInfrastructure):
        r: StorageAccount = field(
            default=StorageAccount(
                {"properties": {}},
                access_tier="Cool",
                enable_hierarchical_namespace=True,
                allow_blob_public_access=True,
                allow_cross_tenant_replication=True,
                allowed_copy_scope="PrivateLink",
                allow_shared_key_access=False,
                custom_domain_name="foo",
                custom_domain_use_subdomain_name=True,
                default_to_oauth_authentication=True,
                dns_endpoint_type="AzureDnsZone",
                enable_nfs_v3=True,
                enable_sftp=True,
                is_local_user_enabled=False,
                kind="BlobStorage",
                managed_identities={"systemAssigned": True, "userAssignedResourceIds": ["identity"]},
                minimum_tls_version="TLS1_3",
                network_acls={
                    "bypass": "Metrics",
                    "defaultAction": "Deny",
                    "resourceAccessRules": [{"resourceId": "foo"}],
                },
                public_network_access="Enabled",
                sas_expiration_period="30",
                supports_https_traffic_only=True,
                sku="Premium_LRS",
                location="westus",
                tags={"foo": "bar"},
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_export_with_role_assignments(export_dir):
    class test(AzureInfrastructure):
        r: StorageAccount = field(
            default=StorageAccount(roles=["Storage Blob Data Owner"], user_roles=["Storage Blob Data Contributor"])
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_storage_export_with_no_user_access(export_dir):
    class test(AzureInfrastructure):
        r: StorageAccount = field(
            default=StorageAccount(roles=["Storage Blob Data Owner"], user_roles=["Storage Blob Data Contributor"])
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2], user_access=False)


def test_storage_client():
    from azure.storage.blob import BlobServiceClient

    r = StorageAccount()
    with pytest.raises(TypeError):
        r.get_client(BlobServiceClient)


def test_storage_infra():
    class TestInfra(AzureInfrastructure):
        data: StorageAccount = StorageAccount()

    assert isinstance(TestInfra.data, StorageAccount)
    infra = TestInfra()
    assert isinstance(infra.data, StorageAccount)
    assert infra.data.properties == {"properties": {}}

    infra = TestInfra(data=StorageAccount(name="foo"))
    assert infra.data._settings["name"]() == "foo"


def test_storage_app():
    from azure.storage.blob import BlobServiceClient

    r = StorageAccount.reference(name="test", resource_group="test")

    class TestApp(AzureApp):
        client: BlobServiceClient

    with pytest.raises(TypeError):
        app = TestApp()

    with pytest.raises(TypeError):
        app = TestApp(client=r)
