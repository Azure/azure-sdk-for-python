# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_misc.py
DESCRIPTION:
    These samples demonstrate different ways to configure generic entities including jobs, assets, and components.
USAGE:
    python ml_samples_misc.py

"""

import os


class MiscConfigurationOptions(object):
    def ml_misc_config(self):
        from azure.identity import DefaultAzureCredential

        from azure.ai.ml import MLClient

        # subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        # resource_group = os.environ["RESOURCE_GROUP_NAME"]
        subscription_id = "e9b2ec51-5c94-4fa8-809a-dc1e695e4896"
        resource_group = "dipeck-rg1"
        credential = DefaultAzureCredential()
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name="r-bug-bash")

        # [START job_operations_create_and_update]
        import uuid

        from azure.ai.ml import load_job

        job_name = f"iris-dataset-job-{str(uuid.uuid4())}"
        created_job = ml_client.jobs.create_or_update(
            name=job_name,
            job=load_job(
                "./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test.yml",
                params_override=[{"name": job_name}, {"compute": "cpucluster"}],
            ),
        )
        updated_job = ml_client.jobs.create_or_update(
            job=load_job(
                "./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test.yml",
                params_override=[{"name": "new_job_name"}, {"compute": "cpucluster"}],
            )
        )

        # [START job_operations_list]
        from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType

        list_of_jobs = ml_client.jobs.list(parent_job_name=job_name, list_view_type=ListViewType.ARCHIVED_ONLY)
        # [END job_operations_list]

        # [START job_operations_get]
        retrieved_job = ml_client.jobs.get(job_name)
        # [END job_operations_get]

        # [START job_operations_show_services]
        job_services = ml_client.jobs.show_services(job_name)
        # [END job_operations_show_services]

        # [START job_operations_cancel]
        cancel_poller = ml_client.jobs.begin_cancel(job_name)
        print(cancel_poller.result())
        # [END job_operations_cancel]

        # [START job_operations_validate]
        from azure.ai.ml import load_job
        from azure.ai.ml.entities import PipelineJob

        pipeline_job: PipelineJob = load_job(
            "./sdk/ml/azure-ai-ml/tests/test_configs/pipeline_jobs/invalid/combo.yml",
            params_override=[{"name": job_name}, {"compute": "cpucluster"}],
        )
        print(ml_client.jobs.validate(pipeline_job).error_messages)
        # [END job_operations_validate]

        # [START job_operations_archive]
        ml_client.jobs.archive(name=job_name)
        # [END job_operations_archive]

        # [START job_operations_restore]
        ml_client.jobs.restore(name=job_name)
        # [END job_operations_restore]

        # [START job_operations_stream_logs]
        running_job = ml_client.jobs.create_or_update(
            load_job(
                "./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test.yml",
                params_override=[{"name": job_name}, {"compute": "cpucluster"}],
            )
        )
        ml_client.jobs.stream(running_job)
        # [END job_operations_stream_logs]

        # [START job_operations_download]
        ml_client.jobs.download(name=job_name, download_path="./job-1-logs", all=True)
        # [END job_operations_download]


if __name__ == "__main__":
    sample = MiscConfigurationOptions()
    sample.ml_misc_config()
