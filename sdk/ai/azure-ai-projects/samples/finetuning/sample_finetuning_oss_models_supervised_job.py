# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.fine_tuning.jobs` methods to create supervised fine-tuning jobs using open-source model.
    Supported open-source models with SFT: Ministral-3b

USAGE:
    python sample_finetuning_oss_models_supervised_job.py

    Before running the sample:

    pip install azure-ai-projects>=2.0.0b1 azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry portal.
    2) MODEL_NAME - Optional. The base model name to use for fine-tuning. Default to the `gpt-4.1` model.
    3) TRAINING_FILE_PATH - Optional. Path to the training data file. Default to the `data` folder.
    4) VALIDATION_FILE_PATH - Optional. Path to the validation data file. Default to the `data` folder.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from pathlib import Path

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_name = os.environ.get("MODEL_NAME", "Ministral-3B")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "sft_training_set.jsonl"))
validation_file_path = os.environ.get(
    "VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "sft_validation_set.jsonl")
)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # [START finetuning_oss_model_supervised_job_sample]
    print("Uploading training file...")
    with open(training_file_path, "rb") as f:
        train_file = openai_client.files.create(file=f, purpose="fine-tune")
    print(f"Uploaded training file with ID: {train_file.id}")

    print("Uploading validation file...")
    with open(validation_file_path, "rb") as f:
        validation_file = openai_client.files.create(file=f, purpose="fine-tune")
    print(f"Uploaded validation file with ID: {validation_file.id}")

    print("Creating supervised fine-tuning job")
    fine_tuning_job = openai_client.fine_tuning.jobs.create(
        training_file=train_file.id,
        validation_file=validation_file.id,
        model=model_name,
        method={
            "type": "supervised",
            "supervised": {"hyperparameters": {"n_epochs": 3, "batch_size": 1, "learning_rate_multiplier": 1.0}},
        },
        extra_body={"trainingType": "GlobalStandard"}, # Removing this field would lead to the default trainingType behaviour, which may change in the future.
    )
    print(fine_tuning_job)
    # [END finetuning_oss_model_supervised_job_sample]
