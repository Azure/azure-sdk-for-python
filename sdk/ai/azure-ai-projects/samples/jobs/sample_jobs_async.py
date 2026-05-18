# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    `client.beta.jobs` methods to create, get, list, validate, stream logs,
    show services, download outputs, cancel, and delete CommandJobs.

USAGE:
    python sample_jobs_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the
       overview page of your Microsoft Foundry project.
    2) JOB_COMPUTE_ID - Required. The full resource ID of the compute cluster to run the job on.
       Example: /subscriptions/<sub>/resourceGroups/<rg>/providers/microsoft.cognitiveservices/accounts/<acct>/computes/<cluster>
    3) JOB_ENVIRONMENT_IMAGE - Required. The Docker image to use as the job environment.
       Example: mcr.microsoft.com/azureml/curated/acpt-pytorch-2.2-cuda12.1:48
    4) JOB_NAME - Optional. The name of the job to create. Defaults to "sample-command-job-async".
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    CommandJob,
    JobResourceConfiguration,
    Input,
    Output,
    AssetTypes,
    InputOutputModes,
)

load_dotenv()


async def main() -> None:

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    compute_id = os.environ["JOB_COMPUTE_ID"]
    environment_image = os.environ["JOB_ENVIRONMENT_IMAGE"]
    job_name = os.environ.get("JOB_NAME", "sample-command-job-async")

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        # --- Validate a job definition before submitting ---
        print("Validate a CommandJob definition")
        job_to_validate = CommandJob(
            display_name=job_name,
            command="echo hello",
            environment_image_reference=environment_image,
            compute=compute_id,
            resources=JobResourceConfiguration(instance_count=1),
        )
        validation_result = project_client.beta.jobs.validate(job_to_validate)
        print(validation_result)

        # --- Create or update a job ---
        print(f"\nCreate (or update) job `{job_name}`:")
        job = CommandJob(
            display_name=job_name,
            command="python ${{inputs.src}}/train.py --output_dir ${{outputs.output}}",
            environment_image_reference=environment_image,
            compute=compute_id,
            inputs={"src": Input(path="./data", type=AssetTypes.URI_FOLDER)},
            outputs={"output": Output(type=AssetTypes.URI_FOLDER, mode=InputOutputModes.READ_WRITE_MOUNT)},
            resources=JobResourceConfiguration(instance_count=1),
            tags={"sample": "true"},
        )
        created_job = await project_client.beta.jobs.create_or_update(name=job_name, job=job)
        print(created_job)

        # --- Get a job ---
        print(f"\nGet job `{job_name}`:")
        retrieved_job = await project_client.beta.jobs.get(name=job_name)
        print(retrieved_job)

        # --- List all jobs ---
        print("\nList all jobs:")
        async for listed_job in project_client.beta.jobs.list():
            print(listed_job)

        # --- Show services for a running job ---
        print(f"\nShow services for job `{job_name}`:")
        services = await project_client.beta.jobs.show_services(job_name)
        if services:
            for svc_name, svc in services.items():
                print(f"  {svc_name}: {vars(svc)}")
        else:
            print("  No services available.")

        # --- Stream job logs (blocks until job completes) ---
        print(f"\nStream logs for job `{job_name}`:")
        await project_client.beta.jobs.stream(name=job_name)

        # --- Download job outputs ---
        print(f"\nDownload outputs for job `{job_name}`:")
        await project_client.beta.jobs.download(name=job_name, all=True)
        print("Downloaded.")

        # --- Cancel a job ---
        print(f"\nCancel job `{job_name}`:")
        cancel_poller = await project_client.beta.jobs.begin_cancel(job_name)
        await cancel_poller.result()
        print("Cancelled.")

        # --- Delete a job ---
        print(f"\nDelete job `{job_name}`:")
        delete_poller = await project_client.beta.jobs.begin_delete(job_name)
        await delete_poller.result()
        print("Deleted.")


if __name__ == "__main__":
    asyncio.run(main())
