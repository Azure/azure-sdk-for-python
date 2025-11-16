# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to generate cluster insights from evaluation runs
    using the synchronous AIProjectClient.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_evaluation_cluster_insight.py

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
import json
import tempfile
from typing import Union
from pprint import pprint
from dotenv import load_dotenv
from azure.ai.projects.models._enums import OperationState
from azure.ai.projects.models._models import EvaluationRunClusterInsightsRequest, Insight, InsightModelConfiguration
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai.types.eval_create_params import DataSourceConfigCustom, TestingCriterionLabelModel
from openai.types.evals.create_eval_jsonl_run_data_source_param import CreateEvalJSONLRunDataSourceParam, SourceFileID
from openai.types.evals.run_create_response import RunCreateResponse
from openai.types.evals.run_retrieve_response import RunRetrieveResponse

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")

if not model_deployment_name:
    raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME environment variable is not set")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Create an evaluation
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    )
    testing_criteria = [
        TestingCriterionLabelModel(
            type="label_model",
            name="sentiment_analysis",
            model=model_deployment_name,
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
        data_source_config=data_source_config, 
        testing_criteria=testing_criteria, 
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    # Create and upload JSONL data as a dataset
    eval_data = [
        {"item": {"query": "I love programming!"}},
        {"item": {"query": "I hate bugs."}},
        {"item": {"query": "The weather is nice today."}},
        {"item": {"query": "This is the worst movie ever."}},
        {"item": {"query": "Python is an amazing language."}},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for item in eval_data:
            f.write(json.dumps(item) + "\n")
        temp_file_path = f.name

    dataset = project_client.datasets.upload_file(
        name="sentiment-eval-data",
        version=str(int(time.time())),
        file_path=temp_file_path,
    )
    os.unlink(temp_file_path)
    print(f"Dataset created (id: {dataset.id}, name: {dataset.name}, version: {dataset.version})")

    if not dataset.id:
        raise ValueError("Dataset ID is None")

    # Create an eval run using the uploaded dataset
    eval_run: Union[RunCreateResponse, RunRetrieveResponse] = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name="Eval Run",
        data_source=CreateEvalJSONLRunDataSourceParam(source=SourceFileID(id=dataset.id, type="file_id"), type="jsonl"),
    )
    print(f"Evaluation run created (id: {eval_run.id})")

    while eval_run.status not in ["completed", "failed"]:
        print("Waiting for eval run to complete...")
        eval_run = openai_client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
        print(f"Evaluation run status: {eval_run.status}")
        time.sleep(5)

    # If the eval run completed successfully, generate cluster insights
    if eval_run.status == "completed":
        print("\n✓ Evaluation run completed successfully!")
        print(f"Evaluation run result counts: {eval_run.result_counts}")

        clusterInsight = project_client.insights.generate(
            Insight(
                display_name="Cluster analysis",
                request=EvaluationRunClusterInsightsRequest(eval_id=eval_object.id, run_ids=[eval_run.id], model_configuration=InsightModelConfiguration(model_deployment_name=model_deployment_name)),
            )
        )
        print(f"Started insight generation (id: {clusterInsight.id})")

        while clusterInsight.state not in [OperationState.SUCCEEDED, OperationState.FAILED]:
            print(f"Waiting for insight to be generated...")
            clusterInsight = project_client.insights.get(id=clusterInsight.id)
            print(f"Insight status: {clusterInsight.state}")
            time.sleep(5)

        if clusterInsight.state == OperationState.SUCCEEDED:
            print("\n✓ Cluster insights generated successfully!")
            pprint(clusterInsight)

    else:
        print("\n✗ Evaluation run failed. Cannot generate cluster insights.")

    project_client.datasets.delete(name=dataset.id, version=dataset.version)
    print("Dataset deleted")

    openai_client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
