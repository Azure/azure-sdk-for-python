# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Author a two-step PipelineJob from Python function bodies.

Set FOUNDRY_PROJECT_ENDPOINT, JOB_COMPUTE_ID, JOB_ENVIRONMENT_IMAGE,
JOB_NODE_UAI_RESOURCE_ID, and JOB_INSTANCE_TYPE before running. Each function
gets its own generated Code folder, which is uploaded when the job is submitted.
Running this sample uploads both folders and submits a job.
"""

import os
from pathlib import Path

from azure.ai.projects import AIProjectClient, dsl
from azure.ai.projects.dsl import Input, Output
from azure.identity import AzureCliCredential


@dsl.component
def produce(text: str, message: Output(type="uri_file")) -> None:  # type: ignore[valid-type]
    Path(message).write_text(text, encoding="utf-8")


@dsl.component
def consume(message: Input(type="uri_file"), receipt: Output(type="uri_file")) -> None:  # type: ignore[valid-type]
    Path(receipt).write_text(Path(message).read_text(encoding="utf-8").upper(), encoding="utf-8")


@dsl.pipeline(
    compute_id=os.environ["JOB_COMPUTE_ID"],
    environment_image_reference=os.environ["JOB_ENVIRONMENT_IMAGE"],
    user_assigned_identity_id=os.environ["JOB_NODE_UAI_RESOURCE_ID"],
    instance_type=os.environ["JOB_INSTANCE_TYPE"],
)
def workflow(text: str):
    first = produce(text=text)
    second = consume(message=first.outputs.message)
    return {"receipt": second.outputs.receipt}


def main() -> None:
    job = workflow(text="hello")
    with (
        AzureCliCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            credential=credential,
            allow_preview=True,
            retry_total=0,
        ) as client,
    ):
        created = client.beta.jobs.create_or_update(
            job, experiment_name="pipeline_samples", headers={"x-ms-foundry-job-route": "execution"}
        )
        print(f"Submitted {created.name}: {created.id} (status: {created.status})")


if __name__ == "__main__":
    main()
