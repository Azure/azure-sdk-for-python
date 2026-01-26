# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Awaitable, Callable, ClassVar, List

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.agents.middleware.types import ModelCallResult
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, Tool
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

from azure.ai.agentserver.core.tools import FoundryToolLike

from ._chat_model import FoundryToolLateBindingChatModel
from ._tool_node import FoundryToolCallWrapper


class FoundryToolBindingMiddleware(AgentMiddleware):
    """Middleware that binds foundry tools to tool calls in the agent.

    :param foundry_tools: A list of foundry tools to bind.
    :type foundry_tools: List[FoundryToolLike]
    """
    _DummyToolName: ClassVar[str] = "__dummy_tool_by_foundry_middleware__"

    def __init__(self, foundry_tools: List[FoundryToolLike]):
        super().__init__()

        # to ensure `create_agent()` will create a tool node when there are foundry tools to bind
        # this tool will never be bound to model and called
        self.tools = [self._dummy_tool()] if foundry_tools else []

        self._foundry_tools_to_bind = foundry_tools
        self._tool_call_wrapper = FoundryToolCallWrapper(self._foundry_tools_to_bind)

    @classmethod
    def _dummy_tool(cls) -> BaseTool:
        return Tool(name=cls._DummyToolName,
                    func=lambda x: None,
                    description="__dummy_tool_by_foundry_middleware__")

    def wrap_model_call(self, request: ModelRequest,
                        handler: Callable[[ModelRequest], ModelResponse]) -> ModelCallResult:
        """Wrap the model call to use a FoundryToolBindingChatModel.

        :param request: The model request.
        :type request: ModelRequest
        :param handler: The model call handler.
        :type handler: Callable[[ModelRequest], ModelResponse]
        :return: The model call result.
        :rtype: ModelCallResult
        """
        return handler(self._wrap_model(request))

    async def awrap_model_call(self, request: ModelRequest,
                               handler: Callable[[ModelRequest], Awaitable[ModelResponse]]) -> ModelCallResult:
        """Asynchronously wrap the model call to use a FoundryToolBindingChatModel.

        :param request: The model request.
        :type request: ModelRequest
        :param handler: The model call handler.
        :type handler: Callable[[ModelRequest], Awaitable[ModelResponse]]
        :return: The model call result.
        :rtype: ModelCallResult
        """
        return await handler(self._wrap_model(request))

    def _wrap_model(self, request: ModelRequest) -> ModelRequest:
        """Wrap the model in the request with a FoundryToolBindingChatModel.

        :param request: The model request.
        :type request: ModelRequest
        :return: The modified model request.
        :rtype: ModelRequest
        """
        if not self._foundry_tools_to_bind:
            return request
        wrapper = FoundryToolLateBindingChatModel(request.model, request.runtime, self._foundry_tools_to_bind)
        return request.override(model=wrapper, tools=self._remove_dummy_tool(request))

    def _remove_dummy_tool(self, request: ModelRequest) -> list:
        """Remove the dummy tool from the request's tools if present.

        :param request: The model request.
        :type request: ModelRequest
        :return: The list of tools without the dummy tool.
        :rtype: list
        """
        if not request.tools:
            return []
        return [tool for tool in request.tools if not isinstance(tool, Tool) or tool.name != self._DummyToolName]

    def wrap_tool_call(self, request: ToolCallRequest,
                       handler: Callable[[ToolCallRequest], ToolMessage | Command]) -> ToolMessage | Command:
        """Wrap the tool call to use FoundryToolCallWrapper.

        :param request: The tool call request.
        :type request: ToolCallRequest
        :param handler: The tool call handler.
        :type handler: Callable[[ToolCallRequest], ToolMessage | Command]
        :return: The tool call result.
        :rtype: ToolMessage | Command
        """
        return self._tool_call_wrapper.call_tool(request, handler)

    async def awrap_tool_call(
            self,
            request: ToolCallRequest,
            handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]]) -> ToolMessage | Command:
        """Asynchronously wrap the tool call to use FoundryToolCallWrapper.

        :param request: The tool call request.
        :type request: ToolCallRequest
        :param handler: The tool call handler.
        :type handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]]
        :return: The tool call result.
        :rtype: ToolMessage | Command
        """
        return await self._tool_call_wrapper.call_tool_async(request, handler)
