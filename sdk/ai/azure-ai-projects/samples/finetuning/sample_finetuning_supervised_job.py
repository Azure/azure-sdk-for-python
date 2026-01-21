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

    pip install azure-ai-projects>=2.0.0b1 python-dotenv azure-mgmt-cognitiveservices httpx

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
import httpx
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
resource_group = os.environ.get("AZURE_AI_PROJECTS_AZURE_RESOURCE_GROUP", "")
account_name = os.environ.get("AZURE_AI_PROJECTS_AZURE_AOAI_ACCOUNT", "")


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

        print("Waiting for deployment to complete...")
        deployment.result()

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


def wait_for_file_processing(credential, endpoint, file_id, poll_interval_seconds=2, max_wait_seconds=300):
    """Wait for an imported file to be processed.

    This is a custom implementation for files imported via the Azure-specific endpoint.

    Args:
        credential: Azure credential for authentication.
        endpoint: The Azure AI Project endpoint.
        file_id: The file ID to check.
        poll_interval_seconds: How often to poll for status (default 2 seconds).
        max_wait_seconds: Maximum time to wait (default 300 seconds).

    Returns:
        The file status when processed or error.
    """
    import_url = f"{endpoint}/openai/files/{file_id}?api-version=2025-11-15-preview"
    token = credential.get_token("https://ai.azure.com/.default")

    start_time = time.time()
    while True:
        with httpx.Client() as http_client:
            response = http_client.get(
                import_url,
                headers={"Authorization": f"Bearer {token.token}"},
            )
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "unknown")
                print(f"File {file_id} status: {status}")

                if status == "processed":
                    return result
                elif status == "error":
                    raise Exception(f"File processing failed: {result}")

        if time.time() - start_time > max_wait_seconds:
            raise TimeoutError(f"Timeout waiting for file {file_id} to process")

        time.sleep(poll_interval_seconds)


def import_file_from_url(credential, endpoint, filename, content_url):
    """Import a file from a URL (Azure Blob with SAS token or public URL) for fine-tuning.

    This uses the Azure-specific /openai/files/import endpoint.
    Useful when files are stored in Azure Blob Storage or publicly accessible locations.

    Args:
        credential: Azure credential for authentication.
        endpoint: The Azure AI Project endpoint.
        filename: Name for the imported file.
        content_url: URL to import from (Azure Blob URL with SAS token or public URL).

    Returns:
        The file ID of the imported file.
    """
    import_url = f"{endpoint}/openai/files/import?api-version=2025-11-15-preview"

    import_request = {"filename": filename, "purpose": "fine-tune", "content_url": content_url}

    token = credential.get_token("https://ai.azure.com/.default")

    with httpx.Client(timeout=60.0) as http_client:
        response = http_client.post(
            import_url,
            json=import_request,
            headers={"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"},
        )
        response.raise_for_status()

        result = response.json()
        file_id = result["id"]
        print(f"Imported file {filename}: {file_id}")
        return file_id


def import_files_from_url_and_create_job(openai_client, credential, training_file_url, validation_file_url):
    """Import files from URLs and create a fine-tuning job.

    This demonstrates importing training and validation files from URLs
    (e.g., Azure Blob Storage with SAS tokens or public URLs like GitHub raw files).
    """
    print("Importing training file from URL...")
    train_file_id = import_file_from_url(credential, endpoint, "imported_training_set.jsonl", training_file_url)

    print("Importing validation file from URL...")
    validation_file_id = import_file_from_url(credential, endpoint, "imported_validation_set.jsonl", validation_file_url)

    print("Waiting for imported files to be processed...")
    # Now that we use the local SDK with correct base_url, standard OpenAI methods should work
    openai_client.files.wait_for_processing(train_file_id)
    openai_client.files.wait_for_processing(validation_file_id)

    print("Creating supervised fine-tuning job with imported files...")
    fine_tuning_job = openai_client.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=validation_file_id,
        model=model_name,
        method={
            "type": "supervised",
            "supervised": {"hyperparameters": {"n_epochs": 3, "batch_size": 1, "learning_rate_multiplier": 1.0}},
        },
        extra_body={"trainingType": "Standard"},
    )
    print(f"Created fine-tuning job with imported files: {fine_tuning_job.id}")
    print(f"Status: {fine_tuning_job.status}")
    return fine_tuning_job


