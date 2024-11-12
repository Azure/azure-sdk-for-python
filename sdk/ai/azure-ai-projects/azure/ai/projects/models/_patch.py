# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
import base64
import datetime
import inspect
import json
import logging
import math
import re
from abc import ABC, abstractmethod
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
    get_args,
    get_origin,
)

from azure.core.credentials import AccessToken, TokenCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._enums import AgentStreamEvent, ConnectionType
from ._models import (
    AzureAISearchResource,
    AzureAISearchToolDefinition,
    BingGroundingToolDefinition,
    CodeInterpreterToolDefinition,
    CodeInterpreterToolResource,
    FileSearchToolDefinition,
    FileSearchToolResource,
    FunctionDefinition,
    FunctionToolDefinition,
    GetConnectionResponse,
    IndexResource,
    MessageDeltaChunk,
    MessageImageFileContent,
    MessageTextContent,
    MessageTextFileCitationAnnotation,
    MessageTextFilePathAnnotation,
    OpenAIPageableListOfThreadMessage,
    RequiredFunctionToolCall,
    RunStep,
    RunStepDeltaChunk,
    SharepointToolDefinition,
    SubmitToolOutputsAction,
    ThreadMessage,
    ThreadRun,
    ToolConnection,
    ToolConnectionList,
    ToolDefinition,
    ToolResources,
)

logger = logging.getLogger(__name__)


StreamEventData = Union[MessageDeltaChunk, ThreadMessage, ThreadRun, RunStep, None]


def _filter_parameters(model_class: Type, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove the parameters, non present in class public fields; return shallow copy of a dictionary.

    **Note:** Classes inherited from the model check that the parameters are present
    in the list of attributes and if they are not, the error is being raised. This check may not
    be relevant for classes, not inherited from azure.ai.projects._model_base.Model.
    :param Type model_class: The class of model to be used.
    :param parameters: The parsed dictionary with parameters.
    :type parameters: Union[str, Dict[str, Any]]
    :return: The dictionary with all invalid parameters removed.
    :rtype: Dict[str, Any]
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


def _safe_instantiate(model_class: Type, parameters: Union[str, Dict[str, Any]]) -> Union[str, StreamEventData]:
    """
    Instantiate class with the set of parameters from the server.

    :param Type model_class: The class of model to be used.
    :param parameters: The parsed dictionary with parameters.
    :type parameters: Union[str, Dict[str, Any]]
    :return: The class of model_class type if parameters is a dictionary, or the parameters themselves otherwise.
    :rtype: Any
    """
    if not isinstance(parameters, dict):
        return parameters
    return cast(StreamEventData, model_class(**_filter_parameters(model_class, parameters)))


class ConnectionProperties:
    """The properties of a single connection.

    :ivar id: A unique identifier for the connection.
    :vartype id: str
    :ivar name: The friendly name of the connection.
    :vartype name: str
    :ivar authentication_type: The authentication type used by the connection.
    :vartype authentication_type: ~azure.ai.projects.models._models.AuthenticationType
    :ivar connection_type: The connection type .
    :vartype connection_type: ~azure.ai.projects.models._models.ConnectionType
    :ivar endpoint_url: The endpoint URL associated with this connection
    :vartype endpoint_url: str
    :ivar key: The api-key to be used when accessing the connection.
    :vartype key: str
    :ivar token_credential: The TokenCredential to be used when accessing the connection.
    :vartype token_credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(
        self,
        *,
        connection: GetConnectionResponse,
        token_credential: Union[TokenCredential, AsyncTokenCredential, None] = None,
    ) -> None:
        self.id = connection.id
        self.name = connection.name
        self.authentication_type = connection.properties.auth_type
        self.connection_type = cast(ConnectionType, connection.properties.category)
        self.endpoint_url = (
            connection.properties.target[:-1]
            if connection.properties.target.endswith("/")
            else connection.properties.target
        )
        self.key: Optional[str] = None
        if hasattr(connection.properties, "credentials"):
            if hasattr(connection.properties.credentials, "key"):  # type: ignore
                self.key = connection.properties.credentials.key  # type: ignore
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
            out += ' "key": "REDACTED"\n'
        else:
            out += ' "key": null\n'
        if self.token_credential:
            out += ' "token_credential": "REDACTED"\n'
        else:
            out += ' "token_credential": null\n'
        out += "}\n"
        return out


# TODO: Look into adding an async version of this class
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
    def _get_expiration_date_from_token(cls, jwt_token: str) -> datetime.datetime:
        payload = jwt_token.split(".")[1]
        padded_payload = payload + "=" * (4 - len(payload) % 4)  # Add padding if necessary
        decoded_bytes = base64.urlsafe_b64decode(padded_payload)
        decoded_str = decoded_bytes.decode("utf-8")
        decoded_payload = json.loads(decoded_str)
        expiration_date = decoded_payload.get("exp")
        return datetime.datetime.fromtimestamp(expiration_date, datetime.timezone.utc)

    def _refresh_token(self) -> None:
        logger.debug("[SASTokenCredential._refresh_token] Enter")
        from azure.ai.projects import AIProjectClient

        project_client = AIProjectClient(
            credential=self._credential,
            # Since we are only going to use the "connections" operations, we don't need to supply an endpoint.
            # http://management.azure.com is hard coded in the SDK.
            endpoint="not-needed",
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            project_name=self._project_name,
        )

        connection = project_client.connections.get(connection_name=self._connection_name, with_credentials=True)

        self._sas_token = ""
        if connection is not None and connection.token_credential is not None:
            sas_credential = cast(SASTokenCredential, connection.token_credential)
            self._sas_token = sas_credential._sas_token
        self._expires_on = SASTokenCredential._get_expiration_date_from_token(self._sas_token)
        logger.debug("[SASTokenCredential._refresh_token] Exit. New token expires on %s.", self._expires_on)

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Request an access token for `scopes`.

        :param str scopes: The type of access needed.

        :keyword str claims: Additional claims required in the token, such as those returned in a resource
            provider's claims challenge following an authorization failure.
        :keyword str tenant_id: Optional tenant to include in the token request.
        :keyword bool enable_cae: Indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Defaults to False.

        :rtype: AccessToken
        :return: An AccessToken instance containing the token string and its expiration time in Unix time.
        """
        logger.debug("SASTokenCredential.get_token] Enter")
        if self._expires_on < datetime.datetime.now(datetime.timezone.utc):
            self._refresh_token()
        return AccessToken(self._sas_token, math.floor(self._expires_on.timestamp()))


# Define type_map to translate Python type annotations to JSON Schema types
type_map = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "NoneType": "null",
    "list": "array",
    "dict": "object",
}


