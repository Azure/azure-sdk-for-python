# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tool client for integrating AzureAIToolClient with LangGraph."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, create_model

if TYPE_CHECKING:
    from azure.ai.agentserver.core.client.tools.aio import AzureAIToolClient, FoundryTool


class ToolClient:
    """Client that integrates AzureAIToolClient with LangGraph.
    
    This class provides methods to list tools from AzureAIToolClient and convert them
    to LangChain BaseTool format, as well as invoke tools in a format compatible with
    LangGraph's create_react_agent and StateGraph.
    
    :param tool_client: The AzureAIToolClient instance to use for tool operations.
    :type tool_client: ~azure.ai.agentserver.core.client.tools.aio.AzureAIToolClient
    
    .. admonition:: Example:
    
        .. code-block:: python
        
            from azure.ai.agentserver.core.client.tools.aio import AzureAIToolClient
            from azure.ai.agentserver.langgraph import ToolClient
            from azure.identity.aio import DefaultAzureCredential
            
            async with DefaultAzureCredential() as credential:
                tool_client = AzureAIToolClient(
                    endpoint="https://<your-endpoint>",
                    credential=credential
                )
                
                client = ToolClient(tool_client)
                
                # List tools as LangChain BaseTool instances
                tools = await client.list_tools()
                
                # Use with create_react_agent
                from langgraph.prebuilt import create_react_agent
                from langchain_openai import AzureChatOpenAI
                
                model = AzureChatOpenAI(model="gpt-4o")
                agent = create_react_agent(model, tools)
                
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
        self._tools_cache: Optional[List["FoundryTool"]] = None
        self._langchain_tools_cache: Optional[List[StructuredTool]] = None
    
    async def list_tools(self) -> List[StructuredTool]:
        """List all available tools as LangChain BaseTool instances.
        
        Retrieves tools from AzureAIToolClient and converts them to LangChain
        StructuredTool instances that can be used with LangGraph's create_react_agent
        or StateGraph.
        
        :return: List of LangChain StructuredTool instances.
        :rtype: List[~langchain_core.tools.StructuredTool]
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.
        
        .. admonition:: Example:
        
            .. code-block:: python
            
                client = ToolClient(tool_client)
                tools = await client.list_tools()
                
                # Use with create_react_agent
                agent = create_react_agent(model, tools)
        """
        # Get tools from AzureAIToolClient
        azure_tools = await self._tool_client.list_tools()
        self._tools_cache = azure_tools
        
        # Convert to LangChain StructuredTool instances
        langchain_tools = []
        for azure_tool in azure_tools:
            langchain_tool = self._convert_to_langchain_tool(azure_tool)
            langchain_tools.append(langchain_tool)
        
        self._langchain_tools_cache = langchain_tools
        return langchain_tools
    
    def _convert_to_langchain_tool(self, azure_tool: "FoundryTool") -> StructuredTool:
        """Convert an AzureAITool to a LangChain StructuredTool.
        
        :param azure_tool: The AzureAITool to convert.
        :type azure_tool: ~azure.ai.agentserver.core.client.tools.aio.AzureAITool
        :return: A LangChain StructuredTool instance.
        :rtype: ~langchain_core.tools.StructuredTool
        """
        # Get the input schema from the tool descriptor
        input_schema = azure_tool.input_schema or {}
        
        # Create a Pydantic model for the tool's input schema
        args_schema = self._create_pydantic_model(
            tool_name=azure_tool.name,
            schema=input_schema
        )
        
        # Create an async function that invokes the tool
        async def tool_func(**kwargs: Any) -> str:
            """Invoke the Azure AI tool."""
            result = await azure_tool(**kwargs)
            # Convert result to string for LangChain compatibility
            if isinstance(result, dict):
                import json
                return json.dumps(result)
            return str(result)
        
        # Create a StructuredTool with the async function
        structured_tool = StructuredTool(
            name=azure_tool.name,
            description=azure_tool.description or "No description available",
            coroutine=tool_func,
            args_schema=args_schema,
        )
        
        return structured_tool
    
    def _create_pydantic_model(
        self,
        tool_name: str,
        schema: Dict[str, Any]
    ) -> type[BaseModel]:
        """Create a Pydantic model from a JSON schema.
        
        :param tool_name: Name of the tool (used for model name).
        :type tool_name: str
        :param schema: JSON schema for the tool's input parameters.
        :type schema: Dict[str, Any]
        :return: A Pydantic model class.
        :rtype: type[BaseModel]
        """
        # Get properties from schema
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])
        
        # Build field definitions for Pydantic model
        field_definitions = {}
        for prop_name, prop_schema in properties.items():
            prop_type = self._json_type_to_python_type(prop_schema.get("type", "string"))
            prop_description = prop_schema.get("description", "")
            
            # Determine if field is required
            is_required = prop_name in required_fields
            
            if is_required:
                field_definitions[prop_name] = (
                    prop_type,
                    Field(..., description=prop_description)
                )
            else:
                field_definitions[prop_name] = (
                    Optional[prop_type],
                    Field(None, description=prop_description)
                )
        
        # Create the model dynamically
        model_name = f"{tool_name.replace('-', '_').replace(' ', '_').title()}Input"
        return create_model(model_name, **field_definitions)
    
    def _json_type_to_python_type(self, json_type: str) -> type:
        """Convert JSON schema type to Python type.
        
        :param json_type: JSON schema type string.
        :type json_type: str
        :return: Corresponding Python type.
        :rtype: type
        """
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        return type_mapping.get(json_type, str)
    
    async def invoke_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        **kwargs: Any
    ) -> Any:
        """Invoke a tool by name with the given input.
        
        This method is compatible with LangGraph's tool invocation format and
        returns results in LangChain tool result format (as a string).
        
        :param tool_name: Name of the tool to invoke.
        :type tool_name: str
        :param tool_input: Dictionary of input parameters for the tool.
        :type tool_input: Dict[str, Any]
        :param kwargs: Additional keyword arguments to pass to the tool client.
        :return: The tool execution result as a string (LangChain format).
        :rtype: str
        :raises KeyError: If the tool name is not found.
        :raises ~azure.core.exceptions.HttpResponseError:
            Raised for HTTP communication failures.
        
        .. admonition:: Example:
        
            .. code-block:: python
            
                result = await client.invoke_tool(
                    tool_name="weather_tool",
                    tool_input={"location": "Seattle", "units": "celsius"}
                )
                print(result)  # Returns string result
        """
        # Invoke the tool using the tool client
        result = await self._tool_client.invoke_tool(
            tool=tool_name,
            **tool_input,
            **kwargs
        )
        
        # Convert result to string for LangChain compatibility
        if isinstance(result, dict):
            import json
            return json.dumps(result)
        return str(result)
    
    async def __aenter__(self) -> "ToolClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *exc_details: Any) -> None:
        """Async context manager exit."""
        # The tool_client lifecycle is managed externally
        pass