def create_job_with_auto_deployment(openai_client, train_file_id, validation_file_id, deployment_sku=0):
    """Create a fine-tuning job with auto-deployment enabled.

    When the job completes successfully, Azure OpenAI will automatically deploy the fine-tuned model.

    Args:
        openai_client: The OpenAI client.
        train_file_id: The training file ID.
        validation_file_id: The validation file ID.
        deployment_sku: 0 = Developer tier, 2 = GlobalStandard tier.

    Returns:
        The fine-tuning job object.
    """
    sku_name = "Developer" if deployment_sku == 0 else "GlobalStandard"
    print(f"Creating fine-tuning job with auto-deployment ({sku_name} tier)...")

    fine_tuning_job = openai_client.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=validation_file_id,
        model=model_name,
        method={
            "type": "supervised",
            "supervised": {"hyperparameters": {"n_epochs": 3, "batch_size": 1, "learning_rate_multiplier": 1.0}},
        },
        extra_body={
            "trainingType": "Standard",
            # Azure-specific: Enable auto-deployment when training completes
            "inference_configs": {
                "auto_inference_enabled": True,
                "inference_sku": deployment_sku,  # 0 = Developer, 2 = GlobalStandard
            },
        },
    )
    print(f"Created fine-tuning job with auto-deployment: {fine_tuning_job.id}")
    print(f"Status: {fine_tuning_job.status}")
    print("Model will be automatically deployed when training completes.")
    return fine_tuning_job


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        print("Uploading training file...")
        with open(training_file_path, "rb") as f:
            train_file = openai_client.files.create(file=f, purpose="fine-tune")
        print(f"Uploaded training file with ID: {train_file.id}")

        print("Uploading validation file...")
        with open(validation_file_path, "rb") as f:
            validation_file = openai_client.files.create(file=f, purpose="fine-tune")
        print(f"Uploaded validation file with ID: {validation_file.id}")

        print("Waits for the training and validation files to be processed...")
        openai_client.files.wait_for_processing(train_file.id)
        openai_client.files.wait_for_processing(validation_file.id)

        print("Creating supervised fine-tuning job")
        fine_tuning_job = openai_client.fine_tuning.jobs.create(
            training_file=train_file.id,
            validation_file=validation_file.id,
            model=model_name,
            method={
                "type": "supervised",
                "supervised": {"hyperparameters": {"n_epochs": 3, "batch_size": 1, "learning_rate_multiplier": 1.0}},
            },
            extra_body={
                "trainingType": "Standard"
            },  # Recommended approach to set trainingType. Omitting this field may lead to unsupported behavior.
        )
        print(fine_tuning_job)

        # Uncomment any of the following methods to test specific functionalities:
        # retrieve_job(openai_client, fine_tuning_job.id)

        # list_jobs(openai_client)

        # pause_job(openai_client, fine_tuning_job.id)

        # resume_job(openai_client, fine_tuning_job.id)

        # list_events(openai_client, fine_tuning_job.id)

        # list_checkpoints(openai_client, fine_tuning_job.id)

        # cancel_job(openai_client, fine_tuning_job.id)

        # deployment_name = deploy_model(openai_client, credential, fine_tuning_job.id)

        # infer(openai_client, deployment_name)

        # === Import files from URL examples ===
        # Import from Azure Blob Storage with SAS token:
        # training_url = os.environ.get("FT_TRAINING_FILE_URL")  # Azure Blob URL with SAS token
        # validation_url = os.environ.get("FT_VALIDATION_FILE_URL")  # Azure Blob URL with SAS token
        # import_files_from_url_and_create_job(openai_client, credential, training_url, validation_url)

        # Import from public URL (e.g., GitHub raw files):
        # base_url = "https://raw.githubusercontent.com/azure-ai-foundry/fine-tuning/refs/heads/main/Sample_Datasets/Supervised_Fine_Tuning/Tool-Calling"
        # training_url = f"{base_url}/stock_toolcall_training.jsonl"
        # validation_url = f"{base_url}/stock_toolcall_validation.jsonl"
        # import_files_from_url_and_create_job(openai_client, credential, training_url, validation_url)

        # === Auto-deployment examples ===
        # Create job with auto-deployment (Developer tier - lower cost, suitable for testing):
        # create_job_with_auto_deployment(openai_client, train_file.id, validation_file.id, deployment_sku=0)

        # Create job with auto-deployment (GlobalStandard tier - highest priority):
        # create_job_with_auto_deployment(openai_client, train_file.id, validation_file.id, deployment_sku=2)


if __name__ == "__main__":
    main()
