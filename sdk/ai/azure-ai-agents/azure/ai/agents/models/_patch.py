# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio  # pylint: disable = do-not-import-asyncio
import inspect
import itertools
import json
import logging
import re
from abc import ABC, abstractmethod
import time
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    TYPE_CHECKING,
    cast,
    get_args,
    get_origin,
    overload,
)

from ._enums import AgentStreamEvent, AzureAISearchQueryType, RunStatus
from ._models import (
    AISearchIndexResource,
    AzureAISearchToolResource,
    AzureAISearchToolDefinition,
    AzureFunctionDefinition,
    AzureFunctionStorageQueue,
    AzureFunctionToolDefinition,
    AzureFunctionBinding,
    BingGroundingToolDefinition,
    BrowserAutomationToolConnectionParameters,
    BrowserAutomationToolDefinition,
    BrowserAutomationToolParameters,
    CodeInterpreterToolDefinition,
    CodeInterpreterToolResource,
    ConnectedAgentToolDefinition,
    ConnectedAgentDetails,
    ComputerUseToolDefinition,
    ComputerUseToolParameters,
    FileSearchToolDefinition,
    FileSearchToolResource,
    FunctionDefinition,
    FunctionToolDefinition,
    MCPToolDefinition,
    MCPToolResource,
    MessageImageFileContent,
    MessageTextContent,
    MessageTextFileCitationAnnotation,
    MessageTextUrlCitationAnnotation,
    MessageTextFilePathAnnotation,
    OpenApiAuthDetails,
    OpenApiToolDefinition,
    OpenApiFunctionDefinition,
    RequiredFunctionToolCall,
    RunStep,
    RunStepDeltaChunk,
    DeepResearchToolDefinition,
    DeepResearchDetails,
    DeepResearchBingGroundingConnection,
    BingGroundingSearchConfiguration,
    BingGroundingSearchToolParameters,
    BingCustomSearchToolDefinition,
    BingCustomSearchConfiguration,
    BingCustomSearchToolParameters,
    SharepointToolDefinition,
    SharepointGroundingToolParameters,
    ToolApproval,
    ToolConnection,
    MicrosoftFabricToolDefinition,
    FabricDataAgentToolParameters,
    SubmitToolOutputsAction,
    ThreadRun,
    ToolDefinition,
    ToolResources,
    MessageDeltaTextContent,
    VectorStoreDataSource,
    SubmitToolApprovalAction,
    RequiredMcpToolCall,
    RequiredFunctionToolCallDetails,
)

from ._models import MessageDeltaChunk as MessageDeltaChunkGenerated
from ._models import ThreadMessage as ThreadMessageGenerated
from ._models import MessageAttachment as MessageAttachmentGenerated

from .. import types as _types


# NOTE: Avoid importing RunsOperations here to prevent circular import with operations package.


if TYPE_CHECKING:
    from ..operations import RunsOperations
    from aio.operations import RunsOperations as AsyncRunsOperations


logger = logging.getLogger(__name__)

StreamEventData = Union["RunStepDeltaChunk", "MessageDeltaChunk", "ThreadMessage", ThreadRun, RunStep, str]


def get_tool_resources(tools: List["Tool"]) -> ToolResources:
    """
    Get the tool resources from tools.

    :param tools: The list of tool objects whose resources should be merged.
    :type tools: List[Tool]
    :return: A new ``ToolResources`` instance representing the merged view.
    :rtype: ToolResources
    """
    tool_resources: Dict[str, Any] = {}
    for tool in tools:
        resources = tool.resources
        for key, value in resources.items():
            if key in tool_resources:
                # Special handling for MCP resources - they need to be merged into a single list
                if isinstance(tool_resources[key], list) and isinstance(value, list):
                    tool_resources[key].extend(value)
                elif isinstance(tool_resources[key], dict) and isinstance(value, dict):
                    tool_resources[key].update(value)
                else:
                    # For other types, the new value overwrites the old one
                    tool_resources[key] = value
            else:
                tool_resources[key] = value
    return _create_tool_resources_from_dict(tool_resources)


def get_tool_definitions(tools: List["Tool"]) -> List[ToolDefinition]:
    """
    Get the tool definitions from tools.

    :param tools: Tools from which to collect definitions.
    :type tools: List[Tool]
    :return: List of collected tool definitions.
    :rtype: List[ToolDefinition]
    """
    return [definition for tool in tools for definition in tool.definitions]


def _create_tool_resources_from_dict(resources: Dict[str, Any]) -> ToolResources:
    """
    Safely converts a dictionary into a ToolResources instance.

    :param resources: A dictionary of tool resources. Should be a mapping
        accepted by ~azure.ai.agents.models.AzureAISearchToolResource
    :type resources: Dict[str, Any]
    :return: A ToolResources instance.
    :rtype: ToolResources
    """
    try:
        return ToolResources(**resources)
    except TypeError as e:
        logger.error("Error creating ToolResources: %s", e)  # pylint: disable=do-not-log-exceptions-if-not-debug
        raise ValueError("Invalid resources for ToolResources.") from e


def _has_errors_in_toolcalls_output(tool_outputs: List[Dict]) -> bool:
    """
    Check if any tool output contains an error.

    :param List[Dict] tool_outputs: A list of tool outputs to check.
    :return: True if any output contains an error, False otherwise.
    :rtype: bool
    """
    for tool_output in tool_outputs:
        output = tool_output.get("output")
        if isinstance(output, str):
            try:
                output_json = json.loads(output)
                if "error" in output_json:
                    return True
            except json.JSONDecodeError:
                continue
    return False


