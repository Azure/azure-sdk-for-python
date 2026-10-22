from pathlib import Path
from unittest.mock import patch

import pydash
import pytest
import yaml
from _pytest.logging import LogCaptureFixture
from marshmallow.exceptions import ValidationError
from test_utilities.constants import Test_Resource_Group, Test_Subscription, Test_Workspace_Name

from azure.ai.ml import load_batch_deployment, load_environment
from azure.ai.ml._schema import AnonymousEnvironmentSchema, EnvironmentSchema
from azure.ai.ml._utils._arm_id_utils import PROVIDER_RESOURCE_ID_WITH_VERSION
from azure.ai.ml._utils.utils import is_valid_uuid
from azure.ai.ml.constants._common import ANONYMOUS_ENV_NAME, BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._deployment.batch_deployment import BatchDeployment


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestEnvironmentSchema:
    def test_yaml_load(self) -> None:
        path = Path("./tests/test_configs/environment/environment_conda.yml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)

        dummy_environment_name = "MyDummyEnvName"
        context = {BASE_PATH_CONTEXT_KEY: path.parent, PARAMS_OVERRIDE_KEY: [{"name": dummy_environment_name}]}
        schema = EnvironmentSchema(context=context)
        environment = schema.load(target)

        assert environment.version == "1"
        assert dummy_environment_name == environment.name

        assert "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04" == environment.image

        assert environment.conda_file["name"] == "example-environment"
        assert not environment._is_anonymous

    @patch("azure.ai.ml._schema.assets.environment.module_logger")
    def test_yaml_load_anonymous(self, mock_module_logger) -> None:
        path = Path("./tests/test_configs/environment/environment_conda.yml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)

        dummy_environment_name = "MyDummyEnvName"
        context = {BASE_PATH_CONTEXT_KEY: path.parent, PARAMS_OVERRIDE_KEY: [{"name": dummy_environment_name}]}
        schema = AnonymousEnvironmentSchema(context=context)
        environment = schema.load(target)
        mock_module_logger.warning.assert_called_with(
            "Warning: the provided asset name '%s' will not be used for anonymous registration", dummy_environment_name
        )

        assert environment._is_anonymous

        assert "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04" == environment.image
        assert environment.conda_file["name"] == "example-environment"

    @patch("builtins.print")
    def test_yaml_load_anonymous_bad(self, mock_print) -> None:
        path = Path("./tests/test_configs/environment/environment_conda_bad.yml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)

        dummy_environment_name = "MyDummyEnvName"
        context = {BASE_PATH_CONTEXT_KEY: path.parent, PARAMS_OVERRIDE_KEY: [{"name": dummy_environment_name}]}
        schema = AnonymousEnvironmentSchema(context=context)
        with pytest.raises(ValidationError):
            schema.load(target)

    def test_deserialize(self) -> None:
        path = Path("./tests/test_configs/environment/environment_conda.yml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)

        context = {BASE_PATH_CONTEXT_KEY: path.parent}
        schema = EnvironmentSchema(context=context)
        environment = schema.load(target)

        rest_environment = environment._to_rest_object()
        rest_environment.id = PROVIDER_RESOURCE_ID_WITH_VERSION.format(
            Test_Subscription,
            Test_Resource_Group,
            Test_Workspace_Name,
            "environments",
            environment.name,
            environment._version,
        )

        environment_deserialized = Environment._from_rest_object(rest_environment)

        # Original environment yaml won't have the id
        env_dict = pydash.omit(dict(environment_deserialized._to_dict()), "id")

        expected_env_dict = environment._to_dict()
        assert env_dict == expected_env_dict

    def test_yaml_with_inference_config(self) -> None:
        yml_path = "./tests/test_configs/environment/environment_docker_inference.yml"
        environment = load_environment(yml_path)

        assert "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04" == environment.image
        assert environment.conda_file["name"] == "example-environment"

        assert 5001 == environment.inference_config.scoring_route.port
        assert 5002 == environment.inference_config.liveness_route.port
        assert 5003 == environment.inference_config.readiness_route.port

        assert "/predict" == environment.inference_config.scoring_route.path
        assert "/health/live" == environment.inference_config.liveness_route.path
        assert "/health/ready" == environment.inference_config.readiness_route.path

        assert "linux" == environment.os_type

        rest_environment = environment._to_rest_object()
        rest_environment.id = PROVIDER_RESOURCE_ID_WITH_VERSION.format(
            Test_Subscription,
            Test_Resource_Group,
            Test_Workspace_Name,
            "environments",
            environment.name,
            environment._version,
        )
        environment_deserialized = Environment._from_rest_object(rest_environment)

        # Original environment yaml won't have the id
        env_dict = pydash.omit(dict(environment_deserialized._to_dict()), "id")

        # Path is used to update the context path, not related to the rest object
        expected_env_dict = pydash.omit(dict(environment._to_dict()), "path")

        assert env_dict == expected_env_dict

    def test_yaml_load_error(self) -> None:
        path = Path("./tests/test_configs/environment/environment_conda.yml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            target["name"] = None

        context = {BASE_PATH_CONTEXT_KEY: path.parent}
        schema = EnvironmentSchema(context=context)
        with pytest.raises(ValidationError):
            _ = schema.load(target)

    def test_docker_context(self) -> None:
        path = Path("./tests/test_configs/environment/environment_docker_context.yml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)

        dummy_environment_name = "MyDummyEnvName"
        context = {BASE_PATH_CONTEXT_KEY: path.parent, PARAMS_OVERRIDE_KEY: [{"name": dummy_environment_name}]}
        schema = EnvironmentSchema(context=context)
        environment = schema.load(target)

        assert environment.version == "1"
        assert dummy_environment_name == environment.name
        assert environment.image is None
        assert not environment._is_anonymous

        # docker build context
        assert environment.build
        assert environment.build.path == "./environment_files"
        assert environment.build.dockerfile_path == "DockerfileNonDefault"

    def test_yaml_load_no_version(self) -> None:
        path = Path("./tests/test_configs/environment/environment_no_version.yml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)

        context = {BASE_PATH_CONTEXT_KEY: path.parent}
        schema = EnvironmentSchema(context=context)
        environment = schema.load(target)

        assert environment.version is None
        assert environment._auto_increment_version

    def test_environment_anonymous_name_version(
        self,
    ) -> None:
        batch_deployment1 = load_batch_deployment(
            "tests/test_configs/deployments/batch/batch_deployment_anon_env_with_docker.yaml"
        )
        batch_deployment2 = load_batch_deployment(
            "tests/test_configs/deployments/batch/batch_deployment_anon_env_with_docker.yaml"
        )
        # flaky assertion
        # assert batch_deployment1.environment.version == "880440cb2c75af4b1344125dcd3b2d62"
        assert batch_deployment1.environment.name == ANONYMOUS_ENV_NAME
        assert batch_deployment1.environment.version == batch_deployment2.environment.version
        assert batch_deployment1.environment.name == batch_deployment2.environment.name
