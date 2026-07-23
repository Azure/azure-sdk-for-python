# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an async AIProjectClient, this sample demonstrates how to create an
    agent optimization job and manually poll it to completion.

    Agent optimization automatically improves an agent's system prompt, model
    choice, or tool definitions by running candidate variants against your
    training dataset and scoring them with the evaluators you specify.

USAGE:
    python sample_optimization_job_basic_polling_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.4.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_NAME       - Required. The name of the agent to optimize.
    3) DATASET_NAME             - Required. The name of the registered training dataset.
    4) EVALUATOR_NAME           - Required. The name of a registered project evaluator.
    5) DATASET_VERSION          - Optional. Version of the training dataset. Defaults to "1".
    6) POLL_INTERVAL_SECONDS    - Optional. Seconds between status polls. Defaults to 10.
    7) EVAL_MODEL               - Optional. The model used for evaluation. Defaults to "gpt-4o".
    8) OPTIMIZATION_MODEL       - Optional. The model used for optimization. Defaults to "gpt-5.1".
"""

import asyncio
import json
import os

from dotenv import load_dotenv

from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse, HttpRequest
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
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

terminal_statuses = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        # ------------------------------------------------------------------
        # 1. Create an optimization job without SDK polling.
        # ------------------------------------------------------------------
        print("Creating optimization job...")
        initial_responses: list[PipelineResponse[HttpRequest, AsyncHttpResponse]] = []

        def capture_created_job_response(
            response: PipelineResponse[HttpRequest, AsyncHttpResponse],
        ) -> None:
            initial_responses.append(response)

        await project_client.beta.agents.begin_create_optimization_job(
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
            ),
            polling=False,
            raw_response_hook=capture_created_job_response,
        )
        if not initial_responses:
            raise RuntimeError("The create operation did not return an optimization job.")
        job = OptimizationJob(json.loads(initial_responses[0].http_response.text()))
        print(f"Created job: id={job.id}, status={job.status}")

        # ------------------------------------------------------------------
        # 2. Poll the job to completion.
        # ------------------------------------------------------------------
        while job.status not in terminal_statuses:
            await asyncio.sleep(poll_interval)
            job = await project_client.beta.agents.get_optimization_job(job_id=job.id)
            print(f"Job status: {job.status}")

        if job.warnings:
            for warning in job.warnings:
                print(f"[WARNING] {warning}")

        if job.status == JobStatus.FAILED:
            message = job.error.message if job.error else "<no error message>"
            raise RuntimeError(f"Optimization job `{job.id}` failed: {message}")
        if job.status == JobStatus.CANCELLED:
            raise RuntimeError(f"Optimization job `{job.id}` was cancelled.")

        # ------------------------------------------------------------------
        # 3. Inspect the results.
        # ------------------------------------------------------------------
        if job.result is None:
            raise RuntimeError(f"Optimization job `{job.id}` completed without a result.")

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


if __name__ == "__main__":
    asyncio.run(main())