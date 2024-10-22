# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
import inspect
import json
import logging
import base64
import asyncio

from azure.core.credentials import TokenCredential, AccessToken

from ._enums import AgentStreamEvent, ConnectionType
from ._models import (
    ConnectionsListSecretsResponse,
    MessageDeltaChunk,
    SubmitToolOutputsAction,
    ThreadRun,
    RunStep,
    ThreadMessage,
    RunStepDeltaChunk,
    FunctionToolDefinition,
    FunctionDefinition,
    ToolDefinition,
    ToolResources,
    FileSearchToolDefinition,
    FileSearchToolResource,
    BingGroundingToolDefinition,
    ConnectionListResource,
    AzureAISearchResource,
    AzureAISearchToolDefinition,
    CodeInterpreterToolDefinition,
    CodeInterpreterToolResource,
    RequiredFunctionToolCall,
    ConnectionType,
)

from abc import ABC, abstractmethod
from typing import AsyncIterator, Awaitable, Callable, List, Dict, Any, Type, Optional, Iterator, Tuple, get_origin

logger = logging.getLogger(__name__)


def _filter_parameters(model_class: Type, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove the parameters, non present in class public fields; return shallow copy of a dictionary.

    **Note:** Classes inherited from the model check that the parameters are present
    in the list of attributes and if they are not, the error is being raised. This check may not
    be relevant for classes, not inherited from azure.ai.client._model_base.Model.
    :param model_class: The class of model to be used.
    :param parameters: The parsed dictionary with parameters.
    :return: The dictionary with all invalid parameters removed.
    """
    new_params = {}
    valid_parameters = set(
        filter(
            lambda x: not x.startswith("_") and hasattr(model_class.__dict__[x], "_type"), model_class.__dict__.keys()
        )
    )
    for k in filter(lambda x: x in valid_parameters, parameters.keys()):
        new_params[k] = parameters[k]
    return new_params


def _safe_instantiate(model_class: Type, parameters: Dict[str, Any]) -> Any:
    """
    Instantiate class with the set of parameters from the server.

    :param model_class: The class of model to be used.
    :param parameters: The parsed dictionary with parameters.
    :return: The class of model_class type if parameters is a dictionary, or the parameters themselves otherwise.
    """
    if not isinstance(parameters, dict):
        return parameters
    return model_class(**_filter_parameters(model_class, parameters))


class ConnectionProperties:
    """The properties of a single connection.

    :ivar id: A unique identifier for the connection.
    :vartype id: str
    :ivar name: The friendly name of the connection.
    :vartype name: str
    :ivar authentication_type: The authentication type used by the connection.
    :vartype authentication_type: ~azure.ai.client.models._models.AuthenticationType
    :ivar connection_type: The connection type .
    :vartype connection_type: ~azure.ai.client.models._models.ConnectionType
    :ivar endpoint_url: The endpoint URL associated with this connection
    :vartype endpoint_url: str
    :ivar key: The api-key to be used when accessing the connection.
    :vartype key: str
    :ivar token_credential: The TokenCredential to be used when accessing the connection.
    :vartype token_credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(self, *, connection: ConnectionsListSecretsResponse, token_credential: TokenCredential = None) -> None:
        self.id = connection.id
        self.name = connection.name
        self.authentication_type = connection.properties.auth_type
        self.connection_type = connection.properties.category
        self.endpoint_url = (
            connection.properties.target[:-1]
            if connection.properties.target.endswith("/")
            else connection.properties.target
        )
        self.key: str = None
        if hasattr(connection.properties, "credentials"):
            if hasattr(connection.properties.credentials, "key"):
                self.key = connection.properties.credentials.key
        self.token_credential = token_credential

    def to_evaluator_model_config(self, deployment_name, api_version) -> Dict[str, str]:
        connection_type = self.connection_type.value
        if self.connection_type.value == ConnectionType.AZURE_OPEN_AI:
            connection_type = "azure_openai"

        if self.authentication_type == "ApiKey":
            model_config = {
                "azure_deployment": deployment_name,
                "azure_endpoint": self.endpoint_url,
                "type": connection_type,
                "api_version": api_version,
                "api_key": f"{self.id}/credentials/key",
            }
        else:
            model_config = {
                "azure_deployment": deployment_name,
                "azure_endpoint": self.endpoint_url,
                "type": self.connection_type,
                "api_version": api_version,
            }
        return model_config

    def __str__(self):
        out = "{\n"
        out += f' "name": "{self.name}",\n'
        out += f' "id": "{self.id}",\n'
        out += f' "authentication_type": "{self.authentication_type}",\n'
        out += f' "connection_type": "{self.connection_type}",\n'
        out += f' "endpoint_url": "{self.endpoint_url}",\n'
        if self.key:
            out += f' "key": "{self.key}",\n'
        else:
            out += f' "key": null,\n'
        if self.token_credential:
            access_token = self.token_credential.get_token("https://cognitiveservices.azure.com/.default")
            out += f' "token_credential": "{access_token.token}", expires on {access_token.expires_on} ({datetime.datetime.fromtimestamp(access_token.expires_on, datetime.timezone.utc)})\n'
        else:
            out += f' "token_credential": null\n'
        out += "}\n"
        return out


class SASTokenCredential(TokenCredential):
    def __init__(
        self,
        *,
        sas_token: str,
        credential: TokenCredential,
        subscription_id: str,
        resource_group_name: str,
        project_name: str,
        connection_name: str,
    ):
        self._sas_token = sas_token
        self._credential = credential
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._project_name = project_name
        self._connection_name = connection_name
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self._sas_token)
        logger.debug("[SASTokenCredential.__init__] Exit. Given token expires on %s.", self._expires_on)

    @classmethod
    def _get_expiration_date_from_token(cls, jwt_token: str) -> datetime:
        payload = jwt_token.split(".")[1]
        padded_payload = payload + "=" * (4 - len(payload) % 4)  # Add padding if necessary
        decoded_bytes = base64.urlsafe_b64decode(padded_payload)
        decoded_str = decoded_bytes.decode("utf-8")
        decoded_payload = json.loads(decoded_str)
        expiration_date = decoded_payload.get("exp")
        return datetime.datetime.fromtimestamp(expiration_date, datetime.timezone.utc)

    def _refresh_token(self) -> None:
        logger.debug("[SASTokenCredential._refresh_token] Enter")
        from azure.ai.client import AzureAIClient

        ai_client = AzureAIClient(
            credential=self._credential,
            endpoint="not-needed",  # Since we are only going to use the "endpoints" operations, we don't need to supply an endpoint. http://management.azure.com is hard coded in the SDK.
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            project_name=self._project_name,
        )

        connection = ai_client.endpoints.get(connection_name=self._connection_name, populate_secrets=True)

        self._sas_token = connection.properties.credentials.sas
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self._sas_token)
        logger.debug("[SASTokenCredential._refresh_token] Exit. New token expires on %s.", self._expires_on)

    def get_token(self) -> AccessToken:
        logger.debug("SASTokenCredential.get_token] Enter")
        if self._expires_on < datetime.datetime.now(datetime.timezone.utc):
            self._refresh_token()
        return AccessToken(self._sas_token, self._expires_on.timestamp())


