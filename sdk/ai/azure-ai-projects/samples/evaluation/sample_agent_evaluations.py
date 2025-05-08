# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.evaluations` methods to submit evaluation for an agent run.

USAGE:
    python sample_agent_evaluations.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

import os, time

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEvaluationRequest,
    InputDataset,
    EvaluatorIds,
    EvaluatorConfiguration,
    AgentEvaluationSamplingConfiguration,
    AgentEvaluationRedactionConfiguration,
)
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]


with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    # TODO : Remove api_version when the service is stable
    with AIProjectClient(endpoint=endpoint, credential=credential, api_version="latest") as project_client:

        # [START evaluations_agent_sample]
        agent = project_client.agents.create_agent(
            model=model_deployment_name,
            name="my-agent",
            instructions="You are helpful agent",
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = project_client.agents.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = project_client.agents.messages.create(
            thread_id=thread.id, role="user", content="Hello, tell me a joke"
        )
        print(f"Created message, message ID: {message.id}")

        run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)

        # Poll the run as long as run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            # Wait for a second
            time.sleep(1)
            run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
            print(f"Run status: {run.status}")

        agent_evaluation_request = AgentEvaluationRequest(
            run_id=run.id,
            thread_id=thread.id,
            evaluators={
                "violence": EvaluatorConfiguration(
                    id=EvaluatorIds.VIOLENCE,
                )
            },
            sampling_configuration=AgentEvaluationSamplingConfiguration(
                name="test",
                sampling_percent=100,
                max_request_rate=100,
            ),
            redaction_configuration=AgentEvaluationRedactionConfiguration(
                redact_score_properties=False,
            ),
            app_insights_connection_string=project_client.telemetry.get_connection_string(),
        )

        agent_evaluation_response = project_client.evaluations.create_agent_evaluation(
            evaluation=agent_evaluation_request
        )

        print(agent_evaluation_response)

        # [END evaluations_agent_sample]
