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
endpoint = "https://foundrysdk-eastus2-foundry-resou.services.ai.azure.com/api/projects/foundrysdk-eastus2-project"
model_name = os.environ.get("MODEL_NAME", "gpt-4.1")
script_dir = Path(__file__).parent
training_file_path = os.environ.get("TRAINING_FILE_PATH", os.path.join(script_dir, "data", "sft_training_set.jsonl"))
validation_file_path = os.environ.get(
    "VALIDATION_FILE_PATH", os.path.join(script_dir, "data", "sft_validation_set.jsonl")
)

# For Deployment and inferencing on model
subscription_id = "856c80fd-f14e-436b-b434-fbc44a9103f7"
resource_group = "foundrysdk-eastus2-rg"
account_name = "foundrysdk-eastus2-foundry-resou"


def pause_job(openai_client, job_id):
    """Pause a fine-tuning job.

    Job needs to be in running state in order to pause.
    """
    print(f"Pausing fine-tuning job with ID: {job_id}")
    paused_job = openai_client.fine_tuning.jobs.pause(job_id)
    print(paused_job)


def resume_job(openai_client, job_id):
    """Resume a fine-tuning job.

    Job needs to be in paused state in order to resume.
    """
    print(f"Resuming fine-tuning job with ID: {job_id}")
    resumed_job = openai_client.fine_tuning.jobs.resume(job_id)
    print(resumed_job)


def deploy_model(openai_client, credential, job_id):
    """Deploy the fine-tuned model.

    Deploy model using Azure Management SDK (azure-mgmt-cognitiveservices).
    Note: Deployment can only be started after the fine-tuning job completes successfully.
    """
    print(f"Retrieving fine-tuning job with ID: {job_id}")
    fine_tuned_model_name = openai_client.fine_tuning.jobs.retrieve(job_id).fine_tuned_model
    deployment_name = "gpt-4-1-fine-tuned"

    with CognitiveServicesManagementClient(credential=credential, subscription_id=subscription_id) as cogsvc_client:

        deployment_model = DeploymentModel(format="OpenAI", name=fine_tuned_model_name, version="1")

        deployment_properties = DeploymentProperties(model=deployment_model)

        deployment_sku = Sku(name="GlobalStandard", capacity=100)

        deployment_config = Deployment(properties=deployment_properties, sku=deployment_sku)

        print(f"Deploying fine-tuned model: {fine_tuned_model_name} with deployment name: {deployment_name}")
        deployment = cogsvc_client.deployments.begin_create_or_update(
            resource_group_name=resource_group,
            account_name=account_name,
            deployment_name=deployment_name,
            deployment=deployment_config,
        )

        while deployment.status() not in ["Succeeded", "Failed"]:
            time.sleep(30)
            print(f"Deployment status: {deployment.status()}")

    print(f"Model deployment completed: {deployment_name}")
    return deployment_name


def infer(openai_client, deployment_name):
    """Perform inference on the deployed fine-tuned model."""
    print(f"Testing fine-tuned model via deployment: {deployment_name}")

    response = openai_client.responses.create(
        model=deployment_name, input=[{"role": "user", "content": "Who invented the telephone?"}]
    )
    print(f"Model response: {response.output_text}")


def list_jobs(openai_client):
    """List fine-tuning jobs."""
    print("Listing all fine-tuning jobs:")
    for job in openai_client.fine_tuning.jobs.list():
        print(job)


def list_events(openai_client, job_id):
    """List events of a fine-tuning job."""
    print(f"Listing events of fine-tuning job: {job_id}")
    for event in openai_client.fine_tuning.jobs.list_events(job_id):
        print(event)


def list_checkpoints(openai_client, job_id):
    """List checkpoints of a fine-tuning job.

    Note that to retrieve the checkpoints, job needs to be in terminal state.
    """
    print(f"Listing checkpoints of fine-tuning job: {job_id}")
    for checkpoint in openai_client.fine_tuning.jobs.checkpoints.list(job_id):
        print(checkpoint)


def cancel_job(openai_client, job_id):
    """Cancel a fine-tuning job."""
    print(f"Cancelling fine-tuning job with ID: {job_id}")
    cancelled_job = openai_client.fine_tuning.jobs.cancel(job_id)
    print(f"Successfully cancelled fine-tuning job: {cancelled_job.id}, Status: {cancelled_job.status}")


def retrieve_job(openai_client, job_id):
    """Retrieve a fine-tuning job."""
    print(f"Getting fine-tuning job with ID: {job_id}")
    retrieved_job = openai_client.fine_tuning.jobs.retrieve(job_id)
    print(retrieved_job)


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        

        # Uncomment any of the following methods to test specific functionalities:
        # retrieve_job(openai_client, fine_tuning_job.id)

        # list_jobs(openai_client)

        # pause_job(openai_client, fine_tuning_job.id)

        # resume_job(openai_client, fine_tuning_job.id)

        # list_events(openai_client, fine_tuning_job.id)

        # list_checkpoints(openai_client, fine_tuning_job.id)

        # cancel_job(openai_client, fine_tuning_job.id)

        # deployment_name = deploy_model(openai_client, credential, fine_tuning_job.id)

        infer(openai_client, "gpt-4-1-fine-tuned")


if __name__ == "__main__":
    main()
