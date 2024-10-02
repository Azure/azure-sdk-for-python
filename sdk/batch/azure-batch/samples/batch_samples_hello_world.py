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

from azure.batch import models
from azure.batch import BatchClient
from azure.identity import DefaultAzureCredential

from configparser import ConfigParser

class BatchSamples():

    def create_pool(self, client: BatchClient, pool_id: str):

        # set up virtual machine configuration
        vm_configuration=models.VirtualMachineConfiguration(
            image_reference=models.ImageReference(
                publisher="MicrosoftWindowsServer",
                offer="WindowsServer",
                sku="2016-Datacenter-smalldisk",
            ),
            node_agent_sku_id="batch.node.windows amd64"
        )

        # set up parameters for a batch pool
        pool_content=models.BatchPoolCreateContent(
            id=pool_id,
            vm_size="standard_d2_v2",
            target_dedicated_nodes=1,
            virtual_machine_configuration=vm_configuration,
        )

        try:
            # create a batch pool
            client.create_pool(pool=pool_content)
        except Exception as e:
            print(e)
    
    def create_job_and_submit_task(self, client: BatchClient, pool_id: str, job_id: str):

        # set up parameters for a batch job
        job_content = models.BatchJobCreateContent(
            id=job_id,
            pool_info=models.BatchPoolInfo(pool_id=pool_id),
        )

        try:
            # create a batch job
            client.create_job(job=job_content)
        except Exception as e:
            print(e)
        
        # set up parameters for a batch task
        task_content = models.BatchTaskCreateContent(
            id="my_task",
            command_line='cmd /c "echo hello world"',
        )

        try:
            # create a batch task
            client.create_task(job_id=job_id, task=task_content)
        except Exception as e:
            print(e)
    
    def cleanup(self, client: BatchClient, pool_id: str, job_id: str):
        # deleting the job
        client.delete_job(job_id=job_id)
        # deleting the pool
        client.delete_pool(pool_id=pool_id)
        
if __name__ =='__main__':
    pool_id = "my_pool"
    job_id = "my_job"

    parser = ConfigParser()
    parser.read("samples.cfg")
    batchAccountEndpoint = parser.get("Batch", "BATCH_ACCOUNT_ENDPOINT")

    credentials = DefaultAzureCredential()
    client = BatchClient(batchAccountEndpoint, credentials)

    sample = BatchSamples()
    sample.create_pool(client, pool_id)
    sample.create_job_and_submit_task(client, pool_id, job_id)
    sample.cleanup(client, pool_id, job_id)
