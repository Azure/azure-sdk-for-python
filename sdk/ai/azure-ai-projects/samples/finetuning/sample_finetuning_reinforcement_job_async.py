# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `.fine_tuning_jobs` methods to create, pause, resume, list events, and list checkpoints for reinforcement fine-tuning jobs.

USAGE:
    python sample_finetuning_reinforcement_job_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiofiles

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_NAME - Required. The base model name to use for fine-tuning (e.g., "o4-mini").
    3) TRAINING_FILE_PATH - Required. Path to the training data file.
    4) VALIDATION_FILE_PATH - Required. Path to the validation data file.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from pathlib import Path

endpoint = os.environ["PROJECT_ENDPOINT"]
model_name = os.environ.get("MODEL_NAME", "o4-mini")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "countdown_train_100.jsonl"))
validation_file_path = os.environ.get("VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "countdown_valid_50.jsonl"))


async def main():
    async with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            # Get async OpenAI client from project client
            async with await project_client.get_openai_client(api_version="2025-04-01-preview") as open_ai_client:

                # [START finetuning_reinforcement_job_async_sample]
                # Upload training and validation files using async OpenAI client
                print("Uploading training file...")
                with open(training_file_path, "rb") as f:
                    train_file = await open_ai_client.files.create(file=f, purpose="fine-tune")
                print(f"Uploaded training file with ID: {train_file.id}")

                print("Uploading validation file...")
                with open(validation_file_path, "rb") as f:
                    validation_file = await open_ai_client.files.create(file=f, purpose="fine-tune")
                print(f"Uploaded validation file with ID: {validation_file.id}")
                
                # Create a fine-tuning job using async OpenAI client with reinforcement method
                grader = {
                    "type": "score_model",
                    "model": "o3-mini",
                    "input": [
                        {
                            "role": "user",
                            "content": "Evaluate the model's response based on correctness and quality. Rate from 0 to 10."
                        }
                    ],
                    "range": [0.0, 10.0]
                }
                
                fine_tuning_job = await open_ai_client.fine_tuning.jobs.create(
                    training_file=train_file.id,
                    validation_file=validation_file.id,
                    model=model_name,
                    method={
                        "type": "reinforcement",
                        "reinforcement": {
                            "grader": grader,
                            "hyperparameters": {
                                "n_epochs": 1,
                                "batch_size": 4,
                                "learning_rate_multiplier": 2,
                                "eval_interval": 5,
                                "eval_samples": 2,
                                "reasoning_effort": "medium"
                            }
                        }
                    }
                )
                print(fine_tuning_job)

                # Pause the fine-tuning job
                print(f"\nPausing fine-tuning job with ID: {fine_tuning_job.id}")
                paused_job = await open_ai_client.fine_tuning.jobs.pause(fine_tuning_job.id)
                print(paused_job)

                # Resume the fine-tuning job
                print(f"\nResuming fine-tuning job with ID: {fine_tuning_job.id}")
                resumed_job = await open_ai_client.fine_tuning.jobs.resume(fine_tuning_job.id)
                print(resumed_job)

                # List events for the fine-tuning job
                print(f"\nListing events for fine-tuning job: {fine_tuning_job.id}")
                async for event in open_ai_client.fine_tuning.jobs.list_events(fine_tuning_job.id, limit=10):
                    print(event)

                # List checkpoints for the fine-tuning job
                # Note that to retrieve the checkpoints, job needs to be in terminal state.
                print(f"\nListing checkpoints for fine-tuning job: {fine_tuning_job.id}")
                async for checkpoint in open_ai_client.fine_tuning.jobs.checkpoints.list(fine_tuning_job.id, limit=10):
                    print(checkpoint)
                # [END finetuning_reinforcement_job_async_sample]


if __name__ == "__main__":
    asyncio.run(main())
