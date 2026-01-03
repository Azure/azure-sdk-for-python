# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
from test_base import TestBase, servicePreparer

from devtools_testutils import is_live_and_not_recording

# from azure.ai.projects.models import ResponsesUserMessageItemParam
from azure.ai.projects.models import AgentReference, ContainerAppAgentDefinition, ProtocolVersionRecord, AgentProtocol


class TestContainerAppAgentsAsync(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    async def test_container_app_agent_async(self, **kwargs):

        container_app_resource_id = kwargs.pop("CONTAINER_APP_RESOURCE_ID")
        ingress_subdomain_suffix = kwargs.pop("CONTAINER_INGRESS_SUBDOMAIN_SUFFIX")

        projects_client = self.create_async_client(operation_group="container", **kwargs)
        openai_client = await projects_client.get_openai_client()

        agent_version = await projects_client.agents.create_version(
            agent_name="MyContainerAppAgent",
            definition=ContainerAppAgentDefinition(
                container_app_resource_id=container_app_resource_id,
                container_protocol_versions=[ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="1")],
                ingress_subdomain_suffix=ingress_subdomain_suffix,
            ),
        )
        print(f"Created agent id: {agent_version.id}, name: {agent_version.name}, version: {agent_version.name}")

        try:
            conversation = await openai_client.conversations.create(
                # items=[ResponsesUserMessageItemParam(content="How many feet are in a mile?")]
                items=[{"type": "message", "role": "user", "content": "How many feet are in a mile?"}]
            )
            print(f"Created conversation with initial user message (id: {conversation.id})")

            try:
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent": AgentReference(name=agent_version.name).as_dict()},
                )
                print(f"Response id: {response.id}, output text: {response.output_text}")
                assert "5280" in response.output_text or "5,280" in response.output_text

            finally:
                await openai_client.conversations.delete(conversation.id)
                print(f"Deleted conversation id: {conversation.id}")

        finally:
            await projects_client.agents.delete_version(
                agent_name=agent_version.name, agent_version=agent_version.version
            )
            print(f"Deleted agent id: {agent_version.id}, name: {agent_version.name}, version: {agent_version.version}")
