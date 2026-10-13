# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""One-step PipelineJob sample. Review the request before running it against a project.

Set FOUNDRY_PROJECT_ENDPOINT, JOB_NAME, JOB_COMPUTE_ID (full compute resource ID),
JOB_ENVIRONMENT_IMAGE (direct container image), JOB_NODE_UAI_RESOURCE_ID (full
user-assigned identity resource ID), and JOB_INSTANCE_TYPE for the target compute.
DefaultAzureCredential must have permission to submit jobs to the project.
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CommandJob, Input, JobResourceConfiguration, PipelineJob
from azure.identity import DefaultAzureCredential


def build_job(compute_id: str, image: str, node_uai_id: str, instance_type: str) -> PipelineJob:
    command = CommandJob(
        command="echo hello ${{inputs.name}}",
        environment_image_reference=image,
        compute=compute_id,
        inputs={"name": Input(type="literal", value="${{parent.inputs.name}}")},
        user_assigned_identity_id=node_uai_id,
        resources=JobResourceConfiguration(
            {
                "instanceCount": 1,
                "instanceType": instance_type,
                "properties": {"AISuperComputer": {"SLATier": "Premium"}},
            }
        ),
    )
    return PipelineJob(
        display_name="Pipeline hello world",
        compute_id=compute_id,
        settings={"default_compute": compute_id, "force_rerun": True},
        inputs={"name": Input(type="literal", value="world")},
        outputs={},
        jobs={"hello": command},
    )


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    job_name = os.environ["JOB_NAME"]
    job = build_job(
        compute_id=os.environ["JOB_COMPUTE_ID"],
        image=os.environ["JOB_ENVIRONMENT_IMAGE"],
        node_uai_id=os.environ["JOB_NODE_UAI_RESOURCE_ID"],
        instance_type=os.environ["JOB_INSTANCE_TYPE"],
    )
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as client,
    ):
        created = client.beta.jobs.create_or_update(
            name=job_name,
            job=job,
            headers={"x-ms-foundry-job-route": "execution"},
        )
        print(f"Submitted {created.name}: {created.id} (status: {created.status})")


if __name__ == "__main__":
    main()
