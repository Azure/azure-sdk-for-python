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

import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEvaluationRequest,
    InputDataset,
    EvaluatorIds,
    EvaluatorConfiguration,
    AgentEvaluationSamplingConfiguration,
)
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"]

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        # [START evaluations_agent_sample]

        agent_evaluation_request = AgentEvaluationRequest(
            run_id="run-id",
            thread_id="thread-id",
            evaluators={
                "violence": EvaluatorConfiguration(
                    id=EvaluatorIds.VIOLENCE,
                )
            },
            sampling_configuration=AgentEvaluationSamplingConfiguration(
                name="test",
                sampling_percent=0.5,
            ),
            app_insights_connection_string=project_client.telemetry.get_connection_string(),
        )

        agent_evaluation_response = project_client.evaluations.create_agent_evaluation(
            evaluation=agent_evaluation_request
        )

        print(agent_evaluation_response)

        # [END evaluations_agent_sample]
