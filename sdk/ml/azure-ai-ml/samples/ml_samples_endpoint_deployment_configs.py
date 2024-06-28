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


class EndpointsDeploymentsConfigurationOptions(object):
    def ml_endpoints_deployments_config_0(self):
        # [START scale_settings_entity_create]
        from azure.ai.ml.entities import ScaleSettings

        scale_settings = ScaleSettings(
            type="scale_type",
        )
        # [END scale_settings_entity_create]

        # [START run_settings_entity_create]
        from azure.ai.ml.entities import RunSettings

        run_settings = RunSettings(
            name="run_settings_name",
            display_name="run_settings_display_name",
            experiment_name="experiment_name",
            description="run_settings_description",
            tags={"tag1": "value1", "tag2": "value2"},
            settings={"setting1": "value1", "setting2": "value2"},
        )
        # [END run_settings_entity_create]

        # [START request_logging_entity_create]
        from azure.ai.ml.entities import RequestLogging

        request_logging = RequestLogging(
            capture_headers=["header1", "header2"],
        )
        # [END request_logging_entity_create]

        # [START payload_response_entity_create]
        from azure.ai.ml.entities import PayloadResponse

        payload_response = PayloadResponse(
            enabled="true",
        )
        # [END payload_response_entity_create]

        # [START oversize_data_config_entity_create]
        from azure.ai.ml.entities import OversizeDataConfig

        oversize_data_config = OversizeDataConfig(
            path="path_to_blob"
        )
        # [END oversize_data_config_entity_create]

        # [START event_hub_entity_create]
        from azure.ai.ml.entities import EventHub

        event_hub = EventHub(
            namespace="event_hub_namespace",
            oversize_data_config=oversize_data_config,
        )
        # [END event_hub_entity_create]

        # [START batch_retry_settings_entity_create]
        from azure.ai.ml.entities import BatchRetrySettings

        batch_retry_settings = BatchRetrySettings(
            max_retries=5,
            timeout=10,
        )
        # [END batch_retry_settings_entity_create]

        # [START online_request_settings_entity_create]
        from azure.ai.ml.entities import OnlineRequestSettings

        online_request_settings = OnlineRequestSettings(
            max_concurrent_requests_per_instance=5000,
            request_timeout_ms=1,
            max_queue_wait_ms=500,
        )
        # [END online_request_settings_entity_create]

        # [START probe_settings_entity_create]
        from azure.ai.ml.entities import ProbeSettings

        probe_settings = ProbeSettings(
            failure_threshold=10,
            success_threshold=1,
            timeout=2,
            period=10,
            initial_delay=10,
        )
        # [END probe_settings_entity_create]

        # [START data_asset_entity_create]
        from azure.ai.ml.entities import DataAsset

        data_asset = DataAsset(
            data_id="data_id",
            name="data_name",
            path="data_path",
            version=1,
        )
        # [END data_asset_entity_create]

        # [START deployment_collection_entity_create]
        from azure.ai.ml.entities import DeploymentCollection

        deployment_collection = DeploymentCollection(
            enabled="true",
            data="data_id",
            sampling_rate=0.5,
            client_id="client_id",
        )
        # [END deployment_collection_entity_create]

        # [START data_collector_entity_create]
        from azure.ai.ml.entities import DataCollector

        data_collector = DataCollector(
            collections={"collection1": deployment_collection},
            rolling_rate="hour",
            sampling_rate=0.5,
        )
        # [END data_collector_entity_create]

        # [START resource_requirements_configuration]
        from azure.ai.ml.entities import (
            CodeConfiguration,
            KubernetesOnlineDeployment,
            ResourceRequirementsSettings,
            ResourceSettings,
        )
        from azure.ai.ml import load_model

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

        # [START code_configuration_entity_create]
        from azure.ai.ml.entities import CodeConfiguration

        codeConfig = CodeConfiguration(
            code="code_directory", 
            scoring_script="scoring_script.py"
        )
        # [END code_configuration_entity_create]   

        from azure.ai.ml.entities._deployment.model_batch_deployment_settings import ModelBatchDeploymentSettings

        # [START model_batch_deployment_settings_entity_create]
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

        # [START model_batch_deployment_config]
        from azure.ai.ml.entities import ModelBatchDeployment, ModelBatchDeploymentSettings, CodeConfiguration, BatchRetrySettings

        model_deployment = ModelBatchDeployment(
            name="batch-deployment",
            description="This is a sample batch deployment.",
            endpoint_name="endpoint_name",
            model="model_name",
            code_configuration=codeConfig,
            environment="environment_name",
            compute="compute_name",
            settings=modelBatchDeploymentSetting,
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            compute="cpu-cluster",
            scoring_script="scoring_script",
        )
        # [END model_batch_deployment_config]

        # [START batch_deployment_entity_config]
        from azure.ai.ml.entities import BatchDeployment

        batch_deployment = BatchDeployment(
            name="batch_deployment",
            endpoint_name="endpoint_name",
            description="This is a sample batch deployment.",
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            model="model_name",
            environment="environment_name",
            code_configuration=codeConfig,
        )
        # [END batch_deployment_entity_config]

        # [START pipeline_component_batch_deployment_config]
        from azure.ai.ml.entities import PipelineComponentBatchDeployment

        pipeline_component_batch_deployment = PipelineComponentBatchDeployment(
            name="pipeline_component_batch_deployment",
            endpoint_name="endpoint_name",
            component="component_name",
            settings={"setting1": "value1", "setting2": "value2"},
            tags={"tag1": "value1", "tag2": "value2"},
            description="This is a sample pipeline component batch deployment.",
        )
        # [END pipeline_component_batch_deployment_config]

        # [START managed_online_endpoint_config]
        from azure.ai.ml.entities import ManagedOnlineEndpoint

        managed_online_endpoint = ManagedOnlineEndpoint(
            name="managed_online_endpoint",
            endpoint_name="endpoint_name",
            description="This is a sample managed online endpoint.",
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            model="model_name",
            environment="environment_name",
            code_configuration=codeConfig,
            app_insights_enabled=True,
            scale_settings=scale_settings,
            request_settings=online_request_settings,
            liveness_settings=probe_settings,
            readiness_settings=probe_settings,
            environment_variables={"env1": "value1", "env2": "value2"},
            instance_type="Standard_D2_v2",
            instance_count=2,
            egress_public_network_acess="enabled",
            code_path="code_path",
            scoring_script="scoring_script",
            data_collector=data_collector,
        )
        # [END managed_online_endpoint_config]

        # [START kubernetes_online_deployment_config]
        from azure.ai.ml.entities import KubernetesOnlineDeployment

        kubernetes_online_deployment = KubernetesOnlineDeployment(
            name="kubernetes_online_deployment",
            endpoint_name="endpoint_name",
            description="This is a sample kubernetes online deployment.",
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            model="model_name",
            environment="environment_name",
            app_insights_enabled=True,
            scale_settings=scale_settings,
            request_settings=online_request_settings,
            liveness_settings=probe_settings,
            readiness_settings=probe_settings,
            environment_variables={"env1": "value1", "env2": "value2"},
            code_configuration=codeConfig,
            instance_type="Standard_D2_v2",
            instance_count=2,
            code_path="code_path",
            scoring_script="scoring_script",
        )
        # [END kubernetes_online_deployment_config]

        # [START kubernetes_online_endpoint_config]
        from azure.ai.ml.entities import KubernetesOnlineEndpoint

        kubernetes_online_endpoint = KubernetesOnlineEndpoint(
            name="kubernetes_online_endpoint",
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            description="This is a sample kubernetes online endpoint.",
            location="location",
            traffic={"traffic1": 0.5, "traffic2": 0.5},
            mirror_traffic={"traffic1": 0.5, "traffic2": 0.5},
            compute="compute_name",
            kind="kind",
        )
        # [END kubernetes_online_endpoint_config]

        # [START managed_online_endpoint_config]
        from azure.ai.ml.entities import ManagedOnlineEndpoint

        managed_online_endpoint = ManagedOnlineEndpoint(
            name="managed_online_endpoint",
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            description="This is a sample managed online endpoint.",
            location="location",
            traffic={"traffic1": 0.5, "traffic2": 0.5},
            mirror_traffic={"traffic1": 0.5, "traffic2": 0.5},
            kind="kind",
            public_network_access="enabled",
        )
        # [END managed_online_endpoint_config]

        # [START endpoint_auth_token_config]
        from azure.ai.ml.entities import EndpointAuthToken

        endpoint_auth_token = EndpointAuthToken(
            access_token="access_token",
            token_type="token_type",
            expiry_time_utc="expiry_time_utc",
            refresh_after_time_utc="refresh_after_time_utc",
        )
        # [END endpoint_auth_token_config]

        # [START batch_endpoint_config]
        from azure.ai.ml.entities import BatchEndpoint

        batch_endpoint = BatchEndpoint(
            name="batch_endpoint",
            tags={"tag1": "value1", "tag2": "value2"},
            properties={"prop1": "value1", "prop2": "value2"},
            description="This is a sample batch endpoint.",
            location="location",
            defaults={"deployment_name": "deployment_name"},
            default_deployment_name="default_deployment_name",
            scoring_uri="scoring_uri",
            openapi_uri="openapi_uri",
        )
        # [END batch_endpoint_config]

        # [START online_endpoint_begin_create_update_operation]
        from azure.ai.ml import load_batch_deployment
        from azure.ai.ml.entities import BatchDeployment

        deployment_example = load_batch_deployment(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/deployments/online/online_deployment_1.yaml",
            params_override=[{"name": f"deployment-{randint(0, 1000)}", "endpoint_name": "endpoint_name"}],
        )

        ml_client.batch_deployments.begin_create_or_update(deployment=deployment_example, skip_script_validation=True)
        # [END online_endpoint_begin_create_update_operation]

    def ml_endpoints_deployments_config_1(self):
        from random import randint

        # [START online_deployment_load_example]
        from azure.ai.ml import load_online_endpoint

        endpoint_example = load_online_endpoint(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/endpoints/online/online_endpoint_minimal.yaml",
            params_override=[{"name": f"endpoint-{randint(0, 1000)}"}],
        )
        # [END online_deployment_load_example]
        ml_client.online_endpoints.begin_create_or_update(endpoint_example)
        endpoint_name = endpoint_example.name

        # [START batch_deployment_load_example]
        from azure.ai.ml import load_batch_deployment

        deployment_example = load_batch_deployment(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/deployments/batch/batch_deployment_anon_env_with_image.yaml",
            params_override=[{"name": f"deployment-{randint(0, 1000)}", "endpoint_name": endpoint_example.name}],
        )
        # [END batch_deployment_load_example]

        # [START online_deployment_load_example]
        from azure.ai.ml import load_online_deployment

        deployment_example = load_online_deployment(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/deployments/online/online_deployment_1.yaml",
            params_override=[{"name": f"deployment-{randint(0, 1000)}", "endpoint_name": endpoint_name}],
        )
        # [END online_deployment_load_example]

        # [START online_deployment_begin_create_update_operation]
        from azure.ai.ml import load_online_deployment

        deployment_example = load_online_deployment(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/deployments/online/online_deployment_1.yaml",
            params_override=[{"name": f"deployment-{randint(0, 1000)}", "endpoint_name": endpoint_name}],
        )

        ml_client.online_deployments.begin_create_or_update(deployment=deployment_example, skip_script_validation=True)
        # [END online_deployment_begin_create_update_operation]

        deployment_name = deployment_example.name

        # [START online_deployment_get_operation]
        ml_client.online_deployments.get(deployment_name, endpoint_name)
        # [END online_deployment_get_operation]

        # [START online_deployment_list_operation]
        ml_client.online_deployments.list(endpoint_name)
        # [END online_deployment_list_operation]

        # [START online_deployment_delete_operation]
        ml_client.online_deployments.begin_delete(deployment_name, endpoint_name)
        # [END online_deployment_delete_operation]

        # [START online_deployment_get_logs_operation]
        ml_client.online_deployments.get_logs(deployment_name, endpoint_name, lines=100)
        # [END online_deployment_get_logs_operation]

        from random import randint

        endpoint_name_2 = f"endpoint-{randint(0, 1000)}"

        # [START online_endpoint_create_update_operation]
        from azure.ai.ml.entities import ManagedOnlineEndpoint

        endpoint_example = ManagedOnlineEndpoint(name=endpoint_name_2)
        ml_client.online_endpoints.begin_create_or_update(endpoint_example)
        # [END online_endpoint_create_update_operation]

        # [START online_endpoint_invoke_operation]
        ml_client.online_endpoints.invoke(endpoint_name_2)
        # [END online_endpoint_invoke_operation]

        # [START online_endpoint_list_operation]
        ml_client.online_endpoints.list()
        # [END online_endpoint_list_operation]

        # [START online_endpoint_get_keys_operation]
        ml_client.online_endpoints.get_keys(endpoint_name_2)
        # [END online_endpoint_get_keys_operation]

        # [START online_endpoint_get_operation]
        ml_client.online_endpoints.get(endpoint_name_2)
        # [END online_endpoint_get_operation]

        # [START online_endpoint_delete_operation]
        ml_client.online_endpoints.begin_delete(endpoint_name_2)
        # [END online_endpoint_delete_operation]

        # [START online_endpoint_begin_regenerate_keys_operation]
        ml_client.online_endpoints.begin_regenerate_keys(endpoint_name_2)
        # [END online_endpoint_begin_regenerate_keys_operation]

    def ml_endpoints_deployments_config_2(self):
        from random import randint
        from azure.ai.ml import load_online_endpoint

        endpoint_example = load_online_endpoint(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/endpoints/online/online_endpoint_minimal.yaml",
            params_override=[{"name": f"endpoint-{randint(0, 1000)}"}],
        )

        endpoint_name = endpoint_example.name

        # [START model_batch_deployment_load_example]
        from azure.ai.ml import load_model_batch_deployment

        deployment_example = load_model_batch_deployment(
            source="./sdk/ml/azure-ai-ml/tests/test_configs/deployments/batch/batch_deployment_anon_env_with_image.yaml",
            params_override=[{"name": f"deployment-{randint(0, 1000)}", "endpoint_name": endpoint_name}],
        )
        # [END model_batch_deployment_load_example]




if __name__ == "__main__":
    sample = EndpointsDeploymentsConfigurationOptions()
    sample.ml_endpoints_deployments_config_0()
    sample.ml_endpoints_deployments_config_1()
    sample.ml_endpoints_deployments_config_2()
