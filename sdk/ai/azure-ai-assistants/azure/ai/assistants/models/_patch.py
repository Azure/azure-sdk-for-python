# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ._enums import AssistantStreamEvent
from ._models import MessageDeltaChunk, ThreadRun, RunStep, ThreadMessage, RunStepDeltaChunk
from ._models import (
    FunctionToolDefinition, 
    FunctionDefinition, 
    ToolDefinition, 
    ToolResources, 
    FileSearchToolDefinition, 
    FileSearchToolResource, 
    CodeInterpreterToolDefinition, 
    CodeInterpreterToolResource, 
    RequiredFunctionToolCall
)

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type, Optional, Iterator, Tuple
import inspect, json, logging


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
    def execute(self, tool_call : Any) -> Any:
        """
        Execute the tool with the provided tool call.

        :param tool_call: The tool call to execute.
        :return: The output of the tool operations.
        """
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
                        param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "default",
                        type_map["default"],
                    ),
                    "description": param.annotation.__doc__ if param.annotation != inspect.Parameter.empty else None,
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

    def execute(self, tool_call: RequiredFunctionToolCall) -> Any:
        """
        Execute the function tool with the provided tool call information.

        :param tool_call: The tool call to execute.
        :return: The output of the tool operations.
        """
        function_name = tool_call.function.name
        arguments = tool_call.function.arguments
        return self._handle_function_call(function_name, arguments)
    
    def _handle_function_call(self, function_name: str, arguments: str) -> Any:
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

        try:
            return function(**parsed_arguments) if parsed_arguments else function()
        except TypeError as e:
            logging.error(f"Error executing function '{function_name}': {e}")
            raise

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

    def execute(self, tool_call: Any) -> Any:
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

    def execute(self, tool_call: Any) -> Any:
        pass


class ToolSet:
    """
    A collection of tools that can be used by an assistant.
    """

    def __init__(self):
        self._tools = []

    def add(self, tool: Tool):
        """
        Add a tool to the tool set.

        :param tool: The tool to add.
        """
        self._tools.append(tool)

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
    def resources(self) -> Dict[str, Any]:
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


class AssistantEventHandler:

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


class AssistantRunStream(Iterator[Tuple[str, Any]]):

    def __init__(self, response_iterator: Iterator[bytes], event_handler: Optional[AssistantEventHandler] = None):
        self.response_iterator = response_iterator
        self.buffer = ""
        self.event_handler = event_handler
        self.done = False

    def __enter__(self) -> "AssistantRunStream":
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        # Ensure resource cleanup
        close_method = getattr(self.response_iterator, "close", None)
        if callable(close_method):
            close_method()

    def __iter__(self) -> "AssistantRunStream":
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
                        return self.process_event(event_data_str)
                raise StopIteration

            while "\n\n" in self.buffer:
                event_data_str, self.buffer = self.buffer.split("\n\n", 1)
                return self.process_event(event_data_str)

    def process_event(self, event_data_str: str) -> Tuple[str, Any]:
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
        if (
            event_type.startswith("thread.run.step")
            and isinstance(parsed_data, dict)
            and "expires_at" in parsed_data
        ):
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
            event_data_obj = ThreadRun(**parsed_data) if isinstance(parsed_data, dict) else parsed_data
        elif event_type in {
            AssistantStreamEvent.THREAD_RUN_STEP_CREATED,
            AssistantStreamEvent.THREAD_RUN_STEP_IN_PROGRESS,
            AssistantStreamEvent.THREAD_RUN_STEP_COMPLETED,
            AssistantStreamEvent.THREAD_RUN_STEP_FAILED,
            AssistantStreamEvent.THREAD_RUN_STEP_CANCELLED,
            AssistantStreamEvent.THREAD_RUN_STEP_EXPIRED,
        }:
            event_data_obj = RunStep(**parsed_data) if isinstance(parsed_data, dict) else parsed_data
        elif event_type in {
            AssistantStreamEvent.THREAD_MESSAGE_CREATED,
            AssistantStreamEvent.THREAD_MESSAGE_IN_PROGRESS,
            AssistantStreamEvent.THREAD_MESSAGE_COMPLETED,
            AssistantStreamEvent.THREAD_MESSAGE_INCOMPLETE,
        }:
            event_data_obj = ThreadMessage(**parsed_data) if isinstance(parsed_data, dict) else parsed_data
        elif event_type == AssistantStreamEvent.THREAD_MESSAGE_DELTA:
            event_data_obj = MessageDeltaChunk(**parsed_data) if isinstance(parsed_data, dict) else parsed_data
        elif event_type == AssistantStreamEvent.THREAD_RUN_STEP_DELTA:
            event_data_obj = RunStepDeltaChunk(**parsed_data) if isinstance(parsed_data, dict) else parsed_data
        else:
            event_data_obj = parsed_data

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
                elif event_type == AssistantStreamEvent.ERROR:
                    self.event_handler.on_error(event_data)
                elif event_type == AssistantStreamEvent.DONE:
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
    "AssistantEventHandler",
    "AssistantRunStream",
    "FunctionTool",
    "FileSearchTool",
    "CodeInterpreterTool",
    "Tool",
    "ToolSet",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
