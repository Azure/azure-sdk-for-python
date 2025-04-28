from dataclasses import dataclass
from uuid import uuid4

import pytest
from azure.projects.resources.ai import AIServices
from azure.projects.resources.ai.deployment import AIEmbeddings
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, field, AzureInfrastructure, export, AzureApp

from azure.ai.inference import EmbeddingsClient

TEST_SUB = str(uuid4())
RG = ResourceSymbol("resourcegroup")


def _get_outputs(suffix="", parent="", rg=None):
    outputs = {
        "resource_id": [Output(f"AZURE_AI_EMBEDDINGS_ID", "id", ResourceSymbol(f"embeddings_deployment{suffix}"))],
        "name": [Output(f"AZURE_AI_EMBEDDINGS_NAME", "name", ResourceSymbol(f"embeddings_deployment{suffix}"))],
        "resource_group": [Output(f"AZURE_AI_EMBEDDINGS_RESOURCE_GROUP", rg if rg else DefaultResourceGroup().name)],
    }
    outputs.update(
        {
            "endpoint": [
                Output(
                    f"AZURE_AI_EMBEDDINGS_ENDPOINT",
                    Output("", "properties.endpoint", ResourceSymbol(f"aiservices_account{parent}")).format(
                        "{}openai/deployments/"
                    )
                    + outputs["name"][0].format(),
                    # + "/embeddings",
                )
            ],
            "model_name": [
                Output(
                    f"AZURE_AI_EMBEDDINGS_MODEL_NAME",
                    "properties.model.name",
                    ResourceSymbol(f"embeddings_deployment{suffix}"),
                )
            ],
            "model_format": [
                Output(
                    f"AZURE_AI_EMBEDDINGS_MODEL_FORMAT",
                    "properties.model.format",
                    ResourceSymbol(f"embeddings_deployment{suffix}"),
                )
            ],
            "model_version": [
                Output(
                    f"AZURE_AI_EMBEDDINGS_MODEL_VERSION",
                    "properties.model.version",
                    ResourceSymbol(f"embeddings_deployment{suffix}"),
                )
            ],
        }
    )
    return outputs


