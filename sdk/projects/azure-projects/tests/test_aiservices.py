from dataclasses import dataclass
from uuid import uuid4

import pytest
from azure.projects.resources.ai._resource import AIServices, CognitiveServicesAccount
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._utils import add_defaults
from azure.projects.resources import RESOURCE_FROM_CLIENT_ANNOTATION, ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, field, AzureInfrastructure, export, AzureApp

TEST_SUB = str(uuid4())
RG = ResourceSymbol("resourcegroup")
IDENTITY = {"type": "UserAssigned", "userAssignedIdentities": {"identity": {}}}
RESOURCE_FROM_CLIENT_ANNOTATION["EmptyClient"] = ResourceIdentifiers.ai_services


class EmptyClient:
    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        self.__dict__.update(kwargs)

    def close(self):
        pass


def _get_outputs(suffix="", rg=None):
    return {
        "resource_id": [Output(f"AZURE_AI_AISERVICES_ID", "id", ResourceSymbol(f"aiservices_account{suffix}"))],
        "name": [Output(f"AZURE_AI_AISERVICES_NAME", "name", ResourceSymbol(f"aiservices_account{suffix}"))],
        "resource_group": [Output(f"AZURE_AI_AISERVICES_RESOURCE_GROUP", rg if rg else DefaultResourceGroup().name)],
        "endpoint": [
            Output(
                f"AZURE_AI_AISERVICES_ENDPOINT",
                "properties.endpoint",
                ResourceSymbol(f"aiservices_account{suffix}"),
            )
        ],
    }


