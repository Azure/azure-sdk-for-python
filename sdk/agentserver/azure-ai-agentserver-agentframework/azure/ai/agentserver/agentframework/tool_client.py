# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: disable-error-code="assignment"
"""Tool client for integrating AzureAIToolClient with Agent Framework."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from agent_framework import AIFunction
from pydantic import Field, create_model
from azure.ai.agentserver.core.logger import get_logger
if TYPE_CHECKING:
    from azure.ai.agentserver.core.client.tools.aio import AzureAIToolClient, FoundryTool

logger = get_logger()

# pylint: disable=client-accepts-api-version-keyword,missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
class ToolClient:
    """Client that integrates AzureAIToolClient with Agent Framework.
    
    This class provides methods to list tools from AzureAIToolClient and invoke them
    in a format compatible with Agent Framework agents.
    
    :param tool_client: The AzureAIToolClient instance to use for tool operations.
    :type tool_client: ~azure.ai.agentserver.core.client.tools.aio.AzureAIToolClient
    
    .. admonition:: Example:
    
        .. code-block:: python
        
            from azure.ai.agentserver.core.client.tools.aio import AzureAIToolClient
            from azure.ai.agentserver.agentframework import ToolClient
            from azure.identity.aio import DefaultAzureCredential
            
            async with DefaultAzureCredential() as credential:
                tool_client = AzureAIToolClient(
                    endpoint="https://<your-project-endpoint>",
                    credential=credential
                )
                
                client = ToolClient(tool_client)
                
                # List tools as Agent Framework tool definitions
                tools = await client.list_tools()
                
                # Invoke a tool directly
                result = await client.invoke_tool(
                    tool_name="my_tool",
                    tool_input={"param": "value"}
                )

    :meta private:
    """

    def __init__(self, tool_client: "AzureAIToolClient") -> None:
        """Initialize the ToolClient.
        
        :param tool_client: The AzureAIToolClient instance to use for tool operations.
        :type tool_client: ~azure.ai.agentserver.core.client.tools.aio.AzureAIToolClient
        """
        self._tool_client = tool_client
        self._aifunction_cache: List[AIFunction] = None

    async def list_tools(self) -> List[AIFunction]:
        """List all available tools as Agent Framework tool definitions.
        
        Retrieves tools from AzureAIToolClient and returns them in a format
        compatible with Agent Framework.
        
        :return: List of tool definitions.
        :rtype: List[AIFunction]
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.
        
        .. admonition:: Example:
        
            .. code-block:: python
            
                client = ToolClient(tool_client)
                tools = await client.list_tools()
        """
        # Get tools from AzureAIToolClient
        if self._aifunction_cache is not None:
            return self._aifunction_cache

        azure_tools = await self._tool_client.list_tools()
        self._aifunction_cache = []

        # Convert to Agent Framework tool definitions
        for azure_tool in azure_tools:
            ai_function_tool = self._convert_to_agent_framework_tool(azure_tool)
            self._aifunction_cache.append(ai_function_tool)

        return self._aifunction_cache

    def _convert_to_agent_framework_tool(self, azure_tool: "FoundryTool") -> AIFunction:
        """Convert an AzureAITool to an Agent Framework AI Function
        
        :param azure_tool: The AzureAITool to convert.
        :type azure_tool: ~azure.ai.agentserver.core.client.tools.aio.FoundryTool
        :return: An AI Function Tool.
        :rtype: AIFunction
        """
        # Get the input schema from the tool descriptor
        input_schema = azure_tool.input_schema or {}

        # Create a Pydantic model from the input schema
        properties = input_schema.get("properties", {})
        required_fields = set(input_schema.get("required", []))

        # Build field definitions for the Pydantic model
        field_definitions: Dict[str, Any] = {}
        for field_name, field_info in properties.items():
            field_type = self._json_schema_type_to_python(field_info.get("type", "string"))
            field_description = field_info.get("description", "")
            is_required = field_name in required_fields

            if is_required:
                field_definitions[field_name] = (field_type, Field(description=field_description))
            else:
                field_definitions[field_name] = (Optional[field_type],
                                                 Field(default=None, description=field_description))

        # Create the Pydantic model dynamically
        input_model = create_model(
            f"{azure_tool.name}_input",
            **field_definitions
        )

        # Create a wrapper function that calls the Azure tool
        async def tool_func(**kwargs: Any) -> Any:
            """Dynamically generated function to invoke the Azure AI tool.

            :return: The result from the tool invocation.
            :rtype: Any
            """
            logger.debug("Invoking tool: %s with input: %s", azure_tool.name, kwargs)
            return await azure_tool.ainvoke(kwargs)

        # Create and return the AIFunction
        return AIFunction(
            name=azure_tool.name,
            description=azure_tool.description or "No description available",
            func=tool_func,
            input_model=input_model
        )

    def _json_schema_type_to_python(self, json_type: str) -> type:
        """Convert JSON schema type to Python type.
        
        :param json_type: The JSON schema type string.
        :type json_type: str
        :return: The corresponding Python type.
        :rtype: type
        """
        type_map = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        return type_map.get(json_type, str)

    async def close(self) -> None:
        """Close the tool client and release resources."""
        await self._tool_client.close()

    async def __aenter__(self) -> "ToolClient":
        """Async context manager entry.

        :return: The ToolClient instance.
        :rtype: ToolClient
        """
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        """Async context manager exit.

        :param exc_details: Exception details if an exception occurred.
        :type exc_details: Any
        """
        await self.close()
