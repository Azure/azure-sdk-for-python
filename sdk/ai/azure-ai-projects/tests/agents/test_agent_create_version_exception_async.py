# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.core.exceptions import HttpResponseError
from azure.ai.projects.models import WorkflowAgentDefinition
from azure.ai.projects.operations._patch_agents import _PREVIEW_FEATURE_ADDED_ERROR_MESSAGE

# Minimal workflow YAML — the service rejects the request before validating the
# definition, so the content only needs to be a non-empty string.
_MINIMAL_WORKFLOW_YAML = """\
kind: workflow
trigger:
  kind: OnConversationStart
  id: my_workflow
  actions: []
"""


# To run this test:
# pytest tests\agents\test_agent_create_version_exception_async.py -s
class TestAgentCreateVersionExceptionAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE)
    async def test_create_version_raises_exception_when_allow_preview_not_set_async(self, **kwargs):
        """
        Verify that calling agents.create_version() with a WorkflowAgentDefinition when
        AsyncAIProjectClient was constructed WITHOUT allow_preview=True raises an HttpResponseError
        (HTTP 403) whose message contains the SDK-specific hint pointing users to set
        allow_preview=True.
        """
        # Deliberately create client WITHOUT allow_preview=True
        project_client = self.create_async_client(**kwargs)

        async with project_client:
            with pytest.raises(HttpResponseError) as exc_info:
                await project_client.agents.create_version(
                    agent_name="workflow-agent-preview-test",
                    definition=WorkflowAgentDefinition(workflow=_MINIMAL_WORKFLOW_YAML),
                )

        raised = exc_info.value
        assert raised.status_code == 403
        assert _PREVIEW_FEATURE_ADDED_ERROR_MESSAGE in raised.message
