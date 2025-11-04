# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    .fine_tuning.jobs methods to create, get, list, cancel, pause, resume, list events and list checkpoints supervised fine-tuning jobs.

USAGE:
    python sample_finetuning_supervised_job_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity openai python-dotenv aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_NAME - Optional. The base model name to use for fine-tuning. Default to the `gpt-4.1` model.
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

endpoint = os.environ["PROJECT_ENDPOINT"]
# Supported Models: GPT 4o, 4o-mini, 4.1, 4.1-mini, 4.1-nano;
# Llama 2 and Llama 3.1; Phi 4, Phi-4-mini-instruct; Mistral Nemo, Ministral-3B, Mistral Large (2411); NTT Tsuzumi-7b
model_name = os.environ.get("MODEL_NAME", "gpt-4.1")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "sft_training_set.jsonl"))
validation_file_path = os.environ.get(
    "VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "sft_validation_set.jsonl")
)


async def main():
    async with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            async with await project_client.get_openai_client() as openai_client:

                print("Uploading training file...")
                with open(training_file_path, "rb") as f:
                    train_file = await openai_client.files.create(file=f, purpose="fine-tune")
                print(f"Uploaded training file with ID: {train_file.id}")

                print("Uploading validation file...")
                with open(validation_file_path, "rb") as f:
                    validation_file = await openai_client.files.create(file=f, purpose="fine-tune")
                print(f"Uploaded validation file with ID: {validation_file.id}")

                print("Creating supervised fine-tuning job")
                fine_tuning_job = await openai_client.fine_tuning.jobs.create(
                    training_file=train_file.id,
                    validation_file=validation_file.id,
                    model=model_name,
                    method={
                        "type": "supervised",
                        "supervised": {
                            "hyperparameters": {"n_epochs": 3, "batch_size": 1, "learning_rate_multiplier": 1.0}
                        },
                    },
                )
                print(fine_tuning_job)

                print(f"Getting fine-tuning job with ID: {fine_tuning_job.id}")
                retrieved_job = await openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
                print(retrieved_job)

                print("Listing all fine-tuning jobs:")
                async for job in await openai_client.fine_tuning.jobs.list():
                    print(job)

                print(f"Pausing fine-tuning job with ID: {fine_tuning_job.id}")
                paused_job = await openai_client.fine_tuning.jobs.pause(fine_tuning_job.id)
                print(paused_job)

                print(f"Resuming fine-tuning job with ID: {fine_tuning_job.id}")
                resumed_job = await openai_client.fine_tuning.jobs.resume(fine_tuning_job.id)
                print(resumed_job)

                print(f"Listing events for fine-tuning job: {fine_tuning_job.id}")
                async for event in await openai_client.fine_tuning.jobs.list_events(fine_tuning_job.id, limit=10):
                    print(event)

                # Note that to retrieve the checkpoints, job needs to be in terminal state.
                print(f"Listing checkpoints for fine-tuning job: {fine_tuning_job.id}")
                async for checkpoint in await openai_client.fine_tuning.jobs.checkpoints.list(
                    fine_tuning_job.id, limit=10
                ):
                    print(checkpoint)

                print(f"Cancelling fine-tuning job with ID: {fine_tuning_job.id}")
                cancelled_job = await openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
                print(f"Successfully cancelled fine-tuning job: {cancelled_job.id}, Status: {cancelled_job.status}")


if __name__ == "__main__":
    asyncio.run(main())
