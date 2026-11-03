# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to create an agent
    optimization job and poll its standard LRO to completion.

    Agent optimization automatically improves an agent's system prompt, model
    choice, or tool definitions by running candidate variants against your
    training dataset and scoring them with the evaluators you specify.

USAGE:
    python sample_optimization_job_advanced_app_polling.py

    Before running the sample:

    pip install "azure-ai-projects>=2.8.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_NAME       - Required. The name of the agent to optimize.
    3) EVALUATOR_NAME           - Required. The name of a registered project evaluator.
    4) POLL_INTERVAL_SECONDS    - Optional. Seconds between status polls. Defaults to 10.
    5) EVAL_MODEL               - Required. The evaluation model deployment in
                                  "{connectionName}/{deploymentName}" format.
    6) OPTIMIZATION_MODEL       - Optional. The model used for optimization. Defaults to "gpt-5.1".
"""

import os
import time

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentOptimizationCandidateSearchConfiguration,
    AgentOptimizationConfiguration,
    AgentOptimizationEvaluationConfiguration,
    AgentOptimizationEvaluator,
    AgentOptimizationFoundryAgentTargetConfiguration,
    AgentOptimizationJob,
    AgentOptimizationModelConfiguration,
    AgentOptimizationSpace,
    AgentOptimizationTargetCompletionEvaluationSet,
    AgentOptimizationTargetCompletionInlineDataSource,
    AgentOptimizationTargetCompletionTestCase,
    EvaluationModelConfiguration,
    JobStatus,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
evaluator_name = os.environ["EVALUATOR_NAME"]
poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))
eval_model = os.environ["EVAL_MODEL"]
optimization_model = os.environ.get("OPTIMIZATION_MODEL", "gpt-5.1")

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Create an optimization job without SDK polling.
    # ------------------------------------------------------------------
    print("Creating optimization job...")

    job = AgentOptimizationJob(
        target_configuration=AgentOptimizationFoundryAgentTargetConfiguration(name=agent_name),
        optimization_model_configuration=AgentOptimizationModelConfiguration(model=optimization_model),
        optimization_configuration=AgentOptimizationConfiguration(
            evaluation_configuration=AgentOptimizationEvaluationConfiguration(
                training_set=AgentOptimizationTargetCompletionEvaluationSet(
                    source=AgentOptimizationTargetCompletionInlineDataSource(
                        test_cases=[
                            AgentOptimizationTargetCompletionTestCase(
                                query="What is the capital of France?",
                                ground_truth="Paris",
                            ),
                            AgentOptimizationTargetCompletionTestCase(
                                query="What is 2 + 2?",
                                ground_truth="4",
                            ),
                            AgentOptimizationTargetCompletionTestCase(
                                query="Name the largest ocean on Earth.",
                                ground_truth="Pacific Ocean",
                            ),
                        ],
                    )
                ),
                evaluators=[AgentOptimizationEvaluator(name=evaluator_name)],
                evaluation_model=EvaluationModelConfiguration(model=eval_model),
            ),
            candidate_search_configuration=AgentOptimizationCandidateSearchConfiguration(max_candidates=3),
            agent_optimization_space=AgentOptimizationSpace(),
        ),
    )

    poller = project_client.agents.begin_create_optimization_job(
        job=job,
        polling=False,
    )
    job_id = poller.details["job_id"]
    if not job_id:
        raise RuntimeError("The create operation did not return an optimization job ID.")
    job = project_client.agents.get_optimization_job(job_id=job_id)
    print(f"Created job: id={job.id}, status={job.status}")

    # ------------------------------------------------------------------
    # 2. Poll until the job reaches a terminal state.
    # ------------------------------------------------------------------
    print(f"Polling job `{job.id}` to completion...", end="", flush=True)
    while job.status not in TERMINAL_STATUSES:
        time.sleep(poll_interval)
        job = project_client.agents.get_optimization_job(job_id=job.id)
        print(".", end="", flush=True)
    print()
    print(f"Final job status: `{job.status}`.")

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
    summary = result.candidate_summary
    if summary:
        print(f"\nBaseline candidate: {summary.baseline_id} (score={summary.baseline_score})")
        print(f"Best candidate:     {summary.best_id} (score={summary.best_score})")
        print(f"Completed candidates: {summary.completed_candidate_count}")

    print("Candidates:")
    for candidate in project_client.agents.list_optimization_candidates(job_id=job.id):
        score = candidate.evaluation.score if candidate.evaluation else None
        print(f"  - {candidate.name} | status={candidate.status} | score={score}")
