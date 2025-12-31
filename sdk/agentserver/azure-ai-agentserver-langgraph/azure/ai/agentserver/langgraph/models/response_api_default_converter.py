import time
from typing import Any, AsyncGenerator, AsyncIterator, Dict, TypedDict, Union

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command, Interrupt, StateSnapshot
from langgraph.graph.state import CompiledStateGraph

from azure.ai.agentserver.core.models import Response, ResponseStreamEvent
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .response_api_request_converter import ResponseAPIRequestConverter, ResponseAPIMessageRequestConverter
from .response_api_stream_response_converter import ResponseAPIStreamResponseConverter, ResponseAPIMessagesStreamResponseConverter
from .response_api_non_stream_response_converter import ResponseAPINonStreamResponseConverter, ResponseAPIMessagesNonStreamResponseConverter
from .human_in_the_loop_helper import HumanInTheLoopHelper
from .human_in_the_loop_json_helper import HumanInTheLoopJsonHelper
from .response_api_converter import ResponseAPIConverter, GraphInputArguments

class ResponseAPIDefaultConverter(ResponseAPIConverter):
    """
    Default implementation of ResponseAPIConverter for LangGraph input/output <-> Response API.
    Orchestrates the conversions using default converters and HITL helper.
    """
    def __init__(self,
            graph: CompiledStateGraph,
            create_request_converter=None,
            create_stream_response_converter=None,
            create_non_stream_response_converter=None,
            create_human_in_the_loop_helper=None):
        self._graph = graph
        if create_request_converter:
            self._create_request_converter = create_request_converter
        if create_stream_response_converter:
            self._create_stream_response_converter = create_stream_response_converter
        if create_non_stream_response_converter:
            self._create_non_stream_response_converter = create_non_stream_response_converter
        if create_human_in_the_loop_helper:
            self._create_human_in_the_loop_helper = create_human_in_the_loop_helper

    async def convert_request(self, context: AgentRunContext) -> GraphInputArguments:
        prev_state = await self._aget_state(context)
        input_data = self._convert_request_input(context, prev_state)
        stream_mode = self.get_stream_mode(context)
        return GraphInputArguments({
            "input": input_data,
            "stream_mode": stream_mode})

    async def convert_response_non_stream(self, output: Any, context: AgentRunContext) -> Response:
        converter = self._create_non_stream_response_converter(context)
        output = converter.convert(output)

        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()
        response = Response(
            object="response",
            id=context.response_id,
            agent=agent_id,
            conversation=conversation,
            metadata=context.request.get("metadata"),
            created_at=int(time.time()),
            output=output,
        )
        return response

    async def convert_response_stream(
        self,
        output: AsyncIterator[Dict[str, Any] | Any],
        context: AgentRunContext,
    ) -> AsyncGenerator[ResponseStreamEvent, None]:
        converter = self._create_stream_response_converter(context)
        async for event in output:
            output = converter.convert(event)
            for e in output:
                yield e
        
        state = await self._aget_state(context)
        output = converter.finalize(state) # finalize the response with graph state after stream
        for event in output:
            yield event

    def get_stream_mode(self, context: AgentRunContext) -> str:
        if context.stream:
            return "messages"
        return "updates"

    def _create_request_converter(self, context: AgentRunContext) -> ResponseAPIRequestConverter:
        data = context.request
        return ResponseAPIMessageRequestConverter(data)
    
    def _create_stream_response_converter(self, context: AgentRunContext) -> ResponseAPIMessagesStreamResponseConverter:
        hitl_helper = self._create_human_in_the_loop_helper(context)
        return ResponseAPIMessagesStreamResponseConverter(context, hitl_helper)
    
    def _create_non_stream_response_converter(self, context: AgentRunContext) -> ResponseAPINonStreamResponseConverter:
        hitl_helper = self._create_human_in_the_loop_helper(context)
        return ResponseAPIMessagesNonStreamResponseConverter(context, hitl_helper)

    def _create_human_in_the_loop_helper(self, context: AgentRunContext) -> HumanInTheLoopHelper:
        return HumanInTheLoopJsonHelper(context)

    def _convert_request_input(self, context: AgentRunContext, prev_state: StateSnapshot) -> Union[Dict[str, Any], Command]:
        """
        Convert the CreateResponse input to LangGraph input format, handling HITL if needed.

        :param context: The context for the agent run.
        :type context: AgentRunContext
        :param prev_state: The previous LangGraph state snapshot.
        :type prev_state: StateSnapshot

        :return: The converted LangGraph input data or Command for HITL.
        :rtype: Union[Dict[str, Any], Command]
        """
        hitl_helper = self._create_human_in_the_loop_helper(context)
        command = hitl_helper.validate_and_convert_human_feedback(
            prev_state, context.request.get("input")
        )
        if command is not None:
            return command
        converter = self._create_request_converter(context)
        return converter.convert()
    
    async def _aget_state(self, context: AgentRunContext) -> StateSnapshot:
        config = RunnableConfig(
            configurable={"thread_id": context.conversation_id},
        )
        state = await self._graph.aget_state(config=config)
        return state
