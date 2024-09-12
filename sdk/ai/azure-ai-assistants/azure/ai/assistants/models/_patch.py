# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ._enums import AssistantStreamEvent
from ._models import MessageDeltaChunk, ThreadRun, RunStep, ThreadMessage, RunStepDeltaChunk
from ._models import FunctionToolDefinition, FunctionDefinition, ToolDefinition, ToolResources, FileSearchToolDefinition, FileSearchToolResource, CodeInterpreterToolDefinition, CodeInterpreterToolResource

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import inspect, json


class Tool(ABC):
    """
    An abstract class representing a tool that can be used by an assistant.
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
    def execute(self, tool_calls: List[Any]) -> Any:
        """Execute tool operations based on tool_calls provided."""
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

    def _build_function_definitions(self, functions: Dict[str, Any]) -> List[FunctionToolDefinition]:
        specs = []
        type_map = {"str": "string", "int": "integer", "float": "number", "bool": "boolean", "default": "string"}

        for name, func in functions.items():
            sig = inspect.signature(func)
            params = sig.parameters
            docstring = inspect.getdoc(func)
            description = docstring.split("\n")[0] if docstring else "No description"

            properties = {
                param_name: {
                    "type": type_map.get(
                        param.annotation.__name__ if param.annotation != inspect._empty else "default",
                        type_map["default"],
                    ),
                    "description": param.annotation.__doc__ if param.annotation != inspect._empty else None,
                }
                for param_name, param in params.items()
            }

            function_def = FunctionDefinition(
                name=name,
                description=description,
                parameters={"type": "object", "properties": properties, "required": list(params.keys())},
            )

            tool_def = FunctionToolDefinition(function=function_def)
            specs.append(tool_def)
        return specs

    def execute(self, tool_calls: List[Any]) -> Any:
        """
        Invoke a list of function calls with their specified arguments.

        :param tool_calls: A list of tool call objects, each containing a function name and arguments.
        :return: A list of tool outputs containing the results of the function calls.
        """
        tool_outputs = []

        for tool_call in tool_calls:
            function_response = str(self._handle_function_call(tool_call.function.name, tool_call.function.arguments))
            tool_output = {
                "tool_call_id": tool_call.id,
                "output": function_response,
            }
            tool_outputs.append(tool_output)

        return tool_outputs

    def _handle_function_call(self, function_name, arguments):
        if function_name in self._functions:
            function = self._functions[function_name]

            try:
                parsed_arguments = json.loads(arguments)
            except json.JSONDecodeError:
                parsed_arguments = {}

            if isinstance(parsed_arguments, dict):
                if not parsed_arguments:
                    return function()
                else:
                    try:
                        return function(**parsed_arguments)
                    except TypeError as e:
                        return None
            else:
                return None

    @property
    def definitions(self) -> List[FunctionToolDefinition]:
        """
        Get the function definitions.

        :return: A list of function definitions.
        """
        return self._definitions

    @property
    def resources(self) -> ToolResources:
        """
        Get the tool resources for the assistant.

        :return: An empty ToolResources as FunctionTool doesn't have specific resources.
        """
        return ToolResources()


class FileSearchTool(Tool):
    """
    A tool that searches for uploaded file information from the created vector stores.
    """

    def __init__(self):
        self.vector_store_ids = []

    def add_vector_store(self, store_id: str):
        """
        Add a vector store ID to the list of vector stores to search for files.
        """
        # TODO
        self.vector_store_ids.append(store_id)

    @property
    def definitions(self) -> List[FileSearchToolDefinition]:
        """
        Get the file search tool definitions.
        """
        return [FileSearchToolDefinition()]
    
    @property
    def resources(self) -> ToolResources:
        """
        Get the file search resources.       
        """
        return ToolResources(
            file_search=FileSearchToolResource(
                vector_store_ids=self.vector_store_ids
            )
        )

    def execute(self, tool_calls: List[Any]) -> Any:
        pass


class CodeInterpreterTool(Tool):
    """
    A tool that interprets code files uploaded to the assistant.
    """

    def __init__(self):
        self.file_ids = []

    def add_file(self, file_id: str):
        """
        Add a file ID to the list of files to interpret.

        :param file_id: The ID of the file to interpret.
        """
        # TODO
        self.file_ids.append(file_id)

    @property
    def definitions(self) -> List[CodeInterpreterToolDefinition]:
        """
        Get the code interpreter tool definitions.
        """
        return [CodeInterpreterToolDefinition()]

    @property
    def resources(self) -> ToolResources:
        """
        Get the code interpreter resources.
        """
        return ToolResources(
            code_interpreter=CodeInterpreterToolResource(
                file_ids=self.file_ids
            )
        )

    def execute(self, tool_calls: List[Any]) -> Any:
        pass


class ToolSet:
    """
    A collection of tools that can be used by an assistant.
    """

    def __init__(self):
        self.tools = []

    def add(self, tool: Tool):
        """
        Add a tool to the tool set.

        :param tool: The tool to add.
        """
        self.tools.append(tool)

    @property
    def definitions(self) -> List[ToolDefinition]:
        """
        Get the definitions for all tools in the tool set.
        """
        tools = []
        for tool in self.tools:
            tools.extend(tool.definitions)
        return tools

    @property
    def resources(self) -> Dict[str, Any]:
        """
        Get the resources for all tools in the tool set.
        """
        tool_resources = {}
        for tool in self.tools:
            resources = tool.resources
            for key, value in resources.items():
                if key in tool_resources:
                    if isinstance(tool_resources[key], dict) and isinstance(value, dict):
                        tool_resources[key].update(value)
                else:
                    tool_resources[key] = value
        return tool_resources

    def get_definitions_and_resources(self) -> Dict[str, Any]:
        """
        Get the definitions and resources for all tools in the tool set.

        :return: A dictionary containing the tool resources and definitions.
        """
        return {
            "tool_resources": self.resources,
            "tools": self.definitions,
        }

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Execute a tool operation based on the tool name provided.

        :param tool_name: The name of the tool to execute.
        :param params: The parameters to pass to the tool
        :return: The result of the tool operation.
        """
        for tool in self.tools:
            tool_definitions = tool.definitions
            if any(tool_name in definition.type for definition in tool_definitions):
                return tool.execute(params)
        raise ValueError(f"Tool {tool_name} not found.")


