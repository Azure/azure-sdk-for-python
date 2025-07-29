from dataclasses import dataclass
from uuid import uuid4

import pytest
from azure.projects.resources.ai import AIServices
from azure.projects.resources.ai.deployment import AIChat
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, field, AzureInfrastructure, export, AzureApp

from azure.ai.inference import ChatCompletionsClient

TEST_SUB = str(uuid4())
RG = ResourceSymbol("resourcegroup")


def _get_outputs(suffix="", parent="", rg=None):
    outputs = {
        "resource_id": [Output(f"AZURE_AI_CHAT_ID", "id", ResourceSymbol(f"chat_deployment{suffix}"))],
        "name": [Output(f"AZURE_AI_CHAT_NAME", "name", ResourceSymbol(f"chat_deployment{suffix}"))],
        "resource_group": [Output(f"AZURE_AI_CHAT_RESOURCE_GROUP", rg if rg else DefaultResourceGroup().name)],
    }
    outputs.update(
        {
            "model_name": [
                Output(
                    f"AZURE_AI_CHAT_MODEL_NAME",
                    "properties.model.name",
                    ResourceSymbol(f"chat_deployment{suffix}"),
                )
            ],
            "model_format": [
                Output(
                    f"AZURE_AI_CHAT_MODEL_FORMAT",
                    "properties.model.format",
                    ResourceSymbol(f"chat_deployment{suffix}"),
                )
            ],
            "model_version": [
                Output(
                    f"AZURE_AI_CHAT_MODEL_VERSION",
                    "properties.model.version",
                    ResourceSymbol(f"chat_deployment{suffix}"),
                )
            ],
        }
    )
    return outputs