# Define type_map to translate Python type annotations to JSON Schema types
type_map = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "bytes": "string",  # Typically encoded as base64-encoded strings in JSON
    "NoneType": "null",
    "datetime": "string",  # Use format "date-time"
    "date": "string",  # Use format "date"
    "UUID": "string",  # Use format "uuid"
}


def _map_type(annotation) -> str:

    if annotation == inspect.Parameter.empty:
        return "string"  # Default type if annotation is missing

    origin = get_origin(annotation)

    if origin in {list, List}:
        return "array"
    elif origin in {dict, Dict}:
        return "object"
    elif hasattr(annotation, "__name__"):
        return type_map.get(annotation.__name__, "string")
    elif isinstance(annotation, type):
        return type_map.get(annotation.__name__, "string")

    return "string"  # Fallback to "string" if type is unrecognized


class Tool(ABC):
    """
    An abstract class representing a tool that can be used by an agent.
    """

    @property
    @abstractmethod
    def definitions(self) -> List[ToolDefinition]:
        """Get the tool definitions."""
        pass

    @property
    @abstractmethod
    def resources(self) -> ToolResources:
        """Get the tool resources."""
        pass

    @abstractmethod
    def execute(self, tool_call: Any) -> Any:
        """
        Execute the tool with the provided tool call.

        :param tool_call: The tool call to execute.
        :return: The output of the tool operations.
        """
        pass

    @abstractmethod
    def updateConnections(self, connection_list: List[Tuple[str, str]]) -> None:
        pass


