from dataclasses import dataclass
from uuid import uuid4

import pytest
from azure.projects.resources.keyvault import KeyVault
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, field, AzureInfrastructure, export, AzureApp

from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.secrets import SecretClient
from azure.keyvault.secrets.aio import SecretClient as AsyncSecretClient

TEST_SUB = str(uuid4())
RG = ResourceSymbol("resourcegroup")


def _get_outputs(suffix="", rg=None):
    return {
        "resource_id": [Output(f"AZURE_KEYVAULT_ID", "id", ResourceSymbol(f"vault{suffix}"))],
        "name": [Output(f"AZURE_KEYVAULT_NAME", "name", ResourceSymbol(f"vault{suffix}"))],
        "resource_group": [Output(f"AZURE_KEYVAULT_RESOURCE_GROUP", rg if rg else DefaultResourceGroup().name)],
        "endpoint": [Output(f"AZURE_KEYVAULT_ENDPOINT", "properties.vaultUri", ResourceSymbol(f"vault{suffix}"))],
    }


def test_keyvault_properties():
    r = KeyVault()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.KeyVault/vaults"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["vault"]
    assert fields["vault"].resource == "Microsoft.KeyVault/vaults"
    assert fields["vault"].properties == {}
    assert fields["vault"].outputs == _get_outputs()
    assert fields["vault"].extensions == {}
    assert fields["vault"].existing == False
    assert fields["vault"].version
    assert fields["vault"].symbol == symbols[0]
    assert fields["vault"].resource_group == None
    assert not fields["vault"].name
    assert fields["vault"].defaults

    r2 = KeyVault(location="westus", sku="premium")
    assert r2.properties == {"location": "westus", "properties": {"sku": {"name": "premium", "family": "A"}}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["vault"]
    assert fields["vault"].resource == "Microsoft.KeyVault/vaults"
    assert fields["vault"].properties == {
        "location": "westus",
        "properties": {"sku": {"name": "premium", "family": "A"}},
    }
    assert fields["vault"].outputs == _get_outputs()
    assert fields["vault"].extensions == {}
    assert fields["vault"].existing == False
    assert fields["vault"].version
    assert fields["vault"].symbol == symbols[0]
    assert fields["vault"].resource_group == None
    assert not fields["vault"].name
    assert fields["vault"].defaults

    r3 = KeyVault(sku="standard")
    assert r3.properties == {"properties": {"sku": {"name": "standard", "family": "A"}}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = KeyVault(name="foo", tags={"test": "value"}, public_network_access="Disabled")
    assert r4.properties == {
        "name": "foo",
        "tags": {"test": "value"},
        "properties": {"publicNetworkAccess": "Disabled"},
    }
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["vault", "vault_foo"]
    assert fields["vault_foo"].resource == "Microsoft.KeyVault/vaults"
    assert fields["vault_foo"].properties == {
        "name": "foo",
        "tags": {"test": "value"},
        "properties": {"publicNetworkAccess": "Disabled"},
    }
    assert fields["vault_foo"].outputs == _get_outputs("_foo")
    assert fields["vault_foo"].extensions == {}
    assert fields["vault_foo"].existing == False
    assert fields["vault_foo"].version
    assert fields["vault_foo"].symbol == symbols[0]
    assert fields["vault_foo"].resource_group == None
    assert fields["vault_foo"].name == "foo"
    assert fields["vault_foo"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = KeyVault(name=param1, sku=param2, public_network_access=param3)
    assert r5.properties == {
        "name": param1,
        "properties": {"sku": {"name": param2, "family": "A"}, "publicNetworkAccess": param3},
    }
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["vault_testa"]
    assert fields["vault_testa"].resource == "Microsoft.KeyVault/vaults"
    assert fields["vault_testa"].properties == {
        "name": param1,
        "properties": {"sku": {"name": param2, "family": "A"}, "publicNetworkAccess": param3},
    }
    assert fields["vault_testa"].outputs == _get_outputs("_testa")
    assert fields["vault_testa"].extensions == {}
    assert fields["vault_testa"].existing == False
    assert fields["vault_testa"].version
    assert fields["vault_testa"].symbol == symbols[0]
    assert fields["vault_testa"].resource_group == None
    assert fields["vault_testa"].name == param1
    assert fields["vault_testa"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_keyvault_reference():
    r = KeyVault.reference(name="foo")
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
    assert list(fields.keys()) == ["vault_foo"]
    assert fields["vault_foo"].resource == "Microsoft.KeyVault/vaults"
    assert fields["vault_foo"].properties == {"name": "foo"}
    assert fields["vault_foo"].outputs == _get_outputs("_foo")
    assert fields["vault_foo"].extensions == {}
    assert fields["vault_foo"].existing == True
    assert fields["vault_foo"].version
    assert fields["vault_foo"].symbol == symbols[0]
    assert fields["vault_foo"].resource_group == None
    assert fields["vault_foo"].name == "foo"
    assert not fields["vault_foo"].defaults

    rg = ResourceSymbol("resourcegroup_bar")
    r = KeyVault.reference(name="foo", resource_group="bar")
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar")}
    assert r._settings["resource_group"]() == "bar"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_bar", "vault_foo"]
    assert fields["vault_foo"].resource == "Microsoft.KeyVault/vaults"
    assert fields["vault_foo"].properties == {"name": "foo", "scope": rg}
    assert fields["vault_foo"].outputs == _get_outputs("_foo", "bar")
    assert fields["vault_foo"].extensions == {}
    assert fields["vault_foo"].existing == True
    assert fields["vault_foo"].version
    assert fields["vault_foo"].symbol == symbols[0]
    assert fields["vault_foo"].resource_group == rg
    assert fields["vault_foo"].name == "foo"
    assert not fields["vault_foo"].defaults

    r = KeyVault.reference(name="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB))
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar")}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.KeyVault/vaults/foo"
    )


def test_keyvault_defaults():
    sku_param = Parameter("AISku", default="premium")
    r = KeyVault(location="westus", sku=sku_param, public_network_access="Disabled")
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    add_defaults(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    assert field.properties == {
        "name": GLOBAL_PARAMS["defaultName"],
        "location": "westus",
        "properties": {
            "sku": {"name": sku_param, "family": "A"},
            "accessPolicies": [],
            "enableRbacAuthorization": True,
            "publicNetworkAccess": "Disabled",
            "tenantId": GLOBAL_PARAMS["tenantId"],
        },
        "tags": GLOBAL_PARAMS["azdTags"],
    }


def test_keyvault_export(export_dir):
    class test(AzureInfrastructure):
        r: KeyVault = KeyVault()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_keyvault_export_existing(export_dir):
    class test(AzureInfrastructure):
        r: KeyVault = field(default=KeyVault.reference(name="kvtest"))

    export(
        test(resource_group=ResourceGroup.reference(name="kvtest"), identity=None),
        output_dir=export_dir[0],
        infra_dir=export_dir[2],
    )


def test_keyvault_export_with_properties(export_dir):
    class test(AzureInfrastructure):
        r: KeyVault = field(
            default=KeyVault(
                {"properties": {}},
                sku="premium",
                location="westus",
                public_network_access="Disabled",
                network_acls={"bypass": "AzureServices", "defaultAction": "Deny"},
                tags={"foo": "bar"},
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_keyvault_export_with_role_assignments(export_dir):
    user_role = Parameter("UserRole")

    class test(AzureInfrastructure):
        r: KeyVault = KeyVault(roles=["Key Vault Administrator"], user_roles=["Key Vault Administrator"])

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_keyvault_export_with_no_user_access(export_dir):
    class test(AzureInfrastructure):
        r: KeyVault = field(default=KeyVault(roles=["Key Vault Administrator"], user_roles=["Key Vault Administrator"]))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2], user_access=False)


def test_keyvault_export_multiple_vaults(export_dir):
    # TODO: If these are ordered the other way around they are merged....
    # Is that correct?
    class test(AzureInfrastructure):
        r1: KeyVault = KeyVault()
        r2: KeyVault = KeyVault(name="foo", public_network_access="Enabled")

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_keyvault_export_duplicate_vaults(export_dir):
    class test(AzureInfrastructure):
        r1: KeyVault = KeyVault(public_network_access="Enabled")
        r2: KeyVault = KeyVault(public_network_access=Parameter("LocalAuth"))

    with pytest.raises(ValueError):
        export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])

    class test(AzureInfrastructure):
        r1: KeyVault = KeyVault(public_network_access="Enabled")
        r2: KeyVault = KeyVault()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


# TODO:
# def test_keyvault_export_with_parameters(export_dir):


def test_keyvault_client():
    r = KeyVault.reference(name="test", resource_group="test")
    with pytest.raises(TypeError):
        r.get_client()

    assert r._settings["name"]() == "test"
    r._settings["api_version"].set_value("v1.0")
    client = r.get_client(SecretClient, api_version="1234", verify_challenge_resource=True)
    assert client.vault_url == "https://test.vault.azure.net"
    assert client.api_version == "1234"

    client = r.get_client(AsyncSecretClient)
    assert isinstance(client, AsyncSecretClient)
    assert client.vault_url == "https://test.vault.azure.net"
    assert client.api_version == "v1.0"


def test_keyvault_infra():
    class TestInfra(AzureInfrastructure):
        kv: KeyVault

    with pytest.raises(AttributeError):
        TestInfra.kv
    with pytest.raises(TypeError):
        infra = TestInfra()
    infra = TestInfra(kv=KeyVault())
    assert isinstance(infra.kv, KeyVault)
    assert infra.kv.properties == {"properties": {}}

    infra = TestInfra(kv=KeyVault(name="foo"))
    assert infra.kv._settings["name"]() == "foo"


def test_keyvault_app():
    r = KeyVault.reference(name="test", resource_group="test")

    class TestApp(AzureApp):
        client: KeyClient

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(client=r)
    assert isinstance(app.client, KeyClient)
    assert app.client.vault_url == "https://test.vault.azure.net"

    override_client = KeyClient("https://foobar.vault.azure.net/", credential=DefaultAzureCredential())
    app = TestApp(client=override_client)
    assert app.client.vault_url == "https://foobar.vault.azure.net"

    class TestApp(AzureApp):
        client: SecretClient

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(client=r)
    assert isinstance(app.client, SecretClient)
    assert app.client.vault_url == "https://test.vault.azure.net"

    override_client = SecretClient("https://foobar.vault.azure.net/", credential=DefaultAzureCredential())
    app = TestApp(client=override_client)
    assert app.client.vault_url == "https://foobar.vault.azure.net"

    class TestApp(AzureApp):
        client: KeyClient = field(default=r, api_version="v1.0")

    app = TestApp()
    assert isinstance(app.client, KeyClient)
    assert app.client.vault_url == "https://test.vault.azure.net"
    assert app.client.api_version == "v1.0"

    override_client = KeyClient(
        "https://foobar.vault.azure.net/", credential=DefaultAzureCredential(), api_version="v2.0"
    )
    app = TestApp(client=override_client)
    assert app.client.vault_url == "https://foobar.vault.azure.net"
    assert app.client.api_version == "v2.0"

    class TestApp(AzureApp):
        client: KeyClient = field(default=override_client, api_version="v1.0")

    app = TestApp()
    assert app.client.vault_url == "https://foobar.vault.azure.net"
    assert app.client.api_version == "v2.0"

    app = TestApp(client=r)
    assert isinstance(app.client, KeyClient)
    assert app.client.vault_url == "https://test.vault.azure.net"
    assert app.client.api_version == "v1.0"

    def client_builder(**kwargs):
        return KeyClient("https://different.vault.azure.net", credential=DefaultAzureCredential(), **kwargs)

    class TestApp(AzureApp):
        client: KeyClient = field(default_factory=client_builder, api_version="v3.0")

    app = TestApp()
    assert app.client.vault_url == "https://different.vault.azure.net"
    assert app.client.api_version == "v3.0"

    class TestApp(AzureApp):
        client_a: KeyClient = field(api_version="v1.5")
        client_b: SecretClient = field(api_version="v2.5")

    app = TestApp.load(config_store={"AZURE_KEYVAULT_ENDPOINT": "https://test.vault.azure.net"})
    assert isinstance(app.client_a, KeyClient)
    assert app.client_a.vault_url == "https://test.vault.azure.net"
    assert app.client_a.api_version == "v1.5"
    assert isinstance(app.client_b, SecretClient)
    assert app.client_b.vault_url == "https://test.vault.azure.net"
    assert app.client_b.api_version == "v2.5"
