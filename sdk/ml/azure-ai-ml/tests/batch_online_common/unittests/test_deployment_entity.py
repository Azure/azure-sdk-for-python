import copy

import pytest
import yaml
import json
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_batch_deployment, load_online_deployment
from azure.ai.ml._restclient.v2022_10_01.models import BatchOutputAction, EndpointComputeType
from azure.ai.ml._restclient.v2023_04_01_preview.models import OnlineDeployment as RestOnlineDeploymentData
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities import (
    BatchDeployment,
    CodeConfiguration,
    DefaultScaleSettings,
    KubernetesOnlineDeployment,
    ManagedOnlineDeployment,
    OnlineDeployment,
    OnlineEndpoint,
    ProbeSettings,
    ResourceRequirementsSettings,
    ResourceSettings,
    TargetUtilizationScaleSettings,
)
from azure.ai.ml.constants._common import ArmConstants
from azure.ai.ml.exceptions import DeploymentException
from azure.ai.ml.entities._assets import Environment, Model, Code
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration


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
    BLUE_K8S_ONLINE_DEPLOYMENT = "tests/test_configs/deployments/online/online_deployment_blue_k8s.yaml"
    MINIMAL_DEPLOYMENT = "tests/test_configs/deployments/online/online_endpoint_deployment_k8s_minimum.yml"
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
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)
        blue_copy = copy.deepcopy(blue)

        blue_copy.code_configuration = CodeConfiguration(code="blah path", scoring_script="blah.py")
        blue_copy.model = Model(name="blah code")
        blue_copy.environment = Environment(name="blah model")
        blue_copy.endpoint_name = "blah endpoint"

        blue._merge_with(blue_copy)

        assert blue.model.name == blue_copy.model.name
        assert blue.environment.name == blue_copy.environment.name
        assert blue.code_configuration.code == blue_copy.code_configuration.code
        assert blue.code_configuration.scoring_script == blue_copy.code_configuration.scoring_script
        assert blue.endpoint_name == blue_copy.endpoint_name

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
        with open(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT, 'r') as f:
            blue = yaml.safe_load(f)
            blue["scale_settings"] = {"type":"default", "min_instances": 1, "max_instances": 2, "polling_interval": 3, "target_utilization_percentage": 4}

            class OnlineDeploymentDict(dict):
                def __init__(self, *args, **kwargs):
                    super(OnlineDeploymentDict, self).__init__(*args, **kwargs)
                    self.scale_settings = "default"

            blue = OnlineDeploymentDict(blue)
            OnlineDeployment._set_scale_settings(blue)
            assert len(blue["scale_settings"]) == 1
            assert blue["scale_settings"]["type"] == "default"

    def test_kubenetes_deployment_to_dict(self) -> None:
         with open(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT, 'r') as f:
            minimal_deployment = yaml.safe_load(f)
            online_deployment_dict = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)._to_dict()
            assert online_deployment_dict["name"]== minimal_deployment["name"]
            assert online_deployment_dict['endpoint_name']== minimal_deployment['endpoint_name']
            assert online_deployment_dict['model']['name']== minimal_deployment['model']['name']
            assert online_deployment_dict['type']== 'kubernetes'

    def test_managed_deployment_to_dict(self) -> None:
         with open(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT, 'r') as f:
            minimal_deployment = yaml.safe_load(f)
            online_deployment_dict = load_online_deployment(TestOnlineDeploymentFromYAML.MINIMAL_DEPLOYMENT)._to_dict()
            assert online_deployment_dict["name"]== minimal_deployment["name"]
            assert online_deployment_dict['endpoint_name']== minimal_deployment['endpoint_name']
            assert online_deployment_dict['model']['name']== minimal_deployment['model']['name']
            assert online_deployment_dict['type']== 'managed'


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
        assert arm_resource[2][0]["type"] == 'Microsoft.MachineLearningServices/workspaces/models/versions'
        assert arm_resource[2][1]["model_version"]["name"] == blue.model.name
    
    
    def test_get_arm_resource_and_params_for_kubenets_deployment(self) -> None:
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.BLUE_ONLINE_DEPLOYMENT)
        arm_resource = blue._get_arm_resource_and_params(location="westus2")
        
        assert arm_resource[0][0][ArmConstants.DEPENDSON_PARAMETER_NAME][0] == f"{blue.environment._arm_type}Deployment"
        assert arm_resource[0][0][ArmConstants.DEPENDSON_PARAMETER_NAME][1] == f"{blue.model._arm_type}Deployment"
        assert arm_resource[0][1]["online_deployment"]["name"] == blue.name
        assert arm_resource[1][0]["type"] == "Microsoft.MachineLearningServices/workspaces/environments/versions"
        assert arm_resource[1][1]["environment_version"]["name"] == blue.environment.name
        assert arm_resource[2][0]["type"] == 'Microsoft.MachineLearningServices/workspaces/models/versions'
        assert arm_resource[2][1]["model_version"]["name"] == blue.model.name

    def test_preview_mir_deployment(self) -> None:
        with open(TestOnlineDeploymentFromYAML.PREVIEW_DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)
        blue = load_online_deployment(TestOnlineDeploymentFromYAML.PREVIEW_DEPLOYMENT)
        assert isinstance(blue, OnlineDeployment)
        for key, value in target.items():
            if isinstance(value, str):
                assert getattr(blue, key) == value


