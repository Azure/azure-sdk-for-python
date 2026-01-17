# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

from typing import Awaitable, Callable, List

from azure.ai.agentserver.core.tools import FoundryToolLike
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.agents.middleware.types import ModelCallResult
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

from ._chat_model import FoundryToolLateBindingChatModel
from ._tool_node import FoundryToolCallWrapper


class FoundryToolBindingMiddleware(AgentMiddleware):
    """Middleware that binds foundry tools to tool calls in the agent.

    :param foundry_tools: A list of foundry tools to bind.
    :type foundry_tools: List[FoundryToolLike]
    """

    def __init__(self, foundry_tools: List[FoundryToolLike]):
        super().__init__()
        self._foundry_tools_to_bind = foundry_tools

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
        return super().wrap_model_call(self._wrap_model(request), handler)

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
        return await super().awrap_model_call(self._wrap_model(request), handler)

    def _wrap_model(self, request: ModelRequest) -> ModelRequest:
        """Wrap the model in the request with a FoundryToolBindingChatModel.

        :param request: The model request.
        :type request: ModelRequest
        :return: The modified model request.
        :rtype: ModelRequest
        """
        wrapper = FoundryToolLateBindingChatModel(request.model, self._foundry_tools_to_bind)
        return request.override(model=wrapper)

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
        return FoundryToolCallWrapper(self._foundry_tools_to_bind).call_tool(request, handler)

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
        return await FoundryToolCallWrapper(self._foundry_tools_to_bind).call_tool_async(request, handler)
