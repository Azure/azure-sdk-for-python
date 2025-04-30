from dataclasses import dataclass
from uuid import uuid4

import pytest
from azure.projects.resources.search import SearchService
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, field, AzureInfrastructure, export, AzureApp

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.aio import SearchClient as AsyncSearchClient
from azure.search.documents.indexes.aio import SearchIndexClient as AsyncSearchIndexClient

TEST_SUB = str(uuid4())
RG = ResourceSymbol("resourcegroup")
IDENTITY = {"type": "UserAssigned", "userAssignedIdentities": {"identity": {}}}


def _get_outputs(suffix="", rg=None):
    outputs = {
        "resource_id": [Output(f"AZURE_SEARCH_ID", "id", ResourceSymbol(f"searchservice{suffix}"))],
        "name": [Output(f"AZURE_SEARCH_NAME", "name", ResourceSymbol(f"searchservice{suffix}"))],
        "resource_group": [Output(f"AZURE_SEARCH_RESOURCE_GROUP", rg if rg else DefaultResourceGroup().name)],
    }
    outputs.update(
        {
            "endpoint": [
                Output(
                    f"AZURE_SEARCH_ENDPOINT",
                    Output("", "name", ResourceSymbol(f"searchservice{suffix}")).format(
                        "https://{}.search.windows.net/"
                    ),
                )
            ],
        }
    )
    return outputs


