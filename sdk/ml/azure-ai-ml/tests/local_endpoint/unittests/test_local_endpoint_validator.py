# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from pathlib import Path

import pytest
from mock import Mock

from azure.ai.ml._local_endpoints.validators.code_validator import get_code_configuration_artifacts
from azure.ai.ml._local_endpoints.validators.environment_validator import get_environment_artifacts
from azure.ai.ml._local_endpoints.validators.model_validator import get_model_artifacts
from azure.ai.ml.entities import CodeConfiguration, ManagedOnlineDeployment
from azure.ai.ml.entities._assets import Code, Model
from azure.ai.ml.entities._assets.environment import BuildContext, Environment
from azure.ai.ml.exceptions import CloudArtifactsNotSupportedError, RequiredLocalArtifactsNotFoundError


@pytest.fixture
def code_operations():
    return Mock()


@pytest.fixture
def deployment_yaml_base_path():
    return Path(Path(__file__).parent.absolute(), "../../test_configs/deployments/online/")


@pytest.mark.skip(reason="TODO[BUG 1260290] Deployment should not be instantiated")
@pytest.mark.unittest
class TestLocalEndpointEnvironmentValidation:
    def test_environment_contains_cloud_artifacts_fails(self):
        environment = "azureml:."
        deployment = ManagedOnlineDeployment(name="deployment", environment=environment)
        with pytest.raises(RequiredLocalArtifactsNotFoundError):
            get_local_environment_artifacts(endpoint_name="test-endpoint", deployment=deployment)

    def test_environment_is_none_fails(self):
        deployment = ManagedOnlineDeployment(
            name="deployment",
        )
        with pytest.raises(RequiredLocalArtifactsNotFoundError):
            get_local_environment_artifacts(endpoint_name="test-endpoint", deployment=deployment)

    def test_environment_does_not_contain_local_docker_fails(self):
        environment = Environment()
        deployment = ManagedOnlineDeployment(name="deployment", environment=environment)
        with pytest.raises(RequiredLocalArtifactsNotFoundError):
            get_local_environment_artifacts(endpoint_name="test-endpoint", deployment=deployment)

    def test_environment_contains_base_image_succeeds(self):
        environment = Environment(docker_image="ubuntu:latest")
        deployment = ManagedOnlineDeployment(name="deployment", environment=environment)
        (base_image, dockerfile) = get_local_environment_artifacts(endpoint_name="test-endpoint", deployment=deployment)
        assert "ubuntu:latest" == base_image
        assert dockerfile is None

    def test_environment_contains_dockerfile_succeeds(self):
        environment = Environment(dockerfile=BuildContext(dockerfile="file:./Dockerfile"))
        deployment = ManagedOnlineDeployment(
            name="deployment",
            environment=environment,
        )
        (base_image, dockerfile) = get_local_environment_artifacts(endpoint_name="test-endpoint", deployment=deployment)
        assert base_image is None
        assert "file:./Dockerfile" == dockerfile