class FunctionTool(Tool):
    """
    A tool that executes user-defined functions.
    """

    def __init__(self, functions: Dict[str, Any]):
        """
        Initialize FunctionTool with a dictionary of functions.

        :param functions: A dictionary where keys are function names and values are the function objects.
        """
        self._functions = functions
        self._definitions = self._build_function_definitions(functions)

    def _build_function_definitions(self, functions: Dict[str, Any]) -> List[ToolDefinition]:
        specs = []
        for name, func in functions.items():
            sig = inspect.signature(func)
            params = sig.parameters
            docstring = inspect.getdoc(func)
            description = docstring.split("\n")[0] if docstring else "No description"

            properties = {}
            for param_name, param in params.items():
                param_type = _map_type(param.annotation)
                param_description = param.annotation.__doc__ if param.annotation != inspect.Parameter.empty else None
                properties[param_name] = {"type": param_type, "description": param_description}

            function_def = FunctionDefinition(
                name=name,
                description=description,
                parameters={"type": "object", "properties": properties, "required": list(params.keys())},
            )
            tool_def = FunctionToolDefinition(function=function_def)
            specs.append(tool_def)
        return specs

    def _get_func_and_args(self, tool_call: RequiredFunctionToolCall) -> Tuple[Any, Dict[str, Any]]:
        function_name = tool_call.function.name
        arguments = tool_call.function.arguments

        if function_name not in self._functions:
            logging.error(f"Function '{function_name}' not found.")
            raise ValueError(f"Function '{function_name}' not found.")

        function = self._functions[function_name]

        try:
            parsed_arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON arguments for function '{function_name}': {e}")
            raise ValueError(f"Invalid JSON arguments: {e}") from e

        if not isinstance(parsed_arguments, dict):
            logging.error(f"Arguments must be a JSON object for function '{function_name}'.")
            raise TypeError("Arguments must be a JSON object.")

        return function, parsed_arguments

    def execute(self, tool_call: RequiredFunctionToolCall) -> Any:
        function, parsed_arguments = self._get_func_and_args(tool_call)

        try:
            return function(**parsed_arguments) if parsed_arguments else function()
        except TypeError as e:
            logging.error(f"Error executing function '{tool_call.function.name}': {e}")
            raise

    def updateConnections(self, connection_list: List[Tuple[str, str]]) -> None:
        pass

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the function definitions.

        :return: A list of function definitions.
        """
        return self._definitions

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources for the agent.

        :return: An empty ToolResources as FunctionTool doesn't have specific resources.
        """
        return ToolResources()


class AsyncFunctionTool(FunctionTool):

    async def execute(self, tool_call: RequiredFunctionToolCall) -> Any:
        function, parsed_arguments = self._get_func_and_args(tool_call)

        try:
            if inspect.iscoroutinefunction(function):
                return await function(**parsed_arguments) if parsed_arguments else await function()
            else:
                return function(**parsed_arguments) if parsed_arguments else function()
        except TypeError as e:
            logging.error(f"Error executing function '{tool_call.function.name}': {e}")
            raise


class AzureAISearchTool(Tool):
    """
    A tool that searches for information using Azure AI Search.
    """

    def __init__(self):
        self.index_list = []

    def add_index(self, index: str):
        """
        Add an index ID to the list of indices used to search.
        """
        # TODO
        self.index_list.append(index)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the Azure AI search tool definitions.
        """
        return [AzureAISearchToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the Azure AI search resources.
        """
        return ToolResources(azure_ai_search=AzureAISearchResource(index_list=self.index_list))

    def execute(self, tool_call: Any) -> Any:
        pass

    def updateConnections(self, connection_list: List[Tuple[str, str]]) -> None:
        pass


