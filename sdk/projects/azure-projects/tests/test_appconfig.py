from dataclasses import dataclass
from uuid import uuid4

import pytest
from azure.projects.resources.appconfig import ConfigStore
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, field, AzureInfrastructure, export, AzureApp

from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AzureAppConfigurationClient
from azure.appconfiguration.aio import AzureAppConfigurationClient as AsyncAzureAppConfigurationClient

TEST_SUB = str(uuid4())
RG = ResourceSymbol("resourcegroup")
IDENTITY = {"type": "UserAssigned", "userAssignedIdentities": {"identity": {}}}


def _get_outputs(suffix="", rg=None):
    outputs = {
        "resource_id": [Output(f"AZURE_APPCONFIG_ID", "id", ResourceSymbol(f"configurationstore{suffix}"))],
        "name": [Output(f"AZURE_APPCONFIG_NAME", "name", ResourceSymbol(f"configurationstore{suffix}"))],
        "resource_group": [Output(f"AZURE_APPCONFIG_RESOURCE_GROUP", rg if rg else DefaultResourceGroup().name)],
        "endpoint": [
            Output(
                f"AZURE_APPCONFIG_ENDPOINT",
                "properties.endpoint",
                ResourceSymbol(f"configurationstore{suffix}"),
            )
        ],
    }
    return outputs


