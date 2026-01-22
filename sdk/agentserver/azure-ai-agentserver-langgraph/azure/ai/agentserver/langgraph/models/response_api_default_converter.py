# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, AsyncIterable, AsyncIterator, Dict, Optional, Union

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, StateSnapshot, StreamMode

from azure.ai.agentserver.core.models import Response, ResponseStreamEvent
from .human_in_the_loop_helper import HumanInTheLoopHelper
from .human_in_the_loop_json_helper import HumanInTheLoopJsonHelper
from .response_api_converter import GraphInputArguments, ResponseAPIConverter
from .response_api_non_stream_response_converter import (ResponseAPIMessagesNonStreamResponseConverter,
                                                         ResponseAPINonStreamResponseConverter)
from .response_api_request_converter import ResponseAPIMessageRequestConverter, ResponseAPIRequestConverter
from .response_api_stream_response_converter import ResponseAPIMessagesStreamResponseConverter
from .._context import LanggraphRunContext


class ResponseAPIDefaultConverter(ResponseAPIConverter):
    """
    Default implementation of ResponseAPIConverter for LangGraph input/output <-> Response API.
    Orchestrates the conversions using default converters and HITL helper.
    """
    def __init__(self,
            graph: CompiledStateGraph,
            create_request_converter: Callable[[LanggraphRunContext], ResponseAPIRequestConverter] | None = None,
            create_stream_response_converter: Callable[
                                                  [LanggraphRunContext],
                                                  ResponseAPIMessagesStreamResponseConverter
                                              ] | None = None,
            create_non_stream_response_converter: Callable[
                                                      [LanggraphRunContext],
                                                      ResponseAPINonStreamResponseConverter
                                                  ] | None = None,
            create_human_in_the_loop_helper: Callable[[LanggraphRunContext], HumanInTheLoopHelper] | None = None):
        self._graph = graph
        self._custom_request_converter_factory = create_request_converter
        self._custom_stream_response_converter_factory = create_stream_response_converter
        self._custom_non_stream_response_converter_factory = create_non_stream_response_converter
        self._custom_human_in_the_loop_helper_factory = create_human_in_the_loop_helper

    async def convert_request(self, context: LanggraphRunContext) -> GraphInputArguments:
        prev_state = await self._aget_state(context)
        input_data = self._convert_request_input(context, prev_state)
        stream_mode = self.get_stream_mode(context)
        return GraphInputArguments(
            input=input_data,
            stream_mode=stream_mode,
            config={},
            context=context,
        )

    async def convert_response_non_stream(
            self, output: Union[dict[str, Any], Any], context: LanggraphRunContext) -> Response:
        agent_run_context = context.agent_run
        converter = self._create_non_stream_response_converter(context)
        converted_output = converter.convert(output)

        agent_id = agent_run_context.get_agent_id_object()
        conversation = agent_run_context.get_conversation_object()
        response = Response(  # type: ignore[call-overload]
            object="response",
            id=agent_run_context.response_id,
            agent=agent_id,
            conversation=conversation,
            metadata=agent_run_context.request.get("metadata"),
            created_at=int(time.time()),
            output=converted_output,
        )
        return response

    async def convert_response_stream(  # type: ignore[override]
        self,
        output: AsyncIterator[Union[Dict[str, Any], Any]],
        context: LanggraphRunContext,
    ) -> AsyncIterable[ResponseStreamEvent]:
        converter = self._create_stream_response_converter(context)
        async for event in output:
            converted_output = converter.convert(event)
            for e in converted_output:
                yield e

        state = await self._aget_state(context)
        finalized_output = converter.finalize(state)  # finalize the response with graph state after stream
        for event in finalized_output:
            yield event

    def get_stream_mode(self, context: LanggraphRunContext) -> StreamMode:
        if context.agent_run.stream:
            return "messages"
        return "updates"

    def _create_request_converter(self, context: LanggraphRunContext) -> ResponseAPIRequestConverter:
        if self._custom_request_converter_factory:
            return self._custom_request_converter_factory(context)
        data = context.agent_run.request
        return ResponseAPIMessageRequestConverter(data)

    def _create_stream_response_converter(
        self, context: LanggraphRunContext
    ) -> ResponseAPIMessagesStreamResponseConverter:
        if self._custom_stream_response_converter_factory:
            return self._custom_stream_response_converter_factory(context)
        hitl_helper = self._create_human_in_the_loop_helper(context)
        return ResponseAPIMessagesStreamResponseConverter(context, hitl_helper=hitl_helper)

    def _create_non_stream_response_converter(
        self, context: LanggraphRunContext
    ) -> ResponseAPINonStreamResponseConverter:
        if self._custom_non_stream_response_converter_factory:
            return self._custom_non_stream_response_converter_factory(context)
        hitl_helper = self._create_human_in_the_loop_helper(context)
        return ResponseAPIMessagesNonStreamResponseConverter(context, hitl_helper)

    def _create_human_in_the_loop_helper(self, context: LanggraphRunContext) -> HumanInTheLoopHelper:
        if self._custom_human_in_the_loop_helper_factory:
            return self._custom_human_in_the_loop_helper_factory(context)
        return HumanInTheLoopJsonHelper(context)

    def _convert_request_input(
        self, context: LanggraphRunContext, prev_state: Optional[StateSnapshot]
    ) -> Union[Dict[str, Any], Command]:
        """
        Convert the CreateResponse input to LangGraph input format, handling HITL if needed.

        :param context: The context for the agent run.
        :type context: LanggraphRunContext
        :param prev_state: The previous LangGraph state snapshot.
        :type prev_state: Optional[StateSnapshot]

        :return: The converted LangGraph input data or Command for HITL.
        :rtype: Union[Dict[str, Any], Command]
        """
        hitl_helper = self._create_human_in_the_loop_helper(context)
        if hitl_helper:
            command = hitl_helper.validate_and_convert_human_feedback(
                prev_state, context.agent_run.request.get("input")
            )
            if command is not None:
                return command
        converter = self._create_request_converter(context)
        return converter.convert()

    async def _aget_state(self, context: LanggraphRunContext) -> Optional[StateSnapshot]:
        config = RunnableConfig(
            configurable={"thread_id": context.agent_run.conversation_id},
        )
        if self._graph.checkpointer:
            state = await self._graph.aget_state(config=config)
            return state
        return None
