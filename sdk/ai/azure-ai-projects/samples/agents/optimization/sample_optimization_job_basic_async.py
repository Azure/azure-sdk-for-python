# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an async AIProjectClient, this sample demonstrates how to create an
    agent optimization job, observe the SDK poller until it is done, and then
    get the result.

    Agent optimization automatically improves an agent's system prompt, model
    choice, or tool definitions by running candidate variants against your
    training dataset and scoring them with the evaluators you specify.

USAGE:
    python sample_optimization_job_app_polling_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.4.0" azure-identity python-dotenv aiohttp

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
import os

from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
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
poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))
eval_model = os.environ.get("EVAL_MODEL", "gpt-4o")
optimization_model = os.environ.get("OPTIMIZATION_MODEL", "gpt-5.1")


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        # ------------------------------------------------------------------
        # 1. Create an optimization job and observe the SDK-managed poller.
        # ------------------------------------------------------------------
        job = OptimizationJob(
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
            ),
        )

        print("Begin creating an agent optimization job.")
        poller = await project_client.beta.agents.begin_create_optimization_job(
            job=job,
            polling_interval=poll_interval,
        )

        print("Waiting for the agent optimization job to complete.")
        result = await poller.result()
        print(f"Final LRO status: `{poller.status()}`.")

        # ------------------------------------------------------------------
        # 2. Inspect the results.
        # ------------------------------------------------------------------
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