def test_appconfig_properties():
    r = ConfigStore()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.AppConfiguration/configurationStores"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["configurationstore"]
    assert fields["configurationstore"].resource == "Microsoft.AppConfiguration/configurationStores"
    assert fields["configurationstore"].properties == {}
    assert fields["configurationstore"].outputs == _get_outputs()
    assert fields["configurationstore"].extensions == {}
    assert fields["configurationstore"].existing == False
    assert fields["configurationstore"].version
    assert fields["configurationstore"].symbol == symbols[0]
    assert fields["configurationstore"].resource_group == None
    assert not fields["configurationstore"].name
    assert fields["configurationstore"].defaults

    r2 = ConfigStore(location="westus", sku="Standard")
    assert r2.properties == {"location": "westus", "sku": {"name": "Standard"}, "properties": {}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["configurationstore"]
    assert fields["configurationstore"].resource == "Microsoft.AppConfiguration/configurationStores"
    assert fields["configurationstore"].properties == {
        "location": "westus",
        "sku": {"name": "Standard"},
    }
    assert fields["configurationstore"].outputs == _get_outputs()
    assert fields["configurationstore"].extensions == {}
    assert fields["configurationstore"].existing == False
    assert fields["configurationstore"].version
    assert fields["configurationstore"].symbol == symbols[0]
    assert fields["configurationstore"].resource_group == None
    assert not fields["configurationstore"].name
    assert fields["configurationstore"].defaults

    r3 = ConfigStore(sku="Free")
    assert r3.properties == {"properties": {}, "sku": {"name": "Free"}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = ConfigStore(name="foo", tags={"test": "value"}, public_network_access="Disabled")
    assert r4.properties == {
        "name": "foo",
        "tags": {"test": "value"},
        "properties": {"publicNetworkAccess": "Disabled"},
    }
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["configurationstore", "configurationstore_foo"]
    assert fields["configurationstore_foo"].resource == "Microsoft.AppConfiguration/configurationStores"
    assert fields["configurationstore_foo"].properties == {
        "name": "foo",
        "tags": {"test": "value"},
        "properties": {"publicNetworkAccess": "Disabled"},
    }
    assert fields["configurationstore_foo"].outputs == _get_outputs("_foo")
    assert fields["configurationstore_foo"].extensions == {}
    assert fields["configurationstore_foo"].existing == False
    assert fields["configurationstore_foo"].version
    assert fields["configurationstore_foo"].symbol == symbols[0]
    assert fields["configurationstore_foo"].resource_group == None
    assert fields["configurationstore_foo"].name == "foo"
    assert fields["configurationstore_foo"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = ConfigStore(name=param1, sku=param2, public_network_access=param3)
    assert r5.properties == {"name": param1, "sku": {"name": param2}, "properties": {"publicNetworkAccess": param3}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["configurationstore_testa"]
    assert fields["configurationstore_testa"].resource == "Microsoft.AppConfiguration/configurationStores"
    assert fields["configurationstore_testa"].properties == {
        "name": param1,
        "sku": {"name": param2},
        "properties": {"publicNetworkAccess": param3},
    }
    assert fields["configurationstore_testa"].outputs == _get_outputs("_testa")
    assert fields["configurationstore_testa"].extensions == {}
    assert fields["configurationstore_testa"].existing == False
    assert fields["configurationstore_testa"].version
    assert fields["configurationstore_testa"].symbol == symbols[0]
    assert fields["configurationstore_testa"].resource_group == None
    assert fields["configurationstore_testa"].name == param1
    assert fields["configurationstore_testa"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_appconfig_reference():
    r = ConfigStore.reference(name="foo")
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
    assert list(fields.keys()) == ["configurationstore_foo"]
    assert fields["configurationstore_foo"].resource == "Microsoft.AppConfiguration/configurationStores"
    assert fields["configurationstore_foo"].properties == {"name": "foo"}
    assert fields["configurationstore_foo"].outputs == _get_outputs("_foo")
    assert fields["configurationstore_foo"].extensions == {}
    assert fields["configurationstore_foo"].existing == True
    assert fields["configurationstore_foo"].version
    assert fields["configurationstore_foo"].symbol == symbols[0]
    assert fields["configurationstore_foo"].resource_group == None
    assert fields["configurationstore_foo"].name == "foo"
    assert not fields["configurationstore_foo"].defaults

    rg = ResourceSymbol("resourcegroup_bar")
    r = ConfigStore.reference(name="foo", resource_group="bar")
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar")}
    assert r._settings["resource_group"]() == "bar"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_bar", "configurationstore_foo"]
    assert fields["configurationstore_foo"].resource == "Microsoft.AppConfiguration/configurationStores"
    assert fields["configurationstore_foo"].properties == {"name": "foo", "scope": rg}
    assert fields["configurationstore_foo"].outputs == _get_outputs("_foo", "bar")
    assert fields["configurationstore_foo"].extensions == {}
    assert fields["configurationstore_foo"].existing == True
    assert fields["configurationstore_foo"].version
    assert fields["configurationstore_foo"].symbol == symbols[0]
    assert fields["configurationstore_foo"].resource_group == rg
    assert fields["configurationstore_foo"].name == "foo"
    assert not fields["configurationstore_foo"].defaults

    r = ConfigStore.reference(name="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB))
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar")}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.AppConfiguration/configurationStores/foo"
    )


def test_appconfig_defaults():
    sku_param = Parameter("ConfigSku", default="Standard")
    r = ConfigStore(location="westus", sku=sku_param, public_network_access="Disabled")
    fields = {}
    params = dict(GLOBAL_PARAMS)
    params["managedIdentityId"] = "identity"
    r.__bicep__(fields, parameters=params)
    add_defaults(fields, parameters=params)
    field = fields.popitem()[1]
    assert field.properties == {
        "name": GLOBAL_PARAMS["defaultName"],
        "location": "westus",
        "sku": {
            "name": sku_param,
        },
        "properties": {
            "disableLocalAuth": True,
            "createMode": "Default",
            "publicNetworkAccess": "Disabled",
            "dataPlaneProxy": {"authenticationMode": "Pass-through", "privateLinkDelegation": "Disabled"},
        },
        "tags": GLOBAL_PARAMS["azdTags"],
        "identity": IDENTITY,
    }


def test_appconfig_export(export_dir):
    class test(AzureInfrastructure):
        r: ConfigStore = ConfigStore()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_export_existing(export_dir):
    class test(AzureInfrastructure):
        r: ConfigStore = field(default=ConfigStore.reference(name="test"))

    export(
        test(resource_group=ResourceGroup.reference(name="test"), identity=None),
        output_dir=export_dir[0],
        infra_dir=export_dir[2],
    )


def test_appconfig_export_with_properties(export_dir):
    class test(AzureInfrastructure):
        r: ConfigStore = field(
            default=ConfigStore(
                {"properties": {}},
                sku="Free",
                create_mode="Default",
                enable_purge_protection=True,
                disable_local_auth=True,
                soft_delete_retention=10,
                location="westus",
                public_network_access="Disabled",
                managed_identities={"systemAssigned": True, "userAssignedResourceIds": ["identity"]},
                tags={"foo": "bar"},
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_export_with_role_assignments(export_dir):
    user_role = Parameter("UserRole")

    class test(AzureInfrastructure):
        r: ConfigStore = ConfigStore(roles=["Contributor"], user_roles=["Contributor"])

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_export_with_no_user_access(export_dir):
    class test(AzureInfrastructure):
        r: ConfigStore = field(default=ConfigStore(roles=["Contributor"], user_roles=["Contributor"]))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2], user_access=False)


def test_appconfig_export_multiple_services(export_dir):
    # TODO: If these are ordered the other way around they are merged....
    # Is that correct?
    class test(AzureInfrastructure):
        r1: ConfigStore = ConfigStore()
        r2: ConfigStore = ConfigStore(name="foo", public_network_access="Enabled")

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_export_duplicate_services(export_dir):
    class test(AzureInfrastructure):
        r1: ConfigStore = ConfigStore(public_network_access="Enabled")
        r2: ConfigStore = ConfigStore(public_network_access=Parameter("LocalAuth"))

    with pytest.raises(ValueError):
        export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])

    class test(AzureInfrastructure):
        r1: ConfigStore = ConfigStore(public_network_access="Enabled")
        r2: ConfigStore = ConfigStore()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


# TODO:
# def test_appconfig_export_with_parameters(export_dir):


def test_appconfig_client():
    r = ConfigStore.reference(name="test", resource_group="test")

    assert r._settings["name"]() == "test"
    r._settings["api_version"].set_value("v1.0")
    client = r.get_client(api_version="1234", verify_challenge_resource=True)
    assert isinstance(client, AzureAppConfigurationClient)
    assert client._impl._config.endpoint == "https://test.azconfig.io"
    assert client._impl._config.api_version == "1234"

    # TODO: This needs to be in an async test case.
    # This raises a runtime error because the Async client creates an asyncio.Lock object
    # when there's no running event loop.
    client = r.get_client(use_async=True)
    assert isinstance(client, AsyncAzureAppConfigurationClient)
    assert client._impl._config.endpoint == "https://test.azconfig.io"
    assert client._impl._config.api_version == "v1.0"


def test_appconfig_infra():
    class TestInfra(AzureInfrastructure):
        config: ConfigStore

    with pytest.raises(AttributeError):
        TestInfra.config
    with pytest.raises(TypeError):
        infra = TestInfra()
    infra = TestInfra(config=ConfigStore())
    assert isinstance(infra.config, ConfigStore)
    assert infra.config.properties == {"properties": {}}

    infra = TestInfra(config=ConfigStore(name="foo"))
    assert infra.config._settings["name"]() == "foo"


def test_appconfig_app():
    r = ConfigStore.reference(name="test", resource_group="test")

    class TestApp(AzureApp):
        config: AzureAppConfigurationClient = field()

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(config=r)
    assert isinstance(app.config, AzureAppConfigurationClient)
    assert app.config._impl._config.endpoint == "https://test.azconfig.io"

    override_client = AzureAppConfigurationClient("https://foobar.azconfig.io", credential=DefaultAzureCredential())
    app = TestApp(config=override_client)
    assert app.config._impl._config.endpoint == "https://foobar.azconfig.io"

    class TestApp(AzureApp):
        client: AzureAppConfigurationClient = field(default=r, api_version="v1.0")

    app = TestApp()
    assert isinstance(app.client, AzureAppConfigurationClient)
    assert app.client._impl._config.endpoint == "https://test.azconfig.io"
    assert app.client._impl._config.api_version == "v1.0"

    override_client = AzureAppConfigurationClient(
        "https://foobar.azconfig.io", credential=DefaultAzureCredential(), api_version="v2.0"
    )
    app = TestApp(client=override_client)
    assert app.client._impl._config.endpoint == "https://foobar.azconfig.io"
    assert app.client._impl._config.api_version == "v2.0"

    class TestApp(AzureApp):
        client: AzureAppConfigurationClient = field(default=override_client, api_version="v1.0")

    app = TestApp()
    assert app.client._impl._config.endpoint == "https://foobar.azconfig.io"
    assert app.client._impl._config.api_version == "v2.0"

    app = TestApp(client=r)
    assert isinstance(app.client, AzureAppConfigurationClient)
    assert app.client._impl._config.endpoint == "https://test.azconfig.io"
    assert app.client._impl._config.api_version == "v1.0"

    def client_builder(**kwargs):
        return AzureAppConfigurationClient(
            "https://different.azconfig.io", credential=DefaultAzureCredential(), **kwargs
        )

    class TestApp(AzureApp):
        client: AzureAppConfigurationClient = field(default_factory=client_builder, api_version="v3.0")

    app = TestApp()
    assert app.client._impl._config.endpoint == "https://different.azconfig.io"
    assert app.client._impl._config.api_version == "v3.0"

    class TestApp(AzureApp):
        client: AzureAppConfigurationClient = field(api_version="v1.5")

    app = TestApp.load(config_store={"AZURE_APPCONFIG_ENDPOINT": "https://test.azconfig.io"})
    assert isinstance(app.client, AzureAppConfigurationClient)
    assert app.client._impl._config.endpoint == "https://test.azconfig.io"
    assert app.client._impl._config.api_version == "v1.5"