class AssistantRunStream:
    def __init__(self, response_iterator):
        self.response_iterator = response_iterator
        self.buffer = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            chunk = next(self.response_iterator, None)
            if chunk is None:
                raise StopIteration

            self.buffer += chunk.decode("utf-8")
            if "\n\n" in self.buffer:
                event_data_str, self.buffer = self.buffer.split("\n\n", 1)
                return self.process_event(event_data_str)

    def process_event(self, event_data_str: str):
        event_lines = event_data_str.strip().split("\n")
        event_type = None
        event_data = ""

        for line in event_lines:
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                event_data = line.split(":", 1)[1].strip()

        try:
            parsed_data = json.loads(event_data)
        except json.JSONDecodeError:
            # Return the raw data if it's not valid JSON
            return event_type, event_data

        # TODO: Workaround for service bug: Rename 'expires_at' to 'expired_at'
        if event_type.startswith("thread.run.step") and "expires_at" in parsed_data:
            parsed_data["expired_at"] = parsed_data.pop("expires_at")

        # Map to the appropriate class instance
        if event_type in {
            AssistantStreamEvent.THREAD_RUN_CREATED,
            AssistantStreamEvent.THREAD_RUN_QUEUED,
            AssistantStreamEvent.THREAD_RUN_IN_PROGRESS,
            AssistantStreamEvent.THREAD_RUN_REQUIRES_ACTION,
            AssistantStreamEvent.THREAD_RUN_COMPLETED,
            AssistantStreamEvent.THREAD_RUN_FAILED,
            AssistantStreamEvent.THREAD_RUN_CANCELLING,
            AssistantStreamEvent.THREAD_RUN_CANCELLED,
            AssistantStreamEvent.THREAD_RUN_EXPIRED,
        }:
            return event_type, ThreadRun(**parsed_data)
        elif event_type in {
            AssistantStreamEvent.THREAD_RUN_STEP_CREATED,
            AssistantStreamEvent.THREAD_RUN_STEP_IN_PROGRESS,
            AssistantStreamEvent.THREAD_RUN_STEP_COMPLETED,
            AssistantStreamEvent.THREAD_RUN_STEP_FAILED,
            AssistantStreamEvent.THREAD_RUN_STEP_CANCELLED,
            AssistantStreamEvent.THREAD_RUN_STEP_EXPIRED,
        }:
            return event_type, RunStep(**parsed_data)
        elif event_type in {
            AssistantStreamEvent.THREAD_MESSAGE_CREATED,
            AssistantStreamEvent.THREAD_MESSAGE_IN_PROGRESS,
            AssistantStreamEvent.THREAD_MESSAGE_COMPLETED,
            AssistantStreamEvent.THREAD_MESSAGE_INCOMPLETE,
        }:
            return event_type, ThreadMessage(**parsed_data)
        elif event_type == AssistantStreamEvent.THREAD_MESSAGE_DELTA:
            return event_type, MessageDeltaChunk(**parsed_data)
        elif event_type == AssistantStreamEvent.THREAD_RUN_STEP_DELTA:
            return event_type, RunStepDeltaChunk(**parsed_data)

        return event_type, parsed_data


__all__: List[str] = [
    "AssistantFunctions",
    "AssistantRunStream",
    "FunctionTool",
    "FileSearchTool",
    "CodeInterpreterTool",
    "ToolSet",
    "Tool",
    "ToolSet",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
