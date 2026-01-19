# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel, LanguageModelInput
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatResult
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.prebuilt import ToolNode

from azure.ai.agentserver.core.tools import FoundryToolLike
from ._tool_node import FoundryToolCallWrapper, FoundryToolNodeWrappers


class FoundryToolLateBindingChatModel(BaseChatModel):
    """A ChatModel that supports late binding of Foundry tools during invocation.

    This ChatModel allows you to specify Foundry tools that will be resolved and bound
    at the time of invocation, rather than at the time of model creation.

    :param delegate: The underlying chat model to delegate calls to.
    :type delegate: BaseChatModel
    :param foundry_tools: A list of Foundry tools to be resolved and bound during invocation.
    :type foundry_tools: List[FoundryToolLike]
    """

    def __init__(self, delegate: BaseChatModel, foundry_tools: List[FoundryToolLike]):
        super().__init__()
        self._delegate = delegate
        self._foundry_tools_to_bind = foundry_tools
        self._bound_tools: List[Dict[str, Any] | type | Callable | BaseTool] = []
        self._bound_kwargs: dict[str, Any] = {}

    @property
    def tool_node(self) -> ToolNode:
        """Get a ToolNode that uses this chat model's Foundry tool call wrappers.

        :return: A ToolNode with Foundry tool call wrappers.
        :rtype: ToolNode
        """
        return ToolNode([], **self.tool_node_wrapper)

    @property
    def tool_node_wrapper(self) -> FoundryToolNodeWrappers:
        """Get the Foundry tool call wrappers for this chat model.

        Example::
        >>> from langgraph.prebuilt import ToolNode
        >>> foundry_tool_bound_chat_model = FoundryToolLateBindingChatModel(...)
        >>> ToolNode([...], **foundry_tool_bound_chat_model.as_wrappers())

        :return: The Foundry tool call wrappers.
        :rtype: FoundryToolNodeWrappers
        """
        return FoundryToolCallWrapper(self._foundry_tools_to_bind).as_wrappers()

    def bind_tools(self,
                   tools: Sequence[
                       Dict[str, Any] | type | Callable | BaseTool  # noqa: UP006
                   ],
                   *,
                   tool_choice: str | None = None,
                   **kwargs: Any) -> Runnable[LanguageModelInput, AIMessage]:
        """Record tools to be bound later during invocation."""

        self._bound_tools.extend(tools)
        if tool_choice is not None:
            self._bound_kwargs["tool_choice"] = tool_choice
        self._bound_kwargs.update(kwargs)

        return self

    def _bound_delegate_for_call(self) -> Runnable[LanguageModelInput, AIMessage]:
        from .._context import LanggraphRunContext

        foundry_tools = LanggraphRunContext.get_current().tools.resolved_tools.get(self._foundry_tools_to_bind)
        all_tools = self._bound_tools.copy()
        all_tools.extend(foundry_tools)

        if not all_tools:
            return self._delegate

        bound_kwargs = self._bound_kwargs or {}
        return self._delegate.bind_tools(all_tools, **bound_kwargs)

    def invoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Any:
        return self._bound_delegate_for_call().invoke(input, config=config, **kwargs)

    async def ainvoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Any:
        return await self._bound_delegate_for_call().ainvoke(input, config=config, **kwargs)

    def stream(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any):
        yield from self._bound_delegate_for_call().stream(input, config=config, **kwargs)

    async def astream(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any):
        async for x in self._bound_delegate_for_call().astream(input, config=config, **kwargs):
            yield x

    @property
    def _llm_type(self) -> str:
        return f"foundry_tool_binding_model({getattr(self.delegate, '_llm_type', type(self.delegate).__name__)})"

    def _generate(self, messages: list[BaseMessage], stop: list[str] | None = None,
                  run_manager: CallbackManagerForLLMRun | None = None, **kwargs: Any) -> ChatResult:
        # should never be called as invoke/ainvoke/stream/astream are redirected to delegate
        raise NotImplementedError()

