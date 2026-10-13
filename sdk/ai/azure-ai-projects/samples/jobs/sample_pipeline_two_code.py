# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Submit a two-step PipelineJob with a separate local Python code folder per step.

Set FOUNDRY_PROJECT_ENDPOINT, JOB_NAME, JOB_COMPUTE_ID (full compute resource ID),
JOB_ENVIRONMENT_IMAGE, JOB_NODE_UAI_RESOURCE_ID (full identity resource ID),
JOB_INSTANCE_TYPE, JOB_PRODUCER_CODE_DIR, and JOB_CONSUMER_CODE_DIR. Use absolute
paths for the code directories. The producer directory must contain produce.py,
which writes its first argument; the consumer directory must contain consume.py,
which reads its first argument.

Running this sample uploads both local code folders and submits a job.
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AssetTypes,
    CommandJob,
    Input,
    InputOutputModes,
    JobResourceConfiguration,
    Output,
    PipelineJob,
)
from azure.identity import AzureCliCredential


def build_job(
    compute_id: str,
    image: str,
    node_uai_id: str,
    instance_type: str,
    producer_code_dir: str,
    consumer_code_dir: str,
) -> PipelineJob:
    resources = JobResourceConfiguration(
        {
            "instanceCount": 1,
            "instanceType": instance_type,
            "properties": {"AISuperComputer": {"SLATier": "Premium"}},
        }
    )
    producer = CommandJob(
        command="python produce.py ${{outputs.message}}",
        code=producer_code_dir,
        environment_image_reference=image,
        compute=compute_id,
        user_assigned_identity_id=node_uai_id,
        resources=resources,
        outputs={
            # Inline nodes serialize the output type and mount mode, not this model's asset name.
            "message": Output(
                type=AssetTypes.URI_FILE,
                asset_name="message",
                mode=InputOutputModes.READ_WRITE_MOUNT,
            )
        },
    )
    consumer = CommandJob(
        command="python consume.py ${{inputs.message}}",
        code=consumer_code_dir,
        environment_image_reference=image,
        compute=compute_id,
        user_assigned_identity_id=node_uai_id,
        resources=resources,
        inputs={
            "message": Input(
                type=AssetTypes.URI_FILE,
                value="${{parent.jobs.produce.outputs.message}}",
            )
        },
    )
    return PipelineJob(
        display_name="Two-step code SDK test",
        compute_id=compute_id,
        settings={"default_compute": compute_id, "force_rerun": True},
        inputs={},
        outputs={},
        jobs={"produce": producer, "consume": consumer},
    )


def main() -> None:
    job_name = os.environ["JOB_NAME"]
    job = build_job(
        compute_id=os.environ["JOB_COMPUTE_ID"],
        image=os.environ["JOB_ENVIRONMENT_IMAGE"],
        node_uai_id=os.environ["JOB_NODE_UAI_RESOURCE_ID"],
        instance_type=os.environ["JOB_INSTANCE_TYPE"],
        producer_code_dir=os.environ["JOB_PRODUCER_CODE_DIR"],
        consumer_code_dir=os.environ["JOB_CONSUMER_CODE_DIR"],
    )
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
            name=job_name,
            job=job,
            headers={"x-ms-foundry-job-route": "execution"},
        )
        print(f"Submitted {created.name}: {created.id} (status: {created.status})")


if __name__ == "__main__":
    main()
