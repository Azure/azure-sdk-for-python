import copy
import json

import pytest
import yaml
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_batch_deployment, load_online_deployment
from azure.ai.ml._restclient.v2022_10_01.models import BatchDeployment as BatchDeploymentData
from azure.ai.ml._restclient.v2022_10_01.models import BatchOutputAction, EndpointComputeType
from azure.ai.ml._restclient.v2023_04_01_preview.models import BatchPipelineComponentDeploymentConfiguration
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    KubernetesOnlineDeployment as RestKubernetesOnlineDeployment,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import ManagedOnlineDeployment as RestManagedOnlineDeployment
from azure.ai.ml._restclient.v2023_04_01_preview.models import OnlineDeployment as RestOnlineDeploymentData
from azure.ai.ml.constants._common import ArmConstants
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities import (
    BatchDeployment,
    CodeConfiguration,
    DefaultScaleSettings,
    Deployment,
    KubernetesOnlineDeployment,
    ManagedOnlineDeployment,
    OnlineDeployment,
    OnlineEndpoint,
    OnlineRequestSettings,
    ProbeSettings,
    ResourceRequirementsSettings,
    ResourceSettings,
    TargetUtilizationScaleSettings,
)
from azure.ai.ml.entities._assets import Code, Environment, Model
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._deployment.model_batch_deployment_settings import (
    ModelBatchDeploymentSettings as BatchDeploymentSettings,
)
from azure.ai.ml.entities._deployment.run_settings import RunSettings
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.exceptions import DeploymentException, ValidationException


@pytest.mark.production_experiences_test
@pytest.mark.unittest
class TestDeploymentSanity:
    def test_instantiate_OnlineEndpoint_fail(self) -> None:
        with pytest.raises(TypeError):
            OnlineEndpoint(name="my-endpoint")

    def test_instantiate_OnlineDeployment_fail(self) -> None:
        with pytest.raises(TypeError):
            OnlineDeployment()

    def test_instantiate_AKSOnlineDeployment(self) -> None:
        with pytest.raises(TypeError):
            ManagedOnlineDeployment()

        ManagedOnlineDeployment(name="my-deployment")

    def test_instantiate_KubernetesOnlineDeployment(self) -> None:
        with pytest.raises(TypeError):
            KubernetesOnlineDeployment()

        KubernetesOnlineDeployment(name="my-deployment")

    def test_instantiate_batchDeployment(self) -> None:
        with pytest.raises(TypeError):
            BatchDeployment()

        BatchDeployment(name="my-deployment")


