from azure.ai.ml.constants import BATCH_ENDPOINT_TYPE, ONLINE_ENDPOINT_TYPE, BatchDeploymentOutputAction
from azure.ai.ml.entities import (
    CodeConfiguration,
    OnlineEndpoint,
    OnlineDeployment,
    BatchDeployment,
    KubernetesOnlineDeployment,
    ManagedOnlineDeployment,
    DefaultScaleSettings,
    TargetUtilizationScaleSettings,
    ProbeSettings,
    ResourceRequirementsSettings,
    ResourceSettings,
)
from azure.ai.ml.entities._assets import Model, Environment
from azure.ai.ml._restclient.v2021_10_01.models import EndpointComputeType, BatchOutputAction
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml import load_online_deployment, load_batch_deployment
import copy
import yaml
import pytest


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
        assert blue.type == EndpointComputeType.MANAGED
        assert blue.endpoint_name == target["endpoint_name"]
        assert "blue" in blue.name
        assert isinstance(blue.model, Model)
        assert isinstance(blue.environment, Environment)
        assert isinstance(blue.code_configuration, CodeConfiguration)
        assert isinstance(blue.liveness_probe, ProbeSettings)
        assert isinstance(blue.readiness_probe, ProbeSettings)
        assert blue.model.name == target["model"]["name"]
        assert blue.instance_type == "cpuInstance"
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
        blue = KubernetesOnlineDeployment.load(TestOnlineDeploymentFromYAML.BLUE_K8S_ONLINE_DEPLOYMENT)
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

    def test_batch_endpoint_deployment_load(self) -> None:
        with open(TestBatchDeploymentSDK.DEPLOYMENT, "r") as f:
            target = yaml.safe_load(f)
        deployment = load_batch_deployment(TestBatchDeploymentSDK.DEPLOYMENT)
        assert isinstance(deployment, BatchDeployment)
        assert isinstance(deployment.model, str)
        assert isinstance(deployment.compute, str)
        assert isinstance(deployment.resources, ResourceConfiguration)
        assert deployment.model == "lightgbm_predict:1"
        assert deployment.output_action == BatchDeploymentOutputAction.APPEND_ROW
        assert deployment.max_concurrency_per_instance == target["max_concurrency_per_instance"]
        assert deployment.retry_settings.max_retries == target["retry_settings"]["max_retries"]
        assert deployment.retry_settings.timeout == target["retry_settings"]["timeout"]
        assert deployment.description == target["description"]

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
            compute="batch-cluster",
            instance_count=2,
            max_concurrency_per_instance=2,
            mini_batch_size=10,
            output_action=BatchOutputAction.APPEND_ROW,
            output_file_name="predictions.csv",
            retry_settings=BatchRetrySettings(max_retries=3, timeout=30),
        )

        assert isinstance(deployment.code_configuration, CodeConfiguration)
        assert deployment.code_configuration.scoring_script == "score.py"
        assert deployment.compute == "batch-cluster"

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
            compute="batch-cluster",
            instance_count=2,
            max_concurrency_per_instance=2,
            mini_batch_size=10,
            output_action=BatchOutputAction.APPEND_ROW,
            output_file_name="predictions.csv",
            retry_settings=BatchRetrySettings(max_retries=3, timeout=30),
        )

        assert isinstance(deployment.code_configuration, CodeConfiguration)
        assert deployment.code_configuration.scoring_script == "score1.py"
        assert deployment.compute == "batch-cluster"

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
                compute="batch-cluster",
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
