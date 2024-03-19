# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_pipeline_job_configurations.py
DESCRIPTION:
    These samples configures some operations of the pipeline job.
USAGE:
    python ml_samples_pipeline_job_configurations.py

"""

import os


class PipelineConfigurationOptions(object):
    def ml_pipeline_config(self):
        from azure.ai.ml import Input, MLClient
        from azure.ai.ml.constants._common import AssetTypes
        from azure.ai.ml.entities import Environment
        from azure.identity import DefaultAzureCredential

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["RESOURCE_GROUP_NAME"]
        workspace_name = "test-ws1"
        credential = DefaultAzureCredential()
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name=workspace_name)
        cpu_cluster = ml_client.compute.get("cpu-cluster")
        job_env = Environment(
            name="my-env",
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
        )
        job_env = ml_client.environments.create_or_update(job_env)
        uri_file_input = Input(
            type=AssetTypes.URI_FILE,
            path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
        )

        # [START configure_pipeline]
        from azure.ai.ml import load_component
        from azure.ai.ml.dsl import pipeline

        component_func = load_component(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/components/helloworld_component.yml"
        )

        # Define a pipeline with decorator
        @pipeline(name="sample_pipeline", description="pipeline description")
        def sample_pipeline_func(pipeline_input1, pipeline_input2):
            # component1 and component2 will be added into the current pipeline
            component1 = component_func(component_in_number=pipeline_input1, component_in_path=uri_file_input)
            component2 = component_func(component_in_number=pipeline_input2, component_in_path=uri_file_input)
            # A decorated pipeline function needs to return outputs.
            # In this case, the pipeline has two outputs: component1's output1 and component2's output1,
            # and let's rename them to 'pipeline_output1' and 'pipeline_output2'
            return {
                "pipeline_output1": component1.outputs.component_out_path,
                "pipeline_output2": component2.outputs.component_out_path,
            }

        # E.g.: This call returns a pipeline job with nodes=[component1, component2],
        pipeline_job = sample_pipeline_func(
            pipeline_input1=1.0,
            pipeline_input2=2.0,
        )
        ml_client.jobs.create_or_update(pipeline_job, experiment_name="pipeline_samples", compute="cpu-cluster")
        # [END configure_pipeline]

        # [START configure_pipeline_job_and_settings]
        from azure.ai.ml.entities import PipelineJob, PipelineJobSettings

        pipeline_job = PipelineJob(
            description="test pipeline job",
            tags={},
            display_name="test display name",
            experiment_name="pipeline_job_samples",
            properties={},
            settings=PipelineJobSettings(force_rerun=True, default_compute="cpu-cluster"),
            jobs={"component1": component_func(component_in_number=1.0, component_in_path=uri_file_input)},
        )

        ml_client.jobs.create_or_update(pipeline_job)
        # [END configure_pipeline_job_and_settings]


if __name__ == "__main__":
    sample = PipelineConfigurationOptions()
    sample.ml_pipeline_config()