@pytest.mark.unittest
class TestOnlineDeploymentFromYAML:
    BLUE_ONLINE_DEPLOYMENT = "tests/test_configs/deployments/online/online_deployment_blue.yaml"
    BLUE_ONLINE_DEPLOYMENT_FULL = "tests/test_configs/deployments/online/online_deployment_blue_full.yaml"
    BLUE_K8S_ONLINE_DEPLOYMENT = "tests/test_configs/deployments/online/online_deployment_blue_k8s.yaml"
    MINIMAL_DEPLOYMENT = "tests/test_configs/deployments/online/online_endpoint_deployment_k8s_minimum.yml"
    MANAGED_DEPLOYMENT_FULL = "tests/test_configs/deployments/online/online_deployment_managed_full.yml"
    PREVIEW_DEPLOYMENT = "tests/test_configs/deployments/online/online_deployment_1.yaml"

    def test_generic_deployment(self) -> None:
        with open(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)
        assert isinstance(blue, OnlineDeployment)
        assert blue.type == EndpointComputeType.KUBERNETES
        assert blue.endpoint_name == target["endpoint_name"]
        assert "blue" in blue.name
        assert isinstance(blue.model, Model)
        assert isinstance(blue.environment, Environment)
        assert isinstance(blue.code_configuration, CodeConfiguration)
        assert isinstance(blue.liveness_probe, ProbeSettings)
        assert isinstance(blue.readiness_probe, ProbeSettings)
        assert blue.model.name == target["model"]["name"]
        assert blue.instance_type == "cpuinstance"
        assert blue.description == target["description"]

    def test_generic_deployment_merge(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT_FULL)
        blue_copy = copy.deepcopy(blue)
        blue_copy.request_settings = OnlineRequestSettings(
            max_concurrent_requests_per_instance=1, max_queue_wait_ms=100, request_timeout_ms=100
        )
        blue_copy.code_configuration = CodeConfiguration(code="blah path", scoring_script="blah.py")
        blue_copy.model = Model(name="blah model")
        blue_copy.environment = Environment(name="blah model")
        blue_copy.endpoint_name = "blah endpoint"
        blue_copy.scale_settings = DefaultScaleSettings()
        blue_copy.request_settings = OnlineRequestSettings(
            max_concurrent_requests_per_instance=1, max_queue_wait_ms=100, request_timeout_ms=100
        )
        blue_copy.instance_count = 3
        blue_copy.instance_type = "STANDARD_L8S_V3"
        blue_copy.tags = {"tag3": "value3"}
        blue_copy.environment_variables = {"env3": "value3"}

        blue._merge_with(blue_copy)

        assert blue.model.name == blue_copy.model.name
        assert blue.environment.name == blue_copy.environment.name
        assert blue.code_configuration.code == blue_copy.code_configuration.code
        assert blue.code_configuration.scoring_script == blue_copy.code_configuration.scoring_script
        assert blue.endpoint_name == blue_copy.endpoint_name
        assert blue.scale_settings.type == blue_copy.scale_settings.type
        assert (
            blue.request_settings.max_concurrent_requests_per_instance
            == blue_copy.request_settings.max_concurrent_requests_per_instance
        )
        assert blue.request_settings.max_queue_wait_ms == blue_copy.request_settings.max_queue_wait_ms
        assert blue.request_settings.request_timeout_ms == blue_copy.request_settings.request_timeout_ms
        assert blue.liveness_probe.failure_threshold == blue_copy.liveness_probe.failure_threshold
        assert blue.liveness_probe.success_threshold == blue_copy.liveness_probe.success_threshold
        assert blue.liveness_probe.timeout == blue_copy.liveness_probe.timeout
        assert blue.liveness_probe.period == blue_copy.liveness_probe.period
        assert blue.liveness_probe.initial_delay == blue_copy.liveness_probe.initial_delay
        assert blue.readiness_probe.failure_threshold == blue_copy.readiness_probe.failure_threshold
        assert blue.readiness_probe.success_threshold == blue_copy.readiness_probe.success_threshold
        assert blue.readiness_probe.timeout == blue_copy.readiness_probe.timeout
        assert blue.readiness_probe.period == blue_copy.readiness_probe.period
        assert blue.readiness_probe.initial_delay == blue_copy.readiness_probe.initial_delay
        assert blue.instance_type == blue_copy.instance_type
        assert blue.instance_count == blue_copy.instance_count
        assert blue.tags == {**blue.tags, **blue_copy.tags}
        assert blue.environment_variables == {**blue.environment_variables, **blue_copy.environment_variables}

    def test_generic_deployment_merge_when_original_attribues_not_set(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)
        blue_copy = copy.deepcopy(blue)
        blue.liveness_probe = None
        blue.readiness_probe = None
        blue.scale_settings = None
        blue.request_settings = None
        blue.resources = ResourceRequirementsSettings()

        blue_copy.code_configuration = CodeConfiguration(code="blah path", scoring_script="blah.py")
        blue_copy.model = Model(name="blah code")
        blue_copy.environment = Environment(name="blah model")
        blue_copy.endpoint_name = "blah endpoint"
        blue_copy.scale_settings = DefaultScaleSettings()
        blue_copy.request_settings = OnlineRequestSettings(
            max_concurrent_requests_per_instance=1, max_queue_wait_ms=100, request_timeout_ms=100
        )
        blue_copy.resources = ResourceRequirementsSettings(
            requests=ResourceSettings(cpu="1n", memory="2"), limits=ResourceSettings(cpu="2", memory="4")
        )
        blue._merge_with(blue_copy)

        assert blue.model.name == blue_copy.model.name
        assert blue.environment.name == blue_copy.environment.name
        assert blue.code_configuration.code == blue_copy.code_configuration.code
        assert blue.code_configuration.scoring_script == blue_copy.code_configuration.scoring_script
        assert blue.endpoint_name == blue_copy.endpoint_name
        assert blue.scale_settings.type == blue_copy.scale_settings.type
        assert blue.liveness_probe.failure_threshold == blue_copy.liveness_probe.failure_threshold
        assert blue.liveness_probe.success_threshold == blue_copy.liveness_probe.success_threshold
        assert blue.liveness_probe.timeout == blue_copy.liveness_probe.timeout
        assert blue.liveness_probe.period == blue_copy.liveness_probe.period
        assert blue.liveness_probe.initial_delay == blue_copy.liveness_probe.initial_delay
        assert blue.readiness_probe.failure_threshold == blue_copy.readiness_probe.failure_threshold
        assert blue.readiness_probe.success_threshold == blue_copy.readiness_probe.success_threshold
        assert blue.readiness_probe.timeout == blue_copy.readiness_probe.timeout
        assert blue.readiness_probe.period == blue_copy.readiness_probe.period
        assert blue.request_settings.max_queue_wait_ms == blue_copy.request_settings.max_queue_wait_ms
        assert blue.request_settings.request_timeout_ms == blue_copy.request_settings.request_timeout_ms

    def test_generic_deployment_merge_props(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)
        blue_copy = copy.deepcopy(blue)

        blue.tags = {"otag": "otagvalue"}
        blue.properties = {"oprop": "opropvalue"}
        blue.environment_variables = {"oev": "oevvalue"}

        blue_copy.tags = {"ntag": "ntagvalue"}
        blue_copy.properties = {"nprop": "npropvalue"}
        blue_copy.environment_variables = {"nev": "nevvalue"}

        blue._merge_with(blue_copy)
        assert len(blue.tags) == 2
        assert blue.tags["ntag"] == "ntagvalue"
        assert blue.tags["otag"] == "otagvalue"

        assert len(blue.properties) == 2
        assert blue.properties["nprop"] == "npropvalue"
        assert blue.properties["oprop"] == "opropvalue"

        assert len(blue.environment_variables) == 2
        assert blue.environment_variables["nev"] == "nevvalue"
        assert blue.environment_variables["oev"] == "oevvalue"

    def test_generic_deployment_merge_endpoint_mismatch(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)
        blue_copy = copy.deepcopy(blue)

        blue_copy.name = "different deployment"

        with pytest.raises(Exception) as exc:
            blue._merge_with(blue_copy)
        assert "are not matched when merging" in str(exc.value)

    def test_managed_deployment_merge(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT)
        blue.scale_settings = TargetUtilizationScaleSettings(
            min_instances=2, max_instances=5, target_utilization_percentage=8, polling_interval=10
        )
        blue_copy = copy.deepcopy(blue)
        blue_copy.scale_settings = TargetUtilizationScaleSettings(
            min_instances=3, max_instances=4, target_utilization_percentage=11, polling_interval=100
        )
        blue_copy.instance_type = "gpuinstance"

        blue._merge_with(blue_copy)

        assert blue.instance_type == blue_copy.instance_type
        assert blue.scale_settings.min_instances == blue_copy.scale_settings.min_instances
        assert blue.scale_settings.max_instances == blue_copy.scale_settings.max_instances
        assert (
            blue.scale_settings.target_utilization_percentage == blue_copy.scale_settings.target_utilization_percentage
        )
        assert blue.scale_settings.polling_interval == blue_copy.scale_settings.polling_interval

    def test_k8s_deployment(self) -> None:
        with open(TestOnlineDeploymentFromYAML.BLUE_K8S_ONLINE_DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_K8S_ONLINE_DEPLOYMENT)
        assert isinstance(blue, KubernetesOnlineDeployment)
        assert blue.type == EndpointComputeType.KUBERNETES
        assert blue.endpoint_name == target["endpoint_name"]
        assert "blue" in blue.name
        assert isinstance(blue.model, Model)
        assert isinstance(blue.environment, Environment)
        assert isinstance(blue.code_configuration, CodeConfiguration)
        assert isinstance(blue.liveness_probe, ProbeSettings)
        assert isinstance(blue.readiness_probe, ProbeSettings)
        assert isinstance(blue.resources, ResourceRequirementsSettings)
        assert isinstance(blue.resources.requests, ResourceSettings)
        assert isinstance(blue.resources.limits, ResourceSettings)
        assert blue.model.name == target["model"]["name"]
        assert blue.resources.requests.gpu == target["resources"]["requests"]["nvidia.com/gpu"]
        assert blue.description == target["description"]
        assert blue.instance_type == target["instance_type"]

    def test_get_arm_resource(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT)
        arm_resource = blue._get_arm_resource()
        assert arm_resource[ArmConstants.DEPENDSON_PARAMETER_NAME][0] == f"{blue.environment._arm_type}Deployment"
        assert arm_resource[ArmConstants.DEPENDSON_PARAMETER_NAME][1] == f"{blue.model._arm_type}Deployment"

    def test_set_scale_settings(self) -> None:
        with open(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT, "r") as f:
            blue = yaml.safe_load(f)
            blue["scale_settings"] = {
                "type": "default",
                "min_instances": 1,
                "max_instances": 2,
                "polling_interval": 3,
                "target_utilization_percentage": 4,
            }

            class OnlineDeploymentDict(dict):
                def __init__(self, *args, **kwargs):
                    super(OnlineDeploymentDict, self).__init__(*args, **kwargs)
                    self.scale_settings = "default"

            blue = OnlineDeploymentDict(blue)
            OnlineDeployment._set_scale_settings(blue)
            assert len(blue["scale_settings"]) == 1
            assert blue["scale_settings"]["type"] == "default"

    def test_kubenetes_deployment_to_dict(self) -> None:
        with open(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT, "r") as f:
            minimal_deployment = yaml.safe_load(f)
            online_deployment_dict = load_online_deployment(
                TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT
            )._to_dict()
            assert online_deployment_dict["name"] == minimal_deployment["name"]
            assert online_deployment_dict["endpoint_name"] == minimal_deployment["endpoint_name"]
            assert online_deployment_dict["model"]["name"] == minimal_deployment["model"]["name"]
            assert online_deployment_dict["type"] == "kubernetes"

    def test_managed_deployment_to_dict(self) -> None:
        with open(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT, "r") as f:
            minimal_deployment = yaml.safe_load(f)
            online_deployment_dict = load_online_deployment(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT)._to_dict()
            assert online_deployment_dict["name"] == minimal_deployment["name"]
            assert online_deployment_dict["endpoint_name"] == minimal_deployment["endpoint_name"]
            assert online_deployment_dict["model"]["name"] == minimal_deployment["model"]["name"]
            assert online_deployment_dict["type"] == "managed"

    def test_generate_dependencies(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT)
        code, environment_id, model_id = blue._generate_dependencies()
        assert code.code_id == blue.code_configuration.code
        assert code.scoring_script == blue.code_configuration.scoring_script
        assert environment_id == blue.environment.id
        assert model_id == blue.model.id

    def test_get_arm_resource_and_params(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT)
        blue.egress_public_network_access = "Enabled"
        blue.private_network_connection = True
        arm_resource = blue._get_arm_resource_and_params(location="westus2")

        assert arm_resource[0][0][ArmConstants.DEPENDSON_PARAMETER_NAME][0] == f"{blue.environment._arm_type}Deployment"
        assert arm_resource[0][0][ArmConstants.DEPENDSON_PARAMETER_NAME][1] == f"{blue.model._arm_type}Deployment"
        assert arm_resource[0][1]["online_deployment"]["name"] == blue.name
        assert arm_resource[1][0]["type"] == "Microsoft.MachineLearningServices/workspaces/environments/versions"
        assert arm_resource[1][1]["environment_version"]["name"] == blue.environment.name
        assert arm_resource[2][0]["type"] == "Microsoft.MachineLearningServices/workspaces/models/versions"
        assert arm_resource[2][1]["model_version"]["name"] == blue.model.name

    def test_get_arm_resource_and_params_for_kubenets_deployment(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)
        arm_resource = blue._get_arm_resource_and_params(location="westus2")

        assert arm_resource[0][0][ArmConstants.DEPENDSON_PARAMETER_NAME][0] == f"{blue.environment._arm_type}Deployment"
        assert arm_resource[0][0][ArmConstants.DEPENDSON_PARAMETER_NAME][1] == f"{blue.model._arm_type}Deployment"
        assert arm_resource[0][1]["online_deployment"]["name"] == blue.name
        assert arm_resource[1][0]["type"] == "Microsoft.MachineLearningServices/workspaces/environments/versions"
        assert arm_resource[1][1]["environment_version"]["name"] == blue.environment.name
        assert arm_resource[2][0]["type"] == "Microsoft.MachineLearningServices/workspaces/models/versions"
        assert arm_resource[2][1]["model_version"]["name"] == blue.model.name

    def test_preview_mir_deployment(self) -> None:
        with open(TestOnlineDeploymentFromYAML.PREVIEW_DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.PREVIEW_DEPLOYMENT)
        assert isinstance(blue, OnlineDeployment)
        for key, value in target.items():
            if isinstance(value, str):
                assert getattr(blue, key) == value

    def test_managed_online_deployment_to_rest_object(self) -> None:
        managed_deployment = load_online_deployment(TestOnlineDeploymentFromYAML.MANAGED_DEPLOYMENT_FULL)

        managed_deployment_rest = managed_deployment._to_rest_object(location="westus2")

        assert isinstance(managed_deployment_rest.properties, RestManagedOnlineDeployment)
        assert (
            managed_deployment_rest.properties.code_configuration.code_id == managed_deployment.code_configuration.code
        )
        assert (
            managed_deployment_rest.properties.code_configuration.scoring_script
            == managed_deployment.code_configuration.scoring_script
        )
        assert managed_deployment_rest.properties.environment_id == managed_deployment.environment.id
        assert managed_deployment_rest.properties.model == managed_deployment.model.id
        assert managed_deployment_rest.properties.model_mount_path == managed_deployment.model_mount_path
        assert (
            managed_deployment_rest.properties.scale_settings.scale_type.lower()
            == managed_deployment.scale_settings.type.lower()
        )
        assert managed_deployment_rest.properties.properties == managed_deployment.properties
        assert managed_deployment_rest.properties.description == managed_deployment.description
        assert managed_deployment_rest.properties.environment_variables == managed_deployment.environment_variables
        assert managed_deployment_rest.properties.app_insights_enabled == managed_deployment.app_insights_enabled
        assert (
            managed_deployment_rest.properties.request_settings.max_concurrent_requests_per_instance
            == managed_deployment.request_settings.max_concurrent_requests_per_instance
        )
        assert managed_deployment_rest.properties.request_settings.max_queue_wait == "PT1S"
        assert managed_deployment_rest.properties.request_settings.request_timeout == "PT10S"
        assert managed_deployment_rest.properties.liveness_probe.timeout == "PT10S"
        assert managed_deployment_rest.properties.readiness_probe.timeout == "PT10S"
        assert managed_deployment_rest.properties.data_collector.rolling_rate == "hour"
        assert (
            managed_deployment_rest.properties.data_collector.collections["model_inputs"].data_collection_mode
            == "enabled"
        )
        assert (
            managed_deployment_rest.properties.data_collector.request_logging.capture_headers
            == managed_deployment.data_collector.request_logging.capture_headers
        )
        assert (
            managed_deployment_rest.properties.egress_public_network_access
            == managed_deployment.egress_public_network_access
        )
        assert managed_deployment_rest.sku.name == "Default"
        assert managed_deployment_rest.sku.capacity == managed_deployment.instance_count
        assert managed_deployment_rest.location == "westus2"
        assert managed_deployment_rest.tags == managed_deployment.tags

    def test_kubernetes_online_deployment_to_rest_object(self) -> None:
        kubernetes_deployment = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT_FULL)
        kubernetes_deployment.scale_settings = TargetUtilizationScaleSettings(
            min_instances=2, max_instances=5, target_utilization_percentage=8, polling_interval=10
        )

        kubernetes_deployment_rest = kubernetes_deployment._to_rest_object(location="westus2")

        assert isinstance(kubernetes_deployment_rest.properties, RestKubernetesOnlineDeployment)
        assert (
            kubernetes_deployment_rest.properties.code_configuration.code_id
            == kubernetes_deployment.code_configuration.code
        )
        assert (
            kubernetes_deployment_rest.properties.code_configuration.scoring_script
            == kubernetes_deployment.code_configuration.scoring_script
        )
        assert kubernetes_deployment_rest.properties.environment_id == kubernetes_deployment.environment.id
        assert kubernetes_deployment_rest.properties.model == kubernetes_deployment.model.id
        assert kubernetes_deployment_rest.properties.model_mount_path == kubernetes_deployment.model_mount_path
        assert kubernetes_deployment_rest.properties.scale_settings.scale_type == "TargetUtilization"
        assert (
            kubernetes_deployment_rest.properties.scale_settings.min_instances
            == kubernetes_deployment.scale_settings.min_instances
        )
        assert kubernetes_deployment_rest.properties.properties == kubernetes_deployment.properties
        assert kubernetes_deployment_rest.properties.description == kubernetes_deployment.description
        assert (
            kubernetes_deployment_rest.properties.environment_variables == kubernetes_deployment.environment_variables
        )
        assert kubernetes_deployment_rest.properties.app_insights_enabled == kubernetes_deployment.app_insights_enabled
        assert (
            kubernetes_deployment_rest.properties.request_settings.max_concurrent_requests_per_instance
            == kubernetes_deployment.request_settings.max_concurrent_requests_per_instance
        )
        assert kubernetes_deployment_rest.properties.request_settings.max_queue_wait == "PT1S"
        assert kubernetes_deployment_rest.properties.request_settings.request_timeout == "PT10S"
        assert kubernetes_deployment_rest.properties.liveness_probe.timeout == "PT10S"
        assert kubernetes_deployment_rest.properties.readiness_probe.timeout == "PT10S"
        assert kubernetes_deployment_rest.sku.name == "Default"
        assert kubernetes_deployment_rest.sku.capacity == kubernetes_deployment.instance_count
        assert kubernetes_deployment_rest.location == "westus2"
        assert kubernetes_deployment_rest.tags == kubernetes_deployment.tags


