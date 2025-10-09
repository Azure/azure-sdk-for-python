# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.fine_tuning_jobs` methods to create, get, list, and delete fine-tuning jobs.

USAGE:
    python sample_finetuning_job.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_NAME - Required. The base model name to use for fine-tuning (e.g., "gpt-35-turbo").
    3) TRAINING_FILE_PATH - Optional. Path to the training data file (default: "./data/sarcasm_training.jsonl").
    4) VALIDATION_FILE_PATH - Optional. Path to the validation data file (default: "./data/sarcasm_validation.jsonl").
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import JobCreateParams, Method, MethodTrainingType, SupervisedMethodParam, SupervisedHyperparametersParam

endpoint = os.environ["PROJECT_ENDPOINT"]
model_name = os.environ["MODEL_NAME"]
training_file_path = os.environ.get("TRAINING_FILE_PATH", "./data/sarcasm_training.jsonl")
validation_file_path = os.environ.get("VALIDATION_FILE_PATH", "./data/sarcasm_validation.jsonl")

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        # Upload training and validation files
        print("Uploading training file...")
        train_file = project_client.files.create(file=open(training_file_path, "rb"), purpose="fine-tune")
        print(f"Uploaded training file with ID: {train_file.id}")
        
        print("Uploading validation file...")
        valid_file = project_client.files.create(file=open(validation_file_path, "rb"), purpose="fine-tune")
        print(f"Uploaded validation file with ID: {valid_file.id}")
        
        print("\nCreating a new fine-tuning job...")
        
        # Configure supervised fine-tuning method with hyperparameters
        # [START create_fine_tuning_job]
        method = Method(
            type=MethodTrainingType.SUPERVISED,
            supervised=SupervisedMethodParam(
                hyperparameters=SupervisedHyperparametersParam(
                    n_epochs=3,  # Number of training epochs
                    batch_size=1,  # Batch size for training
                    learning_rate_multiplier=1  # Learning rate scaling factor
                )
            )
        )
        
        # Create a fine-tuning job with minimum required parameters
        job_create_params = JobCreateParams(
            model=model_name,
            training_file=train_file.id,
            validation_file=valid_file.id,
            method=method  # Using supervised fine-tuning method with hyperparameters
        )
        
        fine_tuning_job = project_client.fine_tuning_jobs.create(job_create_params)
        print(fine_tuning_job)
        # [END create_fine_tuning_job]

        # Get the fine-tuning job by ID
        # [START get_fine_tuning_job]
        print(f"\nGetting fine-tuning job with ID: {fine_tuning_job.id}")
        retrieved_job = project_client.fine_tuning_jobs.get(fine_tuning_job.id)
        print(retrieved_job)
        # [END get_fine_tuning_job]

        # List all fine-tuning jobs
        # [START list_fine_tuning_jobs]
        print("\nListing all fine-tuning jobs:")
        for job in project_client.fine_tuning_jobs.list():
            print(job)
        # [END list_fine_tuning_jobs]

        # Delete the fine-tuning job
        # [START delete_fine_tuning_job]
        print(f"\nDeleting fine-tuning job with ID: {fine_tuning_job.id}")
        project_client.fine_tuning_jobs.delete(fine_tuning_job.id)
        print(f"Successfully deleted fine-tuning job: {fine_tuning_job.id}")
        # [END delete_fine_tuning_job]
