# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Awaitable, Callable, List, TypedDict, Union

from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import AsyncToolCallWrapper, ToolCallRequest, ToolCallWrapper
from langgraph.types import Command

from azure.ai.agentserver.core.tools import FoundryToolLike

ToolInvocationResult = Union[ToolMessage, Command]
ToolInvocation = Callable[[ToolCallRequest], ToolInvocationResult]
AsyncToolInvocation = Callable[[ToolCallRequest], Awaitable[ToolInvocationResult]]


class FoundryToolNodeWrappers(TypedDict):
    """A TypedDict for Foundry tool node wrappers.

    Example::
        >>> from langgraph.prebuilt import ToolNode
        >>> call_wrapper = FoundryToolCallWrapper(...)
        >>> ToolNode([...], **call_wrapper.as_wrappers())

    :param wrap_tool_call: The synchronous tool call wrapper.
    :type wrap_tool_call: ToolCallWrapper
    :param awrap_tool_call: The asynchronous tool call wrapper.
    :type awrap_tool_call: AsyncToolCallWrapper
    """

    wrap_tool_call: ToolCallWrapper  # type: ignore[valid-type]

    awrap_tool_call: AsyncToolCallWrapper  # type: ignore[valid-type]


class FoundryToolCallWrapper:
    """A ToolCallWrapper that tries to resolve invokable foundry tools from context if tool is not resolved yet."""
    def __init__(self, foundry_tools: List[FoundryToolLike]):
        self._allowed_foundry_tools = foundry_tools

    def as_wrappers(self) -> FoundryToolNodeWrappers:
        """Get the wrappers as a TypedDict.

        :return: The wrappers as a TypedDict.
        :rtype: FoundryToolNodeWrappers
        """
        return FoundryToolNodeWrappers(
            wrap_tool_call=self.call_tool,
            awrap_tool_call=self.call_tool_async,
        )

    def call_tool(self, request: ToolCallRequest, invocation: ToolInvocation) -> ToolInvocationResult:
        """Call the tool, resolving foundry tools from context if necessary.

        :param request: The tool call request.
        :type request: ToolCallRequest
        :param invocation: The tool invocation function.
        :type invocation: ToolInvocation
        :return: The result of the tool invocation.
        :rtype: ToolInvocationResult
        """
        return invocation(self._maybe_calling_foundry_tool(request))

    async def call_tool_async(self, request: ToolCallRequest, invocation: AsyncToolInvocation) -> ToolInvocationResult:
        """Call the tool, resolving foundry tools from context if necessary.

        :param request: The tool call request.
        :type request: ToolCallRequest
        :param invocation: The tool invocation function.
        :type invocation: AsyncToolInvocation
        :return: The result of the tool invocation.
        :rtype: ToolInvocationResult
        """
        return await invocation(self._maybe_calling_foundry_tool(request))

    def _maybe_calling_foundry_tool(self, request: ToolCallRequest) -> ToolCallRequest:
        from .._context import LanggraphRunContext

        if (request.tool
                or not self._allowed_foundry_tools
                or (context := LanggraphRunContext.from_runtime(request.runtime)) is None):
            # tool is already resolved
            return request

        tool_name = request.tool_call["name"]
        for t in context.tools.resolved_tools.get(self._allowed_foundry_tools):
            if t.name == tool_name:
                return ToolCallRequest(
                    tool_call=request.tool_call,
                    tool=t,
                    state=request.state,
                    runtime=request.runtime,
                )
        return request