@pytest.mark.unittest
class TestLocalEndpointCodeConfigurationValidation:
    def test_code_configuration_does_not_contain_local_path_fails(
        self,
        code_operations,
        deployment_yaml_base_path,
    ):
        code_configuration = CodeConfiguration()
        deployment = ManagedOnlineDeployment(
            name="deployment",
            code_configuration=code_configuration,
            base_path=deployment_yaml_base_path,
        )
        with pytest.raises(RequiredLocalArtifactsNotFoundError):
            get_code_configuration_artifacts(
                endpoint_name="test-endpoint",
                deployment=deployment,
                code_operations=code_operations,
                download_path="",
            )
            assert "path" in e

    def test_code_configuration_is_none_succeeds_for_byoc(
        self,
        code_operations,
        deployment_yaml_base_path,
    ):
        deployment = ManagedOnlineDeployment(
            name="deployment",
            base_path=deployment_yaml_base_path,
        )
        code_directory_path = get_code_configuration_artifacts(
            endpoint_name="test-endpoint",
            deployment=deployment,
            code_operations=code_operations,
            download_path="",
        )
        assert code_directory_path is None

    def test_code_configuration_does_not_contain_scoring_script_fails(
        self,
        code_operations,
        deployment_yaml_base_path,
    ):
        code_configuration = CodeConfiguration(code="../onlinescoring/")
        deployment = ManagedOnlineDeployment(
            name="deployment",
            code_configuration=code_configuration,
            base_path=deployment_yaml_base_path,
        )
        with pytest.raises(RequiredLocalArtifactsNotFoundError) as e:
            get_code_configuration_artifacts(
                endpoint_name="test-endpoint",
                deployment=deployment,
                code_operations=code_operations,
                download_path="",
            )
            assert "scoring_script" in e

    def test_code_configuration_local_path_does_not_exist_failes(self, code_operations, deployment_yaml_base_path):
        code_configuration = CodeConfiguration(code="../model-1/foo/", scoring_script="score.py")
        deployment = ManagedOnlineDeployment(
            name="deployment",
            code_configuration=code_configuration,
            base_path=deployment_yaml_base_path,
        )
        with pytest.raises(RequiredLocalArtifactsNotFoundError) as e:
            get_code_configuration_artifacts(
                endpoint_name="test-endpoint",
                deployment=deployment,
                code_operations=code_operations,
                download_path="",
            )
            assert "code_configuration" in e

    def test_code_configuration_succeeds(self, code_operations, deployment_yaml_base_path):
        code_configuration = CodeConfiguration(code="../model-1/onlinescoring/", scoring_script="score.py")
        deployment = ManagedOnlineDeployment(
            name="deployment",
            code_configuration=code_configuration,
            base_path=deployment_yaml_base_path,
        )
        code_dir = get_code_configuration_artifacts(
            endpoint_name="test-endpoint",
            deployment=deployment,
            code_operations=code_operations,
            download_path="",
        )
        assert "onlinescoring" in str(code_dir)


@pytest.mark.skip(reason="TODO[BUG 1260290] Deployment should not be instantiated")
@pytest.mark.unittest
class TestLocalEndpointModelValidation:
    def test_model_contains_cloud_artifacts_id_fails(self):
        model = Model(id="azureml:.")
        deployment = ManagedOnlineDeployment(
            name="deployment",
            model=model,
        )
        with pytest.raises(RequiredLocalArtifactsNotFoundError):
            get_local_model_artifacts(endpoint_name="test-endpoint", deployment=deployment)

    def test_model_contains_cloud_artifacts_datastore_fails(self):
        model = Model(datastore="azureml:.")
        deployment = ManagedOnlineDeployment(
            name="deployment",
            model=model,
        )
        with pytest.raises(RequiredLocalArtifactsNotFoundError):
            get_local_model_artifacts(endpoint_name="test-endpoint", deployment=deployment)

    def test_model_contains_local_path_and_cloud_artifacts_id_fails(self):
        model = Model(
            id="azureml:.",
            path="../onlinescoring/sklearn_regression_model.pkl",
        )
        deployment = ManagedOnlineDeployment(
            name="deployment",
            model=model,
        )
        with pytest.raises(CloudArtifactsNotSupportedError):
            get_local_model_artifacts(endpoint_name="test-endpoint", deployment=deployment)

    def test_model_contains_local_path_and_cloud_artifacts_datastore_fails(self):
        model = Model(
            datastore="azureml:.",
            path="../onlinescoring/sklearn_regression_model.pkl",
        )
        deployment = ManagedOnlineDeployment(
            name="deployment",
            model=model,
        )
        with pytest.raises(CloudArtifactsNotSupportedError):
            get_local_model_artifacts(endpoint_name="test-endpoint", deployment=deployment)

    def test_model_does_not_contain_local_path_fails(self):
        model = Model()
        deployment = ManagedOnlineDeployment(
            name="deployment",
            model=model,
        )
        with pytest.raises(RequiredLocalArtifactsNotFoundError):
            get_local_model_artifacts(endpoint_name="test-endpoint", deployment=deployment)
            assert "local_path" in e

    def test_model_is_none_fails(self):
        deployment = ManagedOnlineDeployment(
            name="deployment",
        )
        with pytest.raises(RequiredLocalArtifactsNotFoundError) as e:
            get_local_model_artifacts(endpoint_name="test-endpoint", deployment=deployment)
            assert "model" in e

    def test_model_succeeds(self):
        model = Model(local_path="../onlinescoring/sklearn_regression_model.pkl")
        deployment = ManagedOnlineDeployment(
            name="deployment",
            model=model,
        )
        model_path = get_local_model_artifacts(endpoint_name="test-endpoint", deployment=deployment)
        assert str(Path("onlinescoring", "sklearn_regression_model.pkl")) in str(model_path)
