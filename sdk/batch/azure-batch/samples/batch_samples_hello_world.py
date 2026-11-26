# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE:
    batch_samples_hello_world.py

DESCRIPTION:
    Azure Batch sample.

USAGE:
    python batch_samples_hello_world.py
"""

from configparser import ConfigParser

from azure.batch import models
from azure.batch import BatchClient
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential


class BatchSamples:

    def create_pool(self, client: BatchClient, pool_id: str):

        # set up virtual machine configuration
        vm_configuration = models.VirtualMachineConfiguration(
            image_reference=models.BatchVmImageReference(
                publisher="MicrosoftWindowsServer",
                offer="WindowsServer",
                sku="2016-Datacenter-smalldisk",
            ),
            node_agent_sku_id="batch.node.windows amd64",
        )

        # set up parameters for a batch pool
        pool_content = models.BatchPoolCreateOptions(
            id=pool_id,
            vm_size="standard_d2_v2",
            target_dedicated_nodes=1,
            virtual_machine_configuration=vm_configuration,
        )

        try:
            # create a batch pool
            client.create_pool(pool=pool_content)
        except AzureError as e:
            print(e)

    def create_job_and_submit_task(self, client: BatchClient, pool_id: str, job_id: str):

        # set up parameters for a batch job
        job_content = models.BatchJobCreateOptions(
            id=job_id,
            pool_info=models.BatchPoolInfo(pool_id=pool_id),
        )

        try:
            # create a batch job
            client.create_job(job=job_content)
        except AzureError as e:
            print(e)

        # set up parameters for a batch task
        task_content = models.BatchTaskCreateOptions(
            id="my_task",
            command_line='cmd /c "echo hello world"',
        )

        try:
            # create a batch task
            client.create_task(job_id=job_id, task=task_content)
        except AzureError as e:
            print(e)

    def cleanup(self, client: BatchClient, pool_id: str, job_id: str):
        # deleting the job
        client.begin_delete_job(job_id=job_id)
        # deleting the pool
        client.begin_delete_pool(pool_id=pool_id)


if __name__ == "__main__":
    POOL_ID = "my_pool"
    JOB_ID = "my_job"

    parser = ConfigParser()
    parser.read("samples.cfg")
    batchAccountEndpoint = parser.get("Batch", "BATCH_ACCOUNT_ENDPOINT")

    credentials = DefaultAzureCredential()
    batch_client = BatchClient(batchAccountEndpoint, credentials)

    sample = BatchSamples()
    sample.create_pool(batch_client, POOL_ID)
    sample.create_job_and_submit_task(batch_client, POOL_ID, JOB_ID)
    sample.cleanup(batch_client, POOL_ID, JOB_ID)
