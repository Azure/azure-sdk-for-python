# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to create an agent
    optimization job and immediately cancel it.

USAGE:
    python sample_optimization_job_cancel.py

    Before running the sample:

    pip install "azure-ai-projects>=2.4.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_NAME      - Required. The name of the agent to optimize.
    3) DATASET_NAME            - Required. The name of the registered training dataset.
    4) EVALUATOR_NAME          - Required. The name of a registered project evaluator.
    5) DATASET_VERSION         - Optional. Version of the training dataset. Defaults to "1".
    6) POLL_INTERVAL_SECONDS   - Optional. Seconds between status polls. Defaults to 10.
    7) EVAL_MODEL              - Optional. The model used for evaluation. Defaults to "gpt-4o".
    8) OPTIMIZATION_MODEL      - Optional. The model used for optimization. Defaults to "gpt-5.1".

"""

import os
import time

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentOptimizationEvaluatorRef,
    AgentOptimizationJob,
    AgentOptimizationJobInputs,
    AgentOptimizationOptions,
    AgentOptimizationReferenceDatasetInput,
    OptimizedAgentIdentifier,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
dataset_name = os.environ["DATASET_NAME"]
evaluator_name = os.environ["EVALUATOR_NAME"]
dataset_version = os.environ.get("DATASET_VERSION", "1")
poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))
eval_model = os.environ.get("EVAL_MODEL", "gpt-4o")
optimization_model = os.environ.get("OPTIMIZATION_MODEL", "gpt-5.1")


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Create an optimization job and retain the SDK-managed poller.
    # ------------------------------------------------------------------
    job = AgentOptimizationJob(
        inputs=AgentOptimizationJobInputs(
            agent=OptimizedAgentIdentifier(agent_name=agent_name),
            train_dataset=AgentOptimizationReferenceDatasetInput(
                name=dataset_name,
                version=dataset_version,
            ),
            evaluators=[AgentOptimizationEvaluatorRef(name=evaluator_name)],
            options=AgentOptimizationOptions(
                max_candidates=3,
                eval_model=eval_model,
                optimization_model=optimization_model,
            ),
        ),
    )

    created_jobs: list[AgentOptimizationJob] = []

    def raw_response_hook(response):
        response.http_response.read()
        created_jobs.append(AgentOptimizationJob(response.http_response.json()))

    print("Begin creating an agent optimization job.")
    poller = project_client.beta.agents.begin_create_optimization_job(
        job=job,
        polling_interval=poll_interval,
        raw_response_hook=raw_response_hook,
    )
    if not created_jobs:
        raise RuntimeError("The create operation did not return an optimization job.")
    created_job = created_jobs[0]
    print(f"Created job: id={created_job.id}, status={created_job.status}")

    # ------------------------------------------------------------------
    # 2. Cancel it immediately.
    # ------------------------------------------------------------------
    print(f"Cancelling job {created_job.id}...")
    cancelled = project_client.beta.agents.cancel_optimization_job(job_id=created_job.id)
    print(f"Job {cancelled.id} status: {cancelled.status}")

    print("Wait for the SDK poller to observe the cancellation.")
    while not poller.done():
        print(f"status=`{poller.status()}`")
        time.sleep(poll_interval)

    print(f"Final LRO status: `{poller.status()}`.")