def test_aiservices_embeddings_properties():
    r = AIEmbeddings()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r._existing == False
    assert r.identifier == ResourceIdentifiers.ai_embeddings_deployment
    assert r.parent == AIServices()
    assert r.resource == "Microsoft.CognitiveServices/accounts/deployments"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 2
    assert list(fields.keys()) == ["aiservices_account", "aiservices_account.embeddings_deployment"]
    assert (
        fields["aiservices_account.embeddings_deployment"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account.embeddings_deployment"].properties == {
        "parent": ResourceSymbol("aiservices_account"),
    }
    assert fields["aiservices_account.embeddings_deployment"].outputs == _get_outputs()
    assert fields["aiservices_account.embeddings_deployment"].extensions == {}
    assert fields["aiservices_account.embeddings_deployment"].existing == False
    assert fields["aiservices_account.embeddings_deployment"].version
    assert fields["aiservices_account.embeddings_deployment"].symbol == symbols[0]
    assert fields["aiservices_account.embeddings_deployment"].resource_group == None
    assert not fields["aiservices_account.embeddings_deployment"].name
    assert fields["aiservices_account.embeddings_deployment"].defaults

    r2 = AIEmbeddings(model="gpt-4o", capacity=10)
    assert r2.properties == {"name": "gpt-4o", "sku": {"capacity": 10}, "properties": {"model": {"name": "gpt-4o"}}}
    symbols = r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "aiservices_account",
        "aiservices_account.embeddings_deployment",
        "aiservices_account.embeddings_deployment_gpt4o",
    ]
    assert (
        fields["aiservices_account.embeddings_deployment_gpt4o"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].properties == {
        "name": "gpt-4o",
        "sku": {"capacity": 10},
        "properties": {"model": {"name": "gpt-4o"}},
        "parent": ResourceSymbol("aiservices_account"),
        "dependsOn": [
            ResourceSymbol("embeddings_deployment"),
        ],
    }
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].outputs == _get_outputs("_gpt4o")
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].extensions == {}
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].existing == False
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].version
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].symbol == symbols[0]
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].resource_group == None
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].name == "gpt-4o"
    assert fields["aiservices_account.embeddings_deployment_gpt4o"].defaults

    r3 = AIEmbeddings(model="gpt-4o", capacity=30)
    assert r3.properties == {"name": "gpt-4o", "sku": {"capacity": 30}, "properties": {"model": {"name": "gpt-4o"}}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = AIEmbeddings(
        model="secret", account=AIServices(name="foo", tags={"test": "value"}, public_network_access="Disabled")
    )
    assert r4.properties == {"properties": {"model": {"name": "secret"}}, "name": "secret"}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "aiservices_account",
        "aiservices_account.embeddings_deployment",
        "aiservices_account.embeddings_deployment_gpt4o",
        "aiservices_account_foo",
        "aiservices_account_foo.embeddings_deployment_foo_secret",
    ]
    assert (
        fields["aiservices_account_foo.embeddings_deployment_foo_secret"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].properties == {
        "properties": {"model": {"name": "secret"}},
        "name": "secret",
        "parent": ResourceSymbol("aiservices_account_foo"),
    }
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].outputs == _get_outputs(
        "_foo_secret", "_foo"
    )
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].extensions == {}
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].existing == False
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].version
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].symbol == symbols[0]
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].resource_group == None
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].name == "secret"
    assert fields["aiservices_account_foo.embeddings_deployment_foo_secret"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = AIEmbeddings({"properties": {"model": param1}}, sku=param2, capacity=param3, deployment_name="foo")
    assert r5.properties == {
        "name": "foo",
        "sku": {"name": param2, "capacity": param3},
        "properties": {"model": param1},
    }
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["aiservices_account", "aiservices_account.embeddings_deployment_foo"]
    assert (
        fields["aiservices_account.embeddings_deployment_foo"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account.embeddings_deployment_foo"].properties == {
        "name": "foo",
        "sku": {"name": param2, "capacity": param3},
        "properties": {"model": param1},
        "parent": ResourceSymbol("aiservices_account"),
    }
    assert fields["aiservices_account.embeddings_deployment_foo"].outputs == _get_outputs("_foo")
    assert fields["aiservices_account.embeddings_deployment_foo"].extensions == {}
    assert fields["aiservices_account.embeddings_deployment_foo"].existing == False
    assert fields["aiservices_account.embeddings_deployment_foo"].version
    assert fields["aiservices_account.embeddings_deployment_foo"].symbol == symbols[0]
    assert fields["aiservices_account.embeddings_deployment_foo"].resource_group == None
    assert fields["aiservices_account.embeddings_deployment_foo"].name == "foo"
    assert fields["aiservices_account.embeddings_deployment_foo"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_aiservices_embeddings_reference():
    r = AIEmbeddings.reference(name="foo", account="bar")
    assert r.properties == {"name": "foo"}
    assert r._existing == True
    assert r.parent == AIServices(name="bar")
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
    assert list(fields.keys()) == ["aiservices_account_bar", "aiservices_account_bar.embeddings_deployment_bar_foo"]
    assert (
        fields["aiservices_account_bar.embeddings_deployment_bar_foo"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].properties == {
        "name": "foo",
        "parent": ResourceSymbol("aiservices_account_bar"),
    }
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].outputs == _get_outputs("_bar_foo", "_bar")
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].extensions == {}
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].existing == True
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].version
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].symbol == symbols[0]
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].resource_group == None
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].name == "foo"
    assert not fields["aiservices_account_bar.embeddings_deployment_bar_foo"].defaults

    rg = ResourceSymbol("resourcegroup_baz")
    r = AIEmbeddings.reference(name="foo", account="bar", resource_group="baz")
    assert r.properties == {"name": "foo"}
    assert r._settings["resource_group"]() == "baz"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "resourcegroup_baz",
        "aiservices_account_bar",
        "aiservices_account_bar.embeddings_deployment_bar_foo",
    ]
    assert (
        fields["aiservices_account_bar.embeddings_deployment_bar_foo"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].properties == {
        "name": "foo",
        "parent": ResourceSymbol("aiservices_account_bar"),
    }
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].outputs == _get_outputs(
        "_bar_foo", "_bar", "baz"
    )
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].extensions == {}
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].existing == True
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].version
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].symbol == symbols[0]
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].resource_group == None
    assert fields["aiservices_account_bar.embeddings_deployment_bar_foo"].name == "foo"
    assert not fields["aiservices_account_bar.embeddings_deployment_bar_foo"].defaults

    r = AIEmbeddings.reference(
        name="foo",
        account=AIServices.reference(
            name="bar", resource_group=ResourceGroup.reference(name="baz", subscription=TEST_SUB)
        ),
    )
    assert r.properties == {"name": "foo"}
    assert r._settings["subscription"]() == TEST_SUB
    assert r._settings["resource_group"]() == "baz"
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/baz/providers/Microsoft.CognitiveServices/accounts/bar/deployments/foo"
    )


