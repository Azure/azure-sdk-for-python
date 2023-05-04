import re
import uuid
from itertools import tee
from pathlib import Path
from typing import Callable

import pydash
import pytest
from azure.ai.ml import MLClient, MpiDistribution, load_component, load_environment
from azure.ai.ml._restclient.v2022_05_01.models import ListViewType
from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource
from azure.ai.ml.constants._common import (
    ANONYMOUS_COMPONENT_NAME,
    ARM_ID_PREFIX,
    PROVIDER_RESOURCE_ID_WITH_VERSION,
    AzureMLResourceType,
    IPProtectionLevel,
)
from azure.ai.ml.dsl._utils import _sanitize_python_variable_name
from azure.ai.ml.entities import CommandComponent, Component, PipelineComponent
from azure.ai.ml.entities._load_functions import load_code, load_job
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import assert_job_cancel, omit_with_wildcard, sleep_if_live

from .._util import _COMPONENT_TIMEOUT_SECOND
from ..unittests.test_component_schema import load_component_entity_from_rest_json


def create_component(
    client: MLClient,
    component_name: str,
    path="./tests/test_configs/components/helloworld_component.yml",
    params_override=None,
    is_anonymous=False,
):
    default_param_override = [{"name": component_name}]
    if params_override is None:
        params_override = default_param_override
    else:
        params_override += default_param_override

    command_component = load_component(
        source=path,
        params_override=params_override,
    )
    return client.components.create_or_update(command_component, is_anonymous=is_anonymous)


@pytest.fixture
def torch_distribution():
    def create_torch_distribution(has_strs: bool = False):
        # service returns component with stringified integer values
        # need to do comparison with object returned by service with strings
        # comparison with object in SDK is done with integer values
        if not has_strs:
            return {"type": "pytorch", "process_count_per_instance": 4}
        return {"type": "pytorch", "process_count_per_instance": "4"}

    return create_torch_distribution


@pytest.fixture
def tensorflow_distribution():
    def create_tensorflow_distribution(has_strs: bool = False):
        # service returns component with stringified integer values
        # need to do comparison with object returned by service with strings
        # comparison with object in SDK is done with integer values
        if not has_strs:
            return {
                "type": "tensorflow",
                "parameter_server_count": 1,
                "worker_count": 2,
            }
        return {
            "type": "tensorflow",
            "parameter_server_count": "1",
            "worker_count": "2",
        }

    return create_tensorflow_distribution


# previous bodiless_matcher fixture doesn't take effect because of typo, please add it in method level if needed


def assert_component_basic_workflow(
    client: MLClient,
    randstr: Callable[[str], str],
    path: str,
    expected_dict: dict,
    omit_fields: list,
    recorded_component_name: str,
):
    component_name = randstr(recorded_component_name)

    # create a component
    component_resource = create_component(client, component_name, path=path)
    actual_dict = pydash.omit(dict(component_resource._to_dict()), omit_fields)
    assert actual_dict == expected_dict
    assert component_resource.name == component_name
    assert component_resource.creation_context

    # get back
    component = client.components.get(component_name, component_resource.version)
    assert component_resource._to_dict() == component._to_dict()
    assert component_resource.creation_context

    # create a new version
    params_override = [{"name": component_name}, {"version": 2}]
    command_component = load_component(
        source=path,
        params_override=params_override,
    )
    component_resource = client.components.create_or_update(command_component)
    assert component_resource.version == "2"


