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
    cast,
    get_args,
    get_origin,
    overload,
)

from ._enums import AgentStreamEvent, AzureAISearchQueryType
from ._models import (
    AISearchIndexResource,
    AzureAISearchToolResource,
    AzureAISearchToolDefinition,
    AzureFunctionDefinition,
    AzureFunctionStorageQueue,
    AzureFunctionToolDefinition,
    AzureFunctionBinding,
    BingGroundingToolDefinition,
    CodeInterpreterToolDefinition,
    CodeInterpreterToolResource,
    ConnectedAgentToolDefinition,
    ConnectedAgentDetails,
    FileSearchToolDefinition,
    FileSearchToolResource,
    FunctionDefinition,
    FunctionToolDefinition,
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
    BingGroundingSearchConfiguration,
    BingGroundingSearchToolParameters,
    SubmitToolOutputsAction,
    ThreadRun,
    ToolDefinition,
    ToolResources,
    MessageDeltaTextContent,
    VectorStoreDataSource,
)

from ._models import MessageDeltaChunk as MessageDeltaChunkGenerated
from ._models import ThreadMessage as ThreadMessageGenerated
from ._models import MessageAttachment as MessageAttachmentGenerated

from .. import types as _types


logger = logging.getLogger(__name__)

StreamEventData = Union["MessageDeltaChunk", "ThreadMessage", ThreadRun, RunStep, str]


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
        index_asset_id: str = "",
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
        :type filter: str
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
        description: str,
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
        description: str,
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


class BingGroundingTool(Tool[BingGroundingToolDefinition]):
    """
    A tool that searches for information using Bing.
    """

    def __init__(self, connection_id: str, market: str = "", set_lang: str = "", count: int = 5, freshness: str = ""):
        """
        Initialize Bing Custom Search with a connection_id.

        :param connection_id: Connection ID used by tool. Bing Custom Search tools allow only one connection.
        :param market:
        :param set_lang:
        :param count:
        :param freshness:
        """
        self.connection_ids = [
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
                bing_grounding=BingGroundingSearchToolParameters(search_configurations=self.connection_ids)
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
                logger.info("Tool of type %s removed from the ToolSet.", tool_type.__name__)
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

    def get_tool(self, tool_type: Type[ToolT]) -> ToolT:
        """
        Get a tool of the specified type from the tool set.

        :param Type[Tool] tool_type: The type of tool to get.
        :return: The tool of the specified type.
        :rtype: Tool
        :raises ValueError: If a tool of the specified type is not found.
        """
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
        tool_outputs = []

        for tool_call in tool_calls:
            try:
                if tool_call.type == "function":
                    tool = self.get_tool(FunctionTool)
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

    async def _execute_single_tool_call(self, tool_call: Any):
        try:
            tool = self.get_tool(AsyncFunctionTool)
            output = await tool.execute(tool_call)
            return {"tool_call_id": tool_call.id, "output": str(output)}
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {"tool_call_id": tool_call.id, "output": str(e)}

    async def execute_tool_calls(self, tool_calls: List[Any]) -> Any:
        """
        Execute a tool of the specified type with the provided tool calls concurrently.

        :param List[Any] tool_calls: A list of tool calls to execute.
        :return: The output of the tool operations.
        :rtype: Any
        """

        # Execute all tool calls concurrently
        tool_outputs = await asyncio.gather(
            *[self._execute_single_tool_call(tc) for tc in tool_calls if tc.type == "function"]
        )

        return tool_outputs


EventFunctionReturnT = TypeVar("EventFunctionReturnT")
T = TypeVar("T")
BaseAsyncAgentEventHandlerT = TypeVar("BaseAsyncAgentEventHandlerT", bound="BaseAsyncAgentEventHandler")
BaseAgentEventHandlerT = TypeVar("BaseAgentEventHandlerT", bound="BaseAgentEventHandler")


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
    "CodeInterpreterTool",
    "ConnectedAgentTool",
    "AsyncAgentEventHandler",
    "FileSearchTool",
    "FunctionTool",
    "OpenApiTool",
    "BingGroundingTool",
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
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
