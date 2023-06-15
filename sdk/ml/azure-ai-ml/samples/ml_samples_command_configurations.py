# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_command_configurations.py
DESCRIPTION:
    These samples demonstrate different ways to configure Command jobs and components.
USAGE:
    python ml_samples_command_configurations.py

"""

import os


class CommandConfigurationOptions(object):
    def ml_command_config(self):
        from azure.identity import DefaultAzureCredential

        from azure.ai.ml import MLClient

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        credential = DefaultAzureCredential()
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws1")

        from azure.ai.ml.entities import CommandJob, CommandJobLimits
        from azure.ai.ml import Input, Output

        # [START command_job_definition]
        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            inputs={"input1": Input(path="trial.csv")},
            outputs={"default": Output(path="./foo")},
            compute="trial",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            limits=CommandJobLimits(timeout=120),
        )
        # [END command_job_definition]


if __name__ == "__main__":
    sample = CommandConfigurationOptions()
    sample.ml_command_config()
