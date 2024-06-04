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


class MiscConfigurationOptions(object):
    def ml_misc_config_0(self):
        # [START job_operations_create_and_update]
        from azure.ai.ml import load_job

        created_job = ml_client.jobs.create_or_update(
            name=job_name,
            job=load_job(
                "./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test_local_env.yml",
                params_override=[{"name": job_name}, {"compute": "cpucluster"}],
            ),
        )
        # [END job_operations_create_and_update]

        # [START job_operations_list]
        from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType

        list_of_jobs = ml_client.jobs.list(parent_job_name=job_name, list_view_type=ListViewType.ARCHIVED_ONLY)
        # [END job_operations_list]

        # [START job_operations_get]
        retrieved_job = ml_client.jobs.get(job_name)
        # [END job_operations_get]

        # [START job_operations_begin_cancel]
        cancel_poller = ml_client.jobs.begin_cancel(job_name)
        print(cancel_poller.result())
        # [END job_operations_begin_cancel]

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
                "./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test_local_env.yml",
                params_override=[{"name": job_name}, {"compute": "cpucluster"}],
            )
        )
        ml_client.jobs.stream(running_job.name)
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
            properties={"prop1": "value1", "prop2": "value2"},
            type="mlflow_model",
            flavors={
                "sklearn": {"sklearn_version": "0.23.2"},
                "python_function": {"loader_module": "office.plrmodel", "python_version": 3.6},
            },
            stage="Production",
        )
        ml_client.models.create_or_update(model)
        # [END model_entity_create]

        # [START model_operations_archive]
        ml_client.models.archive(name="model1", version="5")
        # [END model_operations_archive]

        # [START model_operations_restore]
        ml_client.models.restore(name="model1", version="5")
        # [END model_operations_restore]

        # [START model_batch_deployment_settings_entity_create]
        from azure.ai.ml.entities._deployment.model_batch_deployment_settings import ModelBatchDeploymentSettings

        modelBatchDeploymentSetting = ModelBatchDeploymentSettings(
            mini_batch_size=256,
            instance_count=5,
            max_concurrency_per_instance=2,
            output_file_name="output-file-name",
            environment_variables={"env1": "value1", "env2": "value2"},
            error_threshold=2,
            logging_level=1,
        )
        # [END model_batch_deployment_settings_entity_create]

        # [START model_configuration_entity_create]
        from azure.ai.ml.entities._assets._artifacts._package.model_configuration import ModelConfiguration

        modelConfiguration = ModelConfiguration(mode="model-mode", mount_path="model-mount-path")
        # [END model_configuration_entity_create]

        # [START model_package_input_entity_create]
        from azure.ai.ml.entities._assets._artifacts._package.model_package import ModelPackageInput

        modelPackageInput = ModelPackageInput(type="input-type", mode="input-mode", mount_path="input-mount-path")
        # [END model_package_input_entity_create]

        # [START model_package_entity_create]
        from azure.ai.ml.entities import AzureMLOnlineInferencingServer, CodeConfiguration, ModelPackage

        modelPackage = ModelPackage(
            inferencing_server=AzureMLOnlineInferencingServer(
                code_configuration=CodeConfiguration(code="../model-1/foo/", scoring_script="score.py")
            ),
            target_environment_name="env-name",
            target_environment_version="1.0",
            environment_variables={"env1": "value1", "env2": "value2"},
            tags={"tag1": "value1", "tag2": "value2"},
        )
        # [END model_package_entity_create]

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

        job = load_job(source="./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test_local_env.yml")
        # [END load_job]

        # [START load_model]
        from azure.ai.ml import load_model

        model = load_model(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/model/model_with_stage.yml",
            params_override=[{"name": "new_model_name"}, {"version": "1"}],
        )
        # [END load_model]

        # [START load_model_package]
        from azure.ai.ml import load_model_package

        model_package = load_model_package(
            "./sdk/ml/azure-ai-ml/tests/test_configs/model_package/model_package_simple.yml"
        )
        # [END load_model_package]

        # [START tensorflow_distribution_configuration]
        from azure.ai.ml import TensorFlowDistribution
        from azure.ai.ml.entities import CommandComponent

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
        from azure.ai.ml import PyTorchDistribution
        from azure.ai.ml.entities import CommandComponent

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
        from azure.ai.ml import MpiDistribution
        from azure.ai.ml.entities import CommandComponent

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
            model=model,
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

        # [START intellectual_property_configuration]
        from azure.ai.ml.constants import IPProtectionLevel
        from azure.ai.ml.entities import CommandComponent, IntellectualProperty

        component = CommandComponent(
            name="random_name",
            version="1",
            environment="azureml:AzureML-Minimal:1",
            command="echo hello",
            intellectual_property=IntellectualProperty(publisher="contoso", protection_level=IPProtectionLevel.ALL),
        )
        # [END intellectual_property_configuration]

        # [START personal_access_token_configuration]
        from azure.ai.ml.entities import PatTokenConfiguration, WorkspaceConnection

        ws_connection = WorkspaceConnection(
            target="my_target",
            type="python_feed",
            credentials=PatTokenConfiguration(pat="abcdefghijklmnopqrstuvwxyz"),
            name="my_connection",
            metadata=None,
        )
        # [END personal_access_token_configuration]

        # [START job_schedule_configuration]
        from azure.ai.ml import load_job
        from azure.ai.ml.entities import JobSchedule, RecurrencePattern, RecurrenceTrigger

        pipeline_job = load_job("./sdk/ml/azure-ai-ml/tests/test_configs/command_job/command_job_test_local_env.yml")
        trigger = RecurrenceTrigger(
            frequency="week",
            interval=4,
            schedule=RecurrencePattern(hours=10, minutes=15, week_days=["Monday", "Tuesday"]),
            start_time="2023-03-10",
        )
        job_schedule = JobSchedule(name="simple_sdk_create_schedule", trigger=trigger, create_job=pipeline_job)
        # [END job_schedule_configuration]

        # [START cron_trigger_configuration]
        from datetime import datetime

        from azure.ai.ml.constants import TimeZone
        from azure.ai.ml.entities import CronTrigger

        trigger = CronTrigger(
            expression="15 10 * * 1",
            start_time=datetime(year=2022, month=3, day=10, hour=10, minute=15),
            end_time=datetime(year=2022, month=6, day=10, hour=10, minute=15),
            time_zone=TimeZone.PACIFIC_STANDARD_TIME,
        )
        # [END cron_trigger_configuration]

        # [START resource_requirements_configuration]
        from azure.ai.ml.entities import (
            CodeConfiguration,
            KubernetesOnlineDeployment,
            ResourceRequirementsSettings,
            ResourceSettings,
        )

        blue_deployment = KubernetesOnlineDeployment(
            name="kubernetes_deployment",
            endpoint_name="online_endpoint_name",
            model=load_model("./sdk/ml/azure-ai-ml/tests/test_configs/model/model_with_stage.yml"),
            environment="azureml:AzureML-Minimal:1",
            code_configuration=CodeConfiguration(
                code="endpoints/online/model-1/onlinescoring", scoring_script="score.py"
            ),
            instance_count=1,
            resources=ResourceRequirementsSettings(
                requests=ResourceSettings(
                    cpu="500m",
                    memory="0.5Gi",
                ),
                limits=ResourceSettings(
                    cpu="1",
                    memory="1Gi",
                ),
            ),
        )
        # [END resource_requirements_configuration]

        # [START ssh_job_service_configuration]
        from azure.ai.ml import command
        from azure.ai.ml.entities import JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService

        node = command(
            name="interactive-command-job",
            description="description",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            command="ls",
            compute="testCompute",
            services={
                "my_ssh": SshJobService(),
                "my_tensorboard": TensorBoardJobService(log_dir="~/blog"),
                "my_jupyter_lab": JupyterLabJobService(),
                "my_vscode": VsCodeJobService(),
            },
        )
        # [END ssh_job_service_configuration]

        # [START build_context_entity_create]
        from azure.ai.ml.entities._assets.environment import BuildContext

        build_context = BuildContext(dockerfile_path="docker-file-path", path="docker-build-context-path")
        # [END build_context_entity_create]

        # [START base_env_entity_create]
        from azure.ai.ml.entities._assets._artifacts._package.base_environment_source import BaseEnvironment

        base_environment = BaseEnvironment(type="base-env-type", resource_id="base-env-resource-id")
        # [END base_env_entity_create]

        # [START env_entity_create]
        from azure.ai.ml.entities._assets.environment import Environment

        environment = Environment(
            name="env-name",
            version="2.0",
            description="env-description",
            image="env-image",
            conda_file="./sdk/ml/azure-ai-ml/tests/test_configs/deployments/model-1/environment/conda.yml",
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            datastore="datastore",
        )
        # [END env_entity_create]

        # [START env_operations_create_or_update]
        from azure.ai.ml.entities import BuildContext, Environment

        env_docker_context = Environment(
            build=BuildContext(
                path="./sdk/ml/azure-ai-ml/tests/test_configs/environment/environment_files",
                dockerfile_path="DockerfileNonDefault",
            ),
            name="create-environment",
            version="2.0",
            description="Environment created from a Docker context.",
        )
        ml_client.environments.create_or_update(env_docker_context)
        # [END env_operations_create_or_update]

        # [START env_entities_validate]
        from azure.ai.ml.entities import BuildContext, Environment

        env_docker_context = Environment(
            build=BuildContext(
                path="./sdk/ml/azure-ai-ml/tests/test_configs/environment/environment_files",
                dockerfile_path="DockerfileNonDefault",
            ),
            name="create-environment",
            version="2.0",
            description="Environment created from a Docker context.",
        )

        env_docker_context.validate()
        # [END env_entities_validate]

        # [START env_operations_archive]
        ml_client.environments.archive("create-environment", "2.0")
        # [END env_operations_archive]

        # [START env_operations_restore]
        ml_client.environments.restore("create-environment", "2.0")
        # [END env_operations_restore]

        # [START env_operations_list]
        ml_client.environments.list()
        # [END env_operations_list]

        # [START env_operations_get]
        ml_client.environments.get("create-environment", "2.0")
        # [END env_operations_get]

    @handle_resource_exists_error
    def ml_misc_config_1(self):
        from random import randint

        from azure.ai.ml import load_batch_endpoint
        from azure.ai.ml.entities import BatchEndpoint

        endpoint_example = load_batch_endpoint(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/endpoints/batch/batch_endpoint_mlflow_new.yaml",
            params_override=[{"name": f"endpoint-{randint(0, 1000)}"}],
        )
        ml_client.batch_endpoints.begin_create_or_update(endpoint_example)
        endpoint_name = endpoint_example.name

        # [START batch_deployment_operations_begin_create_or_update]
        from azure.ai.ml import load_batch_deployment
        from azure.ai.ml.entities import BatchDeployment

        deployment_example = load_batch_deployment(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/deployments/batch/batch_deployment_anon_env_with_image.yaml",
            params_override=[{"name": f"deployment-{randint(0, 1000)}", "endpoint_name": endpoint_example.name}],
        )

        ml_client.batch_deployments.begin_create_or_update(deployment=deployment_example, skip_script_validation=True)
        # [END batch_deployment_operations_begin_create_or_update]

        deployment_name = deployment_example.name

        # [START batch_deployment_operations_get]
        ml_client.batch_deployments.get(deployment_name, endpoint_name)
        # [END batch_deployment_operations_get]

        # [START batch_deployment_operations_list]
        ml_client.batch_deployments.list(endpoint_name)
        # [END batch_deployment_operations_list]

        # [START batch_deployment_operations_list_jobs]
        ml_client.batch_deployments.list_jobs(deployment_name, endpoint_name)
        # [END batch_deployment_operations_list_jobs]

        # [START batch_deployment_operations_delete]
        ml_client.batch_deployments.begin_delete(deployment_name, endpoint_name)
        # [END batch_deployment_operations_delete]

        # [START batch_endpoint_operations_list]
        ml_client.batch_endpoints.list()
        # [END batch_endpoint_operations_list]

        # [START batch_endpoint_operations_get]
        ml_client.batch_endpoints.get(endpoint_name)
        # [END batch_endpoint_operations_get]

        # [START batch_endpoint_operations_delete]
        ml_client.batch_endpoints.begin_delete(endpoint_name)
        # [END batch_endpoint_operations_delete]

        from random import randint

        endpoint_name_2 = f"new-endpoint-{randint(0, 1000)}"

        # [START batch_endpoint_operations_create_or_update]
        from azure.ai.ml.entities import BatchEndpoint

        endpoint_example = BatchEndpoint(name=endpoint_name_2)
        ml_client.batch_endpoints.begin_create_or_update(endpoint_example)
        # [END batch_endpoint_operations_create_or_update]

        # [START batch_endpoint_operations_invoke]
        ml_client.batch_endpoints.invoke(endpoint_name_2)
        # [END batch_endpoint_operations_invoke]

        # [START batch_endpoint_operations_list_jobs]
        ml_client.batch_endpoints.list_jobs(endpoint_name_2)
        # [END batch_endpoint_operations_list_jobs]

    def ml_misc_config_2(self):
        # [START component_operations_create_or_update]
        from azure.ai.ml import load_component
        from azure.ai.ml.entities._component.component import Component

        component_example = load_component(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/components/helloworld_component.yml",
            params_override=[{"version": "1.0.2"}],
        )
        component = ml_client.components.create_or_update(component_example)
        # [END component_operations_create_or_update]
        print(component)

        # [START code_operations_create_or_update]
        from azure.ai.ml.entities._assets._artifacts.code import Code

        code_example = Code(name="my-code-asset", version="2.0", path="./sdk/ml/azure-ai-ml/samples/src")
        code_asset = ml_client._code.create_or_update(code_example)
        # [END code_operations_create_or_update]

        from random import randint

        data_asset_name = f"data_asset_name_{randint(0, 1000)}"
        # [START data_operations_create_or_update]
        from azure.ai.ml.entities import Data

        data_asset_example = Data(name=data_asset_name, version="2.0", path="./sdk/ml/azure-ai-ml/samples/src")
        ml_client.data.create_or_update(data_asset_example)
        # [END data_operations_create_or_update]

        # [START component_operations_list]
        print(ml_client.components.list())
        # [END component_operations_list]

        # [START component_operations_get]
        ml_client.components.get(name=component_example.name, version="1.0.2")
        # [END component_operations_get]

        # [START component_operations_validate]
        from azure.ai.ml.entities._component.component import Component

        ml_client.components.validate(component_example)
        # [END component_operations_validate]

        # [START component_operations_archive]
        ml_client.components.archive(name=component_example.name)
        # [END component_operations_archive]

        # [START component_operations_restore]
        ml_client.components.restore(name=component_example.name)
        # [END component_operations_restore]

        # [START code_operations_get]
        ml_client._code.get(name=code_asset.name, version=code_asset.version)
        # [END code_operations_get]

        # [START data_operations_list]
        ml_client.data.list(name="data_asset_name")
        # [END data_operations_list]

        # [START data_operations_get]
        ml_client.data.get(name="data_asset_name", version="2.0")
        # [END data_operations_get]

        # [START data_operations_import_data]
        from azure.ai.ml.entities._data_import.data_import import DataImport
        from azure.ai.ml.entities._inputs_outputs.external_data import Database

        database_example = Database(query="SELECT ID FROM DataTable", connection="azureml:my_azuresqldb_connection")
        data_import_example = DataImport(
            name="data_asset_name", path="azureml://datastores/workspaceblobstore/paths/", source=database_example
        )
        ml_client.data.import_data(data_import_example)
        # [END data_operations_import_data]

        # [START data_operations_list_materialization_status]
        ml_client.data.list_materialization_status("data_asset_name")
        # [END data_operations_list_materialization_status]

        # [START data_operations_archive]
        ml_client.data.archive("data_asset_name")
        # [END data_operations_archive]

        # [START data_operations_restore]
        ml_client.data.restore("data_asset_name")
        # [END data_operations_restore]

        try:
            # [START data_operations_share]
            ml_client.data.share(
                name="data_asset_name",
                version="2.0",
                registry_name="my-registry",
                share_with_name="transformed-nyc-taxi-data-shared-from-ws",
                share_with_version="2.0",
            )
        # [END data_operations_share]
        except TypeError:
            pass

        # [START datastore_operations_create_or_update]
        from azure.ai.ml.entities import AzureBlobDatastore

        datastore_example = AzureBlobDatastore(
            name="azure_blob_datastore",
            account_name="sdkvnextclidcdnrc7zb7xyy",  # cspell:disable-line
            container_name="testblob",
        )
        ml_client.datastores.create_or_update(datastore_example)
        # [END datastore_operations_create_or_update]

        # [START datastore_operations_list]
        ml_client.datastores.list()
        # [END datastore_operations_list]

        # [START datastore_operations_get]
        ml_client.datastores.get("azure_blob_datastore")
        # [END datastore_operations_get]

        # [START datastore_operations_get_default]
        ml_client.datastores.get_default()
        # [END datastore_operations_get_default]

        # [START datastore_operations_delete]
        ml_client.datastores.delete("azure_blob_datastore")
        # [END datastore_operations_delete]

        # [START validation_result]
        """For example, if repr(self) is:
        ```python
            {
                "errors": [
                    {
                        "path": "jobs.job_a.inputs.input_str",
                        "message": "input_str is required",
                        "value": None,
                    },
                    {
                        "path": "jobs.job_a.inputs.input_str",
                        "message": "input_str must be in the format of xxx",
                        "value": None,
                    },
                    {
                        "path": "settings.on_init",
                        "message": "On_init job name job_b does not exist in jobs.",
                        "value": None,
                    },
                ],
                "warnings": [
                    {
                        "path": "jobs.job_a.inputs.input_str",
                        "message": "input_str is required",
                        "value": None,
                    }
                ]
            }
            ```
            then the error_messages will be:
            ```python
            {
                "jobs.job_a.inputs.input_str": "input_str is required; input_str must be in the format of xxx",
                "settings.on_init": "On_init job name job_b does not exist in jobs.",
            }
            ```
            """
        # [END validation_result]

    @handle_resource_exists_error
    def ml_misc_config_3(self):
        # [START job_operations_show_services]
        job_services = ml_client.jobs.show_services(job_name)
        # [END job_operations_show_services]


if __name__ == "__main__":
    sample = MiscConfigurationOptions()
    sample.ml_misc_config_0()
    sample.ml_misc_config_1()
    sample.ml_misc_config_2()
    sample.ml_misc_config_3()
