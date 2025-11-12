# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to compare evaluation runs and generate
    insights using the synchronous AIProjectClient.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_evaluation_compare_insight.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import time
from pprint import pprint
from dotenv import load_dotenv
from azure.ai.projects.models._enums import OperationState
from azure.ai.projects.models._models import EvaluationComparisonRequest, Insight
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai.types.eval_create_params import DataSourceConfigCustom, TestingCriterionLabelModel
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
)
from openai.types.evals.run_retrieve_response import RunRetrieveResponse

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    openai_client = project_client.get_openai_client()

    # Create a sample evaluation with two eval runs to compare
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    )
    testing_criteria = [
        TestingCriterionLabelModel(
            type="label_model",
            name="sentiment_analysis",
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            input=[
                {
                    "role": "developer",
                    "content": "Classify the sentiment of the following statement as one of 'positive', 'neutral', or 'negative'",
                },
                {"role": "user", "content": "Statement: {{item.query}}"},
            ],
            passing_labels=["positive", "neutral"],
            labels=["positive", "neutral", "negative"],
        )
    ]
    eval_object = openai_client.evals.create(
        name="Sentiment Evaluation",
        data_source_config=data_source_config,  # type: ignore
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    eval_run_1 = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name="Evaluation Run 1",
        data_source=CreateEvalJSONLRunDataSourceParam(
            source=SourceFileContent(
                type="file_content",
                content=[{"item": {"query": "I love programming!"}}, {"item": {"query": "I hate bugs."}}],
            ),
            type="jsonl",
        ),
    )
    print(f"Evaluation run created (id: {eval_run_1.id})")

    eval_run_2 = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name="Evaluation Run 2",
        data_source=CreateEvalJSONLRunDataSourceParam(
            source=SourceFileContent(
                type="file_content",
                content=[
                    {"item": {"query": "The weather is nice today."}},
                    {"item": {"query": "This is the worst movie ever."}},
                ],
            ),
            type="jsonl",
        ),
    )
    print(f"Evaluation run created (id: {eval_run_2.id})")

    # Wait for both evaluation runs to complete
    runs_to_wait = [eval_run_1, eval_run_2]
    completed_runs: dict[str, RunRetrieveResponse] = {}

    while len(completed_runs) < len(runs_to_wait):
        for eval_run in runs_to_wait:
            if eval_run.id in completed_runs:
                continue
            run = openai_client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
            if run.status in ["completed", "failed"]:
                print(f"Evaluation run {run.id} {run.status}")
                completed_runs[eval_run.id] = run
        if len(completed_runs) < len(runs_to_wait):
            time.sleep(5)
            print(f"Waiting for {len(runs_to_wait) - len(completed_runs)} evaluation run(s) to complete...")

    failed_runs = [run for run in completed_runs.values() if run.status == "failed"]

    if not failed_runs:
        print("\n✓ Both evaluation runs completed successfully!")

        # Generate comparison insights
        compareInsight = project_client.insights.generate(
            Insight(
                display_name="Comparison of Evaluation Runs",
                request=EvaluationComparisonRequest(
                    eval_id=eval_object.id, baseline_run_id=eval_run_1.id, treatment_run_ids=[eval_run_2.id]
                ),
            )
        )
        print(f"Started insight generation (id: {compareInsight.id})")

        while compareInsight.state not in [OperationState.SUCCEEDED, OperationState.FAILED]:
            compareInsight = project_client.insights.get(id=compareInsight.id)
            print(f"Waiting for insight to be generated...current status: {compareInsight.state}")
            time.sleep(5)

        if compareInsight.state == OperationState.SUCCEEDED:
            print("\n✓ Evaluation comparison generated successfully!")
            pprint(compareInsight)

    else:
        print("\n✗ One or more eval runs failed. Cannot generate comparison insight.")

    openai_client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
