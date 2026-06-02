# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Snippets extracted from articles/batch/tutorial-parallel-python.md.

import datetime
import os
import shlex
import sys
import time

from azure.batch import BatchClient, models
from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.blob import BlobServiceClient


# [START tutorial_parallel_config]
_BATCH_ACCOUNT_NAME = os.getenv('AZURE_BATCH_ACCOUNT_NAME', '<batch-account-name>')
_BATCH_ACCOUNT_KEY = os.getenv('AZURE_BATCH_ACCOUNT_KEY', '<batch-account-key>')
_BATCH_ACCOUNT_URL = os.getenv('AZURE_BATCH_ACCOUNT_URL', 'https://yourbatchaccount.yourbatchregion.batch.azure.com')
_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', '<storage-account-name>')
_STORAGE_ACCOUNT_KEY = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', '<storage-account-key>')
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


def create_pool(batch_client: BatchClient, pool_id: str, pool_vm_size: str,
                dedicated_node_count: int, low_priority_node_count: int):
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
        vm_size=pool_vm_size,
        target_dedicated_nodes=dedicated_node_count,
        target_low_priority_nodes=low_priority_node_count,
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
        command = "/bin/bash -c \"ffmpeg -i {} {}\"".format(
            shlex.quote(input_file_path), shlex.quote(output_file_path))
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
    return False
    # [END tutorial_parallel_wait_tasks]
