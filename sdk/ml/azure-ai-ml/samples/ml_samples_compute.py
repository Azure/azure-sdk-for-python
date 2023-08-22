# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_compute_configurations.py
DESCRIPTION:
    These samples demonstrate different ways to configure Compute.
USAGE:
    python ml_samples_compute_configurations.py

"""

import os


class ComputeConfigurationOptions(object):
    def ml_compute_config(self):
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        credential = DefaultAzureCredential()
        #        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws1")
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name="r-bug-bash")

        #        cpu_cluster = ml_client.compute.get("cpu-cluster")
        cpu_cluster = ml_client.compute.get("cpucluster")

        # [START load_compute]
        from azure.ai.ml import load_compute

        compute = load_compute(
            "../tests/test_configs/compute/compute-vm.yaml",
            params_override=[{"description": "loaded from compute-vm.yaml"}],
        )

        # [END load_compute]


if __name__ == "__main__":
    sample = ComputeConfigurationOptions()
    sample.ml_compute_config()
