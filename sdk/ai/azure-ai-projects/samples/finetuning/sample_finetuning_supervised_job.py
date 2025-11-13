# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.fine_tuning.jobs` methods to create, get, list, cancel, pause, resume, list events 
    and list checkpoints supervised fine-tuning jobs.
    It also shows how to deploy the fine-tuned model using Azure Cognitive Services Management 
    Client and perform inference on the deployed model.
    Supported OpenAI models: GPT 4o, 4o-mini, 4.1, 4.1-mini

USAGE:
    python sample_finetuning_supervised_job.py

    Before running the sample:

    pip install azure-ai-projects>=2.0.0b1 azure-identity openai python-dotenv azure-mgmt-cognitiveservices

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry portal.
    2) MODEL_NAME - Optional. The base model name to use for fine-tuning. Default to the `gpt-4.1` model.
    3) TRAINING_FILE_PATH - Optional. Path to the training data file. Default to the `data` folder.
    4) VALIDATION_FILE_PATH - Optional. Path to the validation data file. Default to the `data` folder.
    5) AZURE_AI_PROJECTS_AZURE_SUBSCRIPTION_ID - Required. Your Azure subscription ID for fine-tuned model deployment and inferencing.
    6) AZURE_AI_PROJECTS_AZURE_RESOURCE_GROUP - Required. The resource group name containing your Azure OpenAI resource.
    7) AZURE_AI_PROJECTS_AZURE_AOAI_ACCOUNT - Required. The name of your Azure OpenAI account for fine-tuned model deployment and inferencing.
"""

import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import Deployment, DeploymentProperties, DeploymentModel, Sku
from pathlib import Path

load_dotenv()

# For fine-tuning
endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_name = os.environ.get("MODEL_NAME", "gpt-4.1")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "sft_training_set.jsonl"))
validation_file_path = os.environ.get(
    "VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "sft_validation_set.jsonl")
)

# For Deployment and inferencing on model
subscription_id = os.environ["AZURE_AI_PROJECTS_AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["AZURE_AI_PROJECTS_AZURE_RESOURCE_GROUP"]
account_name = os.environ["AZURE_AI_PROJECTS_AZURE_AOAI_ACCOUNT"]

with (
    DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # [START finetuning_supervised_job_sample]
    print("Uploading training file...")
    with open(training_file_path, "rb") as f:
        train_file = openai_client.files.create(file=f, purpose="fine-tune")
    print(f"Uploaded training file with ID: {train_file.id}")

    print("Uploading validation file...")
    with open(validation_file_path, "rb") as f:
        validation_file = openai_client.files.create(file=f, purpose="fine-tune")
    print(f"Uploaded validation file with ID: {validation_file.id}")

    # For OpenAI model supervised fine-tuning jobs, "Standard" is the default training type.
    # To use global standard training, uncomment the extra_body parameter below.
    print("Creating supervised fine-tuning job")
    fine_tuning_job = openai_client.fine_tuning.jobs.create(
        training_file=train_file.id,
        validation_file=validation_file.id,
        model=model_name,
        method={
            "type": "supervised",
            "supervised": {"hyperparameters": {"n_epochs": 3, "batch_size": 1, "learning_rate_multiplier": 1.0}},
        },
        # extra_body={"trainingType":"GlobalStandard"}
    )
    print(fine_tuning_job)

    print(f"Getting fine-tuning job with ID: {fine_tuning_job.id}")
    retrieved_job = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id)
    print(retrieved_job)

    print("Listing all fine-tuning jobs:")
    for job in openai_client.fine_tuning.jobs.list():
        print(job)

    print("Listing only 10 fine-tuning jobs:")
    for job in openai_client.fine_tuning.jobs.list(limit=10):
        print(job)

    print(f"Pausing fine-tuning job with ID: {fine_tuning_job.id}")
    paused_job = openai_client.fine_tuning.jobs.pause(fine_tuning_job.id)
    print(paused_job)

    print(f"Resuming fine-tuning job with ID: {fine_tuning_job.id}")
    resumed_job = openai_client.fine_tuning.jobs.resume(fine_tuning_job.id)
    print(resumed_job)

    print(f"Listing events of fine-tuning job: {fine_tuning_job.id}")
    for event in openai_client.fine_tuning.jobs.list_events(fine_tuning_job.id):
        print(event)

    # Note that to retrieve the checkpoints, job needs to be in terminal state.
    print(f"Listing checkpoints of fine-tuning job: {fine_tuning_job.id}")
    for checkpoint in openai_client.fine_tuning.jobs.checkpoints.list(fine_tuning_job.id):
        print(checkpoint)

    print(f"Cancelling fine-tuning job with ID: {fine_tuning_job.id}")
    cancelled_job = openai_client.fine_tuning.jobs.cancel(fine_tuning_job.id)
    print(f"Successfully cancelled fine-tuning job: {cancelled_job.id}, Status: {cancelled_job.status}")

    # Deploy model (using Azure Management SDK - azure-mgmt-cognitiveservices)
    # Note: Deployment can only be started after the fine-tuning job completes successfully.
    print(f"Getting fine-tuning job with ID: {fine_tuning_job.id}")
    fine_tuned_model_name = openai_client.fine_tuning.jobs.retrieve(fine_tuning_job.id).fine_tuned_model
    deployment_name = "gpt-4-1-fine-tuned"

    with CognitiveServicesManagementClient(credential=credential, subscription_id=subscription_id) as cogsvc_client:

        deployment_model = DeploymentModel(format="OpenAI", name=fine_tuned_model_name, version="1")

        deployment_properties = DeploymentProperties(model=deployment_model)

        deployment_sku = Sku(name="GlobalStandard", capacity=100)

        deployment_config = Deployment(properties=deployment_properties, sku=deployment_sku)

        deployment = cogsvc_client.deployments.begin_create_or_update(
            resource_group_name=resource_group,
            account_name=account_name,
            deployment_name=deployment_name,
            deployment=deployment_config,
        )

        while deployment.status() not in ["Succeeded", "Failed"]:
            time.sleep(30)
            print(f"Status: {deployment.status()}")

    print(f"Testing fine-tuned model via deployment: {deployment_name}")

    response = openai_client.responses.create(
        model=deployment_name, input=[{"role": "user", "content": "Who invented the telephone?"}]
    )
    print(f"Model response: {response.output_text}")
    # [END finetuning_supervised_job_sample]
