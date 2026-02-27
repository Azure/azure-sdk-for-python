# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, AsyncIterable, AsyncIterator, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, StateSnapshot, StreamMode

from azure.ai.agentserver.core.logger import get_logger, get_project_endpoint
from azure.ai.agentserver.core.models import Response, ResponseStreamEvent
from .human_in_the_loop_helper import HumanInTheLoopHelper
from .human_in_the_loop_json_helper import HumanInTheLoopJsonHelper
from .response_api_converter import GraphInputArguments, ResponseAPIConverter
from .response_api_non_stream_response_converter import (ResponseAPIMessagesNonStreamResponseConverter,
                                                         ResponseAPINonStreamResponseConverter)
from .response_api_request_converter import (
    ResponseAPIMessageRequestConverter,
    ResponseAPIRequestConverter,
    convert_item_resource_to_message,
)
from .response_api_stream_response_converter import ResponseAPIMessagesStreamResponseConverter
from ._history import filter_incomplete_tool_calls, merge_messages_without_duplicates, normalize_content
from .._context import LanggraphRunContext

logger = get_logger()


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
        input_data = await self._convert_request_input_with_history(context, prev_state)
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

    async def _convert_request_input_with_history(
        self, context: LanggraphRunContext, prev_state: Optional[StateSnapshot]
    ) -> Union[Dict[str, Any], Command]:
        """
        Convert the CreateResponse input to LangGraph input format, merging historical items
        from AIProjectClient when no checkpoint exists.

        :param context: The context for the agent run.
        :type context: LanggraphRunContext
        :param prev_state: The previous LangGraph state snapshot.
        :type prev_state: Optional[StateSnapshot]

        :return: The converted LangGraph input data or Command for HITL.
        :rtype: Union[Dict[str, Any], Command]
        """
        conversation_id = context.agent_run.conversation_id

        # First, handle HITL if applicable
        hitl_helper = self._create_human_in_the_loop_helper(context)
        if hitl_helper:
            command = hitl_helper.validate_and_convert_human_feedback(
                prev_state, context.agent_run.request.get("input")
            )
            if command is not None:
                logger.info(f"HITL command detected for conversation {conversation_id}")
                return command

        # Convert current request input
        converter = self._create_request_converter(context)
        current_input = converter.convert()

        # Check if checkpoint exists
        has_checkpoint = prev_state is not None and prev_state.values is not None and len(prev_state.values) > 0
        if has_checkpoint:
            logger.info(f"Checkpoint found for conversation {conversation_id}, using existing state")
            return current_input

        # No checkpoint - try to fetch historical items from AIProjectClient
        if not conversation_id:
            logger.debug("No conversation_id provided, skipping historical items fetch")
            return current_input

        logger.info(f"No checkpoint found for conversation {conversation_id}, fetching historical items")
        historical_messages = await self._fetch_historical_items(conversation_id)

        if not historical_messages:
            logger.info(f"No historical items found for conversation {conversation_id}")
            return current_input

        # Merge historical messages with current input, avoiding duplicates
        current_messages = current_input.get("messages", [])
        merged_messages = merge_messages_without_duplicates(
            historical_messages, current_messages, conversation_id
        )

        # Filter again after merge to catch any incomplete tool call sequences
        # that may result from the deduplication removing ToolMessages
        merged_messages = filter_incomplete_tool_calls(merged_messages)
        current_input["messages"] = merged_messages

        return current_input

    async def _fetch_historical_items(self, conversation_id: str) -> List[AnyMessage]:
        """
        Fetch historical conversation items from AIProjectClient and convert to LangGraph messages.

        :param conversation_id: The conversation ID to fetch items for.
        :type conversation_id: str

        :return: List of LangGraph messages converted from historical items.
        :rtype: List[AnyMessage]
        """
        endpoint = get_project_endpoint(logger=logger)
        if not endpoint:
            logger.warning("No project endpoint configured, cannot fetch historical items")
            return []

        try:
            # Import here to avoid circular imports and make dependency optional
            from openai import AsyncOpenAI
            from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

            logger.debug(f"Creating AsyncOpenAI client for endpoint: {endpoint}/openai")

            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")
            openai_client = AsyncOpenAI(
                base_url=f"{endpoint}/openai",
                api_key=token_provider,
                default_query = {"api-version": "2025-11-15-preview"},
            )
            items = []
            async for item in openai_client.conversations.items.list(conversation_id):
                items.append(item)
            items.reverse()

            logger.info(f"Fetched {len(items)} historical items from conversation {conversation_id}")

            # Convert items to LangGraph messages
            messages = []
            for item in items:
                item_dict = item.model_dump() if hasattr(item, 'model_dump') else dict(item)
                message = convert_item_resource_to_message(item_dict)
                if message is not None:
                    messages.append(message)

            # Filter out incomplete tool call sequences
            messages = filter_incomplete_tool_calls(messages)

            return messages

        except ImportError as e:
            logger.warning(f"OpenAI or Azure Identity not available, cannot fetch historical items: {e}", exc_info=True)
            return []
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(f"Failed to fetch historical items for conversation {conversation_id}: {e}", exc_info=True)
            return []

    def _merge_messages_without_duplicates(
        self,
        historical_messages: List[AnyMessage],
        current_messages: List[AnyMessage],
        conversation_id: str,
    ) -> List[AnyMessage]:
        """Delegate to :func:`merge_messages_without_duplicates`."""
        return merge_messages_without_duplicates(historical_messages, current_messages, conversation_id)

    async def _aget_state(self, context: LanggraphRunContext) -> Optional[StateSnapshot]:
        thread_id = context.agent_run.conversation_id
        if not thread_id:
            logger.debug("No conversation_id provided, skipping checkpoint lookup")
            return None
        config = RunnableConfig(
            configurable={"thread_id": thread_id},
        )
        if self._graph.checkpointer:
            logger.debug(f"Checking for existing checkpoint for conversation {thread_id}")
            state = await self._graph.aget_state(config=config)
            if state and state.values:
                logger.debug(f"Checkpoint state retrieved for conversation {thread_id}")
            else:
                logger.debug(f"No checkpoint state found for conversation {thread_id}")
            return state
        logger.debug("No checkpointer configured for graph, skipping checkpoint lookup")
        return None

    def _filter_incomplete_tool_calls(self, messages: List[AnyMessage]) -> List[AnyMessage]:
        """Delegate to :func:`filter_incomplete_tool_calls`."""
        return filter_incomplete_tool_calls(messages)

    def _normalize_content(self, content: Any) -> str:
        """Delegate to :func:`normalize_content`."""
        return normalize_content(content)
