import random
import re
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase
from test_utilities.utils import sleep_if_live

from azure.ai.ml import MLClient, load_environment
from azure.ai.ml._restclient.v2022_05_01.models import ListViewType
from azure.ai.ml.constants._common import ARM_ID_PREFIX
from azure.core.paging import ItemPaged


@pytest.fixture
def env_name(variable_recorder) -> Callable[[str], str]:
    def generate_random_environment_name(env_name: Callable[[str], str]) -> str:
        random_env_name = f"env-test-{str(random.randint(1, 10000000))}"
        return variable_recorder.get_or_record(env_name, random_env_name)

    return generate_random_environment_name


# previous bodiless_matcher fixture doesn't take effect because of typo, please add it in method level if needed


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
@pytest.mark.production_experiences_test
class TestEnvironment(AzureRecordedTestCase):
    def test_environment_create_conda(self, client: MLClient, env_name: Callable[[str], str]) -> None:
        params_override = [{"name": env_name("name")}]
        env = load_environment(
            source="./tests/test_configs/environment/environment_conda.yml", params_override=params_override
        )

        environment = client._environments.create_or_update(env)

        environment_id = _get_environment_arm_id(
            client=client, environment_name=env.name, environment_version=env.version
        )

        assert environment.conda_file
        assert environment.id == environment_id

        env_dump = environment._to_dict()
        assert env_dump
        assert env_dump["id"] == ARM_ID_PREFIX + environment_id
        assert env_dump["conda_file"]
        assert env_dump["description"]

    def test_environment_create_conda_inline(self, client: MLClient, env_name: Callable[[str], str]) -> None:
        params_override = [{"name": env_name("name")}]
        env = load_environment(
            source="./tests/test_configs/environment/environment_conda_inline.yml", params_override=params_override
        )
        environment = client._environments.create_or_update(env)
        environment_id = _get_environment_arm_id(
            client=client, environment_name=env.name, environment_version=env.version
        )

        assert environment.conda_file
        assert environment.id == environment_id

        env_dump = environment._to_dict()
        assert env_dump
        assert env_dump["id"] == ARM_ID_PREFIX + environment_id
        assert env_dump["conda_file"]
        assert env_dump["description"]

    def test_environment_create_or_update_docker(self, client: MLClient, env_name: Callable[[str], str]) -> None:
        params_override = [{"name": env_name("name")}]
        env = load_environment(
            source="./tests/test_configs/environment/environment_docker_image.yml",
            params_override=params_override,
        )
        environment = client._environments.create_or_update(env)

        environment_id = _get_environment_arm_id(
            client=client, environment_name=env.name, environment_version=env.version
        )

        assert environment
        assert environment.image
        assert environment.id == environment_id

        env_dump = environment._to_dict()
        assert env_dump
        assert env_dump["id"] == ARM_ID_PREFIX + environment_id
        assert env_dump["image"] == environment.image

    @pytest.mark.live_test_only("Needs re-recording to work with new test proxy sanitizers")
    def test_environment_create_or_update_docker_context(
        self, client: MLClient, env_name: Callable[[str], str]
    ) -> None:
        params_override = [{"name": env_name("name")}]
        env = load_environment(
            source="./tests/test_configs/environment/environment_docker_context.yml",
            params_override=params_override,
        )
        environment = client._environments.create_or_update(env)

        environment_id = _get_environment_arm_id(
            client=client, environment_name=env.name, environment_version=env.version
        )

        assert environment
        assert environment.build
        assert environment.id == environment_id

        env_dump = environment._to_dict()
        assert env_dump
        assert env_dump["id"] == ARM_ID_PREFIX + environment_id
        assert env_dump["build"]
        assert env_dump["build"]["path"]
        assert env_dump["build"]["dockerfile_path"]

        context_uri = environment.build.path
        dockerfile_path = environment.build.dockerfile_path

        env.build.path = context_uri
        env.build.dockerfile_path = dockerfile_path

        environment_with_context_uri = client._environments.create_or_update(env)
        assert environment_with_context_uri
        assert environment_with_context_uri.build
        assert environment_with_context_uri.id == environment_id
        assert environment_with_context_uri.build.dockerfile_path == dockerfile_path
        assert environment_with_context_uri.build.path == context_uri

    def test_environment_create_or_update_docker_context_and_image(
        self, client: MLClient, env_name: Callable[[str], str]
    ) -> None:
        params_override = [{"name": env_name("name")}]
        env = load_environment(
            source="./tests/test_configs/environment/environment_docker_context.yml",
            params_override=params_override,
        )
        env.image = "blah"

        with pytest.raises(Exception) as error:
            client._environments.create_or_update(env)

        assert "Docker image or Dockerfile should be provided not both" in str(error.value)

    def test_environment_list(self, client: MLClient) -> None:
        environment_list = client._environments.list()
        assert environment_list
        assert isinstance(environment_list, ItemPaged)

    def test_environment_get(self, client: MLClient) -> None:
        environment_name = "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu"
        environment_version = "1"
        environment_id = _get_environment_arm_id(
            client=client, environment_name=environment_name, environment_version=environment_version
        )
        environment = client._environments.get(name=environment_name, version=environment_version)

        assert environment
        assert environment.id == environment_id

    def test_environment_archive_restore_version(self, client: MLClient, env_name: Callable[[str], str]) -> None:
        versions = ["1", "2"]
        version_archived = versions[0]
        name = env_name("name")
        for version in versions:
            params_override = [{"name": name, "version": version}]
            env = load_environment(
                source="./tests/test_configs/environment/environment_conda.yml", params_override=params_override
            )
            client.environments.create_or_update(env)

        def get_environment_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            environment_list = client.environments.list(name=name, list_view_type=ListViewType.ACTIVE_ONLY)
            return [e.version for e in environment_list if e is not None]

        assert version_archived in get_environment_list()
        client.environments.archive(name=name, version=version_archived)
        assert version_archived not in get_environment_list()
        client.environments.restore(name=name, version=version_archived)
        assert version_archived in get_environment_list()

    @pytest.mark.skip(reason="Task 1791832: Inefficient, possibly causing testing pipeline to time out.")
    def test_environment_archive_restore_container(self, client: MLClient, env_name: Callable[[str], str]) -> None:
        name = env_name("name")
        params_override = [{"name": name}]
        env = load_environment(
            source="./tests/test_configs/environment/environment_conda.yml", params_override=params_override
        )
        client.environments.create_or_update(env)

        def get_environment_list():
            # Wait for list index to update before calling list command
            sleep_if_live(30)
            environment_list = client.environments.list(list_view_type=ListViewType.ACTIVE_ONLY)
            return [e.name for e in environment_list if e is not None]

        assert name in get_environment_list()
        client.environments.archive(name=name)
        assert name not in get_environment_list()
        client.environments.restore(name=name)
        assert name in get_environment_list()

    def test_environment_get_latest_label(self, client: MLClient, randstr: Callable[[], str]) -> None:
        name = randstr("name")
        versions = ["foo", "bar", "baz", "foobar"]

        for version in versions:
            created = client.environments.create_or_update(
                load_environment(
                    "./tests/test_configs/environment/environment_conda_inline.yml",
                    params_override=[{"name": name}, {"version": version}],
                )
            )
            assert created.name == name
            assert created.version == version
            sleep_if_live(2)
            assert client.environments.get(name, label="latest").version == version

    @pytest.mark.live_test_only("Needs re-recording to work with new test proxy sanitizers")
    def test_registry_environment_create_conda_and_get(
        self, only_registry_client: MLClient, env_name: Callable[[str], str]
    ) -> None:
        params_override = [{"name": env_name("name")}]
        env = load_environment(
            source="./tests/test_configs/environment/environment_conda.yml", params_override=params_override
        )

        environment = only_registry_client._environments.create_or_update(env)

        environment_id = f"azureml://registries/testFeed/environments/{env.name}/versions/{env.version}"

        assert environment.conda_file
        assert environment.id == environment_id

        env_dump = environment._to_dict()
        assert env_dump
        assert env_dump["id"] == environment_id
        assert env_dump["conda_file"]
        assert env_dump["description"]

        environment = only_registry_client._environments.get(name=env.name, version=env.version)
        assert environment
        assert environment.id == environment_id

    def test_registry_environment_list(self, only_registry_client: MLClient) -> None:
        environment_list = only_registry_client._environments.list()
        assert environment_list
        assert isinstance(environment_list, ItemPaged)


def _get_environment_arm_id(client: MLClient, environment_name: str, environment_version: str) -> str:
    ws_scope = client._operation_scope
    environment_id = (
        "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{"
        "}/environments/{}/versions/{}".format(
            ws_scope.subscription_id,
            ws_scope.resource_group_name,
            ws_scope.workspace_name,
            environment_name,
            environment_version,
        )
    )

    return environment_id