def _map_type(annotation) -> Dict[str, Any]:
    if annotation == inspect.Parameter.empty:
        return {"type": "string"}  # Default type if annotation is missing

    origin = get_origin(annotation)

    if origin in {list, List}:
        args = get_args(annotation)
        item_type = args[0] if args else str
        return {"type": "array", "items": _map_type(item_type)}
    if origin in {dict, Dict}:
        return {"type": "object"}
    if origin is Union:
        args = get_args(annotation)
        # If Union contains None, it is an optional parameter
        if type(None) in args:
            # If Union contains only one non-None type, it is a nullable parameter
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                schema = _map_type(non_none_args[0])
                if "type" in schema:
                    if isinstance(schema["type"], str):
                        schema["type"] = [schema["type"], "null"]
                    elif "null" not in schema["type"]:
                        schema["type"].append("null")
                else:
                    schema["type"] = ["null"]
                return schema
        # If Union contains multiple types, it is a oneOf parameter
        return {"oneOf": [_map_type(arg) for arg in args]}
    if isinstance(annotation, type):
        schema_type = type_map.get(annotation.__name__, "string")
        return {"type": schema_type}

    return {"type": "string"}  # Fallback to "string" if type is unrecognized


def is_optional(annotation) -> bool:
    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        return type(None) in args
    return False


class Tool(ABC):
    """
    An abstract class representing a tool that can be used by an agent.
    """

    @property
    @abstractmethod
    def definitions(self) -> List[ToolDefinition]:
        """Get the tool definitions."""

    @property
    @abstractmethod
    def resources(self) -> ToolResources:
        """Get the tool resources."""

    @abstractmethod
    def execute(self, tool_call: Any) -> Any:
        """
        Execute the tool with the provided tool call.

        :param Any tool_call: The tool call to execute.
        :return: The output of the tool operations.
        """


