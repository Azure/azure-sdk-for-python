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

    pip install "azure-ai-projects>=2.3.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_NAME              - Required. The name of the agent to optimize.
    3) DATASET_NAME            - Required. The name of the registered training dataset.
    4) EVALUATOR_NAME          - Required. The name of a registered project evaluator.
    5) DATASET_VERSION         - Optional. Version of the training dataset. Defaults to "1".
    6) EVAL_MODEL              - Optional. The model used for evaluation. Defaults to "gpt-4o".
    7) OPTIMIZATION_MODEL      - Optional. The model used for optimization. Defaults to "gpt-5.1".

"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    OptimizationAgentIdentifier as AgentIdentifier,
    OptimizationEvaluatorRef as EvaluatorRef,
    OptimizationJob,
    OptimizationJobInputs,
    OptimizationOptions,
    OptimizationReferenceDatasetInput as ReferenceDatasetInput,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
dataset_name = os.environ["DATASET_NAME"]
evaluator_name = os.environ["EVALUATOR_NAME"]
dataset_version = os.environ.get("DATASET_VERSION", "1")
eval_model = os.environ.get("EVAL_MODEL", "gpt-4o")
optimization_model = os.environ.get("OPTIMIZATION_MODEL", "gpt-5.1")


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Create a job.
    # ------------------------------------------------------------------
    print("Creating optimization job...")
    job = project_client.beta.agents.create_optimization_job(
        job=OptimizationJob(
            inputs=OptimizationJobInputs(
                agent=AgentIdentifier(agent_name=agent_name),
                train_dataset=ReferenceDatasetInput(
                    name=dataset_name,
                    version=dataset_version,
                ),
                evaluators=[EvaluatorRef(name=evaluator_name)],
                options=OptimizationOptions(
                    max_candidates=3,
                    eval_model=eval_model,
                    optimization_model=optimization_model,
                ),
            )
        )
    )
    print(f"Created job: id={job.id}, status={job.status}")

    # ------------------------------------------------------------------
    # 2. Cancel it immediately.
    # ------------------------------------------------------------------
    print(f"Cancelling job {job.id}...")
    cancelled = project_client.beta.agents.cancel_optimization_job(job_id=job.id)
    print(f"Job {cancelled.id} status: {cancelled.status}")