@pytest.mark.e2etest
@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "mock_asset_name",
    "mock_component_hash",
    "enable_environment_id_arm_expansion",
)
@pytest.mark.pipeline_test
class TestComponent(AzureRecordedTestCase):
    def test_command_component(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        expected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/development/commandComponent.schema.json",
            "command": "echo Hello World & echo $[[${{inputs.component_in_number}}]] & echo "
            "${{inputs.component_in_path}} & echo "
            "${{outputs.component_out_path}} > "
            "${{outputs.component_out_path}}/component_in_number",
            "description": "This is the basic command component",
            "display_name": "CommandComponentBasic",
            "inputs": {
                "component_in_number": {
                    "default": "10.99",
                    "description": "A number",
                    "optional": True,
                    "type": "number",
                },
                "component_in_path": {"description": "A path", "type": "uri_folder", "optional": False},
            },
            "is_deterministic": True,
            "outputs": {"component_out_path": {"type": "uri_folder"}},
            "resources": {"instance_count": 1},
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "type": "command",
            "version": "0.0.1",
        }
        assert_component_basic_workflow(
            client=client,
            randstr=randstr,
            path="./tests/test_configs/components/helloworld_component.yml",
            expected_dict=expected_dict,
            omit_fields=["name", "creation_context", "id", "code", "environment"],
            recorded_component_name="component_name",
        )

    def test_parallel_component(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        expected_dict = {
            "$schema": "http://azureml/sdk-2-0/ParallelComponent.json",
            "description": "parallel component for batch score",
            "display_name": "BatchScore",
            "error_threshold": 10,
            "input_data": "${{inputs.score_input}}",
            "inputs": {
                "label": {
                    "description": "Other reference data for batch scoring, " "e.g. labels.",
                    "type": "uri_file",
                    "optional": False,
                },
                "score_input": {
                    "description": "The data to be split and scored in " "parallel.",
                    "type": "mltable",
                    "optional": False,
                },
                "score_model": {"description": "The model for batch score.", "type": "custom_model", "optional": False},
            },
            "is_deterministic": True,
            "max_concurrency_per_instance": 12,
            "mini_batch_error_threshold": 5,
            "logging_level": "INFO",
            "mini_batch_size": "10240",
            "outputs": {"scored_result": {"type": "mltable"}, "scoring_summary": {"type": "uri_file"}},
            "retry_settings": {"max_retries": 10, "timeout": 3},
            "type": "parallel",
            "version": "1.0.0",
        }
        assert_component_basic_workflow(
            client=client,
            randstr=randstr,
            path="./tests/test_configs/components/basic_parallel_component_score.yml",
            expected_dict=expected_dict,
            omit_fields=["name", "creation_context", "id", "task"],
            recorded_component_name="component_name",
        )

    def test_automl_component(self, client: MLClient, registry_client: MLClient, randstr: Callable[[str], str]) -> None:
        expected_component_dict = {
            "description": "Component that executes an AutoML Classification task model training in a pipeline.",
            "version": "1.0",
            "$schema": "http://azureml/sdk-2-0/AutoMLComponent.json",
            "display_name": "AutoML Classification",
            "type": "automl",
            "task": "classification",
        }
        omit_fields = [
            "name",
            "creation_context",
            "id",
            # still passing these fields to backend and let backend decide if they want to respect that
            "inputs",
            "outputs",
            "is_deterministic",
        ]
        assert_component_basic_workflow(
            client=client,
            randstr=randstr,
            path="./tests/test_configs/components/automl/classification.yaml",
            expected_dict=expected_component_dict,
            omit_fields=omit_fields,
            recorded_component_name="workspace_component_name",
        )

        assert_component_basic_workflow(
            client=registry_client,
            randstr=randstr,
            path="./tests/test_configs/components/automl/classification.yaml",
            expected_dict=expected_component_dict,
            omit_fields=omit_fields,
            recorded_component_name="registry_component_name",
        )

    def test_spark_component(self, client: MLClient, randstr: Callable[[], str]) -> None:
        expected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/latest/sparkComponent.schema.json",
            "args": "--file_input ${{inputs.file_input}} --output ${{outputs.output}}",
            "conf": {
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.instances": 1,
                "spark.executor.memory": "1g",
            },
            "description": "Aml Spark dataset test module",
            "display_name": "Aml Spark dataset test module",
            "entry": {"file": "kmeans_example.py"},
            "inputs": {"file_input": {"type": "uri_file", "optional": False}},
            "is_deterministic": True,
            "outputs": {"output": {"type": "uri_folder"}},
            "type": "spark",
            "version": "1",
        }
        assert_component_basic_workflow(
            client=client,
            randstr=randstr,
            path="./tests/test_configs/spark_component/component.yml",
            expected_dict=expected_dict,
            omit_fields=["name", "creation_context", "id", "code", "environment"],
            recorded_component_name="spark_component_name",
        )

    def test_datatransfer_copy_urifolder_component(self, client: MLClient, randstr: Callable[[], str]) -> None:
        expected_dict = {
            "$schema": "http://azureml/sdk-2-0/DataTransferComponent.json",
            "data_copy_mode": "merge_with_overwrite",
            "display_name": "Data Transfer Component copy-files",
            "type": "data_transfer",
            "task": "copy_data",
            "inputs": {"folder1": {"type": "uri_folder", "optional": False}},
            "outputs": {"output_folder": {"type": "uri_folder"}},
            "is_deterministic": True,
            "version": "1",
        }
        assert_component_basic_workflow(
            client=client,
            randstr=randstr,
            path="./tests/test_configs/components/data_transfer/copy_files.yaml",
            expected_dict=expected_dict,
            omit_fields=["name", "creation_context", "id"],
            recorded_component_name="datatransfer_copy_urifolder",
        )

    def test_datatransfer_copy_urifile_component(self, client: MLClient, randstr: Callable[[], str]) -> None:
        expected_dict = {
            "$schema": "http://azureml/sdk-2-0/DataTransferComponent.json",
            "data_copy_mode": "fail_if_conflict",
            "display_name": "Data Transfer Component copy uri files",
            "type": "data_transfer",
            "task": "copy_data",
            "inputs": {"folder1": {"type": "uri_file", "optional": False}},
            "outputs": {"output_folder": {"type": "uri_file"}},
            "is_deterministic": True,
            "version": "1",
        }
        assert_component_basic_workflow(
            client=client,
            randstr=randstr,
            path="./tests/test_configs/components/data_transfer/copy_uri_files.yaml",
            expected_dict=expected_dict,
            omit_fields=["name", "creation_context", "id"],
            recorded_component_name="datatransfer_copy_urifile",
        )

    def test_datatransfer_copy_2urifolder_component(self, client: MLClient, randstr: Callable[[], str]) -> None:
        expected_dict = {
            "$schema": "http://azureml/sdk-2-0/DataTransferComponent.json",
            "display_name": "Data Transfer Component merge-files",
            "type": "data_transfer",
            "data_copy_mode": "merge_with_overwrite",
            "task": "copy_data",
            "inputs": {
                "folder1": {"type": "uri_folder", "optional": False},
                "folder2": {"type": "uri_folder", "optional": False},
            },
            "outputs": {"output_folder": {"type": "uri_folder"}},
            "is_deterministic": True,
            "version": "1",
        }
        assert_component_basic_workflow(
            client=client,
            randstr=randstr,
            path="./tests/test_configs/components/data_transfer/merge_files.yaml",
            expected_dict=expected_dict,
            omit_fields=["name", "creation_context", "id"],
            recorded_component_name="datatransfer_copy_2urifolder",
        )

    def test_datatransfer_copy_mixtype_component(self, client: MLClient, randstr: Callable[[], str]) -> None:
        expected_dict = {
            "$schema": "http://azureml/sdk-2-0/DataTransferComponent.json",
            "display_name": "Data Transfer Component merge mix type files",
            "type": "data_transfer",
            "data_copy_mode": "merge_with_overwrite",
            "task": "copy_data",
            "inputs": {
                "input1": {"type": "uri_file", "optional": False},
                "input2": {"type": "uri_file", "optional": False},
                "input3": {"type": "mltable", "optional": False},
            },
            "outputs": {"output_folder": {"type": "uri_folder"}},
            "is_deterministic": True,
            "version": "1",
        }
        assert_component_basic_workflow(
            client=client,
            randstr=randstr,
            path="./tests/test_configs/components/data_transfer/merge_mixtype_files.yaml",
            expected_dict=expected_dict,
            omit_fields=["name", "creation_context", "id"],
            recorded_component_name="datatransfer_copy_mixtype",
        )

    @pytest.mark.parametrize(
        "component_path",
        [
            "type_contract/mltable.yml",
            "type_contract/mlflow_model.yml",
            "type_contract/custom_model.yml",
            "type_contract/path.yml",
            "input_types_component.yml",
        ],
    )
    def test_command_component_create_input_output_types(
        self, client: MLClient, randstr: Callable[[str], str], component_path: str
    ) -> None:
        component_name = randstr("component_name")
        params_override = [{"name": component_name}]
        component_entity = load_component(
            source="./tests/test_configs/components/{}".format(component_path),
            params_override=params_override,
        )
        target_entity = client.components.create_or_update(component_entity)
        target_entity._creation_context = None
        target_entity.resources = None
        component_entity._creation_context = None
        assert target_entity.id
        # server side will remove \n from the code now. Skip them given it's not targeted to check in this test
        # server side will return optional False for optional None input
        omit_fields = ["id", "command", "environment", "inputs.*.optional"]
        assert omit_with_wildcard(component_entity._to_dict(), *omit_fields) == omit_with_wildcard(
            target_entity._to_dict(), *omit_fields
        )

    def test_command_component_with_code(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_name = randstr("component_name")

        component_resource = create_component(
            client,
            component_name,
            path="./tests/test_configs/components/basic_component_code_local_path.yml",
        )
        assert component_resource.name == component_name
        # make sure code is created
        assert component_resource.code
        assert is_ARM_id_for_resource(component_resource.code)

    def test_component_list(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_name = randstr("component name")

        component_resource = create_component(client, component_name)
        assert component_resource.name == component_name

        # list component containers
        component_containers = client.components.list()
        assert isinstance(component_containers.next(), Component)

        # there might be delay so getting the latest version immediately after creation might get wrong result
        sleep_if_live(5)

        # list component versions
        components = client.components.list(name=component_name)
        # creating a copy of iterator
        components, components_copy = tee(components)
        # iterating the whole iterable object to find the number of elements. Not using list.
        assert sum(1 for e in components_copy) == 1
        component = next(iter(components), None)
        assert isinstance(component, Component)

    def test_component_update(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # create a component
        component_name = randstr("component_name")

        component_resource = create_component(client, component_name)
        assert component_resource.id
        rest_path = "./tests/test_configs/components/helloworld_component_rest.json"
        target_entity = load_component_entity_from_rest_json(rest_path)
        assert target_entity._source == "REMOTE.WORKSPACE.COMPONENT"
        component_dict = pydash.omit(
            dict(component_resource._to_dict()),
            "code",
            "environment",
            "name",
            "creation_context",
            "resources",
            "id",
            "inputs.component_in_path.optional",  # backend will return component inputs as optional:False
        )
        expected_dict = pydash.omit(
            dict(target_entity._to_dict()),
            "code",
            "environment",
            "name",
            "creation_context",
            "id",
        )
        assert component_dict == expected_dict

        # create component again with new description and display name
        # TODO: test update tags when supported
        description = "Updated description"
        display_name = "UpdatedComponent"
        params_override = [{"description": description}, {"display_name": display_name}]
        component_entity = Component._load(
            data=component_resource._to_dict(),
            yaml_path="./tests/test_configs/components/helloworld_component.yml",
            params_override=params_override,
        )
        component_resource = client.components.create_or_update(component_entity)
        assert component_resource.description == description
        assert component_resource.display_name == display_name

    @pytest.mark.disable_mock_code_hash
    @pytest.mark.skipif(condition=not is_live(), reason="reuse test, target to verify service-side behavior")
    def test_component_create_twice_same_code_arm_id(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_path = "./tests/test_configs/components/component_for_reuse_test/component.yml"
        component_name = randstr("component_name")
        # create a component
        component_resource1 = create_component(client, component_name, path=component_path)
        # create again
        component_resource2 = create_component(client, component_name, path=component_path)
        # the code arm id should be the same
        assert component_resource1.code == component_resource2.code

    @pytest.mark.skipif(condition=not is_live(), reason="non-deterministic upload fails in playback on CI")
    def test_component_update_code(self, client: MLClient, randstr: Callable[[str], str], tmp_path: Path) -> None:
        component_name = randstr("component_name")
        path = "./tests/test_configs/components/basic_component_code_local_path.yml"

        # create a component
        create_component(client, component_name, path=path)

        # create again with different code and check error msg
        code_path = tmp_path / "code.yml"
        code_path.write_text(
            f"""
        name: {component_name}
        version: 1
        path: ."""
        )
        new_code = load_code(source=code_path)
        code_resource = client._code.create_or_update(new_code)
        params_override = [{"name": component_name, "code": ARM_ID_PREFIX + code_resource.id}]
        command_component = load_component(
            source=path,
            params_override=params_override,
        )
        with pytest.raises(HttpResponseError):
            client.components.create_or_update(command_component)

    @pytest.mark.disable_mock_code_hash
    def test_component_create_default_code(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # step2: test component without code
        component_name = randstr("component_name")
        component_resource1 = create_component(client, component_name)

        # create again with updated tags
        description = "Updated description"
        display_name = "UpdatedComponent"
        params_override = [{"description": description}, {"display_name": display_name}]
        component_resource2 = create_component(client, component_name, params_override=params_override)

        # the code arm id should be the same
        assert component_resource1.code is None
        assert component_resource1.code == component_resource2.code
        assert component_resource2.description == description
        assert component_resource2.display_name == display_name

    @pytest.mark.disable_mock_code_hash
    def test_mpi_component(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_name = randstr("component_name")
        # Test mpi distribution
        params_override = [{"name": component_name}]
        component_entity = load_component(
            source="./tests/test_configs/components/helloworld_component_mpi.yml",
            params_override=params_override,
        )
        # additional fields added_property in distribution and resources are removed.
        mpi_distribution = {"type": "mpi", "process_count_per_instance": 1}
        assert mpi_distribution == component_entity.distribution.__dict__
        mpi_component_resource = client.components.create_or_update(component_entity)
        assert isinstance(mpi_component_resource.distribution, MpiDistribution)
        component_entity = CommandComponent(
            name=randstr("new_name"),
            display_name="CommandComponentMpi",
            description="This is the mpi command component",
            tags={"tag": "tagvalue", "owner": "sdkteam"},
            inputs={
                "component_in_number": {
                    "description": "A number",
                    "type": "number",
                    "default": 10.99,
                },
                "component_in_path": {"description": "A path", "type": "uri_folder"},
            },
            outputs={"component_out_path": {"type": "uri_folder"}},
            command="echo Hello World & echo ${{inputs.component_in_number}} & echo ${{inputs.component_in_path}} "
            "& echo ${{outputs.component_out_path}}",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            distribution=MpiDistribution(
                process_count_per_instance=1,
                # No affect because Mpi object does not allow extra fields
                added_property=7,
            ),
            instance_count=2,
        )
        mpi_entity = client.components.create_or_update(component_entity)

        component_dict = pydash.omit(
            mpi_entity._to_dict(),
            "$schema",
            "id",
            "name",
            "creation_context",
        )
        yaml_component_dict = pydash.omit(
            mpi_component_resource._to_dict(),
            "$schema",
            "id",
            "name",
            "creation_context",
        )
        assert component_dict == yaml_component_dict

    def test_pytorch_component(
        self, client: MLClient, randstr: Callable[[str], str], torch_distribution: Callable[[bool], dict]
    ) -> None:
        component_name = randstr("component_name")
        # Test mpi distribution
        params_override = [{"name": component_name}]
        # Test torch distribution
        component_entity = load_component(
            source="./tests/test_configs/components/helloworld_component_pytorch.yml",
            params_override=params_override,
        )
        # additional fields added_property in distribution and resources are removed.
        torch_resources = {"instance_count": 2, "properties": {}}
        assert component_entity.distribution.__dict__ == torch_distribution()
        assert component_entity.resources._to_rest_object().as_dict() == torch_resources
        torch_component_resource = client.components.create_or_update(component_entity)
        assert torch_component_resource.resources._to_rest_object().as_dict() == torch_resources
        assert torch_component_resource.distribution.__dict__ == torch_distribution(has_strs=True)

    def test_tensorflow_component(
        self, client: MLClient, randstr: Callable[[str], str], tensorflow_distribution: Callable[[bool], dict]
    ) -> None:
        component_name = randstr("component_name")
        # Test mpi distribution
        params_override = [{"name": component_name}]
        # Test tensorflow distribution
        component_entity = load_component(
            source="./tests/test_configs/components/helloworld_component_tensorflow.yml",
            params_override=params_override,
        )
        assert component_entity.distribution.__dict__ == tensorflow_distribution()
        tensorflow_component_resource = client.components.create_or_update(component_entity)
        assert tensorflow_component_resource.distribution.__dict__ == tensorflow_distribution(has_strs=True)

    def test_command_component_create_autoincrement(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_name = randstr("component_name")
        params_override = [{"name": component_name}]
        path = "./tests/test_configs/components/component_no_version.yml"
        command_component = load_component(source=path, params_override=params_override)

        assert command_component.version is None
        assert command_component._auto_increment_version

        created_command_component = client.components.create_or_update(command_component)
        assert created_command_component.version == "1"
        assert created_command_component._auto_increment_version is False

        next_component_asset = client.components.create_or_update(command_component)
        next_version_regex = re.compile(r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{7}")
        assert next_version_regex.match(next_component_asset.version)
        assert next_component_asset._auto_increment_version is False

    @pytest.mark.disable_mock_code_hash
    @pytest.mark.skipif(condition=not is_live(), reason="reuse test, target to verify service-side behavior")
    def test_anonymous_component_reuse(self, client: MLClient, variable_recorder) -> None:
        # component with different name will be created as different instance;
        # therefore component reuse will not work as component name differs

        # component without code
        component_name_1 = variable_recorder.get_or_record("component_name_1", str(uuid.uuid4()))
        component_name_2 = variable_recorder.get_or_record("component_name_2", str(uuid.uuid4()))
        component_resource1 = create_component(
            client, _sanitize_python_variable_name(component_name_1), is_anonymous=True
        )
        component_resource2 = create_component(
            client, _sanitize_python_variable_name(component_name_2), is_anonymous=True
        )
        assert component_resource1.environment == component_resource2.environment
        assert component_resource1.code == component_resource2.code

        # component with inline code and inline environment
        path = "./tests/test_configs/components/helloworld_component_no_paths.yml"
        component_resource1 = create_component(
            client,
            _sanitize_python_variable_name(str(uuid.uuid4())),
            path=path,
            is_anonymous=True,
        )
        component_resource2 = create_component(
            client,
            _sanitize_python_variable_name(str(uuid.uuid4())),
            path=path,
            is_anonymous=True,
        )
        assert component_resource1.environment == component_resource2.environment
        assert component_resource1.code == component_resource2.code

    def test_command_component_dependency_label_resolution(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        """Checks that dependencies of the form azureml:name@label are resolved to a version"""
        environment_name = randstr("environment_name")
        environment_versions = ["foo", "bar"]

        for version in environment_versions:
            client.environments.create_or_update(
                load_environment(
                    "./tests/test_configs/environment/environment_conda_inline.yml",
                    params_override=[{"name": environment_name}, {"version": version}],
                )
            )
        sleep_if_live(10)

        created_component = create_component(
            client,
            randstr("component_name"),
            params_override=[{"environment": f"azureml:{environment_name}@latest"}],
        )
        expected = PROVIDER_RESOURCE_ID_WITH_VERSION.format(
            client._operation_scope._subscription_id,
            client._operation_scope._resource_group_name,
            client._operation_scope.workspace_name,
            AzureMLResourceType.ENVIRONMENT,
            environment_name,
            environment_versions[-1],
        )

        assert created_component.environment == expected

    def test_command_component_get_latest_label(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        name = randstr("name")
        versions = ["foo", "bar", "baz", "foobar"]

        for version in versions:
            create_component(client, name, params_override=[{"version": version}])
            sleep_if_live(5)
            assert client.components.get(name, label="latest").version == version

    def test_anonymous_registration_from_load_component(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        command_component = load_component(source="./tests/test_configs/components/helloworld_component.yml")
        component_resource = client.components.create_or_update(command_component, is_anonymous=True)
        assert component_resource.name == command_component.name
        assert component_resource.version == command_component.version

        anonymous_name, _, anonymous_version = component_resource.id.split("/")[-3:]
        assert anonymous_name == ANONYMOUS_COMPONENT_NAME
        # version calculation has been moved to the server side

        component = client.components.get(anonymous_name, anonymous_version)
        # TODO 1807731: enable this check after server-side fix
        omit_fields = ["creation_context"]
        assert pydash.omit(component_resource._to_dict(), *omit_fields) == pydash.omit(
            component._to_dict(), *omit_fields
        )
        assert component.name == command_component.name
        assert component.version == command_component.version
        assert component._source == "REMOTE.WORKSPACE.COMPONENT"

    def test_component_archive_restore_version(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        name = randstr("namee")
        versions = ["1", "2"]
        version_archived = versions[0]
        for version in versions:
            params_override = [{"version": version}]
            create_component(client, name, params_override=params_override)

        def get_component_list():
            # Wait for list index to update before calling list
            if is_live():
                sleep_if_live(30)
            component_list = client.components.list(name=name, list_view_type=ListViewType.ACTIVE_ONLY)
            return [c.version for c in component_list]

        assert version_archived in get_component_list()
        client.components.archive(name=name, version=version_archived)
        assert version_archived not in get_component_list()
        client.components.restore(name=name, version=version_archived)
        assert version_archived in get_component_list()

    @pytest.mark.skipif(condition=not is_live(), reason="target to verify service-side behavior")
    def test_component_archive_restore_container(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        name = randstr("name")
        create_component(client, name)

        def get_component_list():
            # Wait for list index to update before calling list
            sleep_if_live(30)
            component_list = client.components.list(list_view_type=ListViewType.ACTIVE_ONLY)
            return [c.name for c in component_list]

        assert name in get_component_list()
        client.components.archive(name=name)
        assert name not in get_component_list()
        client.components.restore(name=name)
        assert name in get_component_list()

    def test_entity_command_component_create(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_name = randstr("component_name")
        component = CommandComponent(
            name=component_name,
            display_name="CommandComponentBasic",
            description="This is the basic command component",
            version="3",
            tags={"tag": "tagvalue", "owner": "sdkteam"},
            outputs={"component_out_path": {"type": "path"}},
            command="echo Hello World",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
            code="./tests/test_configs/components/helloworld_components_with_env",
        )
        component_resource = client.components.create_or_update(component)
        assert component_resource.version == "3"

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="registry test, may fail in playback mode during retrieving registry client",
    )
    def test_component_create_get_list_from_registry(
        self, pipelines_registry_client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        component_name = randstr("component_name")

        component_resource = create_component(pipelines_registry_client, component_name)
        assert component_resource.name == component_name
        assert component_resource.code
        assert component_resource.creation_context

        component_get = pipelines_registry_client.components.get(component_name, component_resource.version)
        assert component_resource._to_dict() == component_get._to_dict()
        assert component_resource.creation_context
        assert component_resource._source == "REMOTE.REGISTRY"

        components = pipelines_registry_client.components.list(name=component_name)
        assert isinstance(components, ItemPaged)
        test_component = next(iter(components), None)
        assert isinstance(test_component, Component)

    def test_simple_pipeline_component_create(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_path = "./tests/test_configs/components/helloworld_inline_pipeline_component.yml"

        component = load_component(
            source=component_path,
        )
        # Assert binding on compute not changed after resolve dependencies
        client.components._resolve_dependencies_for_pipeline_component_jobs(
            component, resolver=client.components._orchestrators.get_asset_arm_id, resolve_inputs=False
        )
        assert component.jobs["component_a_job"].compute == "${{parent.inputs.node_compute}}"
        # Assert E2E
        component_name = randstr("component_name")
        rest_pipeline_component = create_component(
            client,
            component_name=component_name,
            path=component_path,
        )
        assert rest_pipeline_component is not None
        component_dict = pydash.omit(
            dict(rest_pipeline_component._to_dict()),
            "name",
            "creation_context",
            "jobs",
            "id",
        )
        expected_dict = {
            "description": "This is the basic pipeline component",
            "tags": {"tag": "tagvalue", "owner": "sdkteam"},
            "version": "1",
            "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
            "display_name": "Hello World Pipeline Component",
            "is_deterministic": False,
            "inputs": {
                "component_in_path": {"type": "uri_folder", "description": "A path", "optional": False},
                "component_in_number": {
                    "type": "number",
                    "optional": True,
                    "default": "10.99",
                    "description": "A number",
                },
                # The azureml: prefix has been resolve and removed by service
                "node_compute": {"type": "string", "default": "cpu-cluster", "optional": False},
            },
            "type": "pipeline",
        }
        assert component_dict == expected_dict
        rest_dict = rest_pipeline_component._to_dict()
        if "jobs" in rest_dict:
            # below line is expected to raise KeyError in live test,
            # it will pass after related changes deployed to canary
            jobs_dict = rest_dict["jobs"]
            # Assert full componentId extra azureml prefix has been removed and parsed to versioned arm id correctly.
            assert "azureml:azureml_anonymous" in jobs_dict["component_a_job"]["component"]
            assert jobs_dict["component_a_job"]["type"] == "command"
            # Assert component show result
            rest_pipeline_component2 = client.components.get(name=component_name, version="1")
            jobs_dict2 = rest_pipeline_component2._to_dict()["jobs"]
            assert jobs_dict == jobs_dict2

    def test_helloworld_nested_pipeline_component(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_path = "./tests/test_configs/components/helloworld_nested_pipeline_component.yml"
        rest_pipeline_component = create_component(
            client,
            component_name=randstr("component_name"),
            path=component_path,
        )
        assert rest_pipeline_component is not None
        component_dict = pydash.omit(
            dict(rest_pipeline_component._to_dict()),
            "name",
            "creation_context",
            # jobs not returned now
            "jobs",
            "id",
        )
        expected_dict = {
            "description": "This is the basic pipeline component",
            "tags": {"tag": "tagvalue", "owner": "sdkteam"},
            "version": "1",
            "$schema": "https://azuremlschemas.azureedge.net/development/pipelineComponent.schema.json",
            "display_name": "Hello World Pipeline Component",
            "is_deterministic": False,
            "inputs": {
                "component_in_path": {
                    "type": "uri_folder",
                    "description": "A path for pipeline component",
                    "optional": False,
                },
                "component_in_number": {
                    "type": "number",
                    "optional": True,
                    "default": "10.99",
                    "description": "A number for pipeline component",
                },
            },
            "outputs": {"nested_output": {"type": "uri_folder"}, "nested_output2": {"type": "uri_folder"}},
            "type": "pipeline",
        }
        assert component_dict == expected_dict

    @pytest.mark.usefixtures("mock_set_headers_with_user_aml_token")
    def test_create_pipeline_component_from_job(self, client: MLClient, randstr: Callable[[str], str]):
        params_override = [{"name": randstr("component_name_0")}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_pipeline_component/pipeline.yml",
            params_override=params_override,
        )
        job = assert_job_cancel(pipeline_job, client)
        name = randstr("component_name_1")
        component = PipelineComponent(name=name, source_job_id=job.id)
        rest_component = client.components.create_or_update(component)
        assert rest_component.name == name

    @pytest.mark.skipif(condition=not is_live(), reason="registry test, target to verify service-side behavior")
    def test_component_with_default_label(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
    ) -> None:
        yaml_path: str = "./tests/test_configs/components/helloworld_component.yml"
        component_name = randstr("component_name")

        create_component(client, component_name, path=yaml_path)

        sleep_if_live(5)  # sleep 5 seconds to wait for index service update

        target_component = client.components.get(component_name, label="latest")

        for default_component in [
            client.components.get(component_name),
            client.components.get(component_name, label="default"),
        ]:
            expected_component_dict = target_component._to_dict()
            default_component_dict = default_component._to_dict()
            assert pydash.omit(default_component_dict, "id") == pydash.omit(expected_component_dict, "id")

            assert default_component.id.endswith(f"/components/{component_name}/labels/default")

            node = default_component()
            assert node._to_rest_object()["componentId"] == default_component.id

    def test_command_component_with_properties_e2e_flow(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        command_component = load_component(
            source="./tests/test_configs/components/helloworld_component_with_properties.yml",
        )
        expected_dict = {
            "$schema": "https://azuremlschemas.azureedge.net/development/commandComponent.schema.json",
            "_source": "YAML.COMPONENT",
            "command": "echo Hello World & echo $[[${{inputs.component_in_number}}]] & "
            "echo ${{inputs.component_in_path}} & echo "
            "${{outputs.component_out_path}} > "
            "${{outputs.component_out_path}}/component_in_number",
            "description": "This is the basic command component",
            "display_name": "CommandComponentBasic",
            "inputs": {
                "component_in_number": {
                    "default": "10.99",
                    "description": "A number",
                    "optional": True,
                    "type": "number",
                },
                "component_in_path": {"description": "A path", "type": "uri_folder"},
            },
            "is_deterministic": True,
            "outputs": {"component_out_path": {"type": "uri_folder"}},
            "properties": {"azureml.pipelines.dynamic": "true"},
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "type": "command",
        }
        omit_fields = ["name", "creation_context", "id", "code", "environment", "version"]
        rest_component = pydash.omit(
            command_component._to_rest_object().as_dict()["properties"]["component_spec"],
            omit_fields,
        )

        assert rest_component == expected_dict

        from_rest_component = client.components.create_or_update(command_component, is_anonymous=True)

        previous_dict = pydash.omit(command_component._to_dict(), omit_fields)
        current_dict = pydash.omit(from_rest_component._to_dict(), omit_fields)
        # TODO(2037030): verify when backend ready
        # assert previous_dict == current_dict

    @pytest.mark.skip(
        reason="TODO (2349965): Message: User/tenant/subscription is not allowed to access registry UnsecureTest-hello-world"
    )
    @pytest.mark.usefixtures("enable_private_preview_schema_features")
    def test_ipp_component_create(self, ipp_registry_client: MLClient, randstr: Callable[[str], str]):
        component_path = "./tests/test_configs/components/component_ipp.yml"
        command_component = load_component(source=component_path)
        from_rest_component = create_component(
            ipp_registry_client,
            component_name=randstr("component_name"),
            path=component_path,
        )

        assert from_rest_component._intellectual_property
        assert from_rest_component._intellectual_property == command_component._intellectual_property

        assert from_rest_component.inputs["training_data"]._intellectual_property
        assert (
            from_rest_component.inputs["training_data"]._intellectual_property
            == command_component.inputs["training_data"]._intellectual_property
        )

        assert from_rest_component.inputs["base_model"]._intellectual_property
        assert from_rest_component.inputs["base_model"]._intellectual_property.protection_level == IPProtectionLevel.ALL

        assert from_rest_component.outputs["model_output_not_ipp"]._intellectual_property

        assert (
            from_rest_component.outputs["model_output_not_ipp"]._intellectual_property
            == command_component.outputs["model_output_not_ipp"]._intellectual_property
        )

        assert from_rest_component.outputs["model_output_ipp"]._intellectual_property
        assert (
            from_rest_component.outputs["model_output_ipp"]._intellectual_property
            == command_component.outputs["model_output_ipp"]._intellectual_property
        )