class BaseFunctionTool(Tool):
    """
    A tool that executes user-defined functions.
    """

    def __init__(self, functions: Set[Callable[..., Any]]):
        """
        Initialize FunctionTool with a set of functions.

        :param functions: A set of function objects.
        """
        self._functions = self._create_function_dict(functions)
        self._definitions = self._build_function_definitions(self._functions)

    def _create_function_dict(self, functions: Set[Callable[..., Any]]) -> Dict[str, Callable[..., Any]]:
        return {func.__name__: func for func in functions}

    def _build_function_definitions(self, functions: Dict[str, Any]) -> List[FunctionToolDefinition]:
        specs: List[FunctionToolDefinition] = []
        # Flexible regex to capture ':param <name>: <description>'
        param_pattern = re.compile(
            r"""
            ^\s*                                   # Optional leading whitespace
            :param                                 # Literal ':param'
            \s+                                    # At least one whitespace character
            (?P<name>[^:\s\(\)]+)                  # Parameter name (no spaces, colons, or parentheses)
            (?:\s*\(\s*(?P<type>[^)]+?)\s*\))?     # Optional type in parentheses, allowing internal spaces
            \s*:\s*                                # Colon ':' surrounded by optional whitespace
            (?P<description>.+)                    # Description (rest of the line)
            """,
            re.VERBOSE,
        )

        for name, func in functions.items():
            sig = inspect.signature(func)
            params = sig.parameters
            docstring = inspect.getdoc(func) or ""
            description = docstring.split("\n", maxsplit=1)[0] if docstring else "No description"

            param_descriptions = {}
            for line in docstring.splitlines():
                line = line.strip()
                match = param_pattern.match(line)
                if match:
                    groups = match.groupdict()
                    param_name = groups.get("name")
                    param_desc = groups.get("description")
                    param_desc = param_desc.strip() if param_desc else "No description"
                    param_descriptions[param_name] = param_desc.strip()

            properties = {}
            required = []
            for param_name, param in params.items():
                param_type_info = _map_type(param.annotation)
                param_description = param_descriptions.get(param_name, "No description")

                properties[param_name] = {**param_type_info, "description": param_description}

                # If the parameter has no default value and is not optional, add it to the required list
                if param.default is inspect.Parameter.empty and not is_optional(param.annotation):
                    required.append(param_name)

            function_def = FunctionDefinition(
                name=name,
                description=description,
                parameters={"type": "object", "properties": properties, "required": required},
            )
            tool_def = FunctionToolDefinition(function=function_def)
            specs.append(tool_def)

        return specs

    def _get_func_and_args(self, tool_call: RequiredFunctionToolCall) -> Tuple[Any, Dict[str, Any]]:
        function_name = tool_call.function.name
        arguments = tool_call.function.arguments

        if function_name not in self._functions:
            logging.error("Function '%s' not found.", function_name)
            raise ValueError(f"Function '{function_name}' not found.")

        function = self._functions[function_name]

        try:
            parsed_arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            logging.error("Invalid JSON arguments for function '%s': %s", function_name, e)
            raise ValueError(f"Invalid JSON arguments: {e}") from e

        if not isinstance(parsed_arguments, dict):
            logging.error("Arguments must be a JSON object for function '%s'.", function_name)
            raise TypeError("Arguments must be a JSON object.")

        return function, parsed_arguments

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the function definitions.

        :return: A list of function definitions.
        :rtype: List[ToolDefinition]
        """
        return cast(List[ToolDefinition], self._definitions)

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources for the agent.

        :return: An empty ToolResources as FunctionTool doesn't have specific resources.
        :rtype: ToolResources
        """
        return ToolResources()


class FunctionTool(BaseFunctionTool):

    def execute(self, tool_call: RequiredFunctionToolCall) -> Any:
        function, parsed_arguments = self._get_func_and_args(tool_call)

        try:
            return function(**parsed_arguments) if parsed_arguments else function()
        except TypeError as e:
            error_message = f"Error executing function '{tool_call.function.name}': {e}"
            logging.error(error_message)
            # Return error message as JSON string back to agent in order to make possible self
            # correction to the function call
            return json.dumps({"error": error_message})


class AsyncFunctionTool(BaseFunctionTool):

    async def execute(self, tool_call: RequiredFunctionToolCall) -> Any:
        function, parsed_arguments = self._get_func_and_args(tool_call)

        try:
            if inspect.iscoroutinefunction(function):
                return await function(**parsed_arguments) if parsed_arguments else await function()
            return function(**parsed_arguments) if parsed_arguments else function()
        except TypeError as e:
            error_message = f"Error executing function '{tool_call.function.name}': {e}"
            logging.error(error_message)
            # Return error message as JSON string back to agent in order to make possible self correction
            # to the function call
            return json.dumps({"error": error_message})


