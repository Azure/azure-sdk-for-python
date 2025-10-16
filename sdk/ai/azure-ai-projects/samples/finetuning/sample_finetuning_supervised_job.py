# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.fine_tuning_jobs` methods to create, get, list, and cancel supervised fine-tuning jobs.

USAGE:
    python sample_finetuning_supervised_job.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_NAME - Required. The base model name to use for fine-tuning (e.g., "gpt-4o-mini").
    3) TRAINING_FILE_PATH - Required. Path to the training data file.
    4) VALIDATION_FILE_PATH - Optional. Path to the validation data file.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from pathlib import Path

endpoint = os.environ["PROJECT_ENDPOINT"]
model_name = os.environ.get("MODEL_NAME", "gpt-4.1")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "training_set.jsonl"))
validation_file_path = os.environ.get("VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "validation_set.jsonl"))

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        # Get OpenAI client from project client
        with project_client.get_openai_client(api_version="2024-10-21") as open_ai_client:

            # [START finetuning_supervised_job_sample]
            # Upload training and validation file using OpenAI client
            print("Uploading training file...")
            with open(training_file_path, "rb") as f:
                train_file = open_ai_client.files.create(file=f, purpose="fine-tune")
            print(f"Uploaded training file with ID: {train_file.id}")

            print("Uploading validation file...")
            with open(validation_file_path, "rb") as f:
                validation_file = open_ai_client.files.create(file=f, purpose="fine-tune")
            print(f"Uploaded validation file with ID: {validation_file.id}")
            
            # Create a supervised fine-tuning job using OpenAI client
            fine_tuning_job = open_ai_client.fine_tuning.jobs.create(
                training_file=train_file.id,
                validation_file=validation_file.id,
                model=model_name,
                method={
                    "type": "supervised",
                    "supervised": {
                        "hyperparameters": {
                            "n_epochs": 3,
                            "batch_size": 1,
                            "learning_rate_multiplier": 1.0
                        }
                    }
                }
            )
            print(fine_tuning_job)

            # Get the fine-tuning job by ID
            print(f"\nGetting fine-tuning job with ID: {fine_tuning_job.id}")
            retrieved_job = open_ai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
            print(retrieved_job)

            # List all fine-tuning jobs
            print("\nListing all fine-tuning jobs:")
            for job in open_ai_client.fine_tuning.jobs.list():
                print(job)

            # Cancel the fine-tuning job
            print(f"\nCancelling fine-tuning job with ID: {fine_tuning_job.id}")
            cancelled_job = open_ai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
            print(f"Successfully cancelled fine-tuning job: {cancelled_job.id}, Status: {cancelled_job.status}")
            # [END finetuning_supervised_job_sample]