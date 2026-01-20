
from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Optional, Protocol, Union, List

from agent_framework import WorkflowBuilder, CheckpointStorage, WorkflowAgent, WorkflowCheckpoint
from agent_framework._workflows import get_checkpoint_summary

from azure.ai.agentserver.core.tools import OAuthConsentRequiredError
from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import (
    CreateResponse,
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.models.projects import ResponseErrorEvent, ResponseFailedEvent

from ._agent_framework import AgentFrameworkCBAgent
from .models.agent_framework_input_converters import AgentFrameworkInputConverter
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
from .models.agent_framework_output_streaming_converter import AgentFrameworkOutputStreamingConverter
from .persistence.agent_thread_repository import AgentThreadRepository
from .persistence.checkpoint_repository import CheckpointRepository

logger = get_logger()

class AgentFrameworkWorkflowAdapter(AgentFrameworkCBAgent):
    """Adapter to run WorkflowBuilder agents within the Agent Framework CBAgent structure."""
    def __init__(self,
                workflow_builder: WorkflowBuilder,
                *,
                thread_repository: Optional[AgentThreadRepository] = None,
                checkpoint_repository: Optional[CheckpointRepository] = None,
                **kwargs: Any) -> None:
        super().__init__(agent=workflow_builder, **kwargs)
        self._workflow_builder = workflow_builder
        self._thread_repository = thread_repository
        self._checkpoint_repository = checkpoint_repository

    async def agent_run(  # pylint: disable=too-many-statements
        self, context: AgentRunContext
    ) -> Union[
        OpenAIResponse,
        AsyncGenerator[ResponseStreamEvent, Any],
    ]:
        try:
            agent = self._build_agent()

            logger.info(f"Starting agent_run with stream={context.stream}")
            request_input = context.request.get("input")

            agent_thread = None
            checkpoint_storage = None
            last_checkpoint = None
            if self._thread_repository:
                agent_thread = await self._thread_repository.get(context.conversation_id, agent=agent)
                if agent_thread:
                    logger.info(f"Loaded agent thread for conversation: {context.conversation_id}")
                else:
                    agent_thread = agent.get_new_thread()

            if self._checkpoint_repository:
                checkpoint_storage = await self._checkpoint_repository.get_or_create(context.conversation_id)
                last_checkpoint = await self._get_latest_checkpoint(checkpoint_storage)
                if last_checkpoint:
                    summary = get_checkpoint_summary(last_checkpoint)
                    if summary.status == "completed":
                        logger.warning("Last checkpoint is completed. Will not resume from it.")
                        last_checkpoint = None  # Do not resume from completed checkpoints
                if last_checkpoint:
                    await self._load_checkpoint(agent, last_checkpoint, checkpoint_storage)
                    logger.info(f"Loaded checkpoint with ID: {last_checkpoint.checkpoint_id}")

            input_converter = AgentFrameworkInputConverter(hitl_helper=self._hitl_helper)
            message = await input_converter.transform_input(
                request_input,
                agent_thread=agent_thread,
                checkpoint=last_checkpoint)
            logger.debug(f"Transformed input message type: {type(message)}")

            # Use split converters
            if context.stream:
                logger.info("Running agent in streaming mode")
                streaming_converter = AgentFrameworkOutputStreamingConverter(context, hitl_helper=self._hitl_helper)

                async def stream_updates():
                    try:
                        update_count = 0
                        try:
                            updates = agent.run_stream(
                                message,
                                thread=agent_thread,
                                checkpoint_storage=checkpoint_storage,
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
            result = await agent.run(
                message,
                thread=agent_thread,
                checkpoint_storage=checkpoint_storage)
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

    def _build_agent(self) -> WorkflowAgent:
        return self._workflow_builder.build().as_agent()

    async def _get_latest_checkpoint(self,
                checkpoint_storage: CheckpointStorage) -> Optional[Any]:
        """Load the latest checkpoint from the given storage.

        :param checkpoint_storage: The checkpoint storage to load from.
        :type checkpoint_storage: CheckpointStorage

        :return: The latest checkpoint if available, None otherwise.
        :rtype: Optional[Any]
        """
        checkpoints = await checkpoint_storage.list_checkpoints()
        if checkpoints:
            latest_checkpoint = max(checkpoints, key=lambda cp: cp.timestamp)
            return latest_checkpoint
        return None

    async def _load_checkpoint(self, agent: WorkflowAgent,
                              checkpoint: WorkflowCheckpoint,
                              checkpoint_storage: CheckpointStorage) -> None:
        """Load the checkpoint data from the given WorkflowCheckpoint.

        :param checkpoint: The WorkflowCheckpoint to load data from.
        :type checkpoint: WorkflowCheckpoint
        """
        logger.info(f"Loading checkpoint ID: {checkpoint.to_dict()} into agent.")
        await agent.run(checkpoint_id=checkpoint.checkpoint_id,
                        checkpoint_storage=checkpoint_storage)