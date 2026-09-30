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
    python sample_optimization_job_basic_async.py

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
    AgentOptimizationCandidateExpand,
    AgentOptimizationCandidateEvaluation,
    AgentOptimizationCandidateOutput,
    AgentOptimizationCandidatePromotionInfo,
    AgentOptimizationCandidateSearchConfiguration,
    AgentOptimizationConfiguration,
    AgentOptimizationEvaluationConfiguration,
    AgentOptimizationEvaluator,
    AgentOptimizationFoundryAgentTargetConfiguration,
    AgentOptimizationJob,
    AgentOptimizationJobResult,
    AgentOptimizationModelConfiguration,
    AgentOptimizationSpace,
    AgentOptimizationTargetCompletionDatasetReferenceDataSource,
    AgentOptimizationTargetCompletionEvaluationSet,
    EvaluationModelConfiguration,
    TargetAttribute,
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


def create_optimization_job() -> AgentOptimizationJob:
    return AgentOptimizationJob(
        display_name=f"Optimize {agent_name}",
        target_configuration=AgentOptimizationFoundryAgentTargetConfiguration(name=agent_name),
        optimization_model_configuration=AgentOptimizationModelConfiguration(model=optimization_model),
        optimization_configuration=AgentOptimizationConfiguration(
            agent_optimization_space=AgentOptimizationSpace(
                target_attributes=[TargetAttribute.INSTRUCTIONS],
            ),
            candidate_search_configuration=AgentOptimizationCandidateSearchConfiguration(max_candidates=3),
            evaluation_configuration=AgentOptimizationEvaluationConfiguration(
                evaluation_model=EvaluationModelConfiguration(model=eval_model),
                evaluators=[AgentOptimizationEvaluator(name=evaluator_name)],
                training_set=AgentOptimizationTargetCompletionEvaluationSet(
                    source=AgentOptimizationTargetCompletionDatasetReferenceDataSource(
                        name=dataset_name,
                        version=dataset_version,
                    )
                ),
            ),
        ),
    )


def print_result_summary(result: AgentOptimizationJobResult) -> None:
    summary = result.candidate_summary
    if summary:
        print(
            f"\nCandidate summary:"
            f" baseline={summary.baseline_id} (score={summary.baseline_score})"
            f" | best={summary.best_id} (score={summary.best_score})"
            f" | completed={summary.completed_candidate_count}"
        )
        promotion = summary.latest_promoted_candidate
        if promotion:
            print(f"Latest promoted candidate: {promotion.promoted_agent.name} at {promotion.promoted_at}")

    if result.termination_reason:
        print(f"Termination reason: {result.termination_reason}")


def print_candidate_details(
    name: str,
    evaluation: AgentOptimizationCandidateEvaluation | None,
    output: AgentOptimizationCandidateOutput | None,
    promotion: AgentOptimizationCandidatePromotionInfo | None,
) -> None:
    print(f"  - {name}", end="")
    if evaluation:
        print(f" | score={evaluation.score} | avg_tokens={evaluation.avg_tokens}", end="")
        if evaluation.eval_id:
            print(f" | eval_id={evaluation.eval_id}", end="")
    if output and hasattr(output, "mutations"):
        print(f" | mutations={len(output.mutations or [])}", end="")
    if promotion:
        print(f" | promoted_agent={promotion.promoted_agent.name}", end="")
    print()


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        # ------------------------------------------------------------------
        # 1. Create an optimization job and observe the SDK-managed poller.
        # ------------------------------------------------------------------
        job = create_optimization_job()

        print("Begin creating an agent optimization job.")
        poller = await project_client.agents.begin_create_optimization_job(
            job=job,
            polling_interval=poll_interval,
        )
        job_id = poller.details["job_id"]
        if not job_id:
            raise RuntimeError("The create operation did not return an optimization job ID.")

        print("Waiting for the agent optimization job to complete.")
        result = await poller.result()
        print(f"Final LRO status: `{poller.status()}`.")

        # ------------------------------------------------------------------
        # 2. Inspect the results.
        # ------------------------------------------------------------------
        print_result_summary(result)

        print("\nCandidates:")
        async for candidate in project_client.agents.list_optimization_candidates(
            job_id=job_id,
            expand=[AgentOptimizationCandidateExpand.MUTATIONS],
            limit=10,
        ):
            print_candidate_details(
                candidate.name,
                candidate.evaluation,
                candidate.output,
                candidate.promotion,
            )


if __name__ == "__main__":
    asyncio.run(main())
