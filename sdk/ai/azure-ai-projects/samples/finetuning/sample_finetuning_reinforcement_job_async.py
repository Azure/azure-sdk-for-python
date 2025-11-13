# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `.fine_tuning.jobs` methods to create reinforcement fine-tuning jobs.
    Supported OpenAI models: o4-mini

USAGE:
    python sample_finetuning_reinforcement_job_async.py

    Before running the sample:

    pip install azure-ai-projects>=2.0.0b1 azure-identity openai python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_NAME - Optional. The base model name to use for fine-tuning. Default to the `o4-mini` model.
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
model_name = os.environ.get("MODEL_NAME", "o4-mini")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "rft_training_set.jsonl"))
validation_file_path = os.environ.get(
    "VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "rft_validation_set.jsonl")
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

        grader = {
            "name": "Response Quality Grader",
            "type": "score_model",
            "model": "o3-mini",
            "input": [
                {
                    "role": "user",
                    "content": "Evaluate the model's response based on correctness and quality. Rate from 0 to 10.",
                }
            ],
            "range": [0.0, 10.0],
        }

        # For OpenAI model RFT fine-tuning jobs, "Standard" is the default training type.
        # To use global standard training, uncomment the extra_body parameter below.
        fine_tuning_job = await openai_client.fine_tuning.jobs.create(
            training_file=train_file.id,
            validation_file=validation_file.id,
            model=model_name,
            method={  # type: ignore[arg-type]
                "type": "reinforcement",
                "reinforcement": {
                    "grader": grader,  # type: ignore[typeddict-item]
                    "hyperparameters": {
                        "n_epochs": 1,
                        "batch_size": 4,
                        "learning_rate_multiplier": 2,
                        "eval_interval": 5,
                        "eval_samples": 2,
                        "reasoning_effort": "medium",
                    },
                },
            },
            # extra_body={"trainingType":"GlobalStandard"}
        )
        print(fine_tuning_job)


if __name__ == "__main__":
    asyncio.run(main())
