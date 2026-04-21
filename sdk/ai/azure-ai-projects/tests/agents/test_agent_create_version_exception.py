# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
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
# pytest tests\agents\test_agent_create_version_exception.py -s
class TestAgentCreateVersionException(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE)
    def test_create_version_raises_exception_when_allow_preview_not_set(self, **kwargs):
        """
        Verify that calling agents.create_version() with a WorkflowAgentDefinition when
        AIProjectClient was constructed WITHOUT allow_preview=True raises an HttpResponseError
        (HTTP 403) whose message contains the SDK-specific hint pointing users to set
        allow_preview=True.
        """
        # Deliberately create client WITHOUT allow_preview=True
        project_client = self.create_client(**kwargs)

        with pytest.raises(HttpResponseError) as exc_info:
            project_client.agents.create_version(
                agent_name="workflow-agent-preview-test",
                definition=WorkflowAgentDefinition(workflow=_MINIMAL_WORKFLOW_YAML),
            )

        raised = exc_info.value
        assert raised.status_code == 403
        assert _PREVIEW_FEATURE_ADDED_ERROR_MESSAGE in raised.message
