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

from ml_samples_compute import handle_resource_exists_error

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["RESOURCE_GROUP_NAME"]
workspace_name = "test-ws1"
credential = DefaultAzureCredential()
ml_client = MLClient(credential, subscription_id, resource_group, workspace_name=workspace_name)

import uuid

job_name = f"iris-dataset-job-{str(uuid.uuid4())}"


class EndpointsConfigurationOptions(object):
    def ml_endpoints_config_0(self):
        
        
        # [START model_batch_deployment_config]
        from azure.ai.ml.entities import ModelBatchDeployment, ModelBatchDeploymentSettings, CodeConfiguration, BatchRetrySettings

        deployment = ModelBatchDeployment(
            name="batch-deployment",
            description="This is a sample batch deployment.",
            endpoint_name="endpoint_name",
            model="model_name",
            code_configuration=CodeConfiguration(
                code="deployment-torch/code/", scoring_script="batch_driver.py"
            ),
            environment="environment_name",
            compute="compute_name",
            settings=ModelBatchDeploymentSettings(
                max_concurrency_per_instance=2,
                mini_batch_size=10,
                instance_count=2,
                output_file_name="predictions.csv",
                retry_settings=BatchRetrySettings(max_retries=3, timeout=30),
                logging_level="info",
            ),
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            compute="cpu-cluster",
            logging_level="info",
            mini_batch_size=10,
            max_concurrency_per_instance=2,
        )

        # [END model_batch_deployment_config]


if __name__ == "__main__":
    sample = EndpointsConfigurationOptions()
    sample.ml_endpoints_config_0()