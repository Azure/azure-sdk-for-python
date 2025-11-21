# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Test to verify model substitution is working correctly.
Creates an agent and asks it to identify its model.
"""

import uuid
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import PromptAgentDefinition


class TestModelVerification(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_model_identity(self, **kwargs):
        """
        Simple test to verify which model is actually being used.
        Creates an agent and asks it to identify its model.
        
        DOES NOT CLEAN UP - agents are left in place for verification.
        """

        # Get model from test_agents_params (which now reads from environment if available)
        model = self.test_agents_params["model_deployment_name"]
        print(f"\n{'='*80}")
        print(f"📋 Model: {model}")
        print(f"{'='*80}\n")

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create unique agent name with model and random ID to avoid conflicts
        random_id = str(uuid.uuid4())[:8]
        agent_name = f"model-verify-{model}-{random_id}"

        # Create agent
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant. When asked what model you are, respond with your exact model name/identifier.",
            ),
            description=f"Model verification test for {model}",
        )
        
        print(f"✅ Agent created:")
        print(f"   - ID: {agent.id}")
        print(f"   - Name: {agent.name}")
        print(f"   - Version: {agent.version}")
        print(f"   - Model parameter passed: {model}")
        
        assert agent.id is not None
        assert agent.name == agent_name

        # Ask the agent what model it is
        print(f"\n❓ Asking agent: What model are you?")
        
        response = openai_client.responses.create(
            input="What model are you? Please tell me your exact model name or identifier.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        print(f"✅ Response completed (id: {response.id})")
        
        response_text = response.output_text
        print(f"\n🤖 Agent's response:")
        print(f"{'='*80}")
        print(response_text)
        print(f"{'='*80}")
        
        # Basic assertions
        assert response.id is not None
        assert len(response_text) > 0, "Expected a response from the agent"
        
        # Print summary
        print(f"\n📊 SUMMARY:")
        print(f"   - Expected model: {model}")
        print(f"   - Agent name: {agent.name}")
        print(f"   - Agent response: {response_text[:100]}...")
        
        # NOTE: NOT cleaning up - agent stays for manual verification
        print(f"\n⚠️  Agent NOT deleted (left for verification)")
        print(f"   Agent: {agent.name}:{agent.version}")