def test_aiservices_properties():
    r = AIServices()
    assert r.properties == {"kind": "AIServices", "properties": {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.CognitiveServices/accounts"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["aiservices_account"]
    assert fields["aiservices_account"].resource == "Microsoft.CognitiveServices/accounts"
    assert fields["aiservices_account"].properties == {"kind": "AIServices"}
    assert fields["aiservices_account"].outputs == _get_outputs()
    assert fields["aiservices_account"].extensions == {}
    assert fields["aiservices_account"].existing == False
    assert fields["aiservices_account"].version
    assert fields["aiservices_account"].symbol == symbols[0]
    assert fields["aiservices_account"].resource_group == None
    assert not fields["aiservices_account"].name
    assert fields["aiservices_account"].defaults

    r2 = AIServices(location="westus", sku="F1")
    assert r2.properties == {"kind": "AIServices", "location": "westus", "sku": {"name": "F1"}, "properties": {}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["aiservices_account"]
    assert fields["aiservices_account"].resource == "Microsoft.CognitiveServices/accounts"
    assert fields["aiservices_account"].properties == {
        "kind": "AIServices",
        "location": "westus",
        "sku": {"name": "F1"},
    }
    assert fields["aiservices_account"].outputs == _get_outputs()
    assert fields["aiservices_account"].extensions == {}
    assert fields["aiservices_account"].existing == False
    assert fields["aiservices_account"].version
    assert fields["aiservices_account"].symbol == symbols[0]
    assert fields["aiservices_account"].resource_group == None
    assert not fields["aiservices_account"].name
    assert fields["aiservices_account"].defaults

    r3 = AIServices(sku="C3")
    assert r3.properties == {"kind": "AIServices", "sku": {"name": "C3"}, "properties": {}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = AIServices(name="foo", tags={"test": "value"}, public_network_access="Disabled")
    assert r4.properties == {
        "name": "foo",
        "kind": "AIServices",
        "tags": {"test": "value"},
        "properties": {"publicNetworkAccess": "Disabled"},
    }
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["aiservices_account", "aiservices_account_foo"]
    assert fields["aiservices_account_foo"].resource == "Microsoft.CognitiveServices/accounts"
    assert fields["aiservices_account_foo"].properties == {
        "name": "foo",
        "kind": "AIServices",
        "tags": {"test": "value"},
        "properties": {"publicNetworkAccess": "Disabled"},
    }
    assert fields["aiservices_account_foo"].outputs == _get_outputs("_foo")
    assert fields["aiservices_account_foo"].extensions == {}
    assert fields["aiservices_account_foo"].existing == False
    assert fields["aiservices_account_foo"].version
    assert fields["aiservices_account_foo"].symbol == symbols[0]
    assert fields["aiservices_account_foo"].resource_group == None
    assert fields["aiservices_account_foo"].name == "foo"
    assert fields["aiservices_account_foo"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = AIServices(name=param1, sku=param2, public_network_access=param3)
    assert r5.properties == {
        "name": param1,
        "kind": "AIServices",
        "sku": {"name": param2},
        "properties": {"publicNetworkAccess": param3},
    }
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["aiservices_account_testa"]
    assert fields["aiservices_account_testa"].resource == "Microsoft.CognitiveServices/accounts"
    assert fields["aiservices_account_testa"].properties == {
        "name": param1,
        "kind": "AIServices",
        "sku": {"name": param2},
        "properties": {"publicNetworkAccess": param3},
    }
    assert fields["aiservices_account_testa"].outputs == _get_outputs("_testa")
    assert fields["aiservices_account_testa"].extensions == {}
    assert fields["aiservices_account_testa"].existing == False
    assert fields["aiservices_account_testa"].version
    assert fields["aiservices_account_testa"].symbol == symbols[0]
    assert fields["aiservices_account_testa"].resource_group == None
    assert fields["aiservices_account_testa"].name == param1
    assert fields["aiservices_account_testa"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_aiservices_reference():
    r = AIServices.reference(name="foo")
    assert r.properties == {"name": "foo", "kind": "AIServices"}
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
    assert list(fields.keys()) == ["aiservices_account_foo"]
    assert fields["aiservices_account_foo"].resource == "Microsoft.CognitiveServices/accounts"
    assert fields["aiservices_account_foo"].properties == {"name": "foo"}
    assert fields["aiservices_account_foo"].outputs == _get_outputs("_foo")
    assert fields["aiservices_account_foo"].extensions == {}
    assert fields["aiservices_account_foo"].existing == True
    assert fields["aiservices_account_foo"].version
    assert fields["aiservices_account_foo"].symbol == symbols[0]
    assert fields["aiservices_account_foo"].resource_group == None
    assert fields["aiservices_account_foo"].name == "foo"
    assert not fields["aiservices_account_foo"].defaults

    rg = ResourceSymbol("resourcegroup_bar")
    r = AIServices.reference(name="foo", resource_group="bar")
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar"), "kind": "AIServices"}
    assert r._settings["resource_group"]() == "bar"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_bar", "aiservices_account_foo"]
    assert fields["aiservices_account_foo"].resource == "Microsoft.CognitiveServices/accounts"
    assert fields["aiservices_account_foo"].properties == {"name": "foo", "scope": rg}
    assert fields["aiservices_account_foo"].outputs == _get_outputs("_foo", "bar")
    assert fields["aiservices_account_foo"].extensions == {}
    assert fields["aiservices_account_foo"].existing == True
    assert fields["aiservices_account_foo"].version
    assert fields["aiservices_account_foo"].symbol == symbols[0]
    assert fields["aiservices_account_foo"].resource_group == rg
    assert fields["aiservices_account_foo"].name == "foo"
    assert not fields["aiservices_account_foo"].defaults

    r = AIServices.reference(name="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB))
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar"), "kind": "AIServices"}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.CognitiveServices/accounts/foo"
    )


def test_aiservices_defaults():
    sku_param = Parameter("AISku", default="S0")
    r = AIServices(location="westus", sku=sku_param, public_network_access="Disabled")
    fields = {}
    params = dict(GLOBAL_PARAMS)
    params["managedIdentityId"] = "identity"
    r.__bicep__(fields, parameters=params)
    add_defaults(fields, parameters=params)
    field = fields.popitem()[1]
    assert field.properties == {
        "name": GLOBAL_PARAMS["defaultName"].format("{}-aiservices"),
        "location": "westus",
        "sku": {"name": sku_param},
        "kind": "AIServices",
        "properties": {
            "customSubDomainName": "${defaultName}-aiservices",
            "networkAcls": {
                "defaultAction": "Allow",
            },
            "publicNetworkAccess": "Disabled",
            "disableLocalAuth": True,
        },
        "identity": IDENTITY,
        "tags": GLOBAL_PARAMS["azdTags"],
    }


def test_aiservices_export(export_dir):
    class test(AzureInfrastructure):
        r: AIServices = AIServices()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_export_existing(export_dir):
    class test(AzureInfrastructure):
        r: AIServices = field(default=AIServices.reference(name="aitest"))

    export(
        test(resource_group=ResourceGroup.reference(name="aitest"), identity=None),
        output_dir=export_dir[0],
        infra_dir=export_dir[2],
    )


def test_aiservices_export_with_properties(export_dir):
    class test(AzureInfrastructure):
        r: AIServices = field(default=AIServices(sku="C2", location="westus", public_network_access="Disabled"))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_export_with_role_assignments(export_dir):
    user_role = Parameter("UserRole")

    class test(AzureInfrastructure):
        r: AIServices = field(
            default=AIServices(
                roles=["Cognitive Services OpenAI Contributor"], user_roles=["Cognitive Services OpenAI User"]
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_export_with_no_user_access(export_dir):
    class test(AzureInfrastructure):
        r: AIServices = field(
            default=AIServices(
                roles=["Cognitive Services OpenAI Contributor"], user_roles=["Cognitive Services OpenAI User"]
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2], user_access=False)


def test_aiservices_export_multiple_cogservices(export_dir):
    class test(AzureInfrastructure):
        c: CognitiveServicesAccount = field(default=CognitiveServicesAccount(kind="MetricsAdvisor"))
        r: AIServices = AIServices()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_export_multiple_ai(export_dir):
    class test(AzureInfrastructure):
        r1: AIServices = field(default=AIServices(disable_local_auth=False))
        r2: AIServices = field(default=AIServices(disable_local_auth=Parameter("LocalAuth", default=True)))

    with pytest.raises(ValueError):
        export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])

    class test(AzureInfrastructure):
        r1: AIServices = field(default=AIServices(disable_local_auth=False))
        r2: AIServices = AIServices

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


# TODO:
# def test_aiservices_export_with_parameters(export_dir):


def test_aiservices_client():
    r = AIServices.reference(name="test", resource_group="test")
    assert r._settings["name"]() == "test"
    r._settings["api_version"].set_value("v1.0")
    r._settings["audience"].set_value("nobody")
    client = r.get_client(EmptyClient, test_attr="test", foo="bar")
    assert client.endpoint == "https://test.services.ai.azure.com/models"
    assert client.credential
    assert client.test_attr == "test"
    assert client.api_version == "v1.0"
    assert client.audience == "nobody"
    assert client.foo == "bar"


def test_aiservices_infra():
    class TestInfra(AzureInfrastructure):
        ai: AIServices

    with pytest.raises(AttributeError):
        TestInfra.ai
    with pytest.raises(TypeError):
        infra = TestInfra()
    infra = TestInfra(ai=AIServices())
    assert isinstance(infra.ai, AIServices)
    assert infra.ai.properties == {"properties": {}, "kind": "AIServices"}

    infra = TestInfra(ai=AIServices(name="foo"))
    assert infra.ai._settings["name"]() == "foo"


def test_aiservices_app():
    r = AIServices.reference(name="test", resource_group="test")

    class TestApp(AzureApp):
        client: EmptyClient

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(client=r)
    assert isinstance(app.client, EmptyClient)
    assert app.client.endpoint == "https://test.services.ai.azure.com/models"
    assert app.client.credential

    override_client = EmptyClient("foobar", test_one="one", api_version="v2.0")
    app = TestApp(client=override_client)
    assert app.client.endpoint == "foobar"
    assert app.client.test_one == "one"
    assert app.client.api_version == "v2.0"

    class TestApp(AzureApp):
        client: EmptyClient = field(default=r, api_version="v1.0")

    app = TestApp()
    assert isinstance(app.client, EmptyClient)
    assert app.client.endpoint == "https://test.services.ai.azure.com/models"
    assert app.client.credential
    assert app.client.api_version == "v1.0"

    app = TestApp(client=override_client)
    assert app.client.endpoint == "foobar"
    assert app.client.test_one == "one"
    assert app.client.api_version == "v2.0"

    class TestApp(AzureApp):
        client: EmptyClient = field(default=override_client, api_version="v1.0")

    app = TestApp()
    assert app.client.endpoint == "foobar"
    assert app.client.test_one == "one"
    assert app.client.api_version == "v2.0"

    app = TestApp(client=r)
    assert isinstance(app.client, EmptyClient)
    assert app.client.endpoint == "https://test.services.ai.azure.com/models"
    assert app.client.credential
    assert app.client.api_version == "v1.0"

    def client_builder(**kwargs):
        return EmptyClient("fake-endpoint", **kwargs)

    class TestApp(AzureApp):
        client: EmptyClient = field(default_factory=client_builder, test_attr="foobar")

    app = TestApp()
    assert app.client.endpoint == "fake-endpoint"
    assert app.client.test_attr == "foobar"

    class TestApp(AzureApp):
        client: EmptyClient = field(api_version="v1.0")

    app = TestApp.load(config_store={"AZURE_AI_AISERVICES_ENDPOINT": "https://test.services.ai.azure.com/models"})
    assert isinstance(app.client, EmptyClient)
    assert app.client.endpoint == "https://test.services.ai.azure.com/models"
    assert app.client.credential
    assert app.client.api_version == "v1.0"
