# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs.

USAGE:
    python sample_evaluations_score_model_grader_with_image.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
"""

import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import time
from pprint import pprint
from openai.types.evals.create_eval_completions_run_data_source_param import (
    CreateEvalCompletionsRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
    InputMessagesTemplate,
    InputMessagesTemplateTemplateEvalItem,
    InputMessagesTemplateTemplateEvalItemContentInputImage,
)
from openai.types.responses import EasyInputMessageParam
from openai.types.eval_create_params import DataSourceConfigCustom
from dotenv import load_dotenv


load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):

    data_source_config = DataSourceConfigCustom(
        {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "The URL of the image to be evaluated."
                    },
                    "caption": {
                        "type": "string",
                        "description": "The caption describing the image."
                    },
                },
                "required": [
                    "image_url",
                    "caption",
                ],
            },
            "include_sample_schema": True,
        }
    )

    testing_criteria = [
        {
            "type": "score_model",
            "name": "score_grader",
            "model": model_deployment_name,
            "input": [
                {
                    "role": "system",
                    "content": "You are an expert grader. Judge how well the model response {{sample.output_text}} describes the image as well as matches the caption {{item.caption}}. Output a score of 1 if it's an excellent match with both. If it's somewhat compatible, output a score around 0.5. Otherwise, give a score of 0."
                },
                {
                    "role": "user",
                    "content":
                        {
                            "type": "input_image", 
                            "image_url": "{{item.image_url}}"
                        }
                }
            ],
            "range": [
                0.0,
                1.0
            ],
            "pass_threshold": 0.5,
        },
    ]

    print("Creating evaluation")
    eval_object = client.evals.create(
        name="OpenAI graders test",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    print("Get evaluation by Id")
    eval_object_response = client.evals.retrieve(eval_object.id)
    print("Evaluation Response:")
    pprint(eval_object_response)

    sourceFileContentContent = SourceFileContentContent(
        item={
            "image_url": "http://lh6.ggpht.com/-IvRtNLNcG8o/TpFyrudaT6I/AAAAAAAAM6o/_11MuAAKalQ/IMG_3422.JPG?imgmax=800",
            "caption": "a very typical bus station",
        },
    )
    sourceFileContent = SourceFileContent(
        type="file_content",
        content=[sourceFileContentContent],
    )
    inputMessages = InputMessagesTemplate(
        type="template",
        template=[
            EasyInputMessageParam(
                role="system",
                content="You are an assistant that analyzes images and provides captions that accurately describe the content of the image.",
            ),
            InputMessagesTemplateTemplateEvalItem(
                role="user",
                type="message",
                content=InputMessagesTemplateTemplateEvalItemContentInputImage(
                    type="input_image",
                    image_url="{{item.image_url}}",
                    detail="auto",
                )
            ),
        ],
    )

    print("Creating Eval Run")
    eval_run_object = client.evals.runs.create(
        eval_id=eval_object.id,
        name="Eval",
        metadata={"team": "eval-exp", "scenario": "notifications-v1"},
        data_source=CreateEvalCompletionsRunDataSourceParam(
            type="completions",
            source=sourceFileContent,
            model=model_deployment_name,
            input_messages=inputMessages,
            sampling_params={
                "temperature": 0.8,
            }
        ),
    )
    print(f"Eval Run created (id: {eval_run_object.id}, name: {eval_run_object.name})")
    pprint(eval_run_object)

    print("Get Eval Run by Id")
    eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
    print("Eval Run Response:")
    pprint(eval_run_response)

    while True:
        run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
        if run.status == "completed" or run.status == "failed":
            output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
            pprint(output_items)
            print(f"Eval Run Report URL: {run.report_url}")

            break
        time.sleep(5)
        print("Waiting for eval run to complete...")

    client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
