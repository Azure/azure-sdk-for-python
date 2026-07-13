# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to create an agent
    optimization job, poll it to completion, and read the results.

    Agent optimization automatically improves an agent's system prompt, model
    choice, or tool definitions by running candidate variants against your
    training dataset and scoring them with the evaluators you specify.

USAGE:
    python sample_optimization_job_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_NAME              - Required. The name of the agent to optimize.
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
    OptimizationAgentIdentifier as AgentIdentifier,
    OptimizationEvaluatorRef as EvaluatorRef,
    JobStatus,
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
poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))
eval_model = os.environ.get("EVAL_MODEL", "gpt-4o")
optimization_model = os.environ.get("OPTIMIZATION_MODEL", "gpt-5.1")

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Create an optimization job.
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
    # 2. Poll until the job reaches a terminal state.
    # ------------------------------------------------------------------
    print(f"Polling job `{job.id}` to completion...", end="", flush=True)
    while job.status not in TERMINAL_STATUSES:
        time.sleep(poll_interval)
        job = project_client.beta.agents.get_optimization_job(job_id=job.id)
        print(".", end="", flush=True)
    print()
    print(f"Final status: {job.status}")

    if job.warnings:
        for warning in job.warnings:
            print(f"[WARNING] {warning}")

    if job.status == JobStatus.FAILED:
        message = job.error.message if job.error else "<no error message>"
        raise RuntimeError(f"Optimization job `{job.id}` failed: {message}")

    # ------------------------------------------------------------------
    # 3. Inspect the results.
    # ------------------------------------------------------------------
    if job.status == JobStatus.SUCCEEDED and job.result:
        result = job.result
        print(f"\nBaseline candidate: {result.baseline}")
        print(f"Best candidate:     {result.best}")
        print(f"Candidates ({len(result.candidates or [])}):")
        for candidate in result.candidates or []:
            print(
                f"  - {candidate.name}"
                f" | avg_score={candidate.avg_score:.4f}"
                f" | avg_tokens={candidate.avg_tokens:.0f}"
            )
            if candidate.eval_id:
                print(f"      eval_id={candidate.eval_id}")