def test_aiservices_chat_properties():
    r = AIChat()
    assert r.properties == {"properties": {}}
    assert r.extensions == {}
    assert r._existing == False
    assert r.identifier == ResourceIdentifiers.ai_chat_deployment
    assert r.parent == AIServices()
    assert r.resource == "Microsoft.CognitiveServices/accounts/deployments"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 2
    assert list(fields.keys()) == ["aiservices_account", "aiservices_account.chat_deployment"]
    assert fields["aiservices_account.chat_deployment"].resource == "Microsoft.CognitiveServices/accounts/deployments"
    assert fields["aiservices_account.chat_deployment"].properties == {
        "parent": ResourceSymbol("aiservices_account"),
    }
    assert fields["aiservices_account.chat_deployment"].outputs == _get_outputs()
    assert fields["aiservices_account.chat_deployment"].extensions == {}
    assert fields["aiservices_account.chat_deployment"].existing == False
    assert fields["aiservices_account.chat_deployment"].version
    assert fields["aiservices_account.chat_deployment"].symbol == symbols[0]
    assert fields["aiservices_account.chat_deployment"].resource_group == None
    assert not fields["aiservices_account.chat_deployment"].name
    assert fields["aiservices_account.chat_deployment"].defaults

    r2 = AIChat(model="gpt-4o", capacity=10)
    assert r2.properties == {"name": "gpt-4o", "sku": {"capacity": 10}, "properties": {"model": {"name": "gpt-4o"}}}
    symbols = r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "aiservices_account",
        "aiservices_account.chat_deployment",
        "aiservices_account.chat_deployment_gpt4o",
    ]
    assert (
        fields["aiservices_account.chat_deployment_gpt4o"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account.chat_deployment_gpt4o"].properties == {
        "name": "gpt-4o",
        "sku": {"capacity": 10},
        "properties": {"model": {"name": "gpt-4o"}},
        "parent": ResourceSymbol("aiservices_account"),
        "dependsOn": [
            ResourceSymbol("chat_deployment"),
        ],
    }
    assert fields["aiservices_account.chat_deployment_gpt4o"].outputs == _get_outputs("_gpt4o")
    assert fields["aiservices_account.chat_deployment_gpt4o"].extensions == {}
    assert fields["aiservices_account.chat_deployment_gpt4o"].existing == False
    assert fields["aiservices_account.chat_deployment_gpt4o"].version
    assert fields["aiservices_account.chat_deployment_gpt4o"].symbol == symbols[0]
    assert fields["aiservices_account.chat_deployment_gpt4o"].resource_group == None
    assert fields["aiservices_account.chat_deployment_gpt4o"].name == "gpt-4o"
    assert fields["aiservices_account.chat_deployment_gpt4o"].defaults

    r3 = AIChat(model="gpt-4o", capacity=30)
    assert r3.properties == {"name": "gpt-4o", "sku": {"capacity": 30}, "properties": {"model": {"name": "gpt-4o"}}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = AIChat(
        model="secret", account=AIServices(name="foo", tags={"test": "value"}, public_network_access="Disabled")
    )
    assert r4.properties == {"properties": {"model": {"name": "secret"}}, "name": "secret"}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "aiservices_account",
        "aiservices_account.chat_deployment",
        "aiservices_account.chat_deployment_gpt4o",
        "aiservices_account_foo",
        "aiservices_account_foo.chat_deployment_foo_secret",
    ]
    assert (
        fields["aiservices_account_foo.chat_deployment_foo_secret"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].properties == {
        "properties": {"model": {"name": "secret"}},
        "name": "secret",
        "parent": ResourceSymbol("aiservices_account_foo"),
    }
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].outputs == _get_outputs("_foo_secret", "_foo")
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].extensions == {}
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].existing == False
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].version
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].symbol == symbols[0]
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].resource_group == None
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].name == "secret"
    assert fields["aiservices_account_foo.chat_deployment_foo_secret"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = AIChat({"properties": {"model": param1}}, sku=param2, capacity=param3, deployment_name="foo")
    assert r5.properties == {
        "name": "foo",
        "sku": {"name": param2, "capacity": param3},
        "properties": {"model": param1},
    }
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["aiservices_account", "aiservices_account.chat_deployment_foo"]
    assert (
        fields["aiservices_account.chat_deployment_foo"].resource == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account.chat_deployment_foo"].properties == {
        "name": "foo",
        "sku": {"name": param2, "capacity": param3},
        "properties": {"model": param1},
        "parent": ResourceSymbol("aiservices_account"),
    }
    assert fields["aiservices_account.chat_deployment_foo"].outputs == _get_outputs("_foo")
    assert fields["aiservices_account.chat_deployment_foo"].extensions == {}
    assert fields["aiservices_account.chat_deployment_foo"].existing == False
    assert fields["aiservices_account.chat_deployment_foo"].version
    assert fields["aiservices_account.chat_deployment_foo"].symbol == symbols[0]
    assert fields["aiservices_account.chat_deployment_foo"].resource_group == None
    assert fields["aiservices_account.chat_deployment_foo"].name == "foo"
    assert fields["aiservices_account.chat_deployment_foo"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_aiservices_chat_reference():
    r = AIChat.reference(name="foo", account="bar")
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
    assert list(fields.keys()) == ["aiservices_account_bar", "aiservices_account_bar.chat_deployment_bar_foo"]
    assert (
        fields["aiservices_account_bar.chat_deployment_bar_foo"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].properties == {
        "name": "foo",
        "parent": ResourceSymbol("aiservices_account_bar"),
    }
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].outputs == _get_outputs("_bar_foo", "_bar")
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].extensions == {}
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].existing == True
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].version
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].symbol == symbols[0]
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].resource_group == None
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].name == "foo"
    assert not fields["aiservices_account_bar.chat_deployment_bar_foo"].defaults

    rg = ResourceSymbol("resourcegroup_baz")
    r = AIChat.reference(name="foo", account="bar", resource_group="baz")
    assert r.properties == {"name": "foo"}
    assert r._settings["resource_group"]() == "baz"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "resourcegroup_baz",
        "aiservices_account_bar",
        "aiservices_account_bar.chat_deployment_bar_foo",
    ]
    assert (
        fields["aiservices_account_bar.chat_deployment_bar_foo"].resource
        == "Microsoft.CognitiveServices/accounts/deployments"
    )
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].properties == {
        "name": "foo",
        "parent": ResourceSymbol("aiservices_account_bar"),
    }
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].outputs == _get_outputs("_bar_foo", "_bar", "baz")
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].extensions == {}
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].existing == True
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].version
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].symbol == symbols[0]
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].resource_group == None
    assert fields["aiservices_account_bar.chat_deployment_bar_foo"].name == "foo"
    assert not fields["aiservices_account_bar.chat_deployment_bar_foo"].defaults

    r = AIChat.reference(
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


def test_aiservices_chat_defaults():
    r = AIChat()
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    add_defaults(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    assert field.properties == {
        "name": Parameter("aiChatModel", default="o1-mini"),
        "sku": {
            "name": Parameter("aiChatModelSku", default="GlobalStandard"),
            "capacity": Parameter("aiChatModelCapacity", default=1),
        },
        "properties": {
            "model": {
                "name": Parameter("aiChatModel", default="o1-mini"),
                "format": Parameter("aiChatModelFormat", default="OpenAI"),
                "version": Parameter("aiChatModelVersion", default="2024-09-12"),
            }
        },
        "parent": ResourceSymbol("aiservices_account"),
    }


def test_aiservices_chat_export(export_dir):
    class test(AzureInfrastructure):
        r: AIChat = AIChat()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_chat_export_existing(export_dir):
    class test(AzureInfrastructure):
        r: AIChat = field(default=AIChat.reference(name="aitest", account="aitest"))

    export(test(identity=None), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_chat_export_with_properties(export_dir):
    class test(AzureInfrastructure):
        r: AIChat = field(default=AIChat(sku="test", capacity=15, format="foo", version="2"))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_chat_export_multiple_deployments(export_dir):
    class test(AzureInfrastructure):
        r: AIChat = field(default=AIChat(model="one"))
        b: AIChat = field(default=AIChat(model="two"))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_aiservices_chat_client():
    r = AIChat.reference(name="gpt-4o", account="test")
    r.model_format = "OpenAI"
    r.model_name = "gpt-4o"
    assert r._settings["name"]() == "gpt-4o"
    client = r.get_client()
    assert isinstance(client, ChatCompletionsClient)

    # TODO: This is giving a weird "proxies" error on CI
    # from openai import AzureOpenAI, AsyncAzureOpenAI
    # client = r.get_client(AzureOpenAI)
    # assert isinstance(client, AzureOpenAI)

    # client = r.get_client(AsyncAzureOpenAI)
    # assert isinstance(client, AsyncAzureOpenAI)

    # from openai.resources import Chat, AsyncChat
    # client = r.get_client(Chat)
    # assert isinstance(client, Chat)

    # client = r.get_client(AsyncChat)
    # assert isinstance(client, AsyncChat)


def test_aiservices_chat_infra():
    class TestInfra(AzureInfrastructure):
        chat_a: AIChat = field(default=AIChat(model="gpt-4o-mini"))
        chat_b: AIChat = field(default=AIChat(model="gpt-4o"))

    assert isinstance(TestInfra.chat_a, AIChat)
    infra = TestInfra()
    assert isinstance(infra.chat_a, AIChat)
    assert infra.chat_a._settings["name"]() == "gpt-4o-mini"
    assert infra.chat_a.properties == {"name": "gpt-4o-mini", "properties": {"model": {"name": "gpt-4o-mini"}}}

    infra = TestInfra(chat_b=AIChat.reference(name="foo", account="bar"))
    assert infra.chat_b._settings["name"]() == "foo"
    assert infra.chat_b.parent == AIServices(name="bar")


def test_aiservices_chat_app():
    r = AIChat.reference(name="test", account="test")
    r.model_format = "OpenAI"
    r.model_name = "gpt-4o"

    class TestApp(AzureApp):
        client: ChatCompletionsClient

    with pytest.raises(TypeError):
        app = TestApp()

    app = TestApp(client=r)
    assert isinstance(app.client, ChatCompletionsClient)
    assert app.client._config.endpoint == "https://test.openai.azure.com/openai/deployments/test"  # /chat/completions"
    assert app.client._config.credential

    app = TestApp(client="test")
    assert app.client == "test"

    # TODO: This gives a "proxies" error in CI
    # from openai.resources.chat import AsyncCompletions
    # class TestApp(AzureApp):
    #     client: AsyncCompletions = field(default=r, api_version="v1.0")

    # app = TestApp()
    # assert isinstance(app.client, AsyncCompletions)

    # app = TestApp(client="override_client")
    # assert app.client == "override_client"

    class TestApp(AzureApp):
        client: ChatCompletionsClient

    app = TestApp.load(
        config_store={
            "AZURE_AI_AISERVICES_NAME": "test",
            "AZURE_AI_CHAT_NAME": "gpt-4o",
            "AZURE_AI_CHAT_MODEL_FORMAT": "OpenAI",
            "AZURE_AI_CHAT_MODEL_NAME": "gpt-4o",
        }
    )
    assert isinstance(app.client, ChatCompletionsClient)

    class TestApp(AzureApp):
        client: ChatCompletionsClient = field(default=r)

    app = TestApp()
    assert isinstance(app.client, ChatCompletionsClient)
