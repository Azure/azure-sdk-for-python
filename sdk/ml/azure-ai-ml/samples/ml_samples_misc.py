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


class MiscConfigurationOptions(object):
    def ml_misc_config(self):
        from azure.identity import DefaultAzureCredential

        from azure.ai.ml import MLClient

        # subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        # resource_group = os.environ["RESOURCE_GROUP_NAME"]
        subscription_id = "e9b2ec51-5c94-4fa8-809a-dc1e695e4896"
        resource_group = "dipeck-rg1"
        credential = DefaultAzureCredential()
        ml_client = MLClient(credential, subscription_id, resource_group, workspace_name="r-bug-bash")

        # [START job_operations_create_and_update]
        import uuid

        from azure.ai.ml import load_job

        job_name = f"iris-dataset-job-{str(uuid.uuid4())}"
        created_job = ml_client.jobs.create_or_update(
            name=job_name,
            job=load_job(
                "./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test.yml",
                params_override=[{"name": job_name}, {"compute": "cpucluster"}],
            ),
        )
        updated_job = ml_client.jobs.create_or_update(
            job=load_job(
                "./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test.yml",
                params_override=[{"name": "new_job_name"}, {"compute": "cpucluster"}],
            )
        )

        # [START job_operations_list]
        from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType

        list_of_jobs = ml_client.jobs.list(parent_job_name=job_name, list_view_type=ListViewType.ARCHIVED_ONLY)
        # [END job_operations_list]

        # [START job_operations_get]
        retrieved_job = ml_client.jobs.get(job_name)
        # [END job_operations_get]

        # [START job_operations_show_services]
        job_services = ml_client.jobs.show_services(job_name)
        # [END job_operations_show_services]

        # [START job_operations_cancel]
        cancel_poller = ml_client.jobs.begin_cancel(job_name)
        print(cancel_poller.result())
        # [END job_operations_cancel]

        # [START job_operations_validate]
        from azure.ai.ml import load_job
        from azure.ai.ml.entities import PipelineJob

        pipeline_job: PipelineJob = load_job(
            "./sdk/ml/azure-ai-ml/tests/test_configs/pipeline_jobs/invalid/combo.yml",
            params_override=[{"name": job_name}, {"compute": "cpucluster"}],
        )
        print(ml_client.jobs.validate(pipeline_job).error_messages)
        # [END job_operations_validate]

        # [START job_operations_archive]
        ml_client.jobs.archive(name=job_name)
        # [END job_operations_archive]

        # [START job_operations_restore]
        ml_client.jobs.restore(name=job_name)
        # [END job_operations_restore]

        # [START job_operations_stream_logs]
        running_job = ml_client.jobs.create_or_update(
            load_job(
                "./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test.yml",
                params_override=[{"name": job_name}, {"compute": "cpucluster"}],
            )
        )
        ml_client.jobs.stream(running_job)
        # [END job_operations_stream_logs]

        # [START job_operations_download]
        ml_client.jobs.download(name=job_name, download_path="./job-1-logs", all=True)
        # [END job_operations_download]

        # [START model_entity_create]
        from azure.ai.ml.entities import Model

        model = Model(
            name="model1",
            version="5",
            description="my first model in prod",
            path="models/very_important_model.pkl",
            tags=["tag1", "tag2"],
            properties={"prop1": "value1", "prop2": "value2"},
            type="mlflow_model",
            flavors={
                "sklearn": {"sklearn_version": "0.23.2"},
                "python_function": {"loader_module": "office.plrmodel", "python_version": 3.6},
            },
            stage="Production",
        )
        # [END model_entity_create]

        # [START create_inputs_outputs]
        from azure.ai.ml import Input, Output
        from azure.ai.ml.entities import CommandJob, CommandJobLimits

        command_job = CommandJob(
            code="./src",
            command="python train.py --ss {search_space.ss}",
            inputs={
                "input1": Input(path="trial.csv", mode="ro_mount", description="trial input data"),
                "input_2": Input(
                    path="azureml:list_data_v2_test:2", type="uri_folder", description="registered data asset"
                ),
            },
            outputs={"default": Output(path="./foo")},
            compute="trial",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            limits=CommandJobLimits(timeout=120),
        )
        # [END create_inputs_outputs]

        # [START load_job]
        from azure.ai.ml import load_job

        job = load_job(source="./configs/batch_setup/lgb.yml")
        # [END load_job]

        # [START load_model]
        from azure.ai.ml import load_model

        model = load_model(
            "./configs/model/model_minimal.yml",
            params_override=[{"name": "new_model_name"}, {"version": "1"}],
        )
        # [END load_model]

        # [START load_model_package]
        from azure.ai.ml import load_model_package

        model_package = load_model_package("./configs/model_packages/model_package_minimal.yml")
        # [END load_model_package]

        # [START tensorflow_distribution_configuration]
        from azure.ai.ml.entities import CommandComponent, TensorFlowDistribution

        component = CommandComponent(
            name="microsoftsamples_tf",
            description="This is the TF command component",
            inputs={
                "component_in_number": {"description": "A number", "type": "number", "default": 10.99},
                "component_in_path": {"description": "A path", "type": "uri_folder"},
            },
            outputs={"component_out_path": {"type": "uri_folder"}},
            command="echo Hello World & echo ${{inputs.component_in_number}} & echo ${{inputs.component_in_path}} "
            "& echo ${{outputs.component_out_path}}",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            distribution=TensorFlowDistribution(
                parameter_server_count=1,
                worker_count=2,
            ),
            instance_count=2,
        )
        # [END tensorflow_distribution_configuration]

        # [START pytorch_distribution_configuration]
        from azure.ai.ml.entities import CommandComponent, PyTorchDistribution

        component = CommandComponent(
            name="microsoftsamples_torch",
            description="This is the PyTorch command component",
            inputs={
                "component_in_number": {"description": "A number", "type": "number", "default": 10.99},
                "component_in_path": {"description": "A path", "type": "uri_folder"},
            },
            outputs={"component_out_path": {"type": "uri_folder"}},
            command="echo Hello World & echo ${{inputs.component_in_number}} & echo ${{inputs.component_in_path}} "
            "& echo ${{outputs.component_out_path}}",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            distribution=PyTorchDistribution(
                process_count_per_instance=2,
            ),
            instance_count=2,
        )
        # [END pytorch_distribution_configuration]

        # [START mpi_distribution_configuration]
        from azure.ai.ml.entities import CommandComponent, MpiDistribution

        component = CommandComponent(
            name="microsoftsamples_mpi",
            description="This is the MPI command component",
            inputs={
                "component_in_number": {"description": "A number", "type": "number", "default": 10.99},
                "component_in_path": {"description": "A path", "type": "uri_folder"},
            },
            outputs={"component_out_path": {"type": "uri_folder"}},
            command="echo Hello World & echo ${{inputs.component_in_number}} & echo ${{inputs.component_in_path}} "
            "& echo ${{outputs.component_out_path}}",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            distribution=MpiDistribution(
                process_count_per_instance=2,
            ),
            instance_count=2,
        )
        # [END mpi_distribution_configuration]

        # [START code_configuration]
        from azure.ai.ml.entities import BatchDeployment, CodeConfiguration

        deployment = BatchDeployment(
            name="non-mlflow-deployment",
            description="this is a sample non-mlflow deployment",
            endpoint_name="my-batch-endpoint",
            model="model",
            code_configuration=CodeConfiguration(
                code="configs/deployments/model-2/onlinescoring", scoring_script="score1.py"
            ),
            environment="env",
            compute="cpu-cluster",
            instance_count=2,
            max_concurrency_per_instance=2,
            mini_batch_size=10,
            output_file_name="predictions.csv",
        )
        # [END code_configuration]


if __name__ == "__main__":
    sample = MiscConfigurationOptions()
    sample.ml_misc_config()
