# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=no-name-in-module,import-error
from __future__ import annotations

from typing import Any, AsyncGenerator, Optional, Union

from agent_framework import AgentProtocol

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.tools import OAuthConsentRequiredError
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)

from .models.agent_framework_input_converters import AgentFrameworkInputConverter
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
from ._agent_framework import AgentFrameworkAgent
from .persistence import AgentThreadRepository

logger = get_logger()

class AgentFrameworkAIAgentAdapter(AgentFrameworkAgent):
    def __init__(self, agent: AgentProtocol,
                 *,
                 thread_repository: Optional[AgentThreadRepository]=None,
                 **kwargs) -> None:
        super().__init__(agent=agent, **kwargs)
        self._agent = agent
        self._thread_repository = thread_repository

    async def agent_run(  # pylint: disable=too-many-statements
        self, context: AgentRunContext
    ) -> Union[
        OpenAIResponse,
        AsyncGenerator[ResponseStreamEvent, Any],
    ]:
        try:
            logger.info("Starting AIAgent agent_run with stream=%s", context.stream)
            request_input = context.request.get("input")

            agent_thread = await self._load_agent_thread(context, self._agent)

            input_converter = AgentFrameworkInputConverter(hitl_helper=self._hitl_helper)
            message = await input_converter.transform_input(
                request_input,
                agent_thread=agent_thread)
            logger.debug("Transformed input message type: %s", type(message))
            # Use split converters
            if context.stream:
                return self._run_streaming_updates(
                    context=context,
                    run_stream=lambda: self.agent.run_stream(
                        message,
                        thread=agent_thread,
                    ),
                    agent_thread=agent_thread,
                )

            # Non-streaming path
            logger.info("Running agent in non-streaming mode")
            result = await self.agent.run(
                message,
                thread=agent_thread)
            logger.debug("Agent run completed, result type: %s", type(result))
            await self._save_agent_thread(context, agent_thread)

            non_streaming_converter = AgentFrameworkOutputNonStreamingConverter(context, hitl_helper=self._hitl_helper)
            transformed_result = non_streaming_converter.transform_output_for_response(result)
            logger.info("Agent run and transformation completed successfully")
            return transformed_result
        except OAuthConsentRequiredError as e:
            logger.info("OAuth consent required during agent run")
            if context.stream:
                # Yield OAuth consent response events
                # Capture e in the closure by passing it as a default argument
                async def oauth_consent_stream(error=e):
                    async for event in self.respond_with_oauth_consent_astream(context, error):
                        yield event
                return oauth_consent_stream()
            return await self.respond_with_oauth_consent(context, e)
        finally:
            pass