@pytest.mark.unittest
class TestBatchDeploymentSDK:
    DEPLOYMENT = "tests/test_configs/deployments/batch/batch_deployment_mlflow.yaml"
    DEPLOYMENT_REST = "tests/test_configs/deployments/batch/batch_deployment_full_rest.json"

    def test_batch_endpoint_deployment_load_and_dump(self) -> None:
        with open(TestBatchDeploymentSDK.DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)

        def simple_batch_deployment_validation(deployment):
            assert isinstance(deployment, BatchDeployment)
            assert isinstance(deployment.model, str)
            assert isinstance(deployment.compute, str)
            # comment out assertion as resources type has changes to JobResourceConfiguration
            # assert isinstance(deployment.resources, ResourceConfiguration)
            assert deployment.model == "lightgbm_predict:1"
            assert deployment.output_action == BatchDeploymentOutputAction.APPEND_ROW
            assert deployment.max_concurrency_per_instance == target["max_concurrency_per_instance"]
            assert deployment.retry_settings.max_retries == target["retry_settings"]["max_retries"]
            assert deployment.retry_settings.timeout == target["retry_settings"]["timeout"]
            assert deployment.description == target["description"]

        verify_entity_load_and_dump(
            load_batch_deployment, simple_batch_deployment_validation, TestBatchDeploymentSDK.DEPLOYMENT
        )

    def test_batch_endpoint_deployment_deprecated_warning(self):
        # Test for warning when using deprecated BatchDeployment class
        with pytest.warns(
            UserWarning, match="This class is intended as a base class and it's direct usage is deprecated"
        ):
            deployment = load_batch_deployment(TestBatchDeploymentSDK.DEPLOYMENT)
            assert deployment._type is None

    def test_batch_endpoint_deployment_to_rest_object(self) -> None:
        with open(TestBatchDeploymentSDK.DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)
        print(target)
        deployment = load_batch_deployment(TestBatchDeploymentSDK.DEPLOYMENT)
        # test REST translation s
        deployment_resource = deployment._to_rest_object(location="westus2")
        rest_representation_properties = deployment_resource.properties
        assert rest_representation_properties.max_concurrency_per_instance == target["max_concurrency_per_instance"]
        assert rest_representation_properties.retry_settings.max_retries == target["retry_settings"]["max_retries"]
        assert rest_representation_properties.retry_settings.timeout == "PT30S"
        assert rest_representation_properties.error_threshold == target["error_threshold"]
        assert rest_representation_properties.output_action == BatchOutputAction.APPEND_ROW
        assert rest_representation_properties.description == target["description"]

    def test_batch_deployment_attributes_access(self) -> None:
        # Create a deployment with settings properties
        deployment = BatchDeployment(
            name="attribute-test-deployment",
            output_action=BatchDeploymentOutputAction.APPEND_ROW,
            output_file_name="test.csv",
            error_threshold=10,
            retry_settings=BatchRetrySettings(max_retries=5, timeout=60),
            logging_level="info",
            mini_batch_size=20,
            max_concurrency_per_instance=4,
            environment_variables={"key1": "value1"},
        )
        assert isinstance(
            deployment._settings, BatchDeploymentSettings
        )  # Test accessing settings attributes through __getattr__
        assert deployment.output_action == BatchDeploymentOutputAction.APPEND_ROW
        assert deployment.output_file_name == "test.csv"
        assert deployment.error_threshold == 10
        assert deployment.retry_settings.max_retries == 5
        assert deployment.retry_settings.timeout == 60
        assert deployment.logging_level == "info"
        assert deployment.mini_batch_size == 20
        assert deployment.max_concurrency_per_instance == 4
        assert deployment.environment_variables == {"key1": "value1"}

        # Test setting settings attributes through __setattr__
        deployment.output_action = BatchDeploymentOutputAction.SUMMARY_ONLY
        deployment.output_file_name = "new.csv"
        deployment.error_threshold = 20
        deployment.retry_settings = BatchRetrySettings(max_retries=10, timeout=120)
        deployment.logging_level = "debug"
        deployment.mini_batch_size = 30
        deployment.max_concurrency_per_instance = 8
        deployment.environment_variables = {"key2": "value2"}

        # Verify attributes were updated correctly
        assert deployment.output_action == BatchDeploymentOutputAction.SUMMARY_ONLY
        assert deployment._settings.output_action == BatchDeploymentOutputAction.SUMMARY_ONLY
        assert deployment.output_file_name == "new.csv"
        assert deployment._settings.output_file_name == "new.csv"
        assert deployment.error_threshold == 20
        assert deployment._settings.error_threshold == 20
        assert deployment.retry_settings.max_retries == 10
        assert deployment._settings.retry_settings.max_retries == 10
        assert deployment.retry_settings.timeout == 120
        assert deployment._settings.retry_settings.timeout == 120
        assert deployment.logging_level == "debug"
        assert deployment._settings.logging_level == "debug"
        assert deployment.mini_batch_size == 30
        assert deployment._settings.mini_batch_size == 30
        assert deployment.max_concurrency_per_instance == 8
        assert deployment._settings.max_concurrency_per_instance == 8
        assert deployment.environment_variables == {"key2": "value2"}
        assert deployment._settings.environment_variables == {"key2": "value2"}

        # Test accessing non-settings attributes
        assert deployment.name == "attribute-test-deployment"

        # Test setting non-settings attributes
        deployment.name = "updated-deployment"
        assert deployment.name == "updated-deployment"

        # Ensure setting a non-existent attribute doesn't raise an exception
        deployment.new_attribute = "test"
        assert deployment.new_attribute == "test"

    def test_to_rest_invalid_when_output_action_summary_and_file_name_provided(self) -> None:
        with open(TestBatchDeploymentSDK.DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)
        deployment = load_batch_deployment(TestBatchDeploymentSDK.DEPLOYMENT)
        deployment.output_action = "summary_only"
        with pytest.raises(ValidationException) as exc:
            deployment._to_rest_object(location="westus2")
        assert "When output_action is set to summary_only, the output_file_name need not to be specified." == str(
            exc.value
        )

    def test_batch_deployment_instance_count_endpoint_name(self) -> None:
        deployment = load_batch_deployment(
            TestBatchDeploymentSDK.DEPLOYMENT, params_override=[{"endpoint_name": "test"}]
        )
        deployment.resources = None
        deployment.instance_count = 10
        assert deployment.instance_count == 10
        assert deployment.endpoint_name == "test"
        deployment.instance_count = 3
        assert deployment.resources.instance_count == 3

    def test_to_rest_object_when_output_action_not_defined(self) -> None:
        deployment = load_batch_deployment(TestBatchDeploymentSDK.DEPLOYMENT)
        deployment.output_action = None
        # test REST translation s
        rest_deployment_resource = deployment._to_rest_object(location="westus2")
        rest_representation_properties = rest_deployment_resource.properties
        assert rest_deployment_resource.location == "westus2"
        assert rest_deployment_resource.tags == {"tag1": "value1", "tag2": "value2"}
        assert rest_representation_properties.output_action is None
        assert rest_representation_properties.max_concurrency_per_instance == deployment.max_concurrency_per_instance
        assert rest_representation_properties.retry_settings.max_retries == deployment.retry_settings.max_retries
        assert rest_representation_properties.retry_settings.timeout == "PT30S"
        assert rest_representation_properties.error_threshold == deployment.error_threshold
        assert rest_representation_properties.description == deployment.description
        assert rest_representation_properties.output_file_name == "append_row.txt"
        assert rest_representation_properties.output_action is None

    def test_from_rest_object(self) -> None:
        with open(TestBatchDeploymentSDK.DEPLOYMENT_REST, "r") as f:
            deployment_rest = BatchDeploymentData.deserialize(json.load(f))
            deployment_rest.properties.deployment_configuration = BatchPipelineComponentDeploymentConfiguration(
                deployment_configuration_type="PipelineComponent",
                settings={
                    "default_datastore": "workspaceblobstore",
                    "default_compute": "aml-compute",
                    "ComponentDeployment.Settings.continue_on_step_failure": "False",
                },
            )
            deployment = BatchDeployment._from_rest_object(deployment_rest)
            assert isinstance(deployment, BatchDeployment)
            assert deployment.name == deployment_rest.name
            assert deployment.id == deployment_rest.id
            assert deployment.endpoint_name == "achauhan-endpoint-name"
            assert deployment.description == deployment_rest.properties.description
            assert deployment.tags == deployment_rest.tags
            assert deployment.model == deployment_rest.properties.model.asset_id
            assert deployment.environment == deployment_rest.properties.environment_id
            assert deployment.code_configuration.code == deployment_rest.properties.code_configuration.code_id
            assert (
                deployment.code_configuration.scoring_script
                == deployment_rest.properties.code_configuration.scoring_script
            )
            assert deployment.output_file_name == deployment_rest.properties.output_file_name
            assert deployment.output_action == "append_row"
            assert deployment.error_threshold == deployment_rest.properties.error_threshold
            assert deployment.retry_settings.max_retries == deployment_rest.properties.retry_settings.max_retries
            assert deployment.retry_settings.timeout == deployment_rest.properties.retry_settings.timeout.seconds
            assert deployment.logging_level == deployment_rest.properties.logging_level
            assert (
                deployment.properties["AzureAsyncOperationUri"]
                == deployment_rest.properties.properties["AzureAsyncOperationUri"]
            )
            assert (
                deployment.properties["deployment_configuration_type"]
                == deployment_rest.properties.deployment_configuration.deployment_configuration_type
            )
            assert (
                deployment.properties["componentDeployment.Settings.continue_on_step_failure"]
                == deployment_rest.properties.deployment_configuration.settings[
                    "ComponentDeployment.Settings.continue_on_step_failure"
                ]
            )
            assert deployment.creation_context.created_by == deployment_rest.system_data.created_by
            assert deployment.creation_context.created_at == deployment_rest.system_data.created_at
            assert deployment.provisioning_state == deployment_rest.properties.provisioning_state

    def test_deployment_from_rest_object_for_batch_deployment(self) -> None:
        from azure.ai.ml._restclient.v2022_02_01_preview.models import BatchDeploymentData as RestBatchDeploymentData

        with open(TestBatchDeploymentSDK.DEPLOYMENT_REST, "r") as f:
            deployment_rest = RestBatchDeploymentData.deserialize(json.load(f))
            deployment = Deployment._from_rest_object(deployment_rest)
            assert isinstance(deployment, BatchDeployment)
            assert deployment.name == deployment_rest.name
            assert deployment.id == deployment_rest.id
            assert deployment.endpoint_name == "achauhan-endpoint-name"
            assert deployment.description == deployment_rest.properties.description
            assert deployment.tags == deployment_rest.tags
            assert deployment.code_path == deployment_rest.properties.code_configuration.code_id

    def test_batch_deployment_promoted_properties(self) -> None:
        deployment = BatchDeployment(
            name="non-mlflow-deployment",
            description="this is a sample non-mlflow deployment",
            endpoint_name="my-batch-endpoint",
            model="model",
            code_path="tests/test_configs/deployments/model-1/onlinescoring",
            scoring_script="score.py",
            environment="env",
            compute="cpu-cluster",
            instance_count=2,
            max_concurrency_per_instance=2,
            mini_batch_size=10,
            output_action=BatchOutputAction.APPEND_ROW,
            output_file_name="predictions.csv",
            retry_settings=BatchRetrySettings(max_retries=3, timeout=30),
        )
        assert isinstance(deployment.code_configuration, CodeConfiguration)
        assert deployment.code_configuration.scoring_script == "score.py"
        assert deployment.compute == "cpu-cluster"

    def test_batch_deployment_regular_properties(self) -> None:
        deployment = BatchDeployment(
            name="non-mlflow-deployment",
            description="this is a sample non-mlflow deployment",
            endpoint_name="my-batch-endpoint",
            model="model",
            code_configuration=CodeConfiguration(
                code="tests/test_configs/deployments/model-2/onlinescoring", scoring_script="score1.py"
            ),
            environment="env",
            compute="cpu-cluster",
            instance_count=2,
            max_concurrency_per_instance=2,
            mini_batch_size=10,
            output_action=BatchOutputAction.APPEND_ROW,
            output_file_name="predictions.csv",
            retry_settings=BatchRetrySettings(max_retries=3, timeout=30),
        )

        assert isinstance(deployment.code_configuration, CodeConfiguration)
        assert deployment.code_configuration.scoring_script == "score1.py"
        assert deployment.compute == "cpu-cluster"

    def test_batch_deployment_except_promoted_proterties(self) -> None:
        with pytest.raises(Exception):
            BatchDeployment(
                name="non-mlflow-deployment",
                description="this is a sample non-mlflow deployment",
                endpoint_name="my-batch-endpoint",
                model="model",
                code_configuration=CodeConfiguration(
                    code="tests/test_configs/deployments/model-2/onlinescoring", scoring_script="score1.py"
                ),
                code_path="tests/test_configs/deployments/model-1/onlinescoring",
                scoring_script="score2.py",
                environment="env",
                compute="cpu-cluster",
                instance_count=2,
                max_concurrency_per_instance=2,
                mini_batch_size=10,
                output_action=BatchOutputAction.APPEND_ROW,
                output_file_name="predictions.csv",
                retry_settings=BatchRetrySettings(max_retries=3, timeout=30),
            )

    def test_batch_deployment_raise_exception_when(self) -> None:
        with pytest.raises(ValidationException) as exc:
            BatchDeployment(
                name="non-mlflow-deployment", instance_count=2, resources=ResourceConfiguration(instance_count=2)
            )
        assert "Can't set instance_count when resources is provided." == str(exc.value)