def test_search_properties():
    r = SearchService()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.Search/searchServices"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["searchservice"]
    assert fields["searchservice"].resource == "Microsoft.Search/searchServices"
    assert fields["searchservice"].properties == {}
    assert fields["searchservice"].outputs == _get_outputs()
    assert fields["searchservice"].extensions == {}
    assert fields["searchservice"].existing == False
    assert fields["searchservice"].version
    assert fields["searchservice"].symbol == symbols[0]
    assert fields["searchservice"].resource_group == None
    assert not fields["searchservice"].name
    assert fields["searchservice"].defaults

    r2 = SearchService(location="westus", sku="free")
    assert r2.properties == {"location": "westus", "sku": {"name": "free"}, "properties": {}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["searchservice"]
    assert fields["searchservice"].resource == "Microsoft.Search/searchServices"
    assert fields["searchservice"].properties == {"location": "westus", "sku": {"name": "free"}}
    assert fields["searchservice"].outputs == _get_outputs()
    assert fields["searchservice"].extensions == {}
    assert fields["searchservice"].existing == False
    assert fields["searchservice"].version
    assert fields["searchservice"].symbol == symbols[0]
    assert fields["searchservice"].resource_group == None
    assert not fields["searchservice"].name
    assert fields["searchservice"].defaults

    r3 = SearchService(sku="standard")
    assert r3.properties == {"properties": {}, "sku": {"name": "standard"}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = SearchService(name="foo", tags={"test": "value"}, public_network_access="Disabled")
    assert r4.properties == {
        "name": "foo",
        "tags": {"test": "value"},
        "properties": {"publicNetworkAccess": "Disabled"},
    }
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["searchservice", "searchservice_foo"]
    assert fields["searchservice_foo"].resource == "Microsoft.Search/searchServices"
    assert fields["searchservice_foo"].properties == {
        "name": "foo",
        "tags": {"test": "value"},
        "properties": {"publicNetworkAccess": "Disabled"},
    }
    assert fields["searchservice_foo"].outputs == _get_outputs("_foo")
    assert fields["searchservice_foo"].extensions == {}
    assert fields["searchservice_foo"].existing == False
    assert fields["searchservice_foo"].version
    assert fields["searchservice_foo"].symbol == symbols[0]
    assert fields["searchservice_foo"].resource_group == None
    assert fields["searchservice_foo"].name == "foo"
    assert fields["searchservice_foo"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = SearchService(name=param1, sku=param2, public_network_access=param3)
    assert r5.properties == {"name": param1, "sku": {"name": param2}, "properties": {"publicNetworkAccess": param3}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["searchservice_testa"]
    assert fields["searchservice_testa"].resource == "Microsoft.Search/searchServices"
    assert fields["searchservice_testa"].properties == {
        "name": param1,
        "sku": {"name": param2},
        "properties": {"publicNetworkAccess": param3},
    }
    assert fields["searchservice_testa"].outputs == _get_outputs("_testa")
    assert fields["searchservice_testa"].extensions == {}
    assert fields["searchservice_testa"].existing == False
    assert fields["searchservice_testa"].version
    assert fields["searchservice_testa"].symbol == symbols[0]
    assert fields["searchservice_testa"].resource_group == None
    assert fields["searchservice_testa"].name == param1
    assert fields["searchservice_testa"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_search_reference():
    r = SearchService.reference(name="foo")
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
    assert list(fields.keys()) == ["searchservice_foo"]
    assert fields["searchservice_foo"].resource == "Microsoft.Search/searchServices"
    assert fields["searchservice_foo"].properties == {"name": "foo"}
    assert fields["searchservice_foo"].outputs == _get_outputs("_foo")
    assert fields["searchservice_foo"].extensions == {}
    assert fields["searchservice_foo"].existing == True
    assert fields["searchservice_foo"].version
    assert fields["searchservice_foo"].symbol == symbols[0]
    assert fields["searchservice_foo"].resource_group == None
    assert fields["searchservice_foo"].name == "foo"
    assert not fields["searchservice_foo"].defaults

    rg = ResourceSymbol("resourcegroup_bar")
    r = SearchService.reference(name="foo", resource_group="bar")
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar")}
    assert r._settings["resource_group"]() == "bar"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_bar", "searchservice_foo"]
    assert fields["searchservice_foo"].resource == "Microsoft.Search/searchServices"
    assert fields["searchservice_foo"].properties == {"name": "foo", "scope": rg}
    assert fields["searchservice_foo"].outputs == _get_outputs("_foo", "bar")
    assert fields["searchservice_foo"].extensions == {}
    assert fields["searchservice_foo"].existing == True
    assert fields["searchservice_foo"].version
    assert fields["searchservice_foo"].symbol == symbols[0]
    assert fields["searchservice_foo"].resource_group == rg
    assert fields["searchservice_foo"].name == "foo"
    assert not fields["searchservice_foo"].defaults

    r = SearchService.reference(name="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB))
    assert r.properties == {"name": "foo", "resource_group": ResourceGroup(name="bar")}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.Search/searchServices/foo"
    )


def test_search_defaults():
    sku_param = Parameter("AISku", default="standard")
    r = SearchService(location="westus", sku=sku_param, public_network_access="Disabled")
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
            "publicNetworkAccess": "Disabled",
        },
        "tags": GLOBAL_PARAMS["azdTags"],
        "identity": IDENTITY,
    }


def test_search_export(export_dir):
    class test(AzureInfrastructure):
        r: SearchService = SearchService()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_search_export_existing(export_dir):
    class test(AzureInfrastructure):
        r: SearchService = field(default=SearchService.reference(name="test"))

    export(
        test(resource_group=ResourceGroup.reference(name="test"), identity=None),
        output_dir=export_dir[0],
        infra_dir=export_dir[2],
    )


def test_search_export_with_properties(export_dir):
    class test(AzureInfrastructure):
        r: SearchService = field(
            default=SearchService(
                {"properties": {}},
                sku="free",
                location="westus",
                public_network_access="Disabled",
                managed_identities={"systemAssigned": True, "userAssignedResourceIds": ["identity"]},
                network_acls={"bypass": "AzureServices", "ipRules": [{"value": "rule"}]},
                tags={"foo": "bar"},
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_search_export_with_role_assignments(export_dir):
    user_role = Parameter("UserRole")

    class test(AzureInfrastructure):
        r: SearchService = SearchService(roles=["Contributor"], user_roles=["Contributor"])

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_search_export_with_no_user_access(export_dir):
    class test(AzureInfrastructure):
        r: SearchService = field(default=SearchService(roles=["Contributor"], user_roles=["Contributor"]))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2], user_access=False)


def test_search_export_multiple_services(export_dir):
    # TODO: If these are ordered the other way around they are merged....
    # Is that correct?
    class test(AzureInfrastructure):
        r1: SearchService = SearchService()
        r2: SearchService = SearchService(name="foo", public_network_access="Enabled")

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_search_export_duplicate_services(export_dir):
    class test(AzureInfrastructure):
        r1: SearchService = SearchService(public_network_access="Enabled")
        r2: SearchService = SearchService(public_network_access=Parameter("LocalAuth"))

    with pytest.raises(ValueError):
        export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])

    class test(AzureInfrastructure):
        r1: SearchService = SearchService(public_network_access="Enabled")
        r2: SearchService = SearchService()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


# TODO:
# def test_search_export_with_parameters(export_dir):


def test_search_client():
    r = SearchService.reference(name="test", resource_group="test")

    assert r._settings["name"]() == "test"
    r._settings["api_version"].set_value("v1.0")
    client = r.get_client(api_version="1234", verify_challenge_resource=True)
    assert isinstance(client, SearchIndexClient)
    assert client._client._config.endpoint == "https://test.search.windows.net/"
    assert client._client._config.api_version == "1234"

    client = r.get_client(index_name="foo", api_version="1234")
    assert isinstance(client, SearchClient)
    assert client._client._config.endpoint == "https://test.search.windows.net/"
    assert client._client._config.api_version == "1234"

    client = r.get_client(use_async=True)
    assert isinstance(client, AsyncSearchIndexClient)
    assert client._client._config.endpoint == "https://test.search.windows.net/"
    assert client._client._config.api_version == "v1.0"

    client = r.get_client(index_name="foo", use_async=True)
    assert isinstance(client, AsyncSearchClient)
    assert client._client._config.endpoint == "https://test.search.windows.net/"
    assert client._client._config.api_version == "v1.0"


def test_search_infra():
    class TestInfra(AzureInfrastructure):
        kv: SearchService

    with pytest.raises(AttributeError):
        TestInfra.kv
    with pytest.raises(TypeError):
        infra = TestInfra()
    infra = TestInfra(kv=SearchService())
    assert isinstance(infra.kv, SearchService)
    assert infra.kv.properties == {"properties": {}}

    infra = TestInfra(kv=SearchService(name="foo"))
    assert infra.kv._settings["name"]() == "foo"


def test_search_app():
    r = SearchService.reference(name="test", resource_group="test")

    class TestApp(AzureApp):
        client: SearchClient = field(index_name="foo")
        indexes: SearchIndexClient = field()

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(client=r, indexes=r)
    assert isinstance(app.client, SearchClient)
    assert isinstance(app.indexes, SearchIndexClient)
    assert app.client._client._config.endpoint == "https://test.search.windows.net/"

    override_client = SearchClient(
        "https://foobar.search.windows.net/", credential=DefaultAzureCredential(), index_name="index"
    )
    app = TestApp(client=override_client, indexes=r)
    assert app.client._client._config.endpoint == "https://foobar.search.windows.net/"

    class TestApp(AzureApp):
        client: SearchIndexClient

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(client=r)
    assert isinstance(app.client, SearchIndexClient)
    assert app.client._client._config.endpoint == "https://test.search.windows.net/"

    override_client = SearchIndexClient("https://foobar.search.windows.net/", credential=DefaultAzureCredential())
    app = TestApp(client=override_client)
    assert app.client._client._config.endpoint == "https://foobar.search.windows.net/"

    class TestApp(AzureApp):
        client: SearchIndexClient = field(default=r, api_version="v1.0")

    app = TestApp()
    assert isinstance(app.client, SearchIndexClient)
    assert app.client._client._config.endpoint == "https://test.search.windows.net/"
    assert app.client._client._config.api_version == "v1.0"

    override_client = SearchIndexClient(
        "https://foobar.search.windows.net/", credential=DefaultAzureCredential(), api_version="v2.0"
    )
    app = TestApp(client=override_client)
    assert app.client._client._config.endpoint == "https://foobar.search.windows.net/"
    assert app.client._client._config.api_version == "v2.0"

    class TestApp(AzureApp):
        client: SearchIndexClient = field(default=override_client, api_version="v1.0")

    app = TestApp()
    assert app.client._client._config.endpoint == "https://foobar.search.windows.net/"
    assert app.client._client._config.api_version == "v2.0"

    app = TestApp(client=r)
    assert isinstance(app.client, SearchIndexClient)
    assert app.client._client._config.endpoint == "https://test.search.windows.net/"
    assert app.client._client._config.api_version == "v1.0"

    def client_builder(**kwargs):
        return SearchIndexClient("https://different.search.windows.net/", credential=DefaultAzureCredential(), **kwargs)

    class TestApp(AzureApp):
        client: SearchIndexClient = field(default_factory=client_builder, api_version="v3.0")

    app = TestApp()
    assert app.client._client._config.endpoint == "https://different.search.windows.net/"
    assert app.client._client._config.api_version == "v3.0"

    class TestApp(AzureApp):
        client_a: SearchIndexClient = field(api_version="v1.5")
        client_b: SearchClient = field(index_name="foo", api_version="v2.5")

    app = TestApp.load(config_store={"AZURE_SEARCH_ENDPOINT": "https://test.search.windows.net/"})
    assert isinstance(app.client_a, SearchIndexClient)
    assert app.client_a._client._config.endpoint == "https://test.search.windows.net/"
    assert app.client_a._client._config.api_version == "v1.5"
    assert isinstance(app.client_b, SearchClient)
    assert app.client_b._client._config.endpoint == "https://test.search.windows.net/"
    assert app.client_b._client._config.api_version == "v2.5"
