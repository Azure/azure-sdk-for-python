# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get, and list evaluations and eval runs.

    The OpenAI official tutorial is here: https://cookbook.openai.com/examples/evaluation/use-cases/evalsapi_audio_inputs

USAGE:
    python sample_evaluations_score_model_grader_with_audio.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b2" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
    3) AZURE_AI_MODEL_DEPLOYMENT_NAME_FOR_AUDIO - Required. The name of the model deployment for audio to use for evaluation, recommend to use "gpt-4o-audio-preview"
"""

import os
import base64

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
)
from openai.types.responses import EasyInputMessageParam, ResponseInputAudioParam
from openai.types.eval_create_params import DataSourceConfigCustom
from dotenv import load_dotenv


load_dotenv()
file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(file_path)

endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")
model_deployment_name_for_audio = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME_FOR_AUDIO", "")


def audio_to_base64(audio_path: str) -> str:
    """Read an audio file and return its base64-encoded content."""
    with open(audio_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


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
                    "audio_data": {
                        "type": "string",
                        "description": "Base64-encoded WAV audio data."
                    },
                    "expected": {
                        "type": "string",
                        "description": "The expected content in the audio."
                    }
                },
                "required": [
                    "audio_data",
                    "expected",
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
                    "content": "You are an audio analyzer. Listen to the audio, return a float score in [0,1] where 1 means the audio has the same meaning as {{item.expected}}.",
                },
                {
                    "role": "user",
                    "content": "{{sample.output_text}}",
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

    source_file_content_content = SourceFileContentContent(
        item={
            "audio_data": audio_to_base64(os.path.join(folder_path, "data_folder/sample_evaluations_score_model_grader_with_audio.wav")),
            "expected": "Don't forget a jacket",
        },
    )
    source_file_content = SourceFileContent(
        type="file_content",
        content=[source_file_content_content],
    )
    input_messages = InputMessagesTemplate(
        type="template",
        template=[
            EasyInputMessageParam(
                role="system",
                content="You are an assistant that can analyze audio input. You will be given an audio input to analyze.",
            ),
            InputMessagesTemplateTemplateEvalItem(
                role="user",
                type="message",
                content="Listen to the following audio and convert to text.",
            ),
            InputMessagesTemplateTemplateEvalItem(
                role="user",
                type="message",
                content=ResponseInputAudioParam(
                    type="input_audio",
                    input_audio={
                        "data": "{{item.audio_data}}",
                        "format": "wav",
                    }
                )
            )
        ],
    )

    print("Creating Eval Run")
    eval_run_object = client.evals.runs.create(
        eval_id=eval_object.id,
        name="Eval",
        metadata={"team": "eval-exp", "scenario": "notifications-v1"},
        data_source=CreateEvalCompletionsRunDataSourceParam(
            type="completions",
            source=source_file_content,
            model=model_deployment_name_for_audio,
            input_messages=input_messages,
            sampling_params={
                "temperature": 0.8,
            },
        )
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
