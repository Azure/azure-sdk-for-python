# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,no-name-in-module,no-member,do-not-import-asyncio
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, Union

from agent_framework import AgentProtocol

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.tools import OAuthConsentRequiredError
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.models.projects import ResponseErrorEvent, ResponseFailedEvent

from .models.agent_framework_input_converters import AgentFrameworkInputConverter
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
from .models.agent_framework_output_streaming_converter import AgentFrameworkOutputStreamingConverter
from ._agent_framework import AgentFrameworkCBAgent
from .persistence import AgentThreadRepository

logger = get_logger()

class AgentFrameworkAIAgentAdapter(AgentFrameworkCBAgent):
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
            logger.info(f"Starting agent_run with stream={context.stream}")
            request_input = context.request.get("input")

            agent_thread = None
            if self._thread_repository:
                agent_thread = await self._thread_repository.get(context.conversation_id)
                if agent_thread:
                    logger.info(f"Loaded agent thread for conversation: {context.conversation_id}")
                else:
                    agent_thread = self.agent.get_new_thread()

            input_converter = AgentFrameworkInputConverter(hitl_helper=self._hitl_helper)
            message = await input_converter.transform_input(
                request_input,
                agent_thread=agent_thread)
            logger.debug(f"Transformed input message type: {type(message)}")

            # Use split converters
            if context.stream:
                logger.info("Running agent in streaming mode")
                streaming_converter = AgentFrameworkOutputStreamingConverter(context, hitl_helper=self._hitl_helper)

                async def stream_updates():
                    try:
                        update_count = 0
                        try:
                            updates = self.agent.run_stream(
                                message,
                                thread=agent_thread,
                            )
                            async for event in streaming_converter.convert(updates):
                                update_count += 1
                                yield event

                            if agent_thread and self._thread_repository:
                                await self._thread_repository.set(context.conversation_id, agent_thread)
                                logger.info(f"Saved agent thread for conversation: {context.conversation_id}")

                            logger.info("Streaming completed with %d updates", update_count)
                        except OAuthConsentRequiredError as e:
                            logger.info("OAuth consent required during streaming updates")
                            if update_count == 0:
                                async for event in self.respond_with_oauth_consent_astream(context, e):
                                    yield event
                            else:
                                # If we've already emitted events, we cannot safely restart a new
                                # OAuth-consent stream (it would reset sequence numbers).
                                yield ResponseErrorEvent(
                                    sequence_number=streaming_converter.next_sequence(),
                                    code="server_error",
                                    message=f"OAuth consent required: {e.consent_url}",
                                    param="agent_run",
                                )
                                yield ResponseFailedEvent(
                                    sequence_number=streaming_converter.next_sequence(),
                                    response=streaming_converter._build_response(status="failed"),  # pylint: disable=protected-access
                                )
                        except Exception as e:  # pylint: disable=broad-exception-caught
                            logger.error("Unhandled exception during streaming updates: %s", e, exc_info=True)

                            # Emit well-formed error events instead of terminating the stream.
                            yield ResponseErrorEvent(
                                sequence_number=streaming_converter.next_sequence(),
                                code="server_error",
                                message=str(e),
                                param="agent_run",
                            )
                            yield ResponseFailedEvent(
                                sequence_number=streaming_converter.next_sequence(),
                                response=streaming_converter._build_response(status="failed"),  # pylint: disable=protected-access
                            )
                    finally:
                        # No request-scoped resources to clean up here today.
                        # Keep this block as a hook for future request-scoped cleanup.
                        pass

                return stream_updates()

            # Non-streaming path
            logger.info("Running agent in non-streaming mode")
            non_streaming_converter = AgentFrameworkOutputNonStreamingConverter(context, hitl_helper=self._hitl_helper)
            result = await self.agent.run(
                message,
                thread=agent_thread)
            logger.debug(f"Agent run completed, result type: {type(result)}")

            if agent_thread and self._thread_repository:
                await self._thread_repository.set(context.conversation_id, agent_thread)
                logger.info(f"Saved agent thread for conversation: {context.conversation_id}")

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
