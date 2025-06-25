import pytest
from unittest.mock import MagicMock

try:
    from azure.ai.evaluation import SKAgentConverter

    has_semantic_kernel = True
except ImportError:
    has_semantic_kernel = False


class FakeFunctionMetadata:
    def __init__(
        self,
        name,
        plugin_name,
        description,
        parameters,
        return_param,
    ):
        self.name = name
        self.plugin_name = plugin_name
        self.description = description
        self.parameters = parameters
        self.return_parameter = return_param
        self.fully_qualified_name = self.plugin_name + "-" + self.name

    def model_dump(self):
        return {
            "name": self.name,
            "plugin_name": self.plugin_name,
            "description": self.description,
            "parameters": self.parameters,
            "fully_qualified_name": self.fully_qualified_name,
            "is_prompt": False,
            "is_asynchronous": False,
            "return_parameter": self.return_parameter,
            "additional_properties": {},
        }


class FakePlugin:
    def __init__(self, functions_metadata):
        self._functions_metadata = functions_metadata

    def get_functions_metadata(self):
        return self._functions_metadata


class FakeKernel:
    def __init__(self, plugins):
        self.plugins = plugins


class FakeChatCompletionAgent:
    def __init__(self, kernel):
        self.kernel = kernel


@pytest.mark.unittest
@pytest.mark.skipif(not has_semantic_kernel, reason="semantic-kernel is not installed")
def test_extract_function_tool_definitions():
    from azure.ai.evaluation import SKAgentConverter

    # Setup mock functions
    get_item_price = FakeFunctionMetadata(
        name="get_item_price",
        plugin_name="MenuPlugin",
        description="Provides the price of the requested menu item.",
        parameters=[
            {
                "name": "menu_item",
                "description": "The name of the menu item.",
                "default_value": None,
                "type_": "str",
                "is_required": True,
                "schema_data": {
                    "type": "string",
                    "description": "The name of the menu item.",
                },
                "include_in_function_choices": True,
            }
        ],
        return_param={
            "name": "return",
            "description": "Returns the price of the menu item.",
            "default_value": None,
            "type_": "str",
            "is_required": True,
            "schema_data": {
                "type": "string",
                "description": "Returns the price of the menu item.",
            },
            "include_in_function_choices": True,
        },
    )

    get_specials = FakeFunctionMetadata(
        name="get_specials",
        plugin_name="MenuPlugin",
        description="Provides a list of specials from the menu.",
        parameters=[],
        return_param={
            "name": "return",
            "description": "Returns the specials from the menu.",
            "default_value": None,
            "type_": "str",
            "is_required": True,
            "schema_data": {
                "type": "string",
                "description": "Returns the specials from the menu.",
            },
            "include_in_function_choices": True,
        },
    )

    plugin = FakePlugin(functions_metadata=[get_item_price, get_specials])
    kernel = FakeKernel(plugins={"MenuPlugin": plugin})
    agent = FakeChatCompletionAgent(kernel=kernel)

    tool_defs = SKAgentConverter._extract_function_tool_definitions(agent)

    assert len(tool_defs) == 2
    assert tool_defs[0].name == "MenuPlugin-get_item_price"
    assert tool_defs[0].description == "Provides the price of the requested menu item."
    assert tool_defs[0].parameters["properties"]["menu_item"]["type"] == "str"
    assert tool_defs[1].name == "MenuPlugin-get_specials"
    assert tool_defs[1].parameters["properties"] == {}
