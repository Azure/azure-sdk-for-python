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
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        credential = DefaultAzureCredential()
        workspace_name = "test-ws1"
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name=workspace_name)

        cpu_cluster = ml_client.compute.get("cpu-cluster")

        # [START spark_monitor_definition]
        from azure.ai.ml.entities import (
            AlertNotification,
            MonitorDefinition,
            MonitoringTarget,
            SparkResourceConfiguration,
        )

        monitor_definition = MonitorDefinition(
            compute=SparkResourceConfiguration(instance_type="standard_e4s_v3", runtime_version="3.3"),
            monitoring_target=MonitoringTarget(
                ml_task="Classification",
                endpoint_deployment_id="azureml:fraud_detection_endpoint:fraud_detection_deployment",
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
            base_path="./sdk/ml/azure-ai-ml/tests/test_configs/dsl_pipeline/spark_job_in_pipeline",
        )

        # [END spark_component_definition]

        # [START spark_entry_type]
        from azure.ai.ml.entities import SparkJobEntry, SparkJobEntryType

        spark_entry = SparkJobEntry(type=SparkJobEntryType.SPARK_JOB_FILE_ENTRY, entry="main.py")

        # [END spark_entry_type]

        # [START spark_job_configuration]
        from azure.ai.ml import Input, Output
        from azure.ai.ml.entities import SparkJob

        spark_job = SparkJob(
            code="./sdk/ml/azure-ai-ml/tests/test_configs/dsl_pipeline/spark_job_in_pipeline/basic_src",
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
        from azure.ai.ml.entities import (
            AutoPauseSettings,
            AutoScaleSettings,
            IdentityConfiguration,
            ManagedIdentityConfiguration,
            SynapseSparkCompute,
        )

        synapse_compute = SynapseSparkCompute(
            name="synapse_name",
            resource_id="/subscriptions/subscription/resourceGroups/group/providers/Microsoft.Synapse/workspaces/workspace/bigDataPools/pool",
            identity=IdentityConfiguration(
                type="UserAssigned",
                user_assigned_identities=[
                    ManagedIdentityConfiguration(
                        resource_id="/subscriptions/subscription/resourceGroups/group/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity"
                    )
                ],
            ),
            scale_settings=AutoScaleSettings(min_node_count=1, max_node_count=3, enabled=True),
            auto_pause_settings=AutoPauseSettings(delay_in_minutes=10, enabled=True),
        )

        # [END synapse_spark_compute_configuration]

        # [START spark_function_configuration_1]
        from azure.ai.ml import Input, Output, spark
        from azure.ai.ml.entities import ManagedIdentityConfiguration

        node = spark(
            experiment_name="builder-spark-experiment-name",
            description="simply spark description",
            code="./sdk/ml/azure-ai-ml/tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            jars=["simple-1.1.1.jar"],
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            identity=ManagedIdentityConfiguration(),
            inputs={
                "input1": Input(
                    type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv", mode="direct"
                )
            },
            outputs={
                "output1": Output(
                    type="uri_file",
                    path="azureml://datastores/workspaceblobstore/spark_titanic_output/titanic.parquet",
                    mode="direct",
                )
            },
            args="--input1 ${{inputs.input1}} --output1 ${{outputs.output1}} --my_sample_rate 0.01",
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.3.0",
            },
        )

        # [END spark_function_configuration_1]

        # [START spark_function_configuration_2]

        node = spark(
            code="./sdk/ml/azure-ai-ml/tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            resources={
                "instance_type": "Standard_E8S_V3",
                "runtime_version": "3.3.0",
            },
            identity={"type": "managed"},
        )

        # [END spark_function_configuration_2]

        # [START spark_dsl_pipeline]
        from azure.ai.ml import Input, Output, dsl, spark
        from azure.ai.ml.constants import AssetTypes, InputOutputModes

        # define the spark task
        first_step = spark(
            code="/src",
            entry={"file": "add_greeting_column.py"},
            py_files=["utils.zip"],
            files=["my_files.txt"],
            driver_cores=2,
            driver_memory="1g",
            executor_cores=1,
            executor_memory="1g",
            executor_instances=1,
            inputs=dict(
                file_input=Input(path="/dataset/iris.csv", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT)
            ),
            args="--file_input ${{inputs.file_input}}",
            resources={"instance_type": "standard_e4s_v3", "runtime_version": "3.3.0"},
        )

        second_step = spark(
            code="/src",
            entry={"file": "count_by_row.py"},
            jars=["scala_project.jar"],
            files=["my_files.txt"],
            driver_cores=2,
            driver_memory="1g",
            executor_cores=1,
            executor_memory="1g",
            executor_instances=1,
            inputs=dict(
                file_input=Input(path="/dataset/iris.csv", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT)
            ),
            outputs=dict(output=Output(type="uri_folder", mode=InputOutputModes.DIRECT)),
            args="--file_input ${{inputs.file_input}} --output ${{outputs.output}}",
            resources={"instance_type": "standard_e4s_v3", "runtime_version": "3.3.0"},
        )

        # Define pipeline
        @dsl.pipeline(description="submit a pipeline with spark job")
        def spark_pipeline_from_builder(data):
            add_greeting_column = first_step(file_input=data)
            count_by_row = second_step(file_input=data)
            return {"output": count_by_row.outputs.output}

        pipeline = spark_pipeline_from_builder(
            data=Input(path="/dataset/iris.csv", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT),
        )
        # [END spark_dsl_pipeline]

        # [START spark_resource_configuration]
        from azure.ai.ml import Input, Output
        from azure.ai.ml.entities._credentials import AmlTokenConfiguration, SparkJob, SparkResourceConfiguration

        spark_job = SparkJob(
            code="./tests/test_configs/spark_job/basic_spark_job/src",
            entry={"file": "./main.py"},
            jars=["simple-1.1.1.jar"],
            identity=AmlTokenConfiguration(),
            driver_cores=1,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            dynamic_allocation_enabled=True,
            dynamic_allocation_min_executors=1,
            dynamic_allocation_max_executors=3,
            name="builder-spark-job",
            experiment_name="builder-spark-experiment-name",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            inputs={
                "input1": Input(
                    type="uri_file", path="azureml://datastores/workspaceblobstore/paths/python/data.csv", mode="direct"
                )
            },
            outputs={
                "output1": Output(
                    type="uri_file",
                    path="azureml://datastores/workspaceblobstore/spark_titanic_output/titanic.parquet",
                    mode="direct",
                )
            },
            resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version="3.3.0"),
        )
        # [END spark_resource_configuration]


if __name__ == "__main__":
    sample = SparkConfigurationOptions()
    sample.ml_spark_config()
