# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Snippets extracted from articles/batch/quick-run-python.md.

import os
import sys

from azure.batch import BatchClient, models
from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.blob import BlobServiceClient


def make_blob_service_client(config):
    # [START quickrun_python_blob_client]
    blob_service_client = BlobServiceClient(
            account_url=f"https://{config.STORAGE_ACCOUNT_NAME}.{config.STORAGE_ACCOUNT_DOMAIN}/",
            credential=config.STORAGE_ACCOUNT_KEY
        )
    # [END quickrun_python_blob_client]
    return blob_service_client


def upload_inputs(blob_service_client, input_container_name, upload_file_to_container):
    # [START quickrun_python_upload_inputs]
    input_file_paths = [os.path.join(sys.path[0], 'taskdata0.txt'),
                        os.path.join(sys.path[0], 'taskdata1.txt'),
                        os.path.join(sys.path[0], 'taskdata2.txt')]

    input_files = [
        upload_file_to_container(blob_service_client, input_container_name, file_path)
        for file_path in input_file_paths]
    # [END quickrun_python_upload_inputs]
    return input_files


def make_batch_client(config):
    # [START quickrun_python_batch_client]
    credentials = AzureNamedKeyCredential(config.BATCH_ACCOUNT_NAME,
            config.BATCH_ACCOUNT_KEY)

    batch_client = BatchClient(
        endpoint=config.BATCH_ACCOUNT_URL,
        credential=credentials)
    # [END quickrun_python_batch_client]
    return batch_client


def create_pool(batch_client: BatchClient, pool_id: str, config):
    # [START quickrun_python_create_pool]
    new_pool = models.BatchPoolCreateOptions(
            id=pool_id,
            virtual_machine_configuration=models.VirtualMachineConfiguration(
                image_reference=models.BatchVmImageReference(
                    publisher="canonical",
                    offer="0001-com-ubuntu-server-focal",
                    sku="22_04-lts",
                    version="latest"
                ),
                node_agent_sku_id="batch.node.ubuntu 22.04"),
            vm_size=config.POOL_VM_SIZE,
            target_dedicated_nodes=config.POOL_NODE_COUNT
        )
    batch_client.create_pool(pool=new_pool)
    # [END quickrun_python_create_pool]


def create_job(batch_client: BatchClient, job_id: str, pool_id: str):
    # [START quickrun_python_create_job]
    job = models.BatchJobCreateOptions(
        id=job_id,
        pool_info=models.BatchPoolInfo(pool_id=pool_id))

    batch_client.create_job(job=job)
    # [END quickrun_python_create_job]


def add_tasks(batch_client: BatchClient, job_id: str, resource_input_files):
    # [START quickrun_python_add_tasks]
    tasks = []

    for idx, input_file in enumerate(resource_input_files):
        command = f"/bin/bash -c \"cat {input_file.file_path}\""
        tasks.append(models.BatchTaskCreateOptions(
            id=f'Task{idx}',
            command_line=command,
            resource_files=[input_file]
        )
        )

    batch_client.create_tasks(job_id=job_id, task_collection=tasks)
    # [END quickrun_python_add_tasks]


def view_task_output(batch_client: BatchClient, job_id: str, config, _read_stream_as_string, text_encoding):
    # [START quickrun_python_view_output]
    tasks = batch_client.list_tasks(job_id=job_id)

    for task in tasks:

        node_id = batch_client.get_task(job_id=job_id, task_id=task.id).node_info.node_id
        print(f"Task: {task.id}")
        print(f"Node: {node_id}")

        stream = batch_client.download_task_file(
            job_id=job_id, task_id=task.id, file_path=config.STANDARD_OUT_FILE_NAME)

        file_text = _read_stream_as_string(
            stream,
            text_encoding)
    # [END quickrun_python_view_output]