def test_aiservices_embeddings_defaults():
    r = AIEmbeddings()
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    add_defaults(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    assert field.properties == {
        "name": GLOBAL_PARAMS["defaultName"].format("{}-embeddings-deployment"),
        "sku": {
            "name": Parameter("aiEmbeddingsModelSku", default="Standard"),
            "capacity": Parameter("aiEmbeddingsModelCapacity", default=30),
        },
        "properties": {
            "model": {
                "name": Parameter("aiEmbeddingsModel", default="gpt-4o-mini"),
                "format": Parameter("aiEmbeddingsModelFormat", default="OpenAI"),
                "version": Parameter("aiEmbeddingsModelVersion", default="2024-07-18"),
            }
        },
        "parent": ResourceSymbol("aiservices_account"),
    }


def test_aiservices_embeddings_export(export_dir):
    class test(AzureInfrastructure):
        r: AIEmbeddings = AIEmbeddings()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_embeddings_export_existing(export_dir):
    class test(AzureInfrastructure):
        r: AIEmbeddings = field(default=AIEmbeddings.reference(name="aitest", account="aitest"))

    export(test(identity=None), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_embeddings_export_with_properties(export_dir):
    class test(AzureInfrastructure):
        r: AIEmbeddings = field(default=AIEmbeddings(sku="test", capacity=15, format="foo", version="2"))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_embeddings_export_multiple_deployments(export_dir):
    class test(AzureInfrastructure):
        r: AIEmbeddings = field(default=AIEmbeddings(model="one"))
        b: AIEmbeddings = field(default=AIEmbeddings(model="two"))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_embeddings_client():
    r = AIEmbeddings.reference(name="gpt-4o", account="test")
    r.model_format = "OpenAI"
    r.model_name = "gpt-4o"
    assert r._settings["name"]() == "gpt-4o"
    client = r.get_client()
    assert isinstance(client, EmbeddingsClient)

    # TODO: This gives a "proxies" error in CI
    # from openai import AzureOpenAI, AsyncAzureOpenAI
    # client = r.get_client(AzureOpenAI)
    # assert isinstance(client, AzureOpenAI)

    # client = r.get_client(AsyncAzureOpenAI)
    # assert isinstance(client, AsyncAzureOpenAI)

    # from openai.resources import Embeddings, AsyncEmbeddings
    # client = r.get_client(Embeddings)
    # assert isinstance(client, Embeddings)

    # client = r.get_client(AsyncEmbeddings)
    # assert isinstance(client, AsyncEmbeddings)


def test_aiservices_embeddings_infra():
    class TestInfra(AzureInfrastructure):
        embeddings_a: AIEmbeddings = field(default=AIEmbeddings(model="gpt-4o-mini"))
        embeddings_b: AIEmbeddings = field(default=AIEmbeddings(model="gpt-4o"))

    assert isinstance(TestInfra.embeddings_a, AIEmbeddings)
    infra = TestInfra()
    assert isinstance(infra.embeddings_a, AIEmbeddings)
    assert infra.embeddings_a._settings["name"]() == "gpt-4o-mini"
    assert infra.embeddings_a.properties == {"name": "gpt-4o-mini", "properties": {"model": {"name": "gpt-4o-mini"}}}

    infra = TestInfra(embeddings_b=AIEmbeddings.reference(name="foo", account="bar"))
    assert infra.embeddings_b._settings["name"]() == "foo"
    assert infra.embeddings_b.parent == AIServices(name="bar")


def test_aiservices_embeddings_app():
    r = AIEmbeddings.reference(name="test", account="test")

    class TestApp(AzureApp):
        client: EmbeddingsClient

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(
        client=r, config_store={"AZURE_AI_EMBEDDINGS_ENDPOINT": "https://test.openai.azure.com/openai/deployments/test"}
    )
    assert isinstance(app.client, EmbeddingsClient)
    assert app.client._config.endpoint == "https://test.openai.azure.com/openai/deployments/test"  # /embeddings"
    assert app.client._config.credential

    app = TestApp(client="test")
    assert app.client == "test"

    # TODO: This gives a "proxies" error in CI
    # from openai.resources.embeddings import AsyncEmbeddings
    # class TestApp(AzureApp):
    #     client: AsyncEmbeddings = field(default=r, api_version="v1.0")

    # app = TestApp()
    # assert isinstance(app.client, AsyncEmbeddings)

    # app = TestApp(client="override_client")
    # assert app.client == "override_client"

    class TestApp(AzureApp):
        client: EmbeddingsClient

    app = TestApp.load(
        config_store={"AZURE_AI_EMBEDDINGS_ENDPOINT_FOO": "https://test.openai.azure.com/openai/deployments/test"}
    )
    assert isinstance(app.client, EmbeddingsClient)

    class TestApp(AzureApp):
        client: EmbeddingsClient = field(default=r)

    app = TestApp(
        config_store={"AZURE_AI_EMBEDDINGS_ENDPOINT_FOO": "https://test.openai.azure.com/openai/deployments/test"}
    )
    assert isinstance(app.client, EmbeddingsClient)