@pytest.mark.unittest
class TestOnlineDeploymentSDK:
    def test_k8s_deployment_with_instance_count(self) -> None:
        deployment = KubernetesOnlineDeployment(
            name="test1", scale_settings=TargetUtilizationScaleSettings(), instance_count=2
        )
        with pytest.raises(Exception):
            deployment._validate_scale_settings()

    def test_auto_scale_settings_missing_max(self) -> None:
        deployment = ManagedOnlineDeployment(
            name="test1", scale_settings=TargetUtilizationScaleSettings(min_instances=2)
        )
        with pytest.raises(Exception):
            deployment._validate_scale_settings()

    def test_target_utilization_scale_settings_normal(self) -> None:
        deployment = ManagedOnlineDeployment(name="test1", scale_settings=DefaultScaleSettings())
        deployment._validate_scale_settings()

    def test_code_path_setter(self) -> None:
        deployment = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)
        deployment.code_path = "new_code_id"
        assert deployment.code_path == "new_code_id"
        assert deployment.code_configuration.code == "new_code_id"

    def test_managed_online_deployment_from_rest_object(self) -> None:
        with open("./tests/test_configs/deployments/online/online_deployment_managed_rest.json", "r") as f:
            rest_object = RestOnlineDeploymentData.deserialize(json.load(f))
            blue_deployment = OnlineDeployment._from_rest_object(rest_object)
            assert isinstance(blue_deployment, ManagedOnlineDeployment)
            assert blue_deployment.name == "blue"
            assert blue_deployment.id == rest_object.id
            assert blue_deployment.properties == rest_object.properties.properties
            assert blue_deployment.tags == rest_object.tags
            assert blue_deployment.description == rest_object.properties.description
            assert blue_deployment.environment_variables == rest_object.properties.environment_variables
            assert blue_deployment.properties == rest_object.properties.properties
            assert blue_deployment.model == rest_object.properties.model
            assert blue_deployment.code_configuration.code == rest_object.properties.code_configuration.code_id
            assert (
                blue_deployment.request_settings.request_timeout_ms
                == rest_object.properties.request_settings.request_timeout.seconds * 1000
            )
            assert blue_deployment.environment == rest_object.properties.environment_id
            assert blue_deployment.endpoint_name == "some-endpoint"
            assert blue_deployment.app_insights_enabled == rest_object.properties.app_insights_enabled
            assert blue_deployment.scale_settings.type == rest_object.properties.scale_settings.scale_type.lower()
            assert (
                blue_deployment.liveness_probe.failure_threshold
                == rest_object.properties.liveness_probe.failure_threshold
            )
            assert blue_deployment.instance_type == rest_object.properties.instance_type
            assert blue_deployment.instance_count == rest_object.sku.capacity
            assert blue_deployment.private_network_connection is None
            assert blue_deployment.egress_public_network_access == rest_object.properties.egress_public_network_access
            assert (
                blue_deployment.data_collector.collections["some-collection"].client_id
                == rest_object.properties.data_collector.collections["some-collection"].client_id
            )
            assert blue_deployment.provisioning_state == rest_object.properties.provisioning_state

    def test_kubenets_online_deployment_from_rest_object_(self) -> None:
        with open("./tests/test_configs/deployments/online/online_deployment_kubernetes_rest.json", "r") as f:
            rest_object = RestOnlineDeploymentData.deserialize(json.load(f))
            blue_deployment = OnlineDeployment._from_rest_object(rest_object)
            assert isinstance(blue_deployment, KubernetesOnlineDeployment)
            assert blue_deployment.name == "blue"
            assert blue_deployment.id == rest_object.id
            assert blue_deployment.properties == rest_object.properties.properties
            assert blue_deployment.tags == rest_object.tags
            assert blue_deployment.description == rest_object.properties.description
            assert blue_deployment.environment_variables == rest_object.properties.environment_variables
            assert blue_deployment.properties == rest_object.properties.properties
            assert blue_deployment.model == rest_object.properties.model
            assert (
                blue_deployment.resources.limits.cpu
                == rest_object.properties.container_resource_requirements.container_resource_limits.cpu
            )
            assert (
                blue_deployment.resources.requests.cpu
                == rest_object.properties.container_resource_requirements.container_resource_requests.cpu
            )
            assert blue_deployment.code_configuration.code == rest_object.properties.code_configuration.code_id
            assert (
                blue_deployment.code_configuration.scoring_script
                == rest_object.properties.code_configuration.scoring_script
            )
            assert (
                blue_deployment.request_settings.request_timeout_ms
                == rest_object.properties.request_settings.request_timeout.seconds * 1000
            )
            assert blue_deployment.environment == rest_object.properties.environment_id
            assert blue_deployment.endpoint_name == "some-endpoint"
            assert blue_deployment.app_insights_enabled == rest_object.properties.app_insights_enabled
            assert blue_deployment.scale_settings.type == "target_utilization"
            assert blue_deployment.scale_settings.min_instances == rest_object.properties.scale_settings.min_instances
            assert blue_deployment.scale_settings.max_instances == rest_object.properties.scale_settings.max_instances
            assert (
                blue_deployment.scale_settings.polling_interval
                == rest_object.properties.scale_settings.polling_interval.seconds
            )
            assert (
                blue_deployment.scale_settings.target_utilization_percentage
                == rest_object.properties.scale_settings.target_utilization_percentage
            )
            assert (
                blue_deployment.liveness_probe.success_threshold
                == rest_object.properties.liveness_probe.success_threshold
            )
            assert blue_deployment.instance_type == rest_object.properties.instance_type
            assert blue_deployment.instance_count == rest_object.sku.capacity
            assert (
                blue_deployment.data_collector.collections["some-collection"].client_id
                == rest_object.properties.data_collector.collections["some-collection"].client_id
            )
            assert blue_deployment.provisioning_state == rest_object.properties.provisioning_state

    def test_deployment_from_rest_object_for_online_deployment(self) -> None:
        from azure.ai.ml._restclient.v2022_05_01.models import OnlineDeploymentData as OnlineDeploymentDataRest

        with open("./tests/test_configs/deployments/online/online_deployment_kubernetes_rest.json", "r") as f:
            rest_object = OnlineDeploymentDataRest.deserialize(json.load(f))
            blue_deployment = Deployment._from_rest_object(rest_object)
            assert isinstance(blue_deployment, KubernetesOnlineDeployment)
            assert blue_deployment.name == "blue"
            assert blue_deployment.id == rest_object.id
            assert blue_deployment.instance_type == rest_object.properties.instance_type

    def test_online_deployment_from_rest_object_unsupported_type(self) -> None:
        with open("./tests/test_configs/deployments/online/online_deployment_kubernetes_rest.json", "r") as f:
            rest_object = RestOnlineDeploymentData.deserialize(json.load(f))
            rest_object.properties.endpoint_compute_type = "Other"
            with pytest.raises(DeploymentException) as exc:
                OnlineDeployment._from_rest_object(rest_object)
            assert str(exc.value) == "Unsupported online endpoint type Other."

    def test__deployment_from_rest_object_unsupported_type(self) -> None:
        with open("./tests/test_configs/deployments/online/online_deployment_kubernetes_rest.json", "r") as f:
            rest_object = RestOnlineDeploymentData.deserialize(json.load(f))
            with pytest.raises(DeploymentException) as exc:
                Deployment._from_rest_object(rest_object)
            assert str(exc.value) == f"Unsupported deployment type {type(rest_object)}"

    def test_online_deployment_from_rest_object_unsupported_scale_settings_type(self) -> None:
        with open("./tests/test_configs/deployments/online/online_deployment_kubernetes_rest.json", "r") as f:
            rest_object = RestOnlineDeploymentData.deserialize(json.load(f))
            rest_object.properties.scale_settings.scale_type = "Other"
            with pytest.raises(DeploymentException) as exc:
                OnlineDeployment._from_rest_object(rest_object)
            assert str(exc.value) == "Unsupported online scale setting type Other."