@pytest.mark.unittest
class TestBatchDeploymentSDK:
    DEPLOYMENT = "tests/test_configs/deployments/batch/batch_deployment_mlflow.yaml"

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

    def test_batch_endpoint_deployment_to_rest_object(self) -> None:
        with open(TestBatchDeploymentSDK.DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)
        print(target)
        deployment = load_batch_deployment(TestBatchDeploymentSDK.DEPLOYMENT)
        # test REST translation
        deployment_resource = deployment._to_rest_object(location="westus2")
        rest_representation_properties = deployment_resource.properties
        assert rest_representation_properties.max_concurrency_per_instance == target["max_concurrency_per_instance"]
        assert rest_representation_properties.retry_settings.max_retries == target["retry_settings"]["max_retries"]
        assert rest_representation_properties.retry_settings.timeout == "PT30S"
        assert rest_representation_properties.error_threshold == target["error_threshold"]
        assert rest_representation_properties.output_action == BatchOutputAction.APPEND_ROW
        assert rest_representation_properties.description == target["description"]

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
            assert blue_deployment.request_settings.request_timeout_ms == rest_object.properties.request_settings.request_timeout.seconds * 1000
            assert blue_deployment.environment == rest_object.properties.environment_id
            assert blue_deployment.endpoint_name == "some-endpoint"
            assert blue_deployment.app_insights_enabled == rest_object.properties.app_insights_enabled
            assert blue_deployment.scale_settings.type == rest_object.properties.scale_settings.scale_type.lower()
            assert blue_deployment.liveness_probe.failure_threshold == rest_object.properties.liveness_probe.failure_threshold
            assert blue_deployment.instance_type == rest_object.properties.instance_type
            assert blue_deployment.instance_count == rest_object.sku.capacity
            assert blue_deployment.private_network_connection is None
            assert blue_deployment.egress_public_network_access == rest_object.properties.egress_public_network_access
            assert blue_deployment.data_collector.collections["some-collection"].client_id == rest_object.properties.data_collector.collections["some-collection"].client_id
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
            assert blue_deployment.resources.limits.cpu == rest_object.properties.container_resource_requirements.container_resource_limits.cpu
            assert blue_deployment.resources.requests.cpu == rest_object.properties.container_resource_requirements.container_resource_requests.cpu
            assert blue_deployment.code_configuration.code == rest_object.properties.code_configuration.code_id
            assert blue_deployment.code_configuration.scoring_script == rest_object.properties.code_configuration.scoring_script
            assert blue_deployment.request_settings.request_timeout_ms == rest_object.properties.request_settings.request_timeout.seconds * 1000
            assert blue_deployment.environment == rest_object.properties.environment_id
            assert blue_deployment.endpoint_name == "some-endpoint"
            assert blue_deployment.app_insights_enabled == rest_object.properties.app_insights_enabled
            assert blue_deployment.scale_settings.type == "target_utilization"
            assert blue_deployment.scale_settings.min_instances == rest_object.properties.scale_settings.min_instances
            assert blue_deployment.scale_settings.max_instances == rest_object.properties.scale_settings.max_instances
            assert blue_deployment.scale_settings.polling_interval == rest_object.properties.scale_settings.polling_interval.seconds
            assert blue_deployment.scale_settings.target_utilization_percentage == rest_object.properties.scale_settings.target_utilization_percentage
            assert blue_deployment.liveness_probe.success_threshold == rest_object.properties.liveness_probe.success_threshold
            assert blue_deployment.instance_type == rest_object.properties.instance_type
            assert blue_deployment.instance_count == rest_object.sku.capacity
            assert blue_deployment.data_collector.collections["some-collection"].client_id == rest_object.properties.data_collector.collections["some-collection"].client_id
            assert blue_deployment.provisioning_state == rest_object.properties.provisioning_state

    def test_online_deployment_from_rest_object_unsupported_type(self) -> None:
                with open("./tests/test_configs/deployments/online/online_deployment_kubernetes_rest.json", "r") as f:
                    rest_object = RestOnlineDeploymentData.deserialize(json.load(f))
                    rest_object.properties.endpoint_compute_type = "Other"
                    with pytest.raises(DeploymentException) as exc:
                        OnlineDeployment._from_rest_object(rest_object)
                    assert str(exc.value) == "Unsupported online endpoint type Other."

