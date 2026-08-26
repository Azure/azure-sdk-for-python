# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from devtools_testutils import recorded_by_proxy

from azure.ai.projects.models import PromptAgentDefinition, ToolType, WebIQPreviewTool

from test_base import TestBase, servicePreparer


@pytest.mark.skip(reason="TODO(WebIQ): enable after Test Proxy recordings are added.")
class TestAgentWebIQ(TestBase):

    @servicePreparer()
    @recorded_by_proxy
    def test_agent_web_iq(self, **kwargs) -> None:
        model_name = kwargs.get("foundry_model_name")
        connection_id = kwargs.get("web_iq_project_connection_id")
        assert isinstance(model_name, str)
        assert isinstance(connection_id, str)

        agent_name = "web-iq-agent"
        created = None

        with self.create_client(operation_group="agents", allow_preview=True, **kwargs) as project_client:
            try:
                created = project_client.agents.create_version(
                    agent_name=agent_name,
                    definition=PromptAgentDefinition(
                        model=model_name,
                        instructions="Use WebIQ to answer questions.",
                        tools=[WebIQPreviewTool(project_connection_id=connection_id)],
                    ),
                )
                self._validate_agent_version(created, expected_name=agent_name)

                fetched = project_client.agents.get_version(
                    agent_name=agent_name,
                    agent_version=created.version,
                )
                assert isinstance(fetched.definition, PromptAgentDefinition)
                assert any(tool.type == ToolType.WEB_IQ_PREVIEW for tool in fetched.definition.tools or [])
            finally:
                if created is not None:
                    project_client.agents.delete_version(
                        agent_name=agent_name,
                        agent_version=created.version,
                        force=True,
                    )