class AzureAISearchTool(Tool):
    """
    A tool that searches for information using Azure AI Search.
    """

    def __init__(self):
        self.index_list = []

    def add_index(self, index: str, name: str):
        """
        Add an index ID to the list of indices used to search.

        :param str index: The index connection id.
        :param str name: The index name.
        """
        # TODO
        self.index_list.append(IndexResource(index_connection_id=index, index_name=name))

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the Azure AI search tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [AzureAISearchToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the Azure AI search resources.

        :rtype: ToolResources
        """
        return ToolResources(azure_ai_search=AzureAISearchResource(index_list=self.index_list))

    def execute(self, tool_call: Any) -> Any:
        pass


class ConnectionTool(Tool):
    """
    A tool that requires connection ids.
    Used as base class for Bing Grounding, Sharepoint, and Microsoft Fabric
    """

    def __init__(self, connection_id: str):
        """
        Initialize ConnectionTool with a connection_id.

        :param connection_id: Connection ID used by tool. All connection tools allow only one connection.
        """
        self.connection_ids = [ToolConnection(connection_id=connection_id)]

    @property
    def resources(self) -> ToolResources:
        """
        Get the connection tool resources.

        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> Any:
        pass


class BingGroundingTool(ConnectionTool):
    """
    A tool that searches for information using Bing.
    """

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the Bing grounding tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [BingGroundingToolDefinition(bing_grounding=ToolConnectionList(connection_list=self.connection_ids))]


class SharepointTool(ConnectionTool):
    """
    A tool that searches for information using Sharepoint.
    """

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the Sharepoint tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [SharepointToolDefinition(sharepoint_grounding=ToolConnectionList(connection_list=self.connection_ids))]


class FileSearchTool(Tool):
    """
    A tool that searches for uploaded file information from the created vector stores.

    :param vector_store_ids: A list of vector store IDs to search for files.
    :type vector_store_ids: list[str]
    """

    def __init__(self, vector_store_ids: Optional[List[str]] = None):
        if vector_store_ids is None:
            self.vector_store_ids = set()
        else:
            self.vector_store_ids = set(vector_store_ids)

    def add_vector_store(self, store_id: str) -> None:
        """
        Add a vector store ID to the list of vector stores to search for files.

        :param store_id: The ID of the vector store to search for files.
        :type store_id: str

        """
        self.vector_store_ids.add(store_id)

    def remove_vector_store(self, store_id: str) -> None:
        """
        Remove a vector store ID from the list of vector stores to search for files.

        :param store_id: The ID of the vector store to remove.
        :type store_id: str

        """
        self.vector_store_ids.remove(store_id)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the file search tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [FileSearchToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the file search resources.

        :rtype: ToolResources
        """
        return ToolResources(file_search=FileSearchToolResource(vector_store_ids=list(self.vector_store_ids)))

    def execute(self, tool_call: Any) -> Any:
        pass


class CodeInterpreterTool(Tool):
    """
    A tool that interprets code files uploaded to the agent.

    :param file_ids: A list of file IDs to interpret.
    :type file_ids: list[str]
    """

    def __init__(self, file_ids: Optional[List[str]] = None):
        if file_ids is None:
            self.file_ids = set()
        else:
            self.file_ids = set(file_ids)

    def add_file(self, file_id: str) -> None:
        """
        Add a file ID to the list of files to interpret.

        :param file_id: The ID of the file to interpret.
        :type file_id: str
        """
        self.file_ids.add(file_id)

    def remove_file(self, file_id: str) -> None:
        """
        Remove a file ID from the list of files to interpret.

        :param file_id: The ID of the file to remove.
        :type file_id: str
        """
        self.file_ids.remove(file_id)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the code interpreter tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [CodeInterpreterToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the code interpreter resources.

        :rtype: ToolResources
        """
        if not self.file_ids:
            return ToolResources()
        return ToolResources(code_interpreter=CodeInterpreterToolResource(file_ids=list(self.file_ids)))

    def execute(self, tool_call: Any) -> Any:
        pass


class BaseToolSet:
    """
    Abstract class for a collection of tools that can be used by an agent.
    """

    def __init__(self) -> None:
        self._tools: List[Tool] = []

    def validate_tool_type(self, tool: Tool) -> None:
        pass

    def add(self, tool: Tool):
        """
        Add a tool to the tool set.

        :param Tool tool: The tool to add.
        :raises ValueError: If a tool of the same type already exists.
        """
        self.validate_tool_type(tool)

        if any(isinstance(existing_tool, type(tool)) for existing_tool in self._tools):
            raise ValueError("Tool of type {type(tool).__name__} already exists in the ToolSet.")
        self._tools.append(tool)

    def remove(self, tool_type: Type[Tool]) -> None:
        """
        Remove a tool of the specified type from the tool set.

        :param Type[Tool] tool_type: The type of tool to remove.
        :raises ValueError: If a tool of the specified type is not found.
        """
        for i, tool in enumerate(self._tools):
            if isinstance(tool, tool_type):
                del self._tools[i]
                logging.info("Tool of type %s removed from the ToolSet.", tool_type.__name__)
                return
        raise ValueError(f"Tool of type {tool_type.__name__} not found in the ToolSet.")

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the definitions for all tools in the tool set.

        :rtype: List[ToolDefinition]
        """
        tools = []
        for tool in self._tools:
            tools.extend(tool.definitions)
        return tools

    @property
    def resources(self) -> ToolResources:
        """
        Get the resources for all tools in the tool set.

        :rtype: ToolResources
        """
        tool_resources: Dict[str, Any] = {}
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

        :param resources: A dictionary of tool resources. Should be a mapping
            accepted by ~azure.ai.projects.models.AzureAISearchResource
        :type resources: Dict[str, Any]
        :return: A ToolResources instance.
        :rtype: ToolResources
        """
        try:
            return ToolResources(**resources)
        except TypeError as e:
            logging.error("Error creating ToolResources: %s", e)
            raise ValueError("Invalid resources for ToolResources.") from e

    def get_definitions_and_resources(self) -> Dict[str, Any]:
        """
        Get the definitions and resources for all tools in the tool set.

        :return: A dictionary containing the tool resources and definitions.
        :rtype: Dict[str, Any]
        """
        return {
            "tool_resources": self.resources,
            "tools": self.definitions,
        }

    def get_tool(self, tool_type: Type[Tool]) -> Tool:
        """
        Get a tool of the specified type from the tool set.

        :param Type[Tool] tool_type: The type of tool to get.
        :return: The tool of the specified type.
        :rtype: Tool
        :raises ValueError: If a tool of the specified type is not found.
        """
        for tool in self._tools:
            if isinstance(tool, tool_type):
                return tool
        raise ValueError(f"Tool of type {tool_type.__name__} not found.")


class ToolSet(BaseToolSet):
    """
    A collection of tools that can be used by an synchronize agent.
    """

    def validate_tool_type(self, tool: Tool) -> None:
        """
        Validate the type of the tool.

        :param Tool tool: The type of the tool to validate.
        :raises ValueError: If the tool type is not a subclass of Tool.
        """
        if isinstance(tool, AsyncFunctionTool):
            raise ValueError(
                "AsyncFunctionTool is not supported in ToolSet.  "
                + "To use async functions, use AsyncToolSet and agents operations in azure.ai.projects.aio."
            )

    def execute_tool_calls(self, tool_calls: List[Any]) -> Any:
        """
        Execute a tool of the specified type with the provided tool calls.

        :param List[Any] tool_calls: A list of tool calls to execute.
        :return: The output of the tool operations.
        :rtype: Any
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
                logging.error("Failed to execute tool call %s: %s", tool_call, e)

        return tool_outputs


class AsyncToolSet(BaseToolSet):
    """
    A collection of tools that can be used by an asynchronous agent.
    """

    def validate_tool_type(self, tool: Tool) -> None:
        """
        Validate the type of the tool.

        :param Tool tool: The type of the tool to validate.
        :raises ValueError: If the tool type is not a subclass of Tool.
        """
        if isinstance(tool, FunctionTool):
            raise ValueError(
                "FunctionTool is not supported in AsyncToolSet.  "
                + "Please use AsyncFunctionTool instead and provide sync and/or async function(s)."
            )

    async def execute_tool_calls(self, tool_calls: List[Any]) -> Any:
        """
        Execute a tool of the specified type with the provided tool calls.

        :param List[Any] tool_calls: A list of tool calls to execute.
        :return: The output of the tool operations.
        :rtype: Any
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
                logging.error("Failed to execute tool call %s: %s", tool_call, e)

        return tool_outputs


class AgentEventHandler:

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        """Handle message delta events.

        :param MessageDeltaChunk delta: The message delta.
        """

    def on_thread_message(self, message: "ThreadMessage") -> None:
        """Handle thread message events.

        :param ThreadMessage message: The thread message.
        """

    def on_thread_run(self, run: "ThreadRun") -> None:
        """Handle thread run events.

        :param ThreadRun run: The thread run.
        """

    def on_run_step(self, step: "RunStep") -> None:
        """Handle run step events.

        :param RunStep step: The run step.
        """

    def on_run_step_delta(self, delta: "RunStepDeltaChunk") -> None:
        """Handle run step delta events.

        :param RunStepDeltaChunk delta: The run step delta.
        """

    def on_error(self, data: str) -> None:
        """Handle error events.

        :param str data: The error event's data.
        """

    def on_done(self) -> None:
        """Handle the completion of the stream."""

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        """Handle any unhandled event types.

        :param str event_type: The event type.
        :param Any event_data: The event's data.
        """


class AsyncAgentEventHandler:

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        """Handle message delta events.

        :param MessageDeltaChunk delta: The message delta.
        """

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        """Handle thread message events.

        :param ThreadMessage message: The thread message.
        """

    async def on_thread_run(self, run: "ThreadRun") -> None:
        """Handle thread run events.

        :param ThreadRun run: The thread run.
        """

    async def on_run_step(self, step: "RunStep") -> None:
        """Handle run step events.

        :param RunStep step: The run step.
        """

    async def on_run_step_delta(self, delta: "RunStepDeltaChunk") -> None:
        """Handle run step delta events.

        :param RunStepDeltaChunk delta: The run step delta.
        """

    async def on_error(self, data: str) -> None:
        """Handle error events.

        :param str data: The error event's data.
        """

    async def on_done(self) -> None:
        """Handle the completion of the stream."""

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        """Handle any unhandled event types.

        :param str event_type: The event type.
        :param Any event_data: The event's data.
        """


class AsyncAgentRunStream(AsyncIterator[Tuple[str, Union[str, StreamEventData]]]):
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

    async def __anext__(self) -> Tuple[str, Union[str, StreamEventData]]:
        while True:
            try:
                chunk = await self.response_iterator.__anext__()
                self.buffer += chunk.decode("utf-8")
            except StopAsyncIteration:
                if self.buffer:
                    event_data_str, self.buffer = self.buffer, ""
                    if event_data_str:
                        return await self._process_event(event_data_str)
                raise

            while "\n\n" in self.buffer:
                event_data_str, self.buffer = self.buffer.split("\n\n", 1)
                return await self._process_event(event_data_str)

    def _parse_event_data(self, event_data_str: str) -> Tuple[str, Union[str, StreamEventData], str]:
        event_lines = event_data_str.strip().split("\n")
        event_type: Optional[str] = None
        event_data = ""
        error_string = ""

        for line in event_lines:
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                event_data = line.split(":", 1)[1].strip()

        if not event_type:
            raise ValueError("Event type not specified in the event data.")

        try:
            parsed_data: Union[str, Dict[str, StreamEventData]] = cast(
                Dict[str, StreamEventData], json.loads(event_data)
            )
        except json.JSONDecodeError:
            parsed_data = event_data

        # Workaround for service bug: Rename 'expires_at' to 'expired_at'
        if event_type.startswith("thread.run.step") and isinstance(parsed_data, dict) and "expires_at" in parsed_data:
            parsed_data["expired_at"] = parsed_data.pop("expires_at")

        # Map to the appropriate class instance
        if event_type in {
            AgentStreamEvent.THREAD_RUN_CREATED.value,
            AgentStreamEvent.THREAD_RUN_QUEUED.value,
            AgentStreamEvent.THREAD_RUN_IN_PROGRESS.value,
            AgentStreamEvent.THREAD_RUN_REQUIRES_ACTION.value,
            AgentStreamEvent.THREAD_RUN_COMPLETED.value,
            AgentStreamEvent.THREAD_RUN_FAILED.value,
            AgentStreamEvent.THREAD_RUN_CANCELLING.value,
            AgentStreamEvent.THREAD_RUN_CANCELLED.value,
            AgentStreamEvent.THREAD_RUN_EXPIRED.value,
        }:
            event_data_obj = _safe_instantiate(ThreadRun, parsed_data)
        elif event_type in {
            AgentStreamEvent.THREAD_RUN_STEP_CREATED.value,
            AgentStreamEvent.THREAD_RUN_STEP_IN_PROGRESS.value,
            AgentStreamEvent.THREAD_RUN_STEP_COMPLETED.value,
            AgentStreamEvent.THREAD_RUN_STEP_FAILED.value,
            AgentStreamEvent.THREAD_RUN_STEP_CANCELLED.value,
            AgentStreamEvent.THREAD_RUN_STEP_EXPIRED.value,
        }:
            event_data_obj = _safe_instantiate(RunStep, parsed_data)
        elif event_type in {
            AgentStreamEvent.THREAD_MESSAGE_CREATED.value,
            AgentStreamEvent.THREAD_MESSAGE_IN_PROGRESS.value,
            AgentStreamEvent.THREAD_MESSAGE_COMPLETED.value,
            AgentStreamEvent.THREAD_MESSAGE_INCOMPLETE.value,
        }:
            event_data_obj = _safe_instantiate(ThreadMessage, parsed_data)
        elif event_type == AgentStreamEvent.THREAD_MESSAGE_DELTA.value:
            event_data_obj = _safe_instantiate(MessageDeltaChunk, parsed_data)
        elif event_type == AgentStreamEvent.THREAD_RUN_STEP_DELTA.value:
            event_data_obj = _safe_instantiate(RunStepDeltaChunk, parsed_data)
        else:
            event_data_obj = ""
            error_string = str(parsed_data)

        return event_type, event_data_obj, error_string

    async def _process_event(self, event_data_str: str) -> Tuple[str, Union[str, StreamEventData]]:
        event_type, event_data_obj, error_string = self._parse_event_data(event_data_str)

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
                    await self.event_handler.on_error(error_string)
                elif event_type == AgentStreamEvent.DONE:
                    await self.event_handler.on_done()
                    self.done = True  # Mark the stream as done
                else:
                    await self.event_handler.on_unhandled_event(event_type, event_data_obj)
            except Exception as e:
                logging.error("Error in event handler for event '%s': %s", event_type, e)

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


class AgentRunStream(Iterator[Tuple[str, Union[str, StreamEventData]]]):
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

    def __next__(self) -> Tuple[str, Union[str, StreamEventData]]:
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
                raise

            while "\n\n" in self.buffer:
                event_data_str, self.buffer = self.buffer.split("\n\n", 1)
                return self._process_event(event_data_str)

    def _parse_event_data(self, event_data_str: str) -> Tuple[str, Union[str, StreamEventData], str]:
        event_lines = event_data_str.strip().split("\n")
        event_type = None
        event_data = ""
        error_string = ""

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
            AgentStreamEvent.THREAD_RUN_CREATED.value,
            AgentStreamEvent.THREAD_RUN_QUEUED.value,
            AgentStreamEvent.THREAD_RUN_IN_PROGRESS.value,
            AgentStreamEvent.THREAD_RUN_REQUIRES_ACTION.value,
            AgentStreamEvent.THREAD_RUN_COMPLETED.value,
            AgentStreamEvent.THREAD_RUN_FAILED.value,
            AgentStreamEvent.THREAD_RUN_CANCELLING.value,
            AgentStreamEvent.THREAD_RUN_CANCELLED.value,
            AgentStreamEvent.THREAD_RUN_EXPIRED.value,
        }:
            event_data_obj = _safe_instantiate(ThreadRun, parsed_data)
        elif event_type in {
            AgentStreamEvent.THREAD_RUN_STEP_CREATED.value,
            AgentStreamEvent.THREAD_RUN_STEP_IN_PROGRESS.value,
            AgentStreamEvent.THREAD_RUN_STEP_COMPLETED.value,
            AgentStreamEvent.THREAD_RUN_STEP_FAILED.value,
            AgentStreamEvent.THREAD_RUN_STEP_CANCELLED.value,
            AgentStreamEvent.THREAD_RUN_STEP_EXPIRED.value,
        }:
            event_data_obj = _safe_instantiate(RunStep, parsed_data)
        elif event_type in {
            AgentStreamEvent.THREAD_MESSAGE_CREATED.value,
            AgentStreamEvent.THREAD_MESSAGE_IN_PROGRESS.value,
            AgentStreamEvent.THREAD_MESSAGE_COMPLETED.value,
            AgentStreamEvent.THREAD_MESSAGE_INCOMPLETE.value,
        }:
            event_data_obj = _safe_instantiate(ThreadMessage, parsed_data)
        elif event_type == AgentStreamEvent.THREAD_MESSAGE_DELTA.value:
            event_data_obj = _safe_instantiate(MessageDeltaChunk, parsed_data)
        elif event_type == AgentStreamEvent.THREAD_RUN_STEP_DELTA.value:
            event_data_obj = _safe_instantiate(RunStepDeltaChunk, parsed_data)
        else:
            event_data_obj = ""
            error_string = str(parsed_data)

        return event_type, event_data_obj, error_string

    def _process_event(self, event_data_str: str) -> Tuple[str, Union[str, StreamEventData]]:
        event_type, event_data_obj, error_string = self._parse_event_data(event_data_str)

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
                    self.event_handler.on_error(error_string)
                elif event_type == AgentStreamEvent.DONE:
                    self.event_handler.on_done()
                    self.done = True  # Mark the stream as done
                else:
                    self.event_handler.on_unhandled_event(event_type, event_data_obj)
            except Exception as e:
                logging.error("Error in event handler for event '%s': %s", event_type, e)

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


class ThreadMessages:
    """
    Represents a collection of messages in a thread.

    :param pageable_list: The pageable list of messages.
    :type pageable_list: ~azure.ai.projects.models.OpenAIPageableListOfThreadMessage

    :return: A collection of messages.
    :rtype: ~azure.ai.projects.models.ThreadMessages
    """

    def __init__(self, pageable_list: OpenAIPageableListOfThreadMessage):
        self._messages = pageable_list.data

    @property
    def messages(self) -> List[ThreadMessage]:
        """Returns all messages in the messages.


        :rtype: List[ThreadMessage]
        """
        return self._messages

    @property
    def text_messages(self) -> List[MessageTextContent]:
        """Returns all text message contents in the messages.

        :rtype: List[MessageTextContent]
        """
        texts = [
            content for msg in self._messages for content in msg.content if isinstance(content, MessageTextContent)
        ]
        return texts

    @property
    def image_contents(self) -> List[MessageImageFileContent]:
        """Returns all image file contents from image message contents in the messages.

        :rtype: List[MessageImageFileContent]
        """
        return [
            content for msg in self._messages for content in msg.content if isinstance(content, MessageImageFileContent)
        ]

    @property
    def file_citation_annotations(self) -> List[MessageTextFileCitationAnnotation]:
        """Returns all file citation annotations from text message annotations in the messages.

        :rtype: List[MessageTextFileCitationAnnotation]
        """
        annotations = [
            annotation
            for msg in self._messages
            for content in msg.content
            if isinstance(content, MessageTextContent)
            for annotation in content.text.annotations
            if isinstance(annotation, MessageTextFileCitationAnnotation)
        ]
        return annotations

    @property
    def file_path_annotations(self) -> List[MessageTextFilePathAnnotation]:
        """Returns all file path annotations from text message annotations in the messages.

        :rtype: List[MessageTextFilePathAnnotation]
        """
        annotations = [
            annotation
            for msg in self._messages
            for content in msg.content
            if isinstance(content, MessageTextContent)
            for annotation in content.text.annotations
            if isinstance(annotation, MessageTextFilePathAnnotation)
        ]
        return annotations

    def get_last_message_by_sender(self, sender: str) -> Optional[ThreadMessage]:
        """Returns the last message from the specified sender.

        :param sender: The role of the sender.
        :type sender: str

        :return: The last message from the specified sender.
        :rtype: ~azure.ai.projects.models.ThreadMessage
        """
        for msg in self._messages:
            if msg.role == sender:
                return msg
        return None

    def get_last_text_message_by_sender(self, sender: str) -> Optional[MessageTextContent]:
        """Returns the last text message from the specified sender.

        :param sender: The role of the sender.
        :type sender: str

        :return: The last text message from the specified sender.
        :rtype: ~azure.ai.projects.models.MessageTextContent
        """
        for msg in self._messages:
            if msg.role == sender:
                for content in msg.content:
                    if isinstance(content, MessageTextContent):
                        return content
        return None


__all__: List[str] = [
    "AgentEventHandler",
    "AgentRunStream",
    "AsyncAgentEventHandler",
    "AsyncAgentRunStream",
    "AsyncFunctionTool",
    "AsyncToolSet",
    "CodeInterpreterTool",
    "ConnectionProperties",
    "ThreadMessages",
    "FileSearchTool",
    "FunctionTool",
    "BingGroundingTool",
    "SharepointTool",
    "AzureAISearchTool",
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
