# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
   `.fine_tuning_jobs` methods to create DPO (Direct Preference Optimization) fine-tuning jobs.
   Supported OpenAI models: GPT-4o, GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, and GPT-4o-mini.

USAGE:
    python sample_finetuning_dpo_job_async.py

    Before running the sample:

    pip install azure-ai-projects>=2.0.0b1 azure-identity openai python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_NAME - Optional. The base model name to use for fine-tuning. Default to the `gpt-4o` model.
    3) TRAINING_FILE_PATH - Optional. Path to the training data file. Default to the `data` folder.
    4) VALIDATION_FILE_PATH - Optional. Path to the validation data file. Default to the `data` folder.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from pathlib import Path

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "dpo_training_set.jsonl"))
validation_file_path = os.environ.get(
    "VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "dpo_validation_set.jsonl")
)


async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        await project_client.get_openai_client() as openai_client,
    ):

        print("Uploading training file...")
        with open(training_file_path, "rb") as f:
            train_file = await openai_client.files.create(file=f, purpose="fine-tune")
        print(f"Uploaded training file with ID: {train_file.id}")

        print("Uploading validation file...")
        with open(validation_file_path, "rb") as f:
            validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
        print(f"Uploaded validation file with ID: {validation_file.id}")

        # For OpenAI model DPO fine-tuning jobs, "Standard" is the default training type.
        # To use global standard training, uncomment the extra_body parameter below.
        print("Creating DPO fine-tuning job")
        fine_tuning_job = await openai_client.fine_tuning.jobs.create(
            training_file=train_file.id,
            validation_file=validation_file.id,
            model=model_name,
            method={
                "type": "dpo",
                "dpo": {
                    "hyperparameters": {
                        "n_epochs": 3,
                        "batch_size": 1,
                        "learning_rate_multiplier": 1.0,
                    }
                },
            },
            # extra_body={"trainingType":"GlobalStandard"}
        )
        print(fine_tuning_job)


if __name__ == "__main__":
    asyncio.run(main())
