# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_spark_configurations.py
DESCRIPTION:
    These samples demonstrate different ways to configure Spark jobs and components.
USAGE:
    python ml_samples_spark_configurations.py

"""

import os


class SparkConfigurationOptions(object):
    def ml_spark_config(self):
        from azure.identity import DefaultAzureCredential

        from azure.ai.ml import MLClient

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        credential = DefaultAzureCredential()
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws1")

        # [START spark_monitor_definition]
        from azure.ai.ml.entities import (
            AlertNotification,
            MonitorDefinition,
            MonitoringTarget,
            SparkResourceConfiguration,
        )

        monitor_definition = MonitorDefinition(
            compute=SparkResourceConfiguration(instance_type="standard_e4s_v3", runtime_version="3.2"),
            monitoring_target=MonitoringTarget(
                endpoint_deployment_id="azureml:fraud_detection_endpoint:fraud_detection_deployment"
            ),
            alert_notification=AlertNotification(emails=["abc@example.com", "def@example.com"]),
        )

        # [END spark_monitor_definition]

        # [START spark_component_definition]
        from azure.ai.ml.entities import SparkComponent

        component = SparkComponent(
            name="add_greeting_column_spark_component",
            display_name="Aml Spark add greeting column test module",
            description="Aml Spark add greeting column test module",
            version="1",
            inputs={
                "file_input": {"type": "uri_file", "mode": "direct"},
            },
            driver_cores=2,
            driver_memory="1g",
            executor_cores=1,
            executor_memory="1g",
            executor_instances=1,
            code="./src",
            entry={"file": "add_greeting_column.py"},
            py_files=["utils.zip"],
            files=["my_files.txt"],
            args="--file_input ${{inputs.file_input}}",
            base_path="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline",
        )

        # [END spark_component_definition]

        # [START spark_entry_type]
        from azure.ai.ml.entities import SparkJobEntry, SparkJobEntryType

        spark_entry = SparkJobEntry(entry_type=SparkJobEntryType.SPARK_JOB_FILE_ENTRY, entry="main.py")

        # [END spark_entry_type]

        # [START spark_job_configuration]
        from azure.ai.ml.entities import Input, Output, SparkJob

        spark_job = SparkJob(
            code="./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/basic_src",
            entry={"file": "sampleword.py"},
            conf={
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.memory": "1g",
                "spark.executor.instances": 1,
            },
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs={
                "input1": Input(
                    type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv", mode="direct"
                )
            },
            compute="synapsecompute",
            outputs={"component_out_path": Output(type="uri_folder")},
            args="--input1 ${{inputs.input1}} --output2 ${{outputs.output1}} --my_sample_rate ${{inputs.sample_rate}}",
        )

        # [END spark_job_configuration]

        # [START materialization_setting_configuration]
        from azure.ai.ml.entities import MaterializationComputeResource, MaterializationSettings

        materialization_settings = MaterializationSettings(
            offline_enabled=True,
            spark_configuration={
                "spark.driver.cores": 2,
                "spark.driver.memory": "18g",
                "spark.executor.cores": 4,
                "spark.executor.memory": "18g",
                "spark.executor.instances": 5,
            },
            resource=MaterializationComputeResource(instance_type="standard_e4s_v3"),
        )
        # [END materialization_setting_configuration]

        # [START synapse_spark_compute_configuration]
        from azure.ai.ml.entities import IdentityConfiguration, SynapseSparkCompute, UserAssignedIdentity

        synapse_compute = SynapseSparkCompute(
            name="synapse_name",
            resource_id="/subscriptions/mysubid/resourceGroups/myrg/providers/Microsoft.Synapse/workspaces/myws/bigDataPools/mysparkpoolname",
            identity=IdentityConfiguration(
                type="UserAssigned",
                user_assigned_identities=[
                    UserAssignedIdentity(
                        resource_id="/subscriptions/mysubid/resourceGroups/myrg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mymanagedidentityname"
                    )
                ],
            ),
        )

        # [END synapse_spark_compute_configuration]


if __name__ == "__main__":
    sample = SparkConfigurationOptions()
    sample.ml_spark_config()
