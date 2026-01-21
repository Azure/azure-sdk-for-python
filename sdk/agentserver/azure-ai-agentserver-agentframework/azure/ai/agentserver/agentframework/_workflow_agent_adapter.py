# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=no-name-in-module,import-error
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Optional,
    Union,
)

from agent_framework import Workflow, CheckpointStorage, WorkflowAgent, WorkflowCheckpoint
from agent_framework._workflows import get_checkpoint_summary

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.tools import OAuthConsentRequiredError

from ._agent_framework import AgentFrameworkAgent
from .models.agent_framework_input_converters import AgentFrameworkInputConverter
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
from .persistence.agent_thread_repository import AgentThreadRepository
from .persistence.checkpoint_repository import CheckpointRepository

logger = get_logger()

class AgentFrameworkWorkflowAdapter(AgentFrameworkAgent):
    """Adapter to run WorkflowBuilder agents within the Agent Framework CBAgent structure."""
    def __init__(self,
                workflow_factory: Callable[[], Workflow],
                *,
                thread_repository: Optional[AgentThreadRepository] = None,
                checkpoint_repository: Optional[CheckpointRepository] = None,
                **kwargs: Any) -> None:
        super().__init__(agent=None, **kwargs)
        self._workflow_factory = workflow_factory
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

            logger.info("Starting WorkflowAgent agent_run with stream=%s", context.stream)
            request_input = context.request.get("input")

            agent_thread = await self._load_agent_thread(context, agent)

            checkpoint_storage = None
            selected_checkpoint = None
            if self._checkpoint_repository:
                checkpoint_storage = await self._checkpoint_repository.get_or_create(context.conversation_id)
                selected_checkpoint = await self._get_latest_checkpoint(checkpoint_storage)
            if selected_checkpoint:
                summary = get_checkpoint_summary(selected_checkpoint)
                if summary.status == "completed":
                    logger.warning(
                        "Selected checkpoint %s is completed. Will not resume from it.",
                        selected_checkpoint.checkpoint_id,
                    )
                    selected_checkpoint = None  # Do not resume from completed checkpoints
                else:
                    await self._load_checkpoint(agent, selected_checkpoint, checkpoint_storage)
                    logger.info("Loaded checkpoint with ID: %s", selected_checkpoint.checkpoint_id)

            input_converter = AgentFrameworkInputConverter(hitl_helper=self._hitl_helper)
            message = await input_converter.transform_input(
                request_input,
                agent_thread=agent_thread,
                checkpoint=selected_checkpoint)
            logger.debug("Transformed input message type: %s", type(message))

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
            logger.debug("WorkflowAgent run completed, result type: %s", type(result))

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
        return self._workflow_factory().as_agent()

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

    async def _load_checkpoint(self,
                               agent: WorkflowAgent,
                              checkpoint: WorkflowCheckpoint,
                              checkpoint_storage: CheckpointStorage) -> None:
        """Load the checkpoint data from the given WorkflowCheckpoint.

        :param agent: The WorkflowAgent to load the checkpoint into.
        :type agent: WorkflowAgent
        :param checkpoint: The WorkflowCheckpoint to load data from.
        :type checkpoint: WorkflowCheckpoint
        :param checkpoint_storage: The storage to load the checkpoint from.
        :type checkpoint_storage: CheckpointStorage
        
        :return: None
        :rtype: None
        """
        await agent.run(checkpoint_id=checkpoint.checkpoint_id,
                        checkpoint_storage=checkpoint_storage)