class BingGroundingTool(Tool):
    """
    A tool that searches for information using Bing.
    """

    def __init__(self):
        self.connection_ids = []

    def add_connection(self, connection_id: str):
        """
        Add a connection ID to the list of connections used to search.
        """
        # TODO
        self.connection_ids.append(connection_id)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the Bing grounding tool definitions.
        """
        return [BingGroundingToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the Bing grounding resources.
        """
        return ToolResources(bing_grounding=ConnectionListResource(connection_list=self.connection_ids))

    def execute(self, tool_call: Any) -> Any:
        pass

    def updateConnections(self, connection_list: List[Tuple[str, str]]) -> None:
        """
        use connection_list to auto-update connections for bing search tool if no pre-existing
        """
        if self.connection_ids.__len__() == 0:
            for name, endpoint_type in connection_list:
                if endpoint_type == "ApiKey":
                    self.connection_ids.append(name)
                    return


class FileSearchTool(Tool):
    """
    A tool that searches for uploaded file information from the created vector stores.
    """

    def __init__(self, vector_store_ids: List[str] = []):
        self.vector_store_ids = vector_store_ids

    def add_vector_store(self, store_id: str):
        """
        Add a vector store ID to the list of vector stores to search for files.
        """
        self.vector_store_ids.append(store_id)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the file search tool definitions.
        """
        return [FileSearchToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the file search resources.
        """
        return ToolResources(file_search=FileSearchToolResource(vector_store_ids=self.vector_store_ids))

    def execute(self, tool_call: Any) -> Any:
        pass


class CodeInterpreterTool(Tool):
    """
    A tool that interprets code files uploaded to the agent.
    """

    def __init__(self):
        self.file_ids = []

    def add_file(self, file_id: str):
        """
        Add a file ID to the list of files to interpret.

        :param file_id: The ID of the file to interpret.
        """
        self.file_ids.append(file_id)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the code interpreter tool definitions.
        """
        return [CodeInterpreterToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the code interpreter resources.
        """
        return ToolResources(code_interpreter=CodeInterpreterToolResource(file_ids=self.file_ids))

    def execute(self, tool_call: Any) -> Any:
        pass

    def updateConnections(self, connection_list: List[Tuple[str, str]]) -> None:
        pass


