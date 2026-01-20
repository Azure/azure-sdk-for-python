
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

from ._agent_framework import AgentFrameworkCBAgent
from .models.agent_framework_input_converters import AgentFrameworkInputConverter
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
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

            agent_thread = await self._load_agent_thread(context, agent)

            checkpoint_storage = None
            last_checkpoint = None
            if self._checkpoint_repository:
                checkpoint_storage = await self._checkpoint_repository.get_or_create(context.conversation_id)
                last_checkpoint = await self._get_latest_checkpoint(checkpoint_storage)
                if last_checkpoint:
                    summary = get_checkpoint_summary(last_checkpoint)
                    if summary.status == "completed":
                        logger.warning(f"Lastest checkpoint {last_checkpoint.checkpoint_id} is completed. Will not resume from it.")
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
                return self._run_streaming_updates(
                    context=context,
                    run_stream=lambda: agent.run_stream(
                        message,
                        thread=agent_thread,
                        checkpoint_storage=checkpoint_storage,
                    ),
                    agent_thread=agent_thread,
                )

            # Non-streaming path
            logger.info("Running WorkflowAgent in non-streaming mode")
            result = await agent.run(
                message,
                thread=agent_thread,
                checkpoint_storage=checkpoint_storage)
            logger.debug(f"WorkflowAgent run completed, result type: {type(result)}")

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