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

        from azure.ai.ml import Input, Output
        from azure.ai.ml.entities import CommandJob, CommandJobLimits

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

        # [START command_function]
        from azure.ai.ml import Input, Output, command

        train_func = command(
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command='echo "hello world"',
            distribution={"type": "Pytorch", "process_count_per_instance": 2},
            inputs={
                "training_data": Input(type="uri_folder"),
                "max_epochs": 20,
                "learning_rate": 1.8,
                "learning_rate_schedule": "time-based",
            },
            outputs={"model_output": Output(type="uri_folder")},
        )
        # [END command_function]

        # [START command_component_definition]
        from azure.ai.ml.entities import CommandComponent

        component = CommandComponent(
            name="sample_command_component_basic",
            display_name="CommandComponentBasic",
            description="This is the basic command component",
            tags={"tag": "tagvalue", "owner": "sdkteam"},
            version="1",
            outputs={"component_out_path": {"type": "uri_folder"}},
            command="echo Hello World",
            code="./src",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        # [END command_component_definition]


if __name__ == "__main__":
    sample = CommandConfigurationOptions()
    sample.ml_command_config()
