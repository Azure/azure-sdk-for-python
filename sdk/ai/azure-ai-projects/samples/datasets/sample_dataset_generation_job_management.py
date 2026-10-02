# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Demonstrates the data generation job management operations on the
    `.datasets` sub-client. The sample:

      1. Submits an `EvaluationDataGenerationJobInputs` job (scenario `evaluation`,
         generation type `simple_qna`) from an inline prompt without SDK polling,
         and reads the job ID from the returned poller's `details`.
      2. Lists the most recent data generation jobs with `list_generation_jobs`.
      3. Gets the job with `get_generation_job`.
      4. Cancels the job with `cancel_generation_job` if it is still queued or
         in progress, and waits for the cancellation to complete.

USAGE:
    python sample_dataset_generation_job_management.py

    Before running the sample:

    pip install "azure-ai-projects>=2.8.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of an Azure OpenAI model
       deployment used to synthesize the QnA samples. For `simple_qna` evaluation
       jobs the deployed model must support the Azure OpenAI Responses API. See the
       supported-model list: https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#model-support
    3) DATASET_NAME - Optional. Name to assign to the generated output dataset.
       Defaults to `datagen-management-sample`. The service caps the rendered
       output name at 50 characters, so keep custom values short — the sample
       appends a unique run id suffix.
    4) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls while waiting for a cancellation to complete. Defaults to 10.
"""

import itertools
import os
import time
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationModelOptions,
    EvaluationDataGenerationJobInputs,
    EvaluationDataGenerationJobOutputConfiguration,
    JobStatus,
    PageOrder,
    PromptDataGenerationJobSource,
    SimpleQnADataGenerationJobConfiguration,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "datagen-management-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

MAX_JOBS_TO_LIST = 10
ACTIVE_STATUSES = {JobStatus.QUEUED, JobStatus.IN_PROGRESS}

# Unique per-run names so repeated runs do not collide.
# Output names are capped at 50 characters by the service.
run_id = (
    f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
)
output_dataset_name = f"{dataset_name}-{run_id}"
if len(output_dataset_name) > 50:
    raise ValueError(
        f"Output dataset name `{output_dataset_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        # ------------------------------------------------------------------
        # 1. Submit a data generation job without SDK polling.
        # ------------------------------------------------------------------
        job_inputs = EvaluationDataGenerationJobInputs(
            name=f"datagen-management-{run_id}",
            sources=[
                PromptDataGenerationJobSource(
                    description="Contoso refund policy",
                    prompt=(
                        "Contoso offers a full refund within 30 days of purchase for any product "
                        "returned in its original condition. After 30 days, store credit may be "
                        "issued at the discretion of customer support. Digital goods are "
                        "non-refundable once downloaded."
                    ),
                ),
            ],
            generation_configuration=SimpleQnADataGenerationJobConfiguration(
                # For evaluation jobs, the service requires max_samples to be between 1 and 1000.
                max_samples=15,
                # `simple_qna` REQUIRES model_options.
                model_options=DataGenerationModelOptions(model=model_name),
            ),
            output_configuration=EvaluationDataGenerationJobOutputConfiguration(
                name=output_dataset_name
            ),
        )

        print("Create a data generation job without SDK polling.")
        poller = project_client.datasets.begin_create_generation_job(
            job=job_inputs, polling=False
        )
        job_id = poller.details["job_id"]
        if not job_id:
            raise RuntimeError(
                "The create operation did not return a data generation job ID."
            )
        print(f"Created data generation job (id: {job_id}).")

        # ------------------------------------------------------------------
        # 2. List the most recent data generation jobs.
        # ------------------------------------------------------------------
        # `limit` sets the page size; the returned pager fetches further pages on
        # demand, so stop iterating after the first few jobs.
        print(f"List up to {MAX_JOBS_TO_LIST} of the most recent data generation jobs:")
        recent_jobs = project_client.datasets.list_generation_jobs(
            limit=MAX_JOBS_TO_LIST, order=PageOrder.DESC
        )
        for listed_job in itertools.islice(recent_jobs, MAX_JOBS_TO_LIST):
            print(
                f"  - id=`{listed_job.id}` name=`{listed_job.name}` "
                f"scenario=`{listed_job.scenario}` status=`{listed_job.status}`"
            )

        # ------------------------------------------------------------------
        # 3. Get the job.
        # ------------------------------------------------------------------
        job = project_client.datasets.get_generation_job(job_id=job_id)
        print(
            f"Got job: id=`{job.id}` name=`{job.name}` scenario=`{job.scenario}` "
            f"status=`{job.status}` created_at=`{job.created_at}`"
        )

        # ------------------------------------------------------------------
        # 4. Cancel the job if it is still running.
        # ------------------------------------------------------------------
        if job.status in ACTIVE_STATUSES:
            print(f"Cancel job `{job_id}` (current status `{job.status}`).")
            job = project_client.datasets.cancel_generation_job(job_id=job_id)
            print(f"Status after the cancel request: `{job.status}`.")

            print("Wait for the cancellation to complete.", end="", flush=True)
            while job.status in ACTIVE_STATUSES:
                time.sleep(poll_interval_seconds)
                job = project_client.datasets.get_generation_job(job_id=job_id)
                print(".", end="", flush=True)
            print()
            print(f"Final job status: `{job.status}`.")
        else:
            print(
                f"Job already reached the terminal status `{job.status}`; nothing to cancel."
            )


if __name__ == "__main__":
    main()
