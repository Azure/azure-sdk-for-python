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

from agent_framework import CheckpointStorage, Workflow, WorkflowAgent, WorkflowCheckpoint

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import (
    Response as OpenAIResponse,
    ResponseStreamEvent,
)
from azure.ai.agentserver.core.tools import OAuthConsentRequiredError
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._agent_framework import AgentFrameworkAgent
from .models.agent_framework_input_converters import transform_input
from .models.agent_framework_output_non_streaming_converter import (
    AgentFrameworkOutputNonStreamingConverter,
)
from .persistence import AgentSessionRepository, CheckpointRepository

logger = get_logger()

class AgentFrameworkWorkflowAdapter(AgentFrameworkAgent):
    """Adapter to run WorkflowBuilder agents within the Agent Framework CBAgent structure."""
    def __init__(
        self,
        workflow_factory: Callable[[], Workflow],
        credentials: Optional[Union[AsyncTokenCredential, TokenCredential]] = None,
        session_repository: Optional[AgentSessionRepository] = None,
        checkpoint_repository: Optional[CheckpointRepository] = None,
        *,
        project_endpoint: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(credentials, session_repository, project_endpoint=project_endpoint, **kwargs)
        self._workflow_factory = workflow_factory
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

            agent_session = await self._load_agent_session(context, agent)

            checkpoint_storage = None
            selected_checkpoint = None
            if self._checkpoint_repository and (conversation_id := context.conversation_id):
                checkpoint_storage = await self._checkpoint_repository.get_or_create(conversation_id)
                if checkpoint_storage:
                    selected_checkpoint = await self._get_latest_checkpoint(checkpoint_storage)
            if selected_checkpoint:
                checkpoint_status = self._checkpoint_status(selected_checkpoint)
                if checkpoint_status == "completed":
                    logger.warning(
                        "Selected checkpoint %s is completed. Will not resume from it.",
                        selected_checkpoint.checkpoint_id,
                    )
                    selected_checkpoint = None  # Do not resume from completed checkpoints
                else:
                    await self._load_checkpoint(agent, selected_checkpoint, checkpoint_storage)
                    logger.info("Loaded checkpoint with ID: %s", selected_checkpoint.checkpoint_id)

            message = transform_input(request_input)
            logger.debug("Transformed input message type: %s", type(message))

            # Use split converters
            if context.stream:
                return self._run_streaming_updates(
                    context=context,
                    stream_runner=lambda: agent.run(
                        message,
                        session=agent_session,
                        checkpoint_storage=checkpoint_storage,
                        stream=True,
                    ),
                    agent_session=agent_session,
                )

            # Non-streaming path
            logger.info("Running WorkflowAgent in non-streaming mode")
            result = await agent.run(
                message,
                session=agent_session,
                checkpoint_storage=checkpoint_storage)
            logger.debug("WorkflowAgent run completed, result type: %s", type(result))

            await self._save_agent_session(context, agent_session)

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


    def _checkpoint_status(self, checkpoint: WorkflowCheckpoint) -> Optional[str]:
        status = getattr(checkpoint, "status", None)
        if status:
            return status
        metadata = getattr(checkpoint, "metadata", None)
        if isinstance(metadata, dict):
            value = metadata.get("status")
            return str(value) if value is not None else None
        return None

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
