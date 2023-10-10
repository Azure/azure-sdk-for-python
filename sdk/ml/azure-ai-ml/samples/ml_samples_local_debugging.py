# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_input_output_configurations.py
DESCRIPTION:
    This sample for setting up local debugging.
USAGE:
    python ml_samples_local_debugging.py

"""


class LocalDebugging(object):
    def ml_local_debugging_with_data(self):
        import os

        from azure.ai.ml import Input, MLClient, command
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.entities import ComputeConfiguration, Data, JobResourceConfiguration
        from azure.identity import DefaultAzureCredential

        # set the environment variables
        os.environ["AZUREML_DEV_URL_MFE"] = f"http://localhost:65535/mferp/managementfrontend/"

        # enter details of your AML workspace
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        workspace_name = "test-ws1"

        # get a handle to the workspace
        ml_client = MLClient(DefaultAzureCredential(), subscription_id, resource_group, workspace_name)

        inputs = {"input_data": Input(type=AssetTypes.URI_FILE, path="./sample_data/titanic.csv")}

        mount_data_path = "-v /d/work/repos:/data"

        job = command(
            # Setting up a local src path fails while uploading snapshots
            # code="./src",  # local path where the code is stored
            # command="python read_data.py --input_data ${{inputs.input_data}}",
            command="sleep 120",
            # inputs=inputs,
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:32",
            docker_args=mount_data_path,
            compute="local",
            resources=JobResourceConfiguration(docker_args=mount_data_path),
        )

        # submit the command
        returned_job = ml_client.jobs.create_or_update(job)
        print(returned_job)


if __name__ == "__main__":
    sample = LocalDebugging()
    sample.ml_local_debugging_with_data()
