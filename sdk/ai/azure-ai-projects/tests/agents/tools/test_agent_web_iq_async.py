# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from devtools_testutils.aio import recorded_by_proxy_async

from azure.ai.projects.models import PromptAgentDefinition, ToolType, WebIQPreviewTool

from test_base import TestBase, servicePreparer


@pytest.mark.skip(reason="TODO(WebIQ): enable after Test Proxy recordings are added.")
class TestAgentWebIQAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_web_iq_async(self, **kwargs) -> None:
        model_name = kwargs.get("foundry_model_name")
        connection_id = kwargs.get("web_iq_project_connection_id")
        assert isinstance(model_name, str)
        assert isinstance(connection_id, str)

        agent_name = "web-iq-agent"
        created = None

        async with self.create_async_client(operation_group="agents", allow_preview=True, **kwargs) as project_client:
            try:
                created = await project_client.agents.create_version(
                    agent_name=agent_name,
                    definition=PromptAgentDefinition(
                        model=model_name,
                        instructions="Use WebIQ to answer questions.",
                        tools=[WebIQPreviewTool(project_connection_id=connection_id)],
                    ),
                )
                self._validate_agent_version(created, expected_name=agent_name)

                fetched = await project_client.agents.get_version(
                    agent_name=agent_name,
                    agent_version=created.version,
                )
                assert isinstance(fetched.definition, PromptAgentDefinition)
                assert any(tool.type == ToolType.WEB_IQ_PREVIEW for tool in fetched.definition.tools or [])
            finally:
                if created is not None:
                    await project_client.agents.delete_version(
                        agent_name=agent_name,
                        agent_version=created.version,
                        force=True,
                    )
