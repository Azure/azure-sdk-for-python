# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `.fine_tuning_jobs` methods to create and retrieve DPO (Direct Preference Optimization) fine-tuning jobs.

USAGE:
    python sample_finetuning_dpo_job_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiofiles

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_NAME - Required. The base model name to use for fine-tuning (e.g., "gpt-4o").
    3) TRAINING_FILE_PATH - Required. Path to the training data file.
    4) VALIDATION_FILE_PATH - Optional. Path to the validation data file.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from pathlib import Path

endpoint = os.environ["PROJECT_ENDPOINT"]
model_name = os.environ.get("MODEL_NAME", "gpt-4o")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "dpo_training_set.jsonl"))
validation_file_path = os.environ.get("VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "dpo_validation_set.jsonl"))


async def main():
    async with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            # Get async OpenAI client from project client
            async with await project_client.get_openai_client(api_version="2025-04-01-preview") as open_ai_client:

                # Upload training and validation file using async OpenAI client
                print("Uploading training file...")
                with open(training_file_path, "rb") as f:
                    train_file = await open_ai_client.files.create(file=f, purpose="fine-tune")
                print(f"Uploaded training file with ID: {train_file.id}")

                print("Uploading validation file...")
                with open(validation_file_path, "rb") as f:
                    validation_file = await open_ai_client.files.create(file=f, purpose="fine-tune")
                print(f"Uploaded validation file with ID: {validation_file.id}")
                
                # Create a DPO fine-tuning job using async OpenAI client
                fine_tuning_job = await open_ai_client.fine_tuning.jobs.create(
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
                        }
                    }
                )
                print(fine_tuning_job)

                # Get the fine-tuning job by ID
                print(f"\nGetting fine-tuning job with ID: {fine_tuning_job.id}")
                retrieved_job = await open_ai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(retrieved_job)


if __name__ == "__main__":
    asyncio.run(main())
