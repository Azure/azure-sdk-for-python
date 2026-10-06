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

    pip install "azure-ai-projects>=2.8.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_NAME      - Required. The name of the agent to optimize.
    3) EVALUATOR_NAME          - Required. The name of a registered project evaluator.
    4) POLL_INTERVAL_SECONDS   - Optional. Seconds between status polls. Defaults to 10.
    5) EVAL_MODEL              - Required. The evaluation model deployment in
                                 "{connectionName}/{deploymentName}" format.
    6) OPTIMIZATION_MODEL      - Optional. The model used for optimization. Defaults to "gpt-5.1".

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
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
evaluator_name = os.environ["EVALUATOR_NAME"]
poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))
eval_model = os.environ["EVAL_MODEL"]
optimization_model = os.environ.get("OPTIMIZATION_MODEL", "gpt-5.1")


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. Create an optimization job and retain the SDK-managed poller.
    # ------------------------------------------------------------------
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

    created_jobs: list[AgentOptimizationJob] = []

    def raw_response_hook(response):
        response.http_response.read()
        created_jobs.append(AgentOptimizationJob(response.http_response.json()))

    print("Begin creating an agent optimization job.")
    poller = project_client.agents.begin_create_optimization_job(
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
    cancelled = project_client.agents.cancel_optimization_job(job_id=created_job.id)
    print(f"Job {cancelled.id} status: {cancelled.status}")

    print("Wait for the SDK poller to observe the cancellation.")
    while not poller.done():
        print(f"status=`{poller.status()}`")
        time.sleep(poll_interval)

    print(f"Final LRO status: `{poller.status()}`.")
