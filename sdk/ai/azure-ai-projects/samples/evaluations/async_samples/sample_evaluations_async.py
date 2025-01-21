# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use evaluation operations from
    the Azure Evaluation service using a asynchronous client.

USAGE:
    python sample_evaluation_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import os

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.models import (
    Evaluation,
    Dataset,
    EvaluatorConfiguration,
    ConnectionType,
)
from azure.ai.evaluation import F1ScoreEvaluator, RelevanceEvaluator, ViolenceEvaluator


async def main():

    async with DefaultAzureCredential() as credential:

        async with AIProjectClient.from_connection_string(
            credential=credential,
            conn_str=os.environ["PROJECT_CONNECTION_STRING"],
        ) as project_client:

            # Upload data for evaluation
            data_id, _ = project_client.upload_file("./data/evaluate_test_data.jsonl")

            default_connection = await project_client.connections.get_default(
                connection_type=ConnectionType.AZURE_OPEN_AI
            )

            deployment_name = "<>"
            api_version = "<>"

            # Create an evaluation
            evaluation = Evaluation(
                display_name="Remote Evaluation",
                description="Evaluation of dataset",
                data=Dataset(id=data_id),
                evaluators={
                    "f1_score": EvaluatorConfiguration(
                        id=F1ScoreEvaluator.id,
                    ),
                    "relevance": EvaluatorConfiguration(
                        id=RelevanceEvaluator.id,
                        init_params={
                            "model_config": default_connection.to_evaluator_model_config(
                                deployment_name=deployment_name, api_version=api_version
                            )
                        },
                    ),
                    "violence": EvaluatorConfiguration(
                        id=ViolenceEvaluator.id,
                        init_params={"azure_ai_project": project_client.scope},
                    ),
                },
            )

            # Create evaluation
            evaluation_response = await project_client.evaluations.create(evaluation)

            # Get evaluation
            get_evaluation_response = await project_client.evaluations.get(evaluation_response.id)

            print("----------------------------------------------------------------")
            print("Created evaluation, evaluation ID: ", get_evaluation_response.id)
            print("Evaluation status: ", get_evaluation_response.status)
            if isinstance(get_evaluation_response.properties, dict):
                print(
                    "AI Foundry URI: ",
                    get_evaluation_response.properties["AiStudioEvaluationUri"],
                )
            print("----------------------------------------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
