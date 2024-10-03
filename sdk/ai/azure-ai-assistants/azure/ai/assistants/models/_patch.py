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
from typing import AsyncIterator, List, Dict, Any, Type, Optional, Iterator, Tuple, get_origin

import inspect, json, logging


# Define type_map to translate Python type annotations to JSON Schema types
type_map = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "bytes": "string",      # Typically encoded as base64-encoded strings in JSON
    "NoneType": "null",
    "datetime": "string",   # Use format "date-time"
    "date": "string",       # Use format "date"
    "UUID": "string",       # Use format "uuid"
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

            function_def = FunctionDefinition(name=name, description=description, parameters={"type": "object", "properties": properties, "required": list(params.keys())})
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

    def validate_tool_type(self, tool_type: Type[Tool]) -> None:
        """
        Validate the type of the tool.

        :param tool_type: The type of the tool to validate.
        :raises ValueError: If the tool type is not a subclass of Tool.
        """
        if isinstance(tool_type, AsyncFunctionTool):
            raise ValueError("AsyncFunctionTool is not supported in ToolSet.  To use async functions, use AsyncToolSet and AssistantClient in azure.ai.assistants.aio.")

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

class AsyncToolSet(ToolSet):
    
    def validate_tool_type(self, tool_type: Type[Tool]) -> None:
        """
        Validate the type of the tool.

        :param tool_type: The type of the tool to validate.
        :raises ValueError: If the tool type is not a subclass of Tool.
        """
        if isinstance(tool_type, FunctionTool):
            raise ValueError("FunctionTool is not supported in AsyncToolSet.  Please use AsyncFunctionTool instead and provide sync and/or async function(s).")

    
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
    
    
class AsyncAssistantEventHandler:

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


class BaseAssistantRunStream:            
    def __enter__(self):
        return self



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

        return event_type, event_data_obj


class AsyncAssistantRunStream(BaseAssistantRunStream, AsyncIterator[Tuple[str, Any]]):
    def __init__(
        self,
        response_iterator: AsyncIterator[bytes],
        event_handler: Optional[AsyncAssistantEventHandler] = None,
    ):
        self.response_iterator = response_iterator
        self.event_handler = event_handler
        self.done = False
        self.buffer = ""
        
    async def __aenter__(self):
        return self
            
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        close_method = getattr(self.response_iterator, "close", None)
        if callable(close_method):
            await close_method()   
        
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
                        return await self.process_event(event_data_str)
                raise StopAsyncIteration

            while "\n\n" in self.buffer:
                event_data_str, self.buffer = self.buffer.split("\n\n", 1)
                return await self.process_event(event_data_str)
            
    async def process_event(self, event_data_str: str) -> Tuple[str, Any]:
        event_type, event_data_obj = super().process_event(event_data_str)

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
                elif event_type == AssistantStreamEvent.ERROR:
                    await self.event_handler.on_error(event_data_obj)
                elif event_type == AssistantStreamEvent.DONE:
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


class AssistantRunStream(BaseAssistantRunStream, Iterator[Tuple[str, Any]]):
    def __init__(
        self,
        response_iterator: Iterator[bytes],
        event_handler: Optional[AssistantEventHandler] = None,
    ):
        self.response_iterator = response_iterator
        self.event_handler = event_handler
        self.done = False
        self.buffer = ""
        
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
                        return self.process_event(event_data_str)
                raise StopIteration

            while "\n\n" in self.buffer:
                event_data_str, self.buffer = self.buffer.split("\n\n", 1)
                return self.process_event(event_data_str)

    def process_event(self, event_data_str: str) -> Tuple[str, Any]:
        event_type, event_data_obj = super().process_event(event_data_str)

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
                    self.event_handler.on_error(event_data_obj)
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
    "AsyncAssistantEventHandler",
    "AssistantEventHandler",
    "AsyncAssistantRunStream",
    "AssistantRunStream",
    "AsyncFunctionTool",
    "AsyncToolSet",
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
