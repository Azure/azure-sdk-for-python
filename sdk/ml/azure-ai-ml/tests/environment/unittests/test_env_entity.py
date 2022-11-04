from pathlib import Path

import pytest
import json
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_component, load_environment
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants._common import ANONYMOUS_ENV_NAME
from azure.ai.ml.entities import Component as ComponentEntity
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._assets.environment import BuildContext


@pytest.mark.unittest
@pytest.mark.production_experience_test
class TestEnvironmentEntity:
    def test_eq_neq(self) -> None:
        environment = Environment(name="name", version="16", image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04")
        same_environment = Environment(name=environment.name, version=environment.version, image=environment.image)
        diff_environment = Environment(
            name=environment.name,
            version=environment.version,
            image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.05",
        )

        assert environment.image == same_environment.image
        assert environment == same_environment
        assert environment != diff_environment

    def test_conda_file_deserialize_and_serialize(self) -> None:
        # Tests that conda file is deserialized same way if using load_environment() or Environment()
        conda_file_path = "tests/test_configs/environment/environment_files/environment.yml"
        env_config_path = "tests/test_configs/environment/environment_conda_name_version.yml"

        conda_file_data = load_yaml(conda_file_path)
        env = Environment(conda_file=conda_file_path)

        def simple_environment_validation(env_loaded):
            assert env.conda_file == conda_file_data
            assert env_loaded.conda_file == conda_file_data

        verify_entity_load_and_dump(load_environment, simple_environment_validation, env_config_path)

    def test_build_context_eq_neq(self) -> None:
        build_context = BuildContext(dockerfile_path="dockerfile_path", path="context_uri")

        same_build_context = BuildContext(
            path=build_context.path,
            dockerfile_path=build_context.dockerfile_path,
        )

        diff_build_context = BuildContext(
            dockerfile_path=build_context.dockerfile_path,
            path=build_context.path + "blah",
        )

        assert build_context == same_build_context
        assert build_context != diff_build_context

    def test_anonymous_environment_loaded_from_yaml(self):
        tests_root_dir = Path(__file__).parent.parent.parent
        components_dir = tests_root_dir / "test_configs/components/helloworld_components_with_env"

        env_0 = load_component(source=components_dir / "helloworld_component_env_inline.yml").environment
        env_1 = load_component(source=components_dir / "helloworld_component_env_path_0.yml").environment
        env_2 = load_component(source=components_dir / "helloworld_component_env_path_1.yml").environment

        assert env_0.name == env_1.name == env_2.name == ANONYMOUS_ENV_NAME
        assert env_0.version == env_1.version == env_2.version
        assert env_0 == env_1 == env_2

    def test_anonymous_environment_version_changes_with_inference_config(self):
        tests_root_dir = Path(__file__).parent.parent.parent
        inference_conf = """{"scoring_route":
                            {"port": "5001",
                            "path": "/predict"},
                        "liveness_route":
                            {"port": "5002",
                            "path": "/health/live"},
                        "readiness_route":
                            {"port": "5003",
                            "path": "/health/ready"}
                        }"""

        inference_conf_obj = json.loads(inference_conf)

        env_no_inference_config = Environment(
                    conda_file=tests_root_dir / "test_configs/deployments/model-1/environment/conda.yml",
                    image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04:20210727.v1"
                )

        env_with_inference_config = Environment(
                    conda_file=tests_root_dir / "test_configs/deployments/model-1/environment/conda.yml",
                    image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04:20210727.v1",
                    inference_config=inference_conf_obj
                )

        assert env_no_inference_config.name == env_no_inference_config.name == ANONYMOUS_ENV_NAME
        assert env_no_inference_config.version != env_with_inference_config.version 
        assert env_no_inference_config.version == "71fccbc128a554b5c3e23330ded8963b"
        assert env_with_inference_config.version == "f223fcd33d34c386cf763b856300f3ce"