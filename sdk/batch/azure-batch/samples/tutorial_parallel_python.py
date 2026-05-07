"""Snippets extracted from articles/batch/tutorial-parallel-python.md.

Migrated from azure-batch 14.x to 15.1.0 (azure.batch.BatchClient).
"""

import datetime
import os
import sys
import time

from azure.batch import BatchClient, models
from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.blob import BlobServiceClient


# [START tutorial_parallel_config]
_BATCH_ACCOUNT_NAME = 'yourbatchaccount'
_BATCH_ACCOUNT_KEY = 'xxxxxxxxxxxxxxxxE+yXrRvJAqT9BlXwwo1CwF+SwAYOxxxxxxxxxxxxxxxx43pXi/gdiATkvbpLRl3x14pcEQ=='
_BATCH_ACCOUNT_URL = 'https://yourbatchaccount.yourbatchregion.batch.azure.com'
_STORAGE_ACCOUNT_NAME = 'mystorageaccount'
_STORAGE_ACCOUNT_KEY = 'xxxxxxxxxxxxxxxxy4/xxxxxxxxxxxxxxxxfwpbIC5aAWA8wDu+AFXZB827Mt9lybZB1nUcQbQiUrkPtilK5BQ=='
# [END tutorial_parallel_config]


def make_blob_client():
    # [START tutorial_parallel_blob_client]
    blob_service_client = BlobServiceClient(
        account_url=f"https://{_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/",
        credential=_STORAGE_ACCOUNT_KEY)
    # [END tutorial_parallel_blob_client]
    return blob_service_client


def make_batch_client():
    # [START tutorial_parallel_batch_client]
    credentials = AzureNamedKeyCredential(_BATCH_ACCOUNT_NAME,
                                          _BATCH_ACCOUNT_KEY)

    batch_client = BatchClient(
        endpoint=_BATCH_ACCOUNT_URL,
        credential=credentials)
    # [END tutorial_parallel_batch_client]
    return batch_client


def upload_inputs(blob_service_client, input_container_name, output_container_name, upload_file_to_container):
    # [START tutorial_parallel_upload_inputs]
    blob_service_client.create_container(input_container_name)
    blob_service_client.create_container(output_container_name)
    input_file_paths = []

    for folder, subs, files in os.walk(os.path.join(sys.path[0], './InputFiles/')):
        for filename in files:
            if filename.endswith(".mp4"):
                input_file_paths.append(os.path.abspath(
                    os.path.join(folder, filename)))

    # Upload the input files. This is the collection of files that are to be processed by the tasks.
    input_files = [
        upload_file_to_container(blob_service_client, input_container_name, file_path)
        for file_path in input_file_paths]
    # [END tutorial_parallel_upload_inputs]
    return input_files


def create_pool(batch_client: BatchClient, pool_id: str, _POOL_VM_SIZE: str,
                _DEDICATED_POOL_NODE_COUNT: int, _LOW_PRIORITY_POOL_NODE_COUNT: int):
    # [START tutorial_parallel_create_pool]
    new_pool = models.BatchPoolCreateOptions(
        id=pool_id,
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=models.BatchVmImageReference(
                publisher="Canonical",
                offer="UbuntuServer",
                sku="20.04-LTS",
                version="latest"
            ),
            node_agent_sku_id="batch.node.ubuntu 20.04"),
        vm_size=_POOL_VM_SIZE,
        target_dedicated_nodes=_DEDICATED_POOL_NODE_COUNT,
        target_low_priority_nodes=_LOW_PRIORITY_POOL_NODE_COUNT,
        start_task=models.BatchStartTask(
            command_line="/bin/bash -c \"apt-get update && apt-get install -y ffmpeg\"",
            wait_for_success=True,
            user_identity=models.UserIdentity(
                auto_user=models.AutoUserSpecification(
                    scope=models.AutoUserScope.POOL,
                    elevation_level=models.ElevationLevel.ADMIN)),
        )
    )
    batch_client.create_pool(pool=new_pool)
    # [END tutorial_parallel_create_pool]


def create_job(batch_client: BatchClient, job_id: str, pool_id: str):
    # [START tutorial_parallel_create_job]
    job = models.BatchJobCreateOptions(
        id=job_id,
        pool_info=models.BatchPoolInfo(pool_id=pool_id))

    batch_client.create_job(job=job)
    # [END tutorial_parallel_create_job]


def add_tasks(batch_client: BatchClient, job_id: str, input_files, output_container_sas_url):
    # [START tutorial_parallel_add_tasks]
    tasks = list()

    for idx, input_file in enumerate(input_files):
        input_file_path = input_file.file_path
        output_file_path = "".join((input_file_path).split('.')[:-1]) + '.mp3'
        command = "/bin/bash -c \"ffmpeg -i {} {} \"".format(
            input_file_path, output_file_path)
        tasks.append(models.BatchTaskCreateOptions(
            id='Task{}'.format(idx),
            command_line=command,
            resource_files=[input_file],
            output_files=[models.OutputFile(
                file_pattern=output_file_path,
                destination=models.OutputFileDestination(
                    container=models.OutputFileBlobContainerDestination(
                        container_url=output_container_sas_url)),
                upload_options=models.OutputFileUploadConfiguration(
                    upload_condition=models.OutputFileUploadCondition.TASK_SUCCESS))]
        )
        )
    batch_client.create_tasks(job_id=job_id, task_collection=tasks)
    # [END tutorial_parallel_add_tasks]


def wait_for_tasks(batch_client: BatchClient, job_id: str, timeout_expiration):
    # [START tutorial_parallel_wait_tasks]
    while datetime.datetime.now() < timeout_expiration:
        print('.', end='')
        sys.stdout.flush()
        tasks = batch_client.list_tasks(job_id=job_id)

        incomplete_tasks = [task for task in tasks if
                            task.state != models.BatchTaskState.COMPLETED]
        if not incomplete_tasks:
            print()
            return True
        else:
            time.sleep(1)
    # [END tutorial_parallel_wait_tasks]