class ToolSet:
    """
    A collection of tools that can be used by an agent.
    """

    def __init__(self):
        self._tools: List[Tool] = []

    def validate_tool_type(self, tool_type: Type[Tool]) -> None:
        """
        Validate the type of the tool.

        :param tool_type: The type of the tool to validate.
        :raises ValueError: If the tool type is not a subclass of Tool.
        """
        if isinstance(tool_type, AsyncFunctionTool):
            raise ValueError(
                "AsyncFunctionTool is not supported in ToolSet.  To use async functions, use AsyncToolSet and agents operations in azure.ai.client.aio."
            )

    def add(self, tool: Tool):
        """
        Add a tool to the tool set.

        :param tool: The tool to add.
        :raises ValueError: If a tool of the same type already exists.
        """
        self.validate_tool_type(type(tool))

        if any(isinstance(existing_tool, type(tool)) for existing_tool in self._tools):
            raise ValueError("Tool of type {type(tool).__name__} already exists in the ToolSet.")
        self._tools.append(tool)

    def remove(self, tool_type: Type[Tool]) -> None:
        """
        Remove a tool of the specified type from the tool set.

        :param tool_type: The type of tool to remove.
        :raises ValueError: If a tool of the specified type is not found.
        """
        for i, tool in enumerate(self._tools):
            if isinstance(tool, tool_type):
                del self._tools[i]
                logging.info(f"Tool of type {tool_type.__name__} removed from the ToolSet.")
                return
        raise ValueError(f"Tool of type {tool_type.__name__} not found in the ToolSet.")

    def updateResources(self, connection_list: List[Tuple[str, str]]) -> None:
        for tool in self._tools:
            tool.updateConnections(connection_list)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the definitions for all tools in the tool set.
        """
        tools = []
        for tool in self._tools:
            tools.extend(tool.definitions)
        return tools

    @property
    def resources(self) -> ToolResources:
        """
        Get the resources for all tools in the tool set.
        """
        tool_resources = {}
        for tool in self._tools:
            resources = tool.resources
            for key, value in resources.items():
                if key in tool_resources:
                    if isinstance(tool_resources[key], dict) and isinstance(value, dict):
                        tool_resources[key].update(value)
                else:
                    tool_resources[key] = value
        return self._create_tool_resources_from_dict(tool_resources)

    def _create_tool_resources_from_dict(self, resources: Dict[str, Any]) -> ToolResources:
        """
        Safely converts a dictionary into a ToolResources instance.
        """
        try:
            return ToolResources(**resources)
        except TypeError as e:
            logging.error(f"Error creating ToolResources: {e}")
            raise ValueError("Invalid resources for ToolResources.") from e

    def get_definitions_and_resources(self) -> Dict[str, Any]:
        """
        Get the definitions and resources for all tools in the tool set.

        :return: A dictionary containing the tool resources and definitions.
        """
        return {
            "tool_resources": self.resources,
            "tools": self.definitions,
        }

    def get_tool(self, tool_type: Type[Tool]) -> Tool:
        """
        Get a tool of the specified type from the tool set.

        :param tool_type: The type of tool to get.
        :return: The tool of the specified type.
        :raises ValueError: If a tool of the specified type is not found.
        """
        for tool in self._tools:
            if isinstance(tool, tool_type):
                return tool
        raise ValueError(f"Tool of type {tool_type.__name__} not found.")

    def execute_tool_calls(self, tool_calls: List[Any]) -> Any:
        """
        Execute a tool of the specified type with the provided tool calls.

        :param tool_calls: A list of tool calls to execute.
        :return: The output of the tool operations.
        """
        tool_outputs = []

        for tool_call in tool_calls:
            try:
                if tool_call.type == "function":
                    tool = self.get_tool(FunctionTool)
                    output = tool.execute(tool_call)
                    tool_output = {
                        "tool_call_id": tool_call.id,
                        "output": output,
                    }
                    tool_outputs.append(tool_output)
            except Exception as e:
                logging.error(f"Failed to execute tool call {tool_call}: {e}")

        return tool_outputs


class AsyncToolSet(ToolSet):

    def validate_tool_type(self, tool_type: Type[Tool]) -> None:
        """
        Validate the type of the tool.

        :param tool_type: The type of the tool to validate.
        :raises ValueError: If the tool type is not a subclass of Tool.
        """
        if isinstance(tool_type, FunctionTool):
            raise ValueError(
                "FunctionTool is not supported in AsyncToolSet.  Please use AsyncFunctionTool instead and provide sync and/or async function(s)."
            )

    async def execute_tool_calls(self, tool_calls: List[Any]) -> Any:
        """
        Execute a tool of the specified type with the provided tool calls.

        :param tool_calls: A list of tool calls to execute.
        :return: The output of the tool operations.
        """
        tool_outputs = []

        for tool_call in tool_calls:
            try:
                if tool_call.type == "function":
                    tool = self.get_tool(AsyncFunctionTool)
                    output = await tool.execute(tool_call)
                    tool_output = {
                        "tool_call_id": tool_call.id,
                        "output": output,
                    }
                    tool_outputs.append(tool_output)
            except Exception as e:
                logging.error(f"Failed to execute tool call {tool_call}: {e}")

        return tool_outputs


class AgentEventHandler:

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        """Handle message delta events."""
        pass

    def on_thread_message(self, message: "ThreadMessage") -> None:
        """Handle thread message events."""
        pass

    def on_thread_run(self, run: "ThreadRun") -> None:
        """Handle thread run events."""
        pass

    def on_run_step(self, step: "RunStep") -> None:
        """Handle run step events."""
        pass

    def on_run_step_delta(self, delta: "RunStepDeltaChunk") -> None:
        """Handle run step delta events."""
        pass

    def on_error(self, data: str) -> None:
        """Handle error events."""
        pass

    def on_done(self) -> None:
        """Handle the completion of the stream."""
        pass

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        """Handle any unhandled event types."""
        pass


class AsyncAgentEventHandler:

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        """Handle message delta events."""
        pass

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        """Handle thread message events."""
        pass

    async def on_thread_run(self, run: "ThreadRun") -> None:
        """Handle thread run events."""
        pass

    async def on_run_step(self, step: "RunStep") -> None:
        """Handle run step events."""
        pass

    async def on_run_step_delta(self, delta: "RunStepDeltaChunk") -> None:
        """Handle run step delta events."""
        pass

    async def on_error(self, data: str) -> None:
        """Handle error events."""
        pass

    async def on_done(self) -> None:
        """Handle the completion of the stream."""
        pass

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        """Handle any unhandled event types."""
        pass


class AsyncAgentRunStream(AsyncIterator[Tuple[str, Any]]):
    def __init__(
        self,
        response_iterator: AsyncIterator[bytes],
        submit_tool_outputs: Callable[[ThreadRun, Optional[AsyncAgentEventHandler]], Awaitable[None]],
        event_handler: Optional["AsyncAgentEventHandler"] = None,
    ):
        self.response_iterator = response_iterator
        self.event_handler = event_handler
        self.done = False
        self.buffer = ""
        self.submit_tool_outputs = submit_tool_outputs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        close_method = getattr(self.response_iterator, "close", None)
        if callable(close_method):
            result = close_method()
            if asyncio.iscoroutine(result):
                await result

    def __aiter__(self):
        return self

    async def __anext__(self) -> Tuple[str, Any]:
        while True:
            try:
                chunk = await self.response_iterator.__anext__()
                self.buffer += chunk.decode("utf-8")
            except StopAsyncIteration:
                if self.buffer:
                    event_data_str, self.buffer = self.buffer, ""
                    if event_data_str:
                        return await self._process_event(event_data_str)
                raise StopAsyncIteration

            while "\n\n" in self.buffer:
                event_data_str, self.buffer = self.buffer.split("\n\n", 1)
                return await self._process_event(event_data_str)

    def _parse_event_data(self, event_data_str: str) -> Tuple[str, Any]:
        event_lines = event_data_str.strip().split("\n")
        event_type = None
        event_data = ""

        for line in event_lines:
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                event_data = line.split(":", 1)[1].strip()

        if not event_type:
            raise ValueError("Event type not specified in the event data.")

        try:
            parsed_data = json.loads(event_data)
        except json.JSONDecodeError:
            parsed_data = event_data

        # Workaround for service bug: Rename 'expires_at' to 'expired_at'
        if event_type.startswith("thread.run.step") and isinstance(parsed_data, dict) and "expires_at" in parsed_data:
            parsed_data["expired_at"] = parsed_data.pop("expires_at")

        # Map to the appropriate class instance
        if event_type in {
            AgentStreamEvent.THREAD_RUN_CREATED,
            AgentStreamEvent.THREAD_RUN_QUEUED,
            AgentStreamEvent.THREAD_RUN_IN_PROGRESS,
            AgentStreamEvent.THREAD_RUN_REQUIRES_ACTION,
            AgentStreamEvent.THREAD_RUN_COMPLETED,
            AgentStreamEvent.THREAD_RUN_FAILED,
            AgentStreamEvent.THREAD_RUN_CANCELLING,
            AgentStreamEvent.THREAD_RUN_CANCELLED,
            AgentStreamEvent.THREAD_RUN_EXPIRED,
        }:
            event_data_obj = _safe_instantiate(ThreadRun, parsed_data)
        elif event_type in {
            AgentStreamEvent.THREAD_RUN_STEP_CREATED,
            AgentStreamEvent.THREAD_RUN_STEP_IN_PROGRESS,
            AgentStreamEvent.THREAD_RUN_STEP_COMPLETED,
            AgentStreamEvent.THREAD_RUN_STEP_FAILED,
            AgentStreamEvent.THREAD_RUN_STEP_CANCELLED,
            AgentStreamEvent.THREAD_RUN_STEP_EXPIRED,
        }:
            event_data_obj = _safe_instantiate(RunStep, parsed_data)
        elif event_type in {
            AgentStreamEvent.THREAD_MESSAGE_CREATED,
            AgentStreamEvent.THREAD_MESSAGE_IN_PROGRESS,
            AgentStreamEvent.THREAD_MESSAGE_COMPLETED,
            AgentStreamEvent.THREAD_MESSAGE_INCOMPLETE,
        }:
            event_data_obj = _safe_instantiate(ThreadMessage, parsed_data)
        elif event_type == AgentStreamEvent.THREAD_MESSAGE_DELTA:
            event_data_obj = _safe_instantiate(MessageDeltaChunk, parsed_data)
        elif event_type == AgentStreamEvent.THREAD_RUN_STEP_DELTA:
            event_data_obj = _safe_instantiate(RunStepDeltaChunk, parsed_data)
        else:
            event_data_obj = parsed_data

        return event_type, event_data_obj

    async def _process_event(self, event_data_str: str) -> Tuple[str, Any]:
        event_type, event_data_obj = self._parse_event_data(event_data_str)

        if (
            isinstance(event_data_obj, ThreadRun)
            and event_data_obj.status == "requires_action"
            and isinstance(event_data_obj.required_action, SubmitToolOutputsAction)
        ):
            await self.submit_tool_outputs(event_data_obj, self.event_handler)
        if self.event_handler:
            try:
                if isinstance(event_data_obj, MessageDeltaChunk):
                    await self.event_handler.on_message_delta(event_data_obj)
                elif isinstance(event_data_obj, ThreadMessage):
                    await self.event_handler.on_thread_message(event_data_obj)
                elif isinstance(event_data_obj, ThreadRun):
                    await self.event_handler.on_thread_run(event_data_obj)
                elif isinstance(event_data_obj, RunStep):
                    await self.event_handler.on_run_step(event_data_obj)
                elif isinstance(event_data_obj, RunStepDeltaChunk):
                    await self.event_handler.on_run_step_delta(event_data_obj)
                elif event_type == AgentStreamEvent.ERROR:
                    await self.event_handler.on_error(event_data_obj)
                elif event_type == AgentStreamEvent.DONE:
                    await self.event_handler.on_done()
                    self.done = True  # Mark the stream as done
                else:
                    await self.event_handler.on_unhandled_event(event_type, event_data_obj)
            except Exception as e:
                logging.error(f"Error in event handler for event '{event_type}': {e}")

        return event_type, event_data_obj

    async def until_done(self) -> None:
        """
        Iterates through all events until the stream is marked as done.
        """
        try:
            async for _ in self:
                pass  # The EventHandler handles the events
        except StopAsyncIteration:
            pass


class AgentRunStream(Iterator[Tuple[str, Any]]):
    def __init__(
        self,
        response_iterator: Iterator[bytes],
        submit_tool_outputs: Callable[[ThreadRun, Optional[AgentEventHandler]], None],
        event_handler: Optional[AgentEventHandler] = None,
    ):
        self.response_iterator = response_iterator
        self.event_handler = event_handler
        self.done = False
        self.buffer = ""
        self.submit_tool_outputs = submit_tool_outputs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        close_method = getattr(self.response_iterator, "close", None)
        if callable(close_method):
            close_method()

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[str, Any]:
        if self.done:
            raise StopIteration
        while True:
            try:
                chunk = next(self.response_iterator)
                self.buffer += chunk.decode("utf-8")
            except StopIteration:
                if self.buffer:
                    event_data_str, self.buffer = self.buffer, ""
                    if event_data_str:
                        return self._process_event(event_data_str)
                raise StopIteration

            while "\n\n" in self.buffer:
                event_data_str, self.buffer = self.buffer.split("\n\n", 1)
                return self._process_event(event_data_str)

    def _parse_event_data(self, event_data_str: str) -> Tuple[str, Any]:
        event_lines = event_data_str.strip().split("\n")
        event_type = None
        event_data = ""

        for line in event_lines:
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                event_data = line.split(":", 1)[1].strip()

        if not event_type:
            raise ValueError("Event type not specified in the event data.")

        try:
            parsed_data = json.loads(event_data)
        except json.JSONDecodeError:
            parsed_data = event_data

        # Workaround for service bug: Rename 'expires_at' to 'expired_at'
        if event_type.startswith("thread.run.step") and isinstance(parsed_data, dict) and "expires_at" in parsed_data:
            parsed_data["expired_at"] = parsed_data.pop("expires_at")

        # Map to the appropriate class instance
        if event_type in {
            AgentStreamEvent.THREAD_RUN_CREATED,
            AgentStreamEvent.THREAD_RUN_QUEUED,
            AgentStreamEvent.THREAD_RUN_IN_PROGRESS,
            AgentStreamEvent.THREAD_RUN_REQUIRES_ACTION,
            AgentStreamEvent.THREAD_RUN_COMPLETED,
            AgentStreamEvent.THREAD_RUN_FAILED,
            AgentStreamEvent.THREAD_RUN_CANCELLING,
            AgentStreamEvent.THREAD_RUN_CANCELLED,
            AgentStreamEvent.THREAD_RUN_EXPIRED,
        }:
            event_data_obj = _safe_instantiate(ThreadRun, parsed_data)
        elif event_type in {
            AgentStreamEvent.THREAD_RUN_STEP_CREATED,
            AgentStreamEvent.THREAD_RUN_STEP_IN_PROGRESS,
            AgentStreamEvent.THREAD_RUN_STEP_COMPLETED,
            AgentStreamEvent.THREAD_RUN_STEP_FAILED,
            AgentStreamEvent.THREAD_RUN_STEP_CANCELLED,
            AgentStreamEvent.THREAD_RUN_STEP_EXPIRED,
        }:
            event_data_obj = _safe_instantiate(RunStep, parsed_data)
        elif event_type in {
            AgentStreamEvent.THREAD_MESSAGE_CREATED,
            AgentStreamEvent.THREAD_MESSAGE_IN_PROGRESS,
            AgentStreamEvent.THREAD_MESSAGE_COMPLETED,
            AgentStreamEvent.THREAD_MESSAGE_INCOMPLETE,
        }:
            event_data_obj = _safe_instantiate(ThreadMessage, parsed_data)
        elif event_type == AgentStreamEvent.THREAD_MESSAGE_DELTA:
            event_data_obj = _safe_instantiate(MessageDeltaChunk, parsed_data)
        elif event_type == AgentStreamEvent.THREAD_RUN_STEP_DELTA:
            event_data_obj = _safe_instantiate(RunStepDeltaChunk, parsed_data)
        else:
            event_data_obj = parsed_data

        return event_type, event_data_obj

    def _process_event(self, event_data_str: str) -> Tuple[str, Any]:
        event_type, event_data_obj = self._parse_event_data(event_data_str)

        if (
            isinstance(event_data_obj, ThreadRun)
            and event_data_obj.status == "requires_action"
            and isinstance(event_data_obj.required_action, SubmitToolOutputsAction)
        ):
            self.submit_tool_outputs(event_data_obj, self.event_handler)
        if self.event_handler:
            try:
                if isinstance(event_data_obj, MessageDeltaChunk):
                    self.event_handler.on_message_delta(event_data_obj)
                elif isinstance(event_data_obj, ThreadMessage):
                    self.event_handler.on_thread_message(event_data_obj)
                elif isinstance(event_data_obj, ThreadRun):
                    self.event_handler.on_thread_run(event_data_obj)
                elif isinstance(event_data_obj, RunStep):
                    self.event_handler.on_run_step(event_data_obj)
                elif isinstance(event_data_obj, RunStepDeltaChunk):
                    self.event_handler.on_run_step_delta(event_data_obj)
                elif event_type == AgentStreamEvent.ERROR:
                    self.event_handler.on_error(event_data_obj)
                elif event_type == AgentStreamEvent.DONE:
                    self.event_handler.on_done()
                    self.done = True  # Mark the stream as done
                else:
                    self.event_handler.on_unhandled_event(event_type, event_data_obj)
            except Exception as e:
                logging.error(f"Error in event handler for event '{event_type}': {e}")

        return event_type, event_data_obj

    def until_done(self) -> None:
        """
        Iterates through all events until the stream is marked as done.
        """
        try:
            for _ in self:
                pass  # The EventHandler handles the events
        except StopIteration:
            pass


__all__: List[str] = [
    "AgentEventHandler",
    "AgentRunStream",
    "AsyncAgentEventHandler",
    "AsyncAgentRunStream",
    "AsyncFunctionTool",
    "AsyncToolSet",
    "CodeInterpreterTool",
    "FileSearchTool",
    "BingGroundingTool",
    "AzureAISearchTool",
    "FunctionTool",
    "SASTokenCredential",
    "Tool",
    "ToolSet",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