def _filter_parameters(model_class: Type, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove the parameters, non present in class public fields; return shallow copy of a dictionary.

    **Note:** Classes inherited from the model check that the parameters are present
    in the list of attributes and if they are not, the error is being raised. This check may not
    be relevant for classes, not inherited from azure.ai.agents._model_base.Model.
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


def _safe_instantiate(
    model_class: Type, parameters: Union[str, Dict[str, Any]], *, generated_class: Optional[Type] = None
) -> StreamEventData:
    """
    Instantiate class with the set of parameters from the server.

    :param Type model_class: The class of model to be used.
    :param parameters: The parsed dictionary with parameters.
    :type parameters: Union[str, Dict[str, Any]]
    :keyword Optional[Type] generated_class: The optional generated type.
    :return: The class of model_class type if parameters is a dictionary, or the parameters themselves otherwise.
    :rtype: Any
    """
    if not generated_class:
        generated_class = model_class
    if not isinstance(parameters, dict):
        return parameters
    return cast(StreamEventData, model_class(**_filter_parameters(generated_class, parameters)))


def _parse_event(event_data_str: str) -> Tuple[str, StreamEventData]:
    event_lines = event_data_str.strip().split("\n")
    event_type: Optional[str] = None
    event_data = ""
    event_obj: StreamEventData
    for line in event_lines:
        if line.startswith("event:"):
            event_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            event_data = line.split(":", 1)[1].strip()

    if not event_type:
        raise ValueError("Event type not specified in the event data.")

    try:
        parsed_data: Union[str, Dict[str, StreamEventData]] = cast(Dict[str, StreamEventData], json.loads(event_data))
    except json.JSONDecodeError:
        parsed_data = event_data

    # Workaround for service bug: Rename 'expires_at' to 'expired_at'
    if event_type.startswith("thread.run.step") and isinstance(parsed_data, dict) and "expires_at" in parsed_data:
        parsed_data["expired_at"] = parsed_data.pop("expires_at")

    if isinstance(parsed_data, dict) and "assistant_id" in parsed_data:
        parsed_data["agent_id"] = parsed_data.pop("assistant_id")

    # Map to the appropriate class instance
    if event_type in {
        AgentStreamEvent.THREAD_RUN_CREATED.value,
        AgentStreamEvent.THREAD_RUN_QUEUED.value,
        AgentStreamEvent.THREAD_RUN_INCOMPLETE.value,
        AgentStreamEvent.THREAD_RUN_IN_PROGRESS.value,
        AgentStreamEvent.THREAD_RUN_REQUIRES_ACTION.value,
        AgentStreamEvent.THREAD_RUN_COMPLETED.value,
        AgentStreamEvent.THREAD_RUN_FAILED.value,
        AgentStreamEvent.THREAD_RUN_CANCELLING.value,
        AgentStreamEvent.THREAD_RUN_CANCELLED.value,
        AgentStreamEvent.THREAD_RUN_EXPIRED.value,
    }:
        event_obj = _safe_instantiate(ThreadRun, parsed_data)
    elif event_type in {
        AgentStreamEvent.THREAD_RUN_STEP_CREATED.value,
        AgentStreamEvent.THREAD_RUN_STEP_IN_PROGRESS.value,
        AgentStreamEvent.THREAD_RUN_STEP_COMPLETED.value,
        AgentStreamEvent.THREAD_RUN_STEP_FAILED.value,
        AgentStreamEvent.THREAD_RUN_STEP_CANCELLED.value,
        AgentStreamEvent.THREAD_RUN_STEP_EXPIRED.value,
    }:
        event_obj = _safe_instantiate(RunStep, parsed_data)
    elif event_type in {
        AgentStreamEvent.THREAD_MESSAGE_CREATED.value,
        AgentStreamEvent.THREAD_MESSAGE_IN_PROGRESS.value,
        AgentStreamEvent.THREAD_MESSAGE_COMPLETED.value,
        AgentStreamEvent.THREAD_MESSAGE_INCOMPLETE.value,
    }:
        event_obj = _safe_instantiate(ThreadMessage, parsed_data, generated_class=ThreadMessageGenerated)
    elif event_type == AgentStreamEvent.THREAD_MESSAGE_DELTA.value:
        event_obj = _safe_instantiate(MessageDeltaChunk, parsed_data, generated_class=MessageDeltaChunkGenerated)

    elif event_type == AgentStreamEvent.THREAD_RUN_STEP_DELTA.value:
        event_obj = _safe_instantiate(RunStepDeltaChunk, parsed_data)
    else:
        event_obj = str(parsed_data)

    return event_type, event_obj


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


def _map_type(annotation) -> Dict[str, Any]:  # pylint: disable=too-many-return-statements
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


class MessageDeltaChunk(MessageDeltaChunkGenerated):
    @property
    def text(self) -> str:
        """Get the text content of the delta chunk.

        :rtype: str
        """
        if not self.delta or not self.delta.content:
            return ""
        return "".join(
            content_part.text.value or ""
            for content_part in self.delta.content
            if isinstance(content_part, MessageDeltaTextContent) and content_part.text
        )


class ThreadMessage(ThreadMessageGenerated):
    @property
    def text_messages(self) -> List[MessageTextContent]:
        """Returns all text message contents in the messages.

        :rtype: List[MessageTextContent]
        """
        if not self.content:
            return []
        return [content for content in self.content if isinstance(content, MessageTextContent)]

    @property
    def image_contents(self) -> List[MessageImageFileContent]:
        """Returns all image file contents from image message contents in the messages.

        :rtype: List[MessageImageFileContent]
        """
        if not self.content:
            return []
        return [content for content in self.content if isinstance(content, MessageImageFileContent)]

    @property
    def file_citation_annotations(self) -> List[MessageTextFileCitationAnnotation]:
        """Returns all file citation annotations from text message annotations in the messages.

        :rtype: List[MessageTextFileCitationAnnotation]
        """
        if not self.content:
            return []

        return [
            annotation
            for content in self.content
            if isinstance(content, MessageTextContent)
            for annotation in content.text.annotations
            if isinstance(annotation, MessageTextFileCitationAnnotation)
        ]

    @property
    def file_path_annotations(self) -> List[MessageTextFilePathAnnotation]:
        """Returns all file path annotations from text message annotations in the messages.

        :rtype: List[MessageTextFilePathAnnotation]
        """
        if not self.content:
            return []
        return [
            annotation
            for content in self.content
            if isinstance(content, MessageTextContent)
            for annotation in content.text.annotations
            if isinstance(annotation, MessageTextFilePathAnnotation)
        ]

    @property
    def url_citation_annotations(self) -> List[MessageTextUrlCitationAnnotation]:
        """Returns all URL citation annotations from text message annotations in the messages.

        :rtype: List[MessageTextUrlCitationAnnotation]
        """
        if not self.content:
            return []
        return [
            annotation
            for content in self.content
            if isinstance(content, MessageTextContent)
            for annotation in content.text.annotations
            if isinstance(annotation, MessageTextUrlCitationAnnotation)
        ]


class MessageAttachment(MessageAttachmentGenerated):
    @overload
    def __init__(
        self,
        *,
        tools: List["FileSearchToolDefinition"],
        file_id: Optional[str] = None,
        data_source: Optional["VectorStoreDataSource"] = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        *,
        tools: List["CodeInterpreterToolDefinition"],
        file_id: Optional[str] = None,
        data_source: Optional["VectorStoreDataSource"] = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        *,
        tools: List["_types.MessageAttachmentToolDefinition"],
        file_id: Optional[str] = None,
        data_source: Optional["VectorStoreDataSource"] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


ToolDefinitionT = TypeVar("ToolDefinitionT", bound=ToolDefinition)
ToolT = TypeVar("ToolT", bound="Tool")


class Tool(ABC, Generic[ToolDefinitionT]):
    """
    An abstract class representing a tool that can be used by an agent.
    """

    @property
    @abstractmethod
    def definitions(self) -> List[ToolDefinitionT]:
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


class BaseFunctionTool(Tool[FunctionToolDefinition]):
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

    def add_functions(self, extra_functions: Set[Callable[..., Any]]) -> None:
        """
        Add more functions into this FunctionTool existing function set.
        If a function with the same name already exists, it is overwritten.

        :param extra_functions: A set of additional functions to be added to
            the existing function set. Functions are defined as callables and
            may have any number of arguments and return types.
        :type extra_functions: Set[Callable[..., Any]]
        """
        # Convert the existing dictionary of { name: function } back into a set
        existing_functions = set(self._functions.values())
        # Merge old + new
        combined = existing_functions.union(extra_functions)
        # Rebuild state
        self._functions = self._create_function_dict(combined)
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
            raise ValueError(
                f"Function '{function_name}' not found. Provide this function "
                f"to `enable_auto_function_calls` function call."
            )

        function = self._functions[function_name]

        try:
            parsed_arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON arguments: {e}") from e

        if not isinstance(parsed_arguments, dict):
            raise TypeError("Arguments must be a JSON object.")

        return function, parsed_arguments

    @property
    def definitions(self) -> List[FunctionToolDefinition]:
        """
        Get the function definitions.

        :return: A list of function definitions.
        :rtype: List[ToolDefinition]
        """
        return self._definitions

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
        try:
            function, parsed_arguments = self._get_func_and_args(tool_call)
            return function(**parsed_arguments) if parsed_arguments else function()
        except Exception as e:  # pylint: disable=broad-exception-caught
            error_message = f"Error executing function '{tool_call.function.name}': {e}"
            logger.error(error_message)
            # Return error message as JSON string back to agent in order to make possible self
            # correction to the function call
            return json.dumps({"error": error_message})


class AsyncFunctionTool(BaseFunctionTool):

    async def execute(self, tool_call: RequiredFunctionToolCall) -> Any:  # pylint: disable=invalid-overridden-method
        try:
            function, parsed_arguments = self._get_func_and_args(tool_call)
            if inspect.iscoroutinefunction(function):
                return await function(**parsed_arguments) if parsed_arguments else await function()
            return function(**parsed_arguments) if parsed_arguments else function()
        except Exception as e:  # pylint: disable=broad-exception-caught
            error_message = f"Error executing function '{tool_call.function.name}': {e}"
            logger.error(error_message)
            # Return error message as JSON string back to agent in order to make possible self correction
            # to the function call
            return json.dumps({"error": error_message})


class AzureAISearchTool(Tool[AzureAISearchToolDefinition]):
    """
    A tool that searches for information using Azure AI Search.
    :param connection_id: Connection ID used by tool. All connection tools allow only one connection.
    """

    def __init__(
        self,
        index_connection_id: str,
        index_name: str,
        query_type: AzureAISearchQueryType = AzureAISearchQueryType.SIMPLE,
        filter: str = "",
        top_k: int = 5,
        index_asset_id: Optional[str] = None,
    ):
        """
        Initialize AzureAISearch with an index_connection_id and index_name, with optional params.

        :param index_connection_id: Index Connection ID used by tool. Allows only one connection.
        :type index_connection_id: str
        :param index_name: Name of Index in search resource to be used by tool.
        :type index_name: str
        :param query_type: Type of query in an AIIndexResource attached to this agent.
            Default value is AzureAISearchQueryType.SIMPLE.
        :type query_type: AzureAISearchQueryType
        :param filter: Odata filter string for search resource.
        :type filter: str
        :param top_k: Number of documents to retrieve from search and present to the model.
        :type top_k: int
        :param index_asset_id: Index asset ID to be used by tool.
        :type filter: Optional[str]
        """
        self.index_list = [
            AISearchIndexResource(
                index_connection_id=index_connection_id,
                index_name=index_name,
                query_type=query_type,
                filter=filter,
                top_k=top_k,
                index_asset_id=index_asset_id,
            )
        ]

    @property
    def definitions(self) -> List[AzureAISearchToolDefinition]:
        """
        Get the Azure AI search tool definitions.

        :return: A list of tool definitions.
        :rtype: List[ToolDefinition]
        """
        return [AzureAISearchToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the Azure AI search resources.

        :return: ToolResources populated with azure_ai_search associated resources.
        :rtype: ToolResources
        """
        return ToolResources(azure_ai_search=AzureAISearchToolResource(index_list=self.index_list))

    def execute(self, tool_call: Any):
        """
        AI Search tool does not execute client-side.

        :param Any tool_call: The tool call to execute.
        """


class OpenApiTool(Tool[OpenApiToolDefinition]):
    """
    A tool that retrieves information using OpenAPI specs.
    Initialized with an initial API definition (name, description, spec, auth),
    this class also supports adding and removing additional API definitions dynamically.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str],
        spec: Any,
        auth: OpenApiAuthDetails,
        default_parameters: Optional[List[str]] = None,
    ) -> None:
        """
        Constructor initializes the tool with a primary API definition.

        :param name: The name of the API.
        :type name: str
        :param description: The API description.
        :type description: str
        :param spec: The API specification.
        :type spec: Any
        :param auth: Authentication details for the API.
        :type auth: OpenApiAuthDetails
        :param default_parameters: List of OpenAPI spec parameters that will use user-provided defaults.
        :type default_parameters:  Optional[List[str]]
        """
        default_params: List[str] = [] if default_parameters is None else default_parameters
        self._default_auth = auth
        self._definitions: List[OpenApiToolDefinition] = [
            OpenApiToolDefinition(
                openapi=OpenApiFunctionDefinition(
                    name=name, description=description, spec=spec, auth=auth, default_params=default_params
                )
            )
        ]

    @property
    def definitions(self) -> List[OpenApiToolDefinition]:
        """
        Get the list of all API definitions for the tool.

        :return: A list of OpenAPI tool definitions.
        :rtype: List[ToolDefinition]
        """
        return self._definitions

    def add_definition(
        self,
        name: str,
        description: Optional[str],
        spec: Any,
        auth: Optional[OpenApiAuthDetails] = None,
        default_parameters: Optional[List[str]] = None,
    ) -> None:
        """
        Adds a new API definition dynamically.
        Raises a ValueError if a definition with the same name already exists.

        :param name: The name of the API.
        :type name: str
        :param description: The description of the API.
        :type description: str
        :param spec: The API specification.
        :type spec: Any
        :param auth: Optional authentication details for this particular API definition.
                     If not provided, the tool's default authentication details will be used.
        :type auth: Optional[OpenApiAuthDetails]
        :param default_parameters: List of OpenAPI spec parameters that will use user-provided defaults.
        :type default_parameters: List[str]
        :raises ValueError: If a definition with the same name exists.
        """
        default_params: List[str] = [] if default_parameters is None else default_parameters

        # Check if a definition with the same name exists.
        if any(definition.openapi.name == name for definition in self._definitions):
            raise ValueError(f"Definition '{name}' already exists and cannot be added again.")

        # Use provided auth if specified, otherwise use default
        auth_to_use = auth if auth is not None else self._default_auth

        new_definition = OpenApiToolDefinition(
            openapi=OpenApiFunctionDefinition(
                name=name, description=description, spec=spec, auth=auth_to_use, default_params=default_params
            )
        )
        self._definitions.append(new_definition)

    def remove_definition(self, name: str) -> None:
        """
        Removes an API definition based on its name.

        :param name: The name of the API definition to remove.
        :type name: str
        :raises ValueError: If the definition with the specified name does not exist.
        """
        for definition in self._definitions:
            if definition.openapi.name == name:
                self._definitions.remove(definition)
                logger.info("Definition '%s' removed. Total definitions: %d.", name, len(self._definitions))
                return
        raise ValueError(f"Definition with the name '{name}' does not exist.")

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources for the agent.

        :return: An empty ToolResources as OpenApiTool doesn't have specific resources.
        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> None:
        """
        OpenApiTool does not execute client-side.
        :param Any tool_call: The tool call to execute.
        :type tool_call: Any
        """


class McpTool(Tool[MCPToolDefinition]):
    """
    A tool that connects to Model Context Protocol (MCP) servers.
    Initialized with server configuration, this class supports managing MCP server connections
    and allowed tools dynamically.
    """

    def __init__(
        self,
        server_label: str,
        server_url: str,
        allowed_tools: Optional[List[str]] = None,
    ) -> None:
        """
        Constructor initializes the tool with MCP server configuration.

        :param server_label: The label for the MCP server.
        :type server_label: str
        :param server_url: The endpoint for the MCP server.
        :type server_url: str
        :param allowed_tools: List of allowed tools for MCP server.
        :type allowed_tools: Optional[List[str]]
        """
        self._server_label = server_label
        self._server_url = server_url
        self._allowed_tools = allowed_tools or []
        self._require_approval = "always"
        self._headers: Dict[str, str] = {}
        self._definition = MCPToolDefinition(
            server_label=server_label,
            server_url=server_url,
            allowed_tools=self._allowed_tools if self._allowed_tools else None,
        )
        self._resource = MCPToolResource(
            server_label=self._server_label, headers=self._headers, require_approval=self._require_approval
        )

    @property
    def definitions(self) -> List[MCPToolDefinition]:
        """
        Get the MCP tool definition.

        :return: A list containing the MCP tool definition.
        :rtype: List[MCPToolDefinition]
        """
        return [self._definition]

    def allow_tool(self, tool_name: str) -> None:
        """
        Add a tool to the list of allowed tools.

        :param tool_name: The name of the tool to allow.
        :type tool_name: str
        """
        if tool_name not in self._allowed_tools:
            self._allowed_tools.append(tool_name)
            # Update the definition
            self._definition = MCPToolDefinition(
                server_label=self._server_label,
                server_url=self._server_url,
                allowed_tools=self._allowed_tools if self._allowed_tools else None,
            )

    def disallow_tool(self, tool_name: str) -> None:
        """
        Remove a tool from the list of allowed tools.

        :param tool_name: The name of the tool to remove from allowed tools.
        :type tool_name: str
        :raises ValueError: If the tool is not in the allowed tools list.
        """
        if tool_name in self._allowed_tools:
            self._allowed_tools.remove(tool_name)
            # Update the definition
            self._definition = MCPToolDefinition(
                server_label=self._server_label,
                server_url=self._server_url,
                allowed_tools=self._allowed_tools if self._allowed_tools else None,
            )
        else:
            raise ValueError(f"Tool '{tool_name}' is not in the allowed tools list.")

    def set_approval_mode(self, require_approval: str) -> None:
        """
        Update the headers for the MCP tool.

        :param require_approval: The require_approval setting to update.
        :type require_approval: str
        """
        self._require_approval = require_approval
        self._resource = MCPToolResource(
            server_label=self._server_label, headers=self._headers, require_approval=self._require_approval
        )

    def update_headers(self, key: str, value: str) -> None:
        """
        Update the headers for the MCP tool.

        :param key: The header key to update.
        :type key: str
        :param value: The new value for the header key.
        :type value: str
        :raises ValueError: If the key is empty.
        """
        if key:
            self._headers[key] = value
            self._resource = MCPToolResource(
                server_label=self._server_label, headers=self._headers, require_approval=self._require_approval
            )
        else:
            raise ValueError("Header key cannot be empty.")

    @property
    def server_label(self) -> str:
        """
        Get the server label for the MCP tool.

        :return: The label identifying the MCP server.
        :rtype: str
        """
        return self._server_label

    @property
    def server_url(self) -> str:
        """
        Get the server URL for the MCP tool.

        :return: The endpoint URL for the MCP server.
        :rtype: str
        """
        return self._server_url

    @property
    def allowed_tools(self) -> List[str]:
        """
        Get the list of allowed tools for the MCP server.

        :return: A copy of the list of tool names that are allowed to be executed on this MCP server.
        :rtype: List[str]
        """
        return self._allowed_tools.copy()

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the headers for the MCP tool.

        :return: Dictionary of HTTP headers to be sent with MCP server requests.
        :rtype: Dict[str, str]
        """
        return self._resource.headers

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources for the agent.

        :return: ToolResources with MCP configuration.
        :rtype: ToolResources
        """
        return ToolResources(mcp=[self._resource])

    def execute(self, tool_call: Any) -> None:
        """
        McpTool approvals should currently be handled client-side.

        :param Any tool_call: The tool call to execute.
        :type tool_call: Any
        """


class AzureFunctionTool(Tool[AzureFunctionToolDefinition]):
    """
    A tool that is used to inform agent about available the Azure function.

    :param name: The azure function name.
    :param description: The azure function description.
    :param parameters: The description of function parameters.
    :param input_queue: Input queue used, by azure function.
    :param output_queue: Output queue used, by azure function.
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        input_queue: AzureFunctionStorageQueue,
        output_queue: AzureFunctionStorageQueue,
    ) -> None:
        self._definitions = [
            AzureFunctionToolDefinition(
                azure_function=AzureFunctionDefinition(
                    function=FunctionDefinition(
                        name=name,
                        description=description,
                        parameters=parameters,
                    ),
                    input_binding=AzureFunctionBinding(storage_queue=input_queue),
                    output_binding=AzureFunctionBinding(storage_queue=output_queue),
                )
            )
        ]

    @property
    def definitions(self) -> List[AzureFunctionToolDefinition]:
        """
        Get the Azure AI search tool definitions.

        :rtype: List[ToolDefinition]
        """
        return self._definitions

    @property
    def resources(self) -> ToolResources:
        """
        Get the Azure AI search resources.

        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> Any:
        pass


class ConnectionTool(Tool[ToolDefinitionT]):
    """
    A tool that requires connection ids.
    Used as base class for Sharepoint and Microsoft Fabric
    """

    def __init__(self, connection_id: str):
        """
        Initialize ConnectionTool with a connection_id.

        :param connection_id: Connection ID used by tool. All connection tools allow only one connection.
        :raises ValueError: If the connection ID is invalid.
        """
        if not _is_valid_connection_id(connection_id):
            raise ValueError(
                "Connection ID '"
                + connection_id
                + "' does not fit the format:"
                + "'/subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/"
                + "providers/<provider_name>/accounts/<account_name>/projects/<project_name>/connections/<connection_name>'"
            )

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


class DeepResearchTool(Tool[DeepResearchToolDefinition]):
    """
    A tool that uses a Deep Research AI model, together with Bing Grounding, to answer user queries.
    """

    def __init__(self, bing_grounding_connection_id: str, deep_research_model: str):
        """
        Initialize a Deep Research tool with a Bing Grounding Connection ID and Deep Research model deployment name.

        :param bing_grounding_connection_id: Connection ID used by tool. Bing Grounding tools allow only one connection.
        :param deep_research_model: The Deep Research model deployment name.
        :raises ValueError: If the connection ID is invalid.
        """

        if not _is_valid_connection_id(bing_grounding_connection_id):
            raise ValueError(
                "Connection ID '"
                + bing_grounding_connection_id
                + "' does not fit the format:"
                + "'/subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/"
                + "providers/<provider_name>/accounts/<account_name>/projects/<project_name>/connections/<connection_name>'"
            )

        self._deep_research_details = DeepResearchDetails(
            model=deep_research_model,
            bing_grounding_connections=[
                DeepResearchBingGroundingConnection(connection_id=bing_grounding_connection_id)
            ],
        )

    @property
    def definitions(self) -> List[DeepResearchToolDefinition]:
        """
        Get the Deep Research tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [DeepResearchToolDefinition(deep_research=self._deep_research_details)]

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources.

        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> Any:
        pass


class BrowserAutomationTool(Tool[BrowserAutomationToolDefinition]):
    """
    A tool that allows your Agent to perform real-world web browser navigation tasks through natural language prompts.
    """

    def __init__(self, connection_id: str):
        """
        Initialize a Browser Automation tool with the ID of the connection to an Azure Playwright service.

        :param connection_id: Connection ID to an Azure Playwright service, to be used by tool. Browser Automation tool allows only one connection.
        :raises ValueError: If the connection ID is invalid.
        """

        if not _is_valid_connection_id(connection_id):
            raise ValueError(
                "Connection ID '"
                + connection_id
                + "' does not fit the format:"
                + "'/subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/"
                + "providers/<provider_name>/accounts/<account_name>/projects/<project_name>/connections/<connection_name>'"
            )

        self._browser_automation_tool_parameters = BrowserAutomationToolParameters(
            connection=BrowserAutomationToolConnectionParameters(id=connection_id)
        )

    @property
    def definitions(self) -> List[BrowserAutomationToolDefinition]:
        """
        Get the Browser Automation tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [BrowserAutomationToolDefinition(browser_automation=self._browser_automation_tool_parameters)]

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources.

        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> Any:
        pass


class ComputerUseTool(Tool[ComputerUseToolDefinition]):
    """
    A tool that enables the agent to perform computer use actions (preview).

    :param display_width: The display width for the computer use tool.
    :type display_width: int
    :param display_height: The display height for the computer use tool.
    :type display_height: int
    :param environment: The target environment for computer use, e.g. "browser", "windows", "mac", or "linux".
    :type environment: str
    """

    def __init__(self, display_width: int, display_height: int, environment: str):
        self._params = ComputerUseToolParameters(
            display_width=display_width, display_height=display_height, environment=environment
        )

    @property
    def definitions(self) -> List[ComputerUseToolDefinition]:
        """
        Get the Computer Use tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [ComputerUseToolDefinition(computer_use_preview=self._params)]

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources.

        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> Any:  # noqa: D401 - client-side execution not applicable
        pass


class BingGroundingTool(Tool[BingGroundingToolDefinition]):
    """
    A tool that searches for information using Bing.
    """

    def __init__(self, connection_id: str, market: str = "", set_lang: str = "", count: int = 5, freshness: str = ""):
        """
        Initialize Bing Grounding tool with a connection_id.

        :param connection_id: Connection ID used by tool. Bing Grounding tools allow only one connection.
        :param market: The market where the results come from.
        :param set_lang: The language to use for user interface strings when calling Bing API.
        :param count: The number of search results to return in the Bing API response.
        :param freshness: Filter search results by a specific time range.
        :raises ValueError: If the connection ID is invalid.

        .. seealso::
           `Bing Web Search API Query Parameters <https://learn.microsoft.com/bing/search-apis/bing-web-search/reference/query-parameters>`_
        """

        if not _is_valid_connection_id(connection_id):
            raise ValueError(
                "Connection ID '"
                + connection_id
                + "' does not fit the format:"
                + "'/subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/"
                + "providers/<provider_name>/accounts/<account_name>/projects/<project_name>/connections/<connection_name>'"
            )

        self._search_configurations = [
            BingGroundingSearchConfiguration(
                connection_id=connection_id, market=market, set_lang=set_lang, count=count, freshness=freshness
            )
        ]

    @property
    def definitions(self) -> List[BingGroundingToolDefinition]:
        """
        Get the Bing grounding tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [
            BingGroundingToolDefinition(
                bing_grounding=BingGroundingSearchToolParameters(search_configurations=self._search_configurations)
            )
        ]

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources.

        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> Any:
        pass


class BingCustomSearchTool(Tool[BingCustomSearchToolDefinition]):
    """
    A tool that searches for information using Bing Custom Search.
    """

    def __init__(
        self,
        connection_id: str,
        instance_name: str,
        market: str = "",
        set_lang: str = "",
        count: int = 5,
        freshness: str = "",
    ):
        """
        Initialize Bing Custom Search with a connection_id.

        :param connection_id: Connection ID used by tool. Bing Custom Search tools allow only one connection.
        :param instance_name: Config instance name used by tool.
        :param market: The market where the results come from.
        :param set_lang: The language to use for user interface strings when calling Bing API.
        :param count: The number of search results to return in the Bing API response.
        :param freshness: Filter search results by a specific time range.
        """
        self._search_configurations = [
            BingCustomSearchConfiguration(
                connection_id=connection_id,
                instance_name=instance_name,
                market=market,
                set_lang=set_lang,
                count=count,
                freshness=freshness,
            )
        ]

    @property
    def definitions(self) -> List[BingCustomSearchToolDefinition]:
        """
        Get the Bing Custom Search tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [
            BingCustomSearchToolDefinition(
                bing_custom_search=BingCustomSearchToolParameters(search_configurations=self._search_configurations)
            )
        ]

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources.

        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> Any:
        pass


class FabricTool(ConnectionTool[MicrosoftFabricToolDefinition]):
    """
    A tool that searches for information using Microsoft Fabric.
    """

    @property
    def definitions(self) -> List[MicrosoftFabricToolDefinition]:
        """
        Get the Microsoft Fabric tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [
            MicrosoftFabricToolDefinition(
                fabric_dataagent=FabricDataAgentToolParameters(connection_list=self.connection_ids)
            )
        ]


class SharepointTool(ConnectionTool[SharepointToolDefinition]):
    """
    A tool that searches for information using Sharepoint.
    """

    @property
    def definitions(self) -> List[SharepointToolDefinition]:
        """
        Get the Sharepoint tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [
            SharepointToolDefinition(
                sharepoint_grounding=SharepointGroundingToolParameters(connection_list=self.connection_ids)
            )
        ]


class ConnectedAgentTool(Tool[ConnectedAgentToolDefinition]):
    """
    A tool that connects to a sub-agent, with a description describing the conditions
    or domain where the sub-agent would be called.
    """

    def __init__(self, id: str, name: str, description: str):
        """
        Initialize ConnectedAgentTool with an id, name, and description.

        :param id: The ID of the connected agent.
        :param name: The name of the connected agent.
        :param description: The description of the connected agent, used by the calling agent
           to determine when to call the connected agent.
        """
        self.connected_agent = ConnectedAgentDetails(id=id, name=name, description=description)

    @property
    def definitions(self) -> List[ConnectedAgentToolDefinition]:
        """
        Get the connected agent tool definitions.

        :rtype: List[ToolDefinition]
        """
        return [ConnectedAgentToolDefinition(connected_agent=self.connected_agent)]

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources for the agent.

        :return: An empty ToolResources as ConnectedAgentTool doesn't have specific resources.
        :rtype: ToolResources
        """
        return ToolResources()

    def execute(self, tool_call: Any) -> None:
        """
        ConnectedAgentTool does not execute client-side.

        :param Any tool_call: The tool call to execute.
        :type tool_call: Any
        """


class FileSearchTool(Tool[FileSearchToolDefinition]):
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
    def definitions(self) -> List[FileSearchToolDefinition]:
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


class CodeInterpreterTool(Tool[CodeInterpreterToolDefinition]):
    """
    A tool that interprets code files uploaded to the agent.

    :param file_ids: A list of file IDs to interpret.
    :type file_ids: list[str]
    :param data_sources: The list of data sources for the enterprise file search.
    :type data_sources: list[VectorStoreDataSource]
    :raises: ValueError if both file_ids and data_sources are provided.
    """

    _INVALID_CONFIGURATION = "file_ids and data_sources are mutually exclusive."

    def __init__(
        self,
        file_ids: Optional[List[str]] = None,
        data_sources: Optional[List[VectorStoreDataSource]] = None,
    ):
        if file_ids and data_sources:
            raise ValueError(CodeInterpreterTool._INVALID_CONFIGURATION)
        self.file_ids = set()
        if file_ids:
            self.file_ids = set(file_ids)
        self.data_sources: Dict[str, VectorStoreDataSource] = {}
        if data_sources:
            self.data_sources = {ds.asset_identifier: ds for ds in data_sources}

    def add_file(self, file_id: str) -> None:
        """
        Add a file ID to the list of files to interpret.

        :param file_id: The ID of the file to interpret.
        :type file_id: str
        :raises: ValueError if data_sources are provided.
        """
        if self.data_sources:
            raise ValueError(CodeInterpreterTool._INVALID_CONFIGURATION)
        self.file_ids.add(file_id)

    def add_data_source(self, data_source: VectorStoreDataSource) -> None:
        """
        Add a data source to the list of data sources to interpret.

        :param data_source: The new data source.
        :type data_source: VectorStoreDataSource
        :raises: ValueError if file_ids are provided.
        """
        if self.file_ids:
            raise ValueError(CodeInterpreterTool._INVALID_CONFIGURATION)
        self.data_sources[data_source.asset_identifier] = data_source

    def remove_file(self, file_id: str) -> None:
        """
        Remove a file ID from the list of files to interpret.

        :param file_id: The ID of the file to remove.
        :type file_id: str
        """
        self.file_ids.discard(file_id)

    def remove_data_source(self, asset_identifier: str) -> None:
        """
        Remove The asset from data_sources.

        :param asset_identifier: The asset identifier to remove.
        :type asset_identifier: str
        """
        self.data_sources.pop(asset_identifier, None)

    @property
    def definitions(self) -> List[CodeInterpreterToolDefinition]:
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
        if not self.file_ids and not self.data_sources:
            return ToolResources()
        if self.file_ids:
            return ToolResources(code_interpreter=CodeInterpreterToolResource(file_ids=list(self.file_ids)))
        return ToolResources(
            code_interpreter=CodeInterpreterToolResource(data_sources=list(self.data_sources.values()))
        )

    def execute(self, tool_call: Any) -> Any:
        pass


class BaseToolSet(ABC):
    """Abstract base class for a collection of tools that can be used by an agent.

    Subclasses must implement ``validate_tool_type`` to enforce any constraints on
    what tool types are allowed in the set.
    """

    def __init__(self) -> None:  # pragma: no cover - simple container init
        self._tools: List[Tool] = []

    @abstractmethod
    def validate_tool_type(self, tool: Tool) -> None:
        """Validate that the provided tool is of an acceptable type for this tool set.

        Implementations should raise ``ValueError`` (or a more specific exception) if
        the tool type is not permitted.

        :param tool: The tool to validate.
        :type tool: Tool
        :return: None
        :rtype: None
        :raises ValueError: If the tool type is not permitted for this tool set.
        """
        raise NotImplementedError

    def add(self, tool: Tool):
        """
        Add a tool to the tool set.

        :param Tool tool: The tool to add.
        :raises ValueError: If a tool of the same type already exists, or if an MCP tool with the same server label already exists.
        """
        self.validate_tool_type(tool)

        # Special handling for OpenApiTool - add definitions to existing tool instead of raising error
        if isinstance(tool, OpenApiTool):
            # Find existing OpenApiTool if any
            existing_openapi_tool = next((t for t in self._tools if isinstance(t, OpenApiTool)), None)
            if existing_openapi_tool:
                # Add all definitions from the new tool to the existing one
                for definition in tool.definitions:
                    existing_openapi_tool.add_definition(
                        name=definition.openapi.name,
                        description=definition.openapi.description,
                        spec=definition.openapi.spec,
                        auth=definition.openapi.auth,
                        default_parameters=definition.openapi.default_params,
                    )
                return  # Early return since we added to existing tool

        # Special handling for McpTool - check for same server label
        if isinstance(tool, McpTool):
            # Check if there's already an MCP tool with the same server label
            for existing_tool in self._tools:
                if isinstance(existing_tool, McpTool) and existing_tool.server_label == tool.server_label:
                    raise ValueError(f"McpTool with server label '{tool.server_label}' already exists in the ToolSet.")
            # Allow multiple MCP tools (with different server labels)
            self._tools.append(tool)
            return

        if any(isinstance(existing_tool, type(tool)) for existing_tool in self._tools):
            raise ValueError(f"Tool of type {type(tool).__name__} already exists in the ToolSet.")
        self._tools.append(tool)

    @overload
    def remove(self, tool_type: Type[Tool]) -> None:
        """Remove a tool by name from the toolset.

        :param tool_type: The tool class to target.
        :type tool_type: Type[Tool]

        """
        ...

    @overload
    def remove(self, tool_type: Type[OpenApiTool], *, name: str) -> None:
        """
        Remove a specific API definition from an OpenApiTool by name.

        :param tool_type: The tool class to target. Must be OpenApiTool.
        :type tool_type: Type[OpenApiTool]
        :keyword name: The name of the OpenAPI definition to remove from the tool.
        :paramtype name: str
        :raises ValueError: If the OpenApiTool isn't found or the named definition doesn't exist.
        """
        ...

    @overload
    def remove(self, tool_type: Type[McpTool], *, server_label: str) -> None:
        """
        Remove a specific McpTool from the toolset by its server label.

        :param tool_type: The tool class to target. Must be McpTool.
        :type tool_type: Type[McpTool]
        :keyword server_label: The unique server label identifying the MCP tool to remove.
        :paramtype server_label: str
        :raises ValueError: If no McpTool with the given server label is found.
        """
        ...

    def remove(self, tool_type: Type[Tool], *, name: Optional[str] = None, server_label: Optional[str] = None) -> None:
        """
        Remove a tool of the specified type from the tool set.
        For OpenApiTool, if 'name' is provided, removes a specific API definition by name.
        For McpTool, if 'server_label' is provided, removes a specific MCP tool by server label.
        For McpTool without server_label, removes ALL MCP tools from the toolset.
        Otherwise, removes the entire tool from the toolset.

        :param tool_type: The type of tool to remove.
        :type tool_type: Type[Tool]
        :keyword name: The name of the OpenAPI definition to remove from the tool.
        :paramtype name: str
        :keyword server_label: The unique server label identifying the MCP tool to remove.
        :paramtype server_label: Optional[str]
        :return: None
        :rtype: None
        :raises ValueError: If a tool of the specified type is not found.
        """
        # Special handling for OpenApiTool with name parameter
        if tool_type == OpenApiTool and name:
            for i, tool in enumerate(self._tools):
                if isinstance(tool, OpenApiTool):
                    tool.remove_definition(name)  # This will raise ValueError if definition not found
                    logger.info("API definition '%s' removed from OpenApiTool.", name)
                    # Check if OpenApiTool has any definitions left
                    if not tool.definitions:
                        del self._tools[i]
                        logger.info("OpenApiTool removed from ToolSet as it has no remaining definitions.")
                    return
            raise ValueError(f"Tool of type {tool_type.__name__} not found in the ToolSet.")

        # Special handling for McpTool with server_label parameter
        if tool_type == McpTool:

            if server_label:
                for i, tool in enumerate(self._tools):
                    if isinstance(tool, McpTool) and tool.server_label == server_label:
                        del self._tools[i]
                        logger.info("McpTool with server label '%s' removed from the ToolSet.", server_label)
                        return
                raise ValueError(f"McpTool with server label '{server_label}' not found in the ToolSet.")

            # Special handling for McpTool without server_label - remove ALL MCP tools
            filtered_removal = [t for t in self._tools if not isinstance(t, McpTool)]
            if len(self._tools) == len(filtered_removal):
                raise ValueError(f"No tools of type {tool_type.__name__} found in the ToolSet.")
            self._tools = filtered_removal
            return

        # Standard tool removal
        for i, tool in enumerate(self._tools):
            if isinstance(tool, tool_type):
                del self._tools[i]
                logger.info("Tool of type %s removed from the ToolSet.", tool_type.__name__)
                return
        raise ValueError(f"Tool of type {tool_type.__name__} not found in the ToolSet.")

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the definitions for all tools in the tool set.

        :rtype: List[ToolDefinition]
        """
        return get_tool_definitions(self._tools)

    @property
    def resources(self) -> ToolResources:
        """
        Get the resources for all tools in the tool set.

        :rtype: ToolResources
        """
        return get_tool_resources(self._tools)

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

    @overload
    def get_tool(self, tool_type: Type[McpTool]) -> McpTool:
        """
        Get an MCP tool from the tool set.

        :param tool_type: The MCP tool type to get.
        :type tool_type: Type[McpTool]
        :return: The MCP tool.
        :rtype: McpTool
        """
        ...

    @overload
    def get_tool(self, tool_type: Type[McpTool], *, server_label: str) -> McpTool:
        """
        Get an MCP tool with a specific server label from the tool set.

        :param tool_type: The MCP tool type to get.
        :type tool_type: Type[McpTool]
        :keyword server_label: The server label of the specific MCP tool to get.
        :paramtype server_label: str
        :return: The MCP tool with the specified server label.
        :rtype: McpTool
        """
        ...

    @overload
    def get_tool(self, tool_type: Type[ToolT]) -> ToolT:
        """
        Get a tool of the specified type from the tool set.

        :param tool_type: The type of tool to get.
        :type tool_type: Type[Tool]
        :return: The tool of the specified type.
        :rtype: Tool
        """
        ...

    def get_tool(self, tool_type: Type[ToolT], *, server_label: Optional[str] = None) -> ToolT:
        """
        Get a tool of the specified type from the tool set.
        For McpTool, if 'server_label' is provided, returns the MCP tool with that specific server label.
        If there are multiple MCP tools and no server_label is provided, raises an error.
        Otherwise, returns the first (or only) tool of the specified type.

        :param tool_type: The type of tool to get.
        :type tool_type: Type[Tool]
        :keyword server_label: The server label of the specific MCP tool to get.
        :paramtype server_label: Optional[str]
        :return: The tool of the specified type.
        :rtype: Tool
        :raises ValueError: If a tool of the specified type is not found, if no McpTool with the specified server_label is found, or if there are multiple MCP tools but no server_label is provided.
        """
        # Special handling for McpTool without server_label - check if there are multiple
        if tool_type == McpTool:
            # Special handling for McpTool with server_label parameter
            if server_label is not None:
                for tool in self._tools:
                    if isinstance(tool, McpTool) and tool.server_label == server_label:
                        return cast(ToolT, tool)
                raise ValueError(f"McpTool with server label '{server_label}' not found in the ToolSet.")
            mcp_tools = [tool for tool in self._tools if isinstance(tool, McpTool)]
            if len(mcp_tools) == 0:
                raise ValueError(f"Tool of type {tool_type.__name__} not found in the ToolSet.")
            if len(mcp_tools) > 1:
                server_labels = [tool.server_label for tool in mcp_tools]
                raise ValueError(
                    f"Multiple McpTool instances found with server labels: {server_labels}. "
                    f"Please specify 'server_label' parameter to identify which MCP tool to retrieve."
                )
            # Only one MCP tool found, return it
            return cast(ToolT, mcp_tools[0])

        # Standard tool retrieval - return first tool of specified type
        for tool in self._tools:
            if isinstance(tool, tool_type):
                return cast(ToolT, tool)
        raise ValueError(f"Tool of type {tool_type.__name__} not found in the ToolSet.")


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
                + "To use async functions, use AsyncToolSet and agents operations in azure.ai.agents.aio."
            )

    def execute_tool_calls(self, tool_calls: List[Any]) -> Any:
        """
        Execute a tool of the specified type with the provided tool calls.

        :param List[Any] tool_calls: A list of tool calls to execute.
        :return: The output of the tool operations.
        :rtype: Any
        """
        return self._execute_tool_calls(tool_calls)

    def _execute_tool_calls(
        self, tool_calls: List[Any], run: Optional[ThreadRun] = None, run_handler: Optional["RunHandler"] = None
    ) -> Any:
        tool_outputs = []

        for tool_call in tool_calls:
            if tool_call.type == "function":
                output: Optional[Any] = None

                tool = self.get_tool(FunctionTool)
                function_name = tool_call.function.name
                try:
                    if run_handler and run and function_name not in tool._functions:  # pylint: disable=protected-access
                        output = run_handler.submit_function_call_output(
                            run=run, tool_call=tool_call, tool_call_details=tool_call.function
                        )
                        if not output:
                            error = f"Function '{function_name}' not handled in submit_function_call_output."
                            logger.error(error)
                            raise ValueError(error)
                    else:
                        output = tool.execute(tool_call)
                    tool_output = {
                        "tool_call_id": tool_call.id,
                        "output": str(output),
                    }
                    tool_outputs.append(tool_output)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    tool_output = {"tool_call_id": tool_call.id, "output": str(e)}
                    tool_outputs.append(tool_output)

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

    async def _execute_single_tool_call(
        self, tool_call: Any, run: Optional[ThreadRun] = None, run_handler: Optional["AsyncRunHandler"] = None
    ):
        output: Optional[Any] = None
        tool = self.get_tool(AsyncFunctionTool)
        function_name = tool_call.function.name
        try:
            if run_handler and run and function_name not in tool._functions:  # pylint: disable=protected-access
                output = await run_handler.submit_function_call_output(
                    run=run, tool_call=tool_call, tool_call_details=tool_call.function
                )
                if not output:
                    error = f"Function '{function_name}' not handled in submit_function_call_output."
                    logger.error(error)
                    raise ValueError(error)
            else:
                output = await tool.execute(tool_call)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {"tool_call_id": tool_call.id, "output": str(e)}
        return {"tool_call_id": tool_call.id, "output": str(output)}

    async def execute_tool_calls(self, tool_calls: List[Any]) -> Any:
        """
        Execute a tool of the specified type with the provided tool calls concurrently.

        :param List[Any] tool_calls: A list of tool calls to execute.
        :return: The output of the tool operations.
        :rtype: Any
        """

        return await self._execute_tool_calls(tool_calls)

    async def _execute_tool_calls(
        self, tool_calls: List[Any], run: Optional[ThreadRun] = None, run_handler: Optional["AsyncRunHandler"] = None
    ) -> Any:

        # Execute all tool calls concurrently
        tool_outputs = await asyncio.gather(
            *[self._execute_single_tool_call(tc, run, run_handler) for tc in tool_calls if tc.type == "function"]
        )

        return tool_outputs


EventFunctionReturnT = TypeVar("EventFunctionReturnT")
T = TypeVar("T")
BaseAsyncAgentEventHandlerT = TypeVar("BaseAsyncAgentEventHandlerT", bound="BaseAsyncAgentEventHandler")
# BaseAgentEventHandlerT is defined after BaseAgentEventHandler class to avoid forward reference during parsing.


async def async_chain(*iterators: AsyncIterator[T]) -> AsyncIterator[T]:
    for iterator in iterators:
        async for item in iterator:
            yield item


class BaseAsyncAgentEventHandler(AsyncIterator[T]):

    def __init__(self) -> None:
        self.response_iterator: Optional[AsyncIterator[bytes]] = None
        self.submit_tool_outputs: Optional[
            Callable[[ThreadRun, "BaseAsyncAgentEventHandler[T]", bool], Awaitable[Any]]
        ] = None
        self.buffer: Optional[bytes] = None

    def initialize(
        self,
        response_iterator: AsyncIterator[bytes],
        submit_tool_outputs: Callable[[ThreadRun, "BaseAsyncAgentEventHandler[T]", bool], Awaitable[Any]],
    ):
        self.response_iterator = (
            async_chain(self.response_iterator, response_iterator) if self.response_iterator else response_iterator
        )
        self.submit_tool_outputs = submit_tool_outputs

    # cspell:disable-next-line
    async def __anext__(self) -> T:
        # cspell:disable-next-line
        event_bytes = await self.__anext_impl__()
        return await self._process_event(event_bytes.decode("utf-8"))

    # cspell:disable-next-line
    async def __anext_impl__(self) -> bytes:
        self.buffer = b"" if self.buffer is None else self.buffer
        if self.response_iterator is None:
            raise ValueError("The response handler was not initialized.")

        if not b"\n\n" in self.buffer:
            async for chunk in self.response_iterator:
                self.buffer += chunk
                if b"\n\n" in self.buffer:
                    break

        if self.buffer == b"":
            raise StopAsyncIteration()

        event_bytes = b""
        if b"\n\n" in self.buffer:
            event_end_index = self.buffer.index(b"\n\n")
            event_bytes = self.buffer[:event_end_index]
            self.buffer = self.buffer[event_end_index:].lstrip()
        else:
            event_bytes = self.buffer
            self.buffer = b""

        return event_bytes

    async def _process_event(self, event_data_str: str) -> T:
        raise NotImplementedError("This method needs to be implemented.")

    async def until_done(self) -> None:
        """
        Iterates through all events until the stream is marked as done.
        Calls the provided callback function with each event data.
        """
        try:
            async for _ in self:
                pass
        except StopAsyncIteration:
            pass


class RunHandler:
    """Helper that drives a run to completion for the "create and process" pattern.

    Extension Points:
        * ``submit_function_call_output`` -- override to customize how function tool results are produced.
        * ``submit_mcp_tool_approval`` -- override to implement an approval workflow (UI prompt, policy, etc.).
    """

    def _start(self, runs_operations: "RunsOperations", run: ThreadRun, polling_interval: int) -> ThreadRun:
        """Poll and process a run until it reaches a terminal state or is cancelled.

        :param runs_operations: Operations client used to retrieve, cancel, and submit tool outputs/approvals.
        :type runs_operations: RunsOperations
        :param run: The initial run returned from create/process call.
        :type run: ThreadRun
        :param polling_interval: Delay (in seconds) between polling attempts.
        :type polling_interval: int
        :return: The final terminal ``ThreadRun`` object (completed, failed, cancelled, or expired).
        :rtype: ThreadRun
        """
        current_retry = 0
        while run.status in [
            RunStatus.QUEUED,
            RunStatus.IN_PROGRESS,
            RunStatus.REQUIRES_ACTION,
        ]:
            time.sleep(polling_interval)
            run = runs_operations.get(thread_id=run.thread_id, run_id=run.id)

            # pylint:disable=protected-access
            if run.status == RunStatus.REQUIRES_ACTION and isinstance(run.required_action, SubmitToolOutputsAction):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    logger.warning("No tool calls provided - cancelling run")
                    runs_operations.cancel(thread_id=run.thread_id, run_id=run.id)
                    break
                # We need tool set only if we are executing local function. In case if
                # the tool is azure_function we just need to wait when it will be finished.
                if any(tool_call.type == "function" for tool_call in tool_calls):
                    toolset = ToolSet()
                    toolset.add(runs_operations._function_tool)
                    tool_outputs = toolset._execute_tool_calls(tool_calls, run, self)

                    if _has_errors_in_toolcalls_output(tool_outputs):
                        if current_retry >= runs_operations._function_tool_max_retry:  # pylint:disable=no-else-return
                            logger.warning(
                                "Tool outputs contain errors - reaching max retry %s",
                                runs_operations._function_tool_max_retry,
                            )
                            return runs_operations.cancel(thread_id=run.thread_id, run_id=run.id)
                        else:
                            logger.warning("Tool outputs contain errors - retrying")
                            current_retry += 1

                    logger.debug("Tool outputs: %s", tool_outputs)
                    if tool_outputs:
                        run2 = runs_operations.submit_tool_outputs(
                            thread_id=run.thread_id, run_id=run.id, tool_outputs=tool_outputs
                        )
                        logger.debug("Tool outputs submitted to run: %s", run2.id)
            elif isinstance(run.required_action, SubmitToolApprovalAction):
                tool_calls = run.required_action.submit_tool_approval.tool_calls
                if not tool_calls:
                    logger.warning("No tool calls provided - cancelling run")
                    runs_operations.cancel(thread_id=run.thread_id, run_id=run.id)
                    break

                tool_approvals = []
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredMcpToolCall):
                        try:
                            tool_approval = self.submit_mcp_tool_approval(  # pylint: disable=assignment-from-none,assignment-from-no-return
                                run=run, tool_call=tool_call
                            )
                            tool_approvals.append(tool_approval)
                        except Exception:  # pylint: disable=broad-exception-caught
                            logger.error("Error occurred while submitting MCP tool approval.")
                            return runs_operations.cancel(thread_id=run.thread_id, run_id=run.id)

                if tool_approvals:
                    run = runs_operations.submit_tool_outputs(
                        thread_id=run.thread_id, run_id=run.id, tool_approvals=tool_approvals
                    )

            logger.debug("Current run ID: %s with status: %s", run.id, run.status)
        return run

    def submit_function_call_output(
        self,  # pylint: disable=unused-argument
        *,
        run: ThreadRun,  # pylint: disable=unused-argument
        tool_call: RequiredFunctionToolCall,  # pylint: disable=unused-argument
        tool_call_details: RequiredFunctionToolCallDetails,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> Any:
        """Produce (or override) the output for a required function tool call.

        Override this to inject custom execution logic, caching, validation, or transformation.
        Return ``None`` to fall back to the default execution path handled.

        :keyword run: Current run requiring the function output.
        :paramtype run: ThreadRun
        :keyword tool_call: The tool call metadata referencing the function tool.
        :paramtype tool_call: RequiredFunctionToolCall
        :keyword tool_call_details: Function arguments/details object.
        :paramtype tool_call_details: RequiredFunctionToolCallDetails
        :paramtype kwargs: Additional keyword arguments for extensibility.
        :return: Stringified result to send back to the service, or ``None`` to delegate to auto function calling.
        :rtype: Any
        """
        error = f"run_handler isn't provided or submit_function_call_output isn't implemented to call {tool_call_details.name}."
        logger.error(error)
        raise NotImplementedError(error)

    def submit_mcp_tool_approval(
        self,  # pylint: disable=unused-argument
        *,
        run: ThreadRun,  # pylint: disable=unused-argument
        tool_call: RequiredMcpToolCall,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> ToolApproval:
        # NOTE: Implementation intentionally returns None; override in subclasses for real approval logic.
        """Return a ``ToolApproval`` for an MCP tool call or ``None`` to indicate rejection/cancellation.

        Override this to implement approval policies (interactive prompt, RBAC, heuristic checks, etc.).
        Returning ``None`` triggers cancellation logic in ``_start``.

        :keyword run: Current run containing the MCP approval request.
        :paramtype run: ThreadRun
        :keyword tool_call: The MCP tool call requiring approval.
        :paramtype tool_call: RequiredMcpToolCall
        :paramtype kwargs: Additional keyword arguments for extensibility.
        :return: A populated ``ToolApproval`` instance to approve or decline.
        :rtype: ToolApproval
        """
        error = "run_handler isn't provided or submit_mcp_tool_approval isn't implemented to approve MCP tool calls."
        logger.error(error)
        raise NotImplementedError(error)


class AsyncRunHandler:
    """Helper that drives a run to completion for the "create and process" pattern.

    Extension Points:
        * ``submit_function_call_output`` -- override to customize how function tool results are produced.
        * ``submit_mcp_tool_approval`` -- override to implement an approval workflow (UI prompt, policy, etc.).
    """

    async def _start(self, runs_operations: "AsyncRunsOperations", run: ThreadRun, polling_interval: int) -> ThreadRun:
        """Poll and process a run until it reaches a terminal state or is cancelled.

        :param runs_operations: Operations client used to retrieve, cancel, and submit tool outputs/approvals.
        :type runs_operations: AsyncRunsOperations
        :param run: The initial run returned from create/process call.
        :type run: ThreadRun
        :param polling_interval: Delay (in seconds) between polling attempts.
        :type polling_interval: int
        :return: The final terminal ``ThreadRun`` object (completed, failed, cancelled, or expired).
        :rtype: ThreadRun
        """
        current_retry = 0
        while run.status in [
            RunStatus.QUEUED,
            RunStatus.IN_PROGRESS,
            RunStatus.REQUIRES_ACTION,
        ]:
            await asyncio.sleep(polling_interval)
            run = await runs_operations.get(thread_id=run.thread_id, run_id=run.id)

            # pylint:disable=protected-access
            if run.status == RunStatus.REQUIRES_ACTION and isinstance(run.required_action, SubmitToolOutputsAction):
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    logger.warning("No tool calls provided - cancelling run")
                    await runs_operations.cancel(thread_id=run.thread_id, run_id=run.id)
                    break
                # We need tool set only if we are executing local function. In case if
                # the tool is azure_function we just need to wait when it will be finished.
                if any(tool_call.type == "function" for tool_call in tool_calls):
                    toolset = AsyncToolSet()
                    toolset.add(runs_operations._function_tool)
                    tool_outputs = await toolset._execute_tool_calls(tool_calls, run, self)

                    if _has_errors_in_toolcalls_output(tool_outputs):
                        if current_retry >= runs_operations._function_tool_max_retry:  # pylint:disable=no-else-return
                            logger.warning(
                                "Tool outputs contain errors - reaching max retry %s",
                                runs_operations._function_tool_max_retry,
                            )
                            return await runs_operations.cancel(thread_id=run.thread_id, run_id=run.id)
                        else:
                            logger.warning("Tool outputs contain errors - retrying")
                            current_retry += 1

                    logger.debug("Tool outputs: %s", tool_outputs)
                    if tool_outputs:
                        run2 = await runs_operations.submit_tool_outputs(
                            thread_id=run.thread_id, run_id=run.id, tool_outputs=tool_outputs
                        )
                        logger.debug("Tool outputs submitted to run: %s", run2.id)
            elif isinstance(run.required_action, SubmitToolApprovalAction):
                tool_calls = run.required_action.submit_tool_approval.tool_calls
                if not tool_calls:
                    logger.warning("No tool calls provided - cancelling run")
                    await runs_operations.cancel(thread_id=run.thread_id, run_id=run.id)
                    break

                tool_approvals = []
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredMcpToolCall):
                        try:
                            tool_approval = self.submit_mcp_tool_approval(  # pylint: disable=assignment-from-none,assignment-from-no-return
                                run=run, tool_call=tool_call
                            )
                            tool_approvals.append(tool_approval)
                        except Exception:  # pylint: disable=broad-exception-caught
                            logger.error("Error occurred while submitting MCP tool approval.")
                            return await runs_operations.cancel(thread_id=run.thread_id, run_id=run.id)

                if tool_approvals:
                    run = await runs_operations.submit_tool_outputs(
                        thread_id=run.thread_id, run_id=run.id, tool_approvals=tool_approvals
                    )

            logger.debug("Current run ID: %s with status: %s", run.id, run.status)
        return run

    async def submit_function_call_output(
        self,  # pylint: disable=unused-argument
        *,
        run: ThreadRun,  # pylint: disable=unused-argument
        tool_call: RequiredFunctionToolCall,  # pylint: disable=unused-argument
        tool_call_details: RequiredFunctionToolCallDetails,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> Any:
        """Produce (or override) the output for a required function tool call.

        Override this to inject custom execution logic, caching, validation, or transformation.
        Return ``None`` to fall back to the default execution path handled.

        :keyword run: Current run requiring the function output.
        :paramtype run: ThreadRun
        :keyword tool_call: The tool call metadata referencing the function tool.
        :paramtype tool_call: RequiredFunctionToolCall
        :keyword tool_call_details: Function arguments/details object.
        :paramtype tool_call_details: RequiredFunctionToolCallDetails
        :paramtype kwargs: Additional keyword arguments for extensibility.
        :return: Stringified result to send back to the service, or ``None`` to delegate to auto function calling.
        :rtype: Any
        """
        error = f"run_handler isn't provided or submit_function_call_output isn't implemented to call {tool_call_details.name}."
        logger.error(error)
        raise NotImplementedError(error)

    def submit_mcp_tool_approval(
        self,  # pylint: disable=unused-argument
        *,
        run: ThreadRun,  # pylint: disable=unused-argument
        tool_call: RequiredMcpToolCall,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> ToolApproval:
        # NOTE: Implementation intentionally returns None; override in subclasses for real approval logic.
        """Return a ``ToolApproval`` for an MCP tool call or ``None`` to indicate rejection/cancellation.

        Override this to implement approval policies (interactive prompt, RBAC, heuristic checks, etc.).
        Returning ``None`` triggers cancellation logic.

        :keyword run: Current run containing the MCP approval request.
        :paramtype run: ThreadRun
        :keyword tool_call: The MCP tool call requiring approval.
        :paramtype tool_call: RequiredMcpToolCall
        :paramtype kwargs: Additional keyword arguments for extensibility.
        :return: A populated ``ToolApproval`` instance to approve or decline.
        :rtype: ToolApproval
        """
        error = "run_handler isn't provided or submit_mcp_tool_approval isn't implemented to approve MCP tool calls."
        logger.error(error)
        raise NotImplementedError(error)


class BaseAgentEventHandler(Iterator[T]):

    def __init__(self) -> None:
        self.response_iterator: Optional[Iterator[bytes]] = None
        self.submit_tool_outputs: Optional[Callable[[ThreadRun, "BaseAgentEventHandler[T]", bool], Any]]
        self.buffer: Optional[bytes] = None

    def initialize(
        self,
        response_iterator: Iterator[bytes],
        submit_tool_outputs: Callable[[ThreadRun, "BaseAgentEventHandler[T]", bool], Any],
    ) -> None:
        self.response_iterator = (
            itertools.chain(self.response_iterator, response_iterator) if self.response_iterator else response_iterator
        )
        self.submit_tool_outputs = submit_tool_outputs

    def __next__(self) -> T:
        event_bytes = self.__next_impl__()
        return self._process_event(event_bytes.decode("utf-8"))

    def __next_impl__(self) -> bytes:
        self.buffer = b"" if self.buffer is None else self.buffer
        if self.response_iterator is None:
            raise ValueError("The response handler was not initialized.")

        if not b"\n\n" in self.buffer:
            for chunk in self.response_iterator:
                self.buffer += chunk
                if b"\n\n" in self.buffer:
                    break

        if self.buffer == b"":
            raise StopIteration()

        event_bytes = b""
        if b"\n\n" in self.buffer:
            event_end_index = self.buffer.index(b"\n\n")
            event_bytes = self.buffer[:event_end_index]
            self.buffer = self.buffer[event_end_index:].lstrip()
        else:
            event_bytes = self.buffer
            self.buffer = b""

        return event_bytes

    def _process_event(self, event_data_str: str) -> T:
        raise NotImplementedError("This method needs to be implemented.")

    def until_done(self) -> None:
        """
        Iterates through all events until the stream is marked as done.
        Calls the provided callback function with each event data.
        """
        try:
            for _ in self:
                pass
        except StopIteration:
            pass


# Now that BaseAgentEventHandler is defined, we can bind the TypeVar.
BaseAgentEventHandlerT = TypeVar("BaseAgentEventHandlerT", bound="BaseAgentEventHandler")


class AsyncAgentEventHandler(BaseAsyncAgentEventHandler[Tuple[str, StreamEventData, Optional[EventFunctionReturnT]]]):
    def __init__(self) -> None:
        super().__init__()
        self._max_retry = 10
        self.current_retry = 0

    def set_max_retry(self, max_retry: int) -> None:
        """
        Set the maximum number of retries for tool output submission.

        :param int max_retry: The maximum number of retries.
        """
        self._max_retry = max_retry

    async def _process_event(self, event_data_str: str) -> Tuple[str, StreamEventData, Optional[EventFunctionReturnT]]:

        event_type, event_data_obj = _parse_event(event_data_str)
        if (
            isinstance(event_data_obj, ThreadRun)
            and event_data_obj.status == "requires_action"
            and isinstance(event_data_obj.required_action, SubmitToolOutputsAction)
        ):
            tool_output = await cast(
                Callable[[ThreadRun, "BaseAsyncAgentEventHandler", bool], Awaitable[Any]], self.submit_tool_outputs
            )(event_data_obj, self, self.current_retry < self._max_retry)

            if _has_errors_in_toolcalls_output(tool_output):
                self.current_retry += 1

        func_rt: Optional[EventFunctionReturnT] = None
        try:
            if isinstance(event_data_obj, MessageDeltaChunk):
                func_rt = await self.on_message_delta(event_data_obj)
            elif isinstance(event_data_obj, ThreadMessage):
                func_rt = await self.on_thread_message(event_data_obj)
            elif isinstance(event_data_obj, ThreadRun):
                func_rt = await self.on_thread_run(event_data_obj)
            elif isinstance(event_data_obj, RunStep):
                func_rt = await self.on_run_step(event_data_obj)
            elif isinstance(event_data_obj, RunStepDeltaChunk):
                func_rt = await self.on_run_step_delta(event_data_obj)
            elif event_type == AgentStreamEvent.ERROR:
                func_rt = await self.on_error(event_data_obj)
            elif event_type == AgentStreamEvent.DONE:
                func_rt = await self.on_done()
            else:
                func_rt = await self.on_unhandled_event(
                    event_type, event_data_obj
                )  # pylint: disable=assignment-from-none
        except Exception:  # pylint: disable=broad-exception-caught
            logger.error("Error in event handler for event '%s'", event_type)
        return event_type, event_data_obj, func_rt

    async def on_message_delta(
        self, delta: "MessageDeltaChunk"  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle message delta events.

        :param MessageDeltaChunk delta: The message delta.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    async def on_thread_message(
        self, message: "ThreadMessage"  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle thread message events.

        :param ThreadMessage message: The thread message.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    async def on_thread_run(
        self, run: "ThreadRun"  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle thread run events.

        :param ThreadRun run: The thread run.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    async def on_run_step(self, step: "RunStep") -> Optional[EventFunctionReturnT]:  # pylint: disable=unused-argument
        """Handle run step events.

        :param RunStep step: The run step.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    async def on_run_step_delta(
        self, delta: "RunStepDeltaChunk"  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle run step delta events.

        :param RunStepDeltaChunk delta: The run step delta.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    async def on_error(self, data: str) -> Optional[EventFunctionReturnT]:  # pylint: disable=unused-argument
        """Handle error events.

        :param str data: The error event's data.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    async def on_done(
        self,
    ) -> Optional[EventFunctionReturnT]:
        """Handle the completion of the stream.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    async def on_unhandled_event(
        self, event_type: str, event_data: str  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle any unhandled event types.

        :param str event_type: The event type.
        :param Any event_data: The event's data.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None


class AgentEventHandler(BaseAgentEventHandler[Tuple[str, StreamEventData, Optional[EventFunctionReturnT]]]):
    def __init__(self) -> None:
        super().__init__()
        self._max_retry = 10
        self.current_retry = 0

    def set_max_retry(self, max_retry: int) -> None:
        """
        Set the maximum number of retries for tool output submission.

        :param int max_retry: The maximum number of retries.
        """
        self._max_retry = max_retry

    def _process_event(self, event_data_str: str) -> Tuple[str, StreamEventData, Optional[EventFunctionReturnT]]:

        event_type, event_data_obj = _parse_event(event_data_str)
        if (
            isinstance(event_data_obj, ThreadRun)
            and event_data_obj.status == "requires_action"
            and isinstance(event_data_obj.required_action, SubmitToolOutputsAction)
        ):
            tool_output = cast(Callable[[ThreadRun, "BaseAgentEventHandler", bool], Any], self.submit_tool_outputs)(
                event_data_obj, self, self.current_retry < self._max_retry
            )

            if _has_errors_in_toolcalls_output(tool_output):
                self.current_retry += 1

        func_rt: Optional[EventFunctionReturnT] = None
        try:
            if isinstance(event_data_obj, MessageDeltaChunk):
                func_rt = self.on_message_delta(event_data_obj)  # pylint: disable=assignment-from-none
            elif isinstance(event_data_obj, ThreadMessage):
                func_rt = self.on_thread_message(event_data_obj)  # pylint: disable=assignment-from-none
            elif isinstance(event_data_obj, ThreadRun):
                func_rt = self.on_thread_run(event_data_obj)  # pylint: disable=assignment-from-none
            elif isinstance(event_data_obj, RunStep):
                func_rt = self.on_run_step(event_data_obj)  # pylint: disable=assignment-from-none
            elif isinstance(event_data_obj, RunStepDeltaChunk):
                func_rt = self.on_run_step_delta(event_data_obj)  # pylint: disable=assignment-from-none
            elif event_type == AgentStreamEvent.ERROR:
                func_rt = self.on_error(event_data_obj)  # pylint: disable=assignment-from-none
            elif event_type == AgentStreamEvent.DONE:
                func_rt = self.on_done()  # pylint: disable=assignment-from-none
            else:
                func_rt = self.on_unhandled_event(event_type, event_data_obj)  # pylint: disable=assignment-from-none
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Error in event handler for event '%s'", event_type)
        return event_type, event_data_obj, func_rt

    def on_message_delta(
        self, delta: "MessageDeltaChunk"  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle message delta events.

        :param MessageDeltaChunk delta: The message delta.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    def on_thread_message(
        self, message: "ThreadMessage"  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle thread message events.

        :param ThreadMessage message: The thread message.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    def on_thread_run(self, run: "ThreadRun") -> Optional[EventFunctionReturnT]:  # pylint: disable=unused-argument
        """Handle thread run events.

        :param ThreadRun run: The thread run.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    def on_run_step(self, step: "RunStep") -> Optional[EventFunctionReturnT]:  # pylint: disable=unused-argument
        """Handle run step events.

        :param RunStep step: The run step.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    def on_run_step_delta(
        self, delta: "RunStepDeltaChunk"  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle run step delta events.

        :param RunStepDeltaChunk delta: The run step delta.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    def on_error(self, data: str) -> Optional[EventFunctionReturnT]:  # pylint: disable=unused-argument
        """Handle error events.

        :param str data: The error event's data.
        :rtype: Optional[EventFunctionReturnT]
        """
        return None

    def on_done(
        self,
    ) -> Optional[EventFunctionReturnT]:
        """Handle the completion of the stream."""
        return None

    def on_unhandled_event(
        self, event_type: str, event_data: str  # pylint: disable=unused-argument
    ) -> Optional[EventFunctionReturnT]:
        """Handle any unhandled event types.

        :param str event_type: The event type.
        :param Any event_data: The event's data.
        """
        return None


class AsyncAgentRunStream(Generic[BaseAsyncAgentEventHandlerT]):
    def __init__(
        self,
        response_iterator: AsyncIterator[bytes],
        submit_tool_outputs: Callable[[ThreadRun, BaseAsyncAgentEventHandlerT, bool], Awaitable[Any]],
        event_handler: BaseAsyncAgentEventHandlerT,
    ):
        self.response_iterator = response_iterator
        self.event_handler = event_handler
        self.submit_tool_outputs = submit_tool_outputs
        self.event_handler.initialize(
            self.response_iterator,
            cast(Callable[[ThreadRun, BaseAsyncAgentEventHandler, bool], Awaitable[Any]], submit_tool_outputs),
        )

    async def __aenter__(self):
        return self.event_handler

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        close_method = getattr(self.response_iterator, "close", None)
        if callable(close_method):
            result = close_method()
            if asyncio.iscoroutine(result):
                await result


class AgentRunStream(Generic[BaseAgentEventHandlerT]):
    def __init__(
        self,
        response_iterator: Iterator[bytes],
        submit_tool_outputs: Callable[[ThreadRun, BaseAgentEventHandlerT, bool], Any],
        event_handler: BaseAgentEventHandlerT,
    ):
        self.response_iterator = response_iterator
        self.event_handler = event_handler
        self.submit_tool_outputs = submit_tool_outputs
        self.event_handler.initialize(
            self.response_iterator,
            cast(Callable[[ThreadRun, BaseAgentEventHandler, bool], Any], submit_tool_outputs),
        )

    def __enter__(self):
        return self.event_handler

    def __exit__(self, exc_type, exc_val, exc_tb):
        close_method = getattr(self.response_iterator, "close", None)
        if callable(close_method):
            close_method()


def _is_valid_connection_id(connection_id: str) -> bool:
    """
    Validates if a string matches the Azure connection resource ID format.

    The expected format is:
    "/subscriptions/<AZURE_SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/
    providers/<AZURE_PROVIDER>/accounts/<ACCOUNT_NAME>/projects/<PROJECT_NAME>/
    connections/<CONNECTION_NAME>"

    :param connection_id: The connection ID string to validate
    :type connection_id: str
    :return: True if the string matches the expected format, False otherwise
    :rtype: bool
    """
    pattern = (
        r"^/subscriptions/[^/]+/resourceGroups/[^/]+/providers/[^/]+/accounts/[^/]+/projects/[^/]+/connections/[^/]+$"
    )

    # Check if the string matches the pattern
    if re.match(pattern, connection_id):
        return True
    return False


__all__: List[str] = [
    "AgentEventHandler",
    "AgentRunStream",
    "AsyncAgentRunStream",
    "AsyncFunctionTool",
    "AsyncToolSet",
    "AzureAISearchTool",
    "AzureFunctionTool",
    "BaseAsyncAgentEventHandler",
    "BaseAgentEventHandler",
    "BrowserAutomationTool",
    "ComputerUseTool",
    "CodeInterpreterTool",
    "ConnectedAgentTool",
    "DeepResearchTool",
    "AsyncAgentEventHandler",
    "FileSearchTool",
    "FunctionTool",
    "McpTool",
    "OpenApiTool",
    "BingGroundingTool",
    "FabricTool",
    "SharepointTool",
    "BingCustomSearchTool",
    "StreamEventData",
    "AzureAISearchTool",
    "Tool",
    "ToolSet",
    "BaseAsyncAgentEventHandlerT",
    "BaseAgentEventHandlerT",
    "ThreadMessage",
    "MessageTextFileCitationAnnotation",
    "MessageDeltaChunk",
    "MessageAttachment",
    "RunHandler",
    "AsyncRunHandler",
    "get_tool_resources",
    "get_tool_definitions",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