from azure.ai.ml._restclient.v2022_05_01.models import BatchRetrySettings as RestBatchRetrySettings
from azure.ai.ml._restclient.v2022_05_01.models import CodeConfiguration as RestCodeConfiguration
from azure.ai.ml.entities._deployment.data_asset import DataAsset
from azure.ai.ml.entities._deployment.data_collector import DataCollector
from azure.ai.ml.entities._deployment.deployment_collection import DeploymentCollection
from azure.ai.ml.entities._deployment.request_logging import RequestLogging


class TestOnlineDeploymentSettings:
    def test_default_scale_settings_equality(self):
        scale_settings1 = DefaultScaleSettings()
        scale_settings2 = DefaultScaleSettings()
        assert scale_settings1 == scale_settings2

        scale_settings2 = TargetUtilizationScaleSettings()
        assert not scale_settings1 == scale_settings2
        assert not scale_settings1 == None

    def test_target_utilization_scale_settings_equality(self):
        scale_settings1 = TargetUtilizationScaleSettings(
            min_instances=2, max_instances=5, target_utilization_percentage=8, polling_interval=10
        )
        scale_settings2 = TargetUtilizationScaleSettings(
            min_instances=2, max_instances=5, target_utilization_percentage=8, polling_interval=10
        )
        assert scale_settings1 == scale_settings2

        scale_settings2 = TargetUtilizationScaleSettings(
            min_instances=3, max_instances=5, target_utilization_percentage=8, polling_interval=10
        )
        assert not scale_settings1 == scale_settings2

        scale_settings2 = TargetUtilizationScaleSettings(
            min_instances=2, max_instances=6, target_utilization_percentage=8, polling_interval=10
        )
        assert not scale_settings1 == scale_settings2

        scale_settings2 = TargetUtilizationScaleSettings(
            min_instances=2, max_instances=5, target_utilization_percentage=9, polling_interval=10
        )
        assert not scale_settings1 == scale_settings2
        scale_settings2 = TargetUtilizationScaleSettings(
            min_instances=2, max_instances=5, target_utilization_percentage=8, polling_interval=11
        )
        assert not scale_settings1 == scale_settings2
        assert not scale_settings1 == None

        scale_settings2 = DefaultScaleSettings()
        assert not scale_settings1 == scale_settings2

    def test_probe_settings_equality(self):
        probe_settings1 = ProbeSettings(failure_threshold=3, success_threshold=2, timeout=10, period=5, initial_delay=5)
        probe_settings2 = ProbeSettings(failure_threshold=3, success_threshold=2, timeout=10, period=5, initial_delay=5)
        assert probe_settings1 == probe_settings2

        probe_settings2 = ProbeSettings(failure_threshold=4, success_threshold=2, timeout=10, period=5, initial_delay=5)
        assert not probe_settings1 == probe_settings2

        probe_settings2 = ProbeSettings(failure_threshold=3, success_threshold=3, timeout=10, period=5, initial_delay=5)
        assert not probe_settings1 == probe_settings2

        probe_settings2 = ProbeSettings(failure_threshold=3, success_threshold=2, timeout=11, period=5, initial_delay=5)
        assert not probe_settings1 == probe_settings2

        probe_settings2 = ProbeSettings(failure_threshold=3, success_threshold=2, timeout=10, period=6, initial_delay=5)
        assert not probe_settings1 == probe_settings2

        probe_settings2 = ProbeSettings(failure_threshold=3, success_threshold=2, timeout=10, period=5, initial_delay=6)
        assert not probe_settings1 == probe_settings2

        assert not probe_settings1 == None

    def test_online_request_settings_equality(self):
        request_settings1 = OnlineRequestSettings(
            max_concurrent_requests_per_instance=1, max_queue_wait_ms=100, request_timeout_ms=100
        )
        request_settings2 = OnlineRequestSettings(
            max_concurrent_requests_per_instance=1, max_queue_wait_ms=100, request_timeout_ms=100
        )
        assert request_settings1 == request_settings2

        request_settings2 = OnlineRequestSettings(
            max_concurrent_requests_per_instance=2, max_queue_wait_ms=100, request_timeout_ms=100
        )
        assert not request_settings1 == request_settings2

        request_settings2 = OnlineRequestSettings(
            max_concurrent_requests_per_instance=1, max_queue_wait_ms=101, request_timeout_ms=100
        )
        assert not request_settings1 == request_settings2

        request_settings2 = OnlineRequestSettings(
            max_concurrent_requests_per_instance=1, max_queue_wait_ms=100, request_timeout_ms=101
        )
        assert not request_settings1 == request_settings2
        assert not request_settings1 == None
        assert not request_settings1 == DefaultScaleSettings()

    def test_batch_retry_settings_merge_with(self):
        retry_settings1 = BatchRetrySettings(max_retries=3, timeout=30)
        retry_settings2 = BatchRetrySettings(max_retries=4, timeout=40)
        retry_settings1._merge_with(retry_settings2)
        assert retry_settings1.max_retries == retry_settings2.max_retries
        assert retry_settings1.timeout == retry_settings2.timeout

    def test_batch_retry_settings_from_rest_object(self):
        rest_batch_retry_settings = RestBatchRetrySettings(max_retries=3, timeout=30)
        retry_settings = BatchRetrySettings._from_rest_object(rest_batch_retry_settings)
        assert retry_settings.max_retries == rest_batch_retry_settings.max_retries

    def test_batch_retry_settings_to_rest_object(self):
        retry_settings = BatchRetrySettings(max_retries=3, timeout=30)
        rest_batch_retry_settings = retry_settings._to_rest_object()
        assert rest_batch_retry_settings.max_retries == retry_settings.max_retries
        assert rest_batch_retry_settings.timeout == "PT30S"

    def test_resource_settings_equality(self):
        resource_settings1 = ResourceSettings(cpu="1n", memory="2")
        resource_settings2 = ResourceSettings(cpu="1n", memory="2")
        assert resource_settings1 == resource_settings2
        assert not resource_settings1 != resource_settings2

        resource_settings2 = ResourceSettings(cpu="2n", memory="2")
        assert not resource_settings1 == resource_settings2
        assert resource_settings1 != resource_settings2

        resource_settings2 = ResourceSettings(cpu="1n", memory="3")
        assert not resource_settings1 == resource_settings2
        assert resource_settings1 != resource_settings2

        assert not resource_settings1 == None
        assert not resource_settings1 == DefaultScaleSettings()

    def test_resource_requirement_settings_equality(self):
        resource_requirements_settings1 = ResourceRequirementsSettings(
            requests=ResourceSettings(cpu="1n", memory="2"), limits=ResourceSettings(cpu="2n", memory="2")
        )
        resource_requirements_settings2 = ResourceRequirementsSettings(
            requests=ResourceSettings(cpu="1n", memory="2"), limits=ResourceSettings(cpu="2n", memory="2")
        )
        resource_requirements_settings3 = ResourceRequirementsSettings(
            requests=ResourceSettings(cpu="2n", memory="2"), limits=ResourceSettings(cpu="2n", memory="2")
        )
        assert resource_requirements_settings1 == resource_requirements_settings2
        assert not resource_requirements_settings1 == resource_requirements_settings3
        assert not resource_requirements_settings1 == None

    def test_code_configuration_equality(self):
        code_configuration1 = CodeConfiguration(code="some_code", scoring_script="some_script")
        code_configuration2 = CodeConfiguration(code="some_code", scoring_script="some_script")
        assert code_configuration1 == code_configuration2
        code_configuration2 = CodeConfiguration(code="some_code1", scoring_script="some_script")
        assert not code_configuration1 == code_configuration2
        code_configuration2 = CodeConfiguration(code="some_code", scoring_script="some_script1")
        assert not code_configuration1 == code_configuration2
        assert not code_configuration1 == None
        assert not code_configuration1 == DefaultScaleSettings()

    def test_code_configuration_to_rest(self) -> None:
        code_configuration = CodeConfiguration(code="some_code", scoring_script="some_script")
        rest_code_configuration = code_configuration._to_rest_code_configuration()
        assert rest_code_configuration.code_id == code_configuration.code
        assert rest_code_configuration.scoring_script == code_configuration.scoring_script

    def test_from_rest_code_configuration(self):
        rest_code_configuration = RestCodeConfiguration(code_id="some_code", scoring_script="some_script")
        code_configuration = CodeConfiguration._from_rest_code_configuration(rest_code_configuration)
        assert code_configuration.code == rest_code_configuration.code_id
        assert code_configuration.scoring_script == rest_code_configuration.scoring_script

    def test_data_collector_to_dict(self):
        data_collector = DataCollector(
            rolling_rate="Hour",
            sampling_rate=1.2,
            collections={
                "model_inputs": DeploymentCollection(
                    enabled="true",
                    client_id="some_id",
                    data=DataAsset(data_id="data_id", name="some_name", path="some_path", version=1),
                )
            },
            request_logging=RequestLogging(capture_headers=["header1", "header2"]),
        )
        data_collector_dict = data_collector._to_dict()
        assert data_collector_dict["rolling_rate"] == data_collector.rolling_rate.lower()
        assert data_collector_dict["sampling_rate"] == data_collector.sampling_rate
        assert (
            data_collector_dict["collections"]["model_inputs"]["enabled"]
            == data_collector.collections["model_inputs"].enabled
        )
        assert (
            data_collector_dict["collections"]["model_inputs"]["client_id"]
            == data_collector.collections["model_inputs"].client_id
        )
        assert (
            data_collector_dict["collections"]["model_inputs"]["data"]["data_id"]
            == data_collector.collections["model_inputs"].data.data_id
        )
        assert (
            data_collector_dict["collections"]["model_inputs"]["data"]["name"]
            == data_collector.collections["model_inputs"].data.name
        )
        assert (
            data_collector_dict["collections"]["model_inputs"]["data"]["path"]
            == data_collector.collections["model_inputs"].data.path
        )
        assert data_collector_dict["collections"]["model_inputs"]["data"]["version"] == str(
            data_collector.collections["model_inputs"].data.version
        )
        assert (
            data_collector_dict["request_logging"]["capture_headers"] == data_collector.request_logging.capture_headers
        )

    def test_data_asset_to_dict(self):
        data_asset = DataAsset(data_id="data_id", name="some_name", path="some_path", version=1)
        data_asset_dict = data_asset._to_dict()
        assert data_asset_dict["data_id"] == data_asset.data_id
        assert data_asset_dict["name"] == data_asset.name
        assert data_asset_dict["path"] == data_asset.path
        assert data_asset_dict["version"] == str(data_asset.version)

    def test_deployment_collection_to_dict(self):
        deployment_collection = DeploymentCollection(
            enabled="true",
            client_id="some_id",
            data=DataAsset(data_id="data_id", name="some_name", path="some_path", version=1),
        )
        deployment_collection_dict = deployment_collection._to_dict()
        assert deployment_collection_dict["enabled"] == deployment_collection.enabled
        assert deployment_collection_dict["client_id"] == deployment_collection.client_id
        assert deployment_collection_dict["data"]["data_id"] == deployment_collection.data.data_id
        assert deployment_collection_dict["data"]["name"] == deployment_collection.data.name
        assert deployment_collection_dict["data"]["path"] == deployment_collection.data.path
        assert deployment_collection_dict["data"]["version"] == str(deployment_collection.data.version)

    def test_request_logging_to_dict(self):
        request_logging = RequestLogging(capture_headers=["header1", "header2"])
        request_logging_dict = request_logging._to_dict()
        assert request_logging_dict["capture_headers"] == request_logging.capture_headers

    def test_data_asset_to_dict(self):
        data_asset = DataAsset(data_id="data_id", name="some_name", path="some_path", version=1)
        data_asset_dict = data_asset._to_dict()
        assert data_asset_dict["data_id"] == data_asset.data_id
        assert data_asset_dict["name"] == data_asset.name
        assert data_asset_dict["path"] == data_asset.path
        assert data_asset_dict["version"] == str(data_asset.version)

    def test_request_logging_from_rest_object(self):
        rest_request_logging = RequestLogging(capture_headers=["header1", "header2"])
        request_logging = RequestLogging._from_rest_object(rest_request_logging)
        assert request_logging.capture_headers == rest_request_logging.capture_headers

    def test_ru_settings_to_dict(self):
        run_settings = RunSettings(
            name="some-name",
            display_name="some-display-name",
            experiment_name="some-experiment-name",
            description="some-description",
            tags={"tag1": "value1"},
            settings={"setting1": "value1"},
        )
        run_settings_dict = run_settings._to_dict()
        assert run_settings_dict["name"] == run_settings.name
        assert run_settings_dict["display_name"] == run_settings.display_name
        assert run_settings_dict["experiment_name"] == run_settings.experiment_name
        assert run_settings_dict["description"] == run_settings.description
        assert run_settings_dict["tags"] == run_settings.tags
        assert run_settings_dict["settings"] == run_settings.settings
