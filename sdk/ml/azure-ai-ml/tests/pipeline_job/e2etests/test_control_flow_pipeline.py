from typing import Callable

import pytest
from azure.ai.ml import MLClient, load_job
from azure.ai.ml.entities._builders import Command, Pipeline
from azure.ai.ml.entities._builders.do_while import DoWhile
from azure.ai.ml.entities._builders.parallel_for import ParallelFor
from devtools_testutils import AzureRecordedTestCase
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, omit_with_wildcard

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND
from .test_pipeline_job import assert_job_cancel

omit_fields = [
    "name",
    "properties.display_name",
    "properties.settings",
    "properties.jobs.*._source",
    "properties.jobs.*.componentId",
    "jobs.*.component",
]


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "enable_pipeline_private_preview_features",
    "enable_private_preview_schema_features",
    "enable_private_preview_pipeline_node_types",
    "mock_asset_name",
    "mock_component_hash",
    "mock_set_headers_with_user_aml_token",
    "mock_anon_component_version",
)
@pytest.mark.timeout(timeout=_PIPELINE_JOB_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestConditionalNodeInPipeline(AzureRecordedTestCase):
    pass


class TestIfElse(TestConditionalNodeInPipeline):
    def test_happy_path_if_else(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        my_job = load_job(
            "./tests/test_configs/pipeline_jobs/control_flow/if_else/simple_pipeline.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(my_job, client)

        pipeline_job_dict = created_pipeline._to_rest_object().as_dict()

        pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)
        assert pipeline_job_dict["properties"]["jobs"] == {
            "conditionnode": {
                "condition": "${{parent.jobs.result.outputs.output}}",
                "false_block": "${{parent.jobs.node1}}",
                "true_block": "${{parent.jobs.node2}}",
                "type": "if_else",
            },
            "node1": {
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "1"}},
                "name": "node1",
                "type": "command",
            },
            "node2": {
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "2"}},
                "name": "node2",
                "type": "command",
            },
            "result": {"name": "result", "type": "command"},
        }

    def test_if_else_one_branch(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        my_job = load_job(
            "./tests/test_configs/pipeline_jobs/control_flow/if_else/one_branch.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(my_job, client)

        pipeline_job_dict = created_pipeline._to_rest_object().as_dict()

        pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)
        assert pipeline_job_dict["properties"]["jobs"] == {
            "conditionnode": {
                "condition": "${{parent.jobs.result.outputs.output}}",
                "true_block": "${{parent.jobs.node1}}",
                "type": "if_else",
            },
            "node1": {
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "1"}},
                "name": "node1",
                "type": "command",
            },
            "result": {"name": "result", "type": "command"},
        }

    def test_if_else_literal_condition(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        my_job = load_job(
            "./tests/test_configs/pipeline_jobs/control_flow/if_else/literal_condition.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(my_job, client)

        pipeline_job_dict = created_pipeline._to_rest_object().as_dict()

        pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)
        assert pipeline_job_dict["properties"]["jobs"] == {
            "conditionnode": {"condition": True, "true_block": "${{parent.jobs.node1}}", "type": "if_else"},
            "node1": {
                "inputs": {"component_in_number": {"job_input_type": "literal", "value": "1"}},
                "name": "node1",
                "type": "command",
            },
        }

    def test_if_else_multiple_block(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        my_job = load_job(
            "./tests/test_configs/pipeline_jobs/control_flow/if_else/multiple_block.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(my_job, client)

        pipeline_job_dict = created_pipeline._to_dict()

        pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)
        assert pipeline_job_dict["jobs"] == {
            "conditionnode": {
                "condition": "${{parent.jobs.result.outputs.output}}",
                "false_block": "${{parent.jobs.node3}}",
                "true_block": ["${{parent.jobs.node1}}", "${{parent.jobs.node2}}"],
                "type": "if_else",
            },
            "node1": {"inputs": {"component_in_number": "1"}, "type": "command"},
            "node2": {"inputs": {"component_in_number": "2"}, "type": "command"},
            "node3": {"inputs": {"component_in_number": "3"}, "type": "command"},
            "result": {"type": "command"},
        }

    def test_if_else_single_multiple_block(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        my_job = load_job(
            "./tests/test_configs/pipeline_jobs/control_flow/if_else/single_multiple_block.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(my_job, client)

        pipeline_job_dict = created_pipeline._to_dict()

        pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)
        assert pipeline_job_dict["jobs"] == {
            "conditionnode": {
                "condition": "${{parent.jobs.result.outputs.output}}",
                "true_block": ["${{parent.jobs.node1}}", "${{parent.jobs.node2}}"],
                "type": "if_else",
            },
            "node1": {"inputs": {"component_in_number": "1"}, "type": "command"},
            "node2": {"inputs": {"component_in_number": "2"}, "type": "command"},
            "node3": {"inputs": {"component_in_number": "3"}, "type": "command"},
            "result": {"type": "command"},
        }


class TestDoWhile(TestConditionalNodeInPipeline):
    @pytest.mark.disable_mock_code_hash
    def test_pipeline_with_do_while_node(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/pipeline_jobs/control_flow/do_while/pipeline.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(pipeline_job, client)
        assert len(created_pipeline.jobs) == 7
        assert isinstance(created_pipeline.jobs["pipeline_body_node"], Pipeline)
        assert isinstance(created_pipeline.jobs["do_while_job_with_pipeline_job"], DoWhile)
        assert isinstance(created_pipeline.jobs["do_while_true_job_with_pipeline_job"], DoWhile)
        assert isinstance(created_pipeline.jobs["do_while_job_with_command_component"], DoWhile)
        assert isinstance(created_pipeline.jobs["command_component_body_node"], Command)
        assert isinstance(created_pipeline.jobs["get_do_while_result"], Command)

    def test_do_while_pipeline_with_primitive_inputs(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/pipeline_jobs/control_flow/do_while/pipeline_with_primitive_inputs.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(pipeline_job, client)
        assert len(created_pipeline.jobs) == 5
        assert isinstance(created_pipeline.jobs["pipeline_body_node"], Pipeline)
        assert isinstance(created_pipeline.jobs["do_while_job_with_pipeline_job"], DoWhile)
        assert isinstance(created_pipeline.jobs["do_while_job_with_command_component"], DoWhile)
        assert isinstance(created_pipeline.jobs["command_component_body_node"], Command)
        assert isinstance(created_pipeline.jobs["get_do_while_result"], Command)


def assert_foreach(client: MLClient, job_name, source, expected_node, yaml_node=None):
    if yaml_node is None:
        yaml_node = expected_node
    params_override = [{"name": job_name}]
    pipeline_job = load_job(
        source,
        params_override=params_override,
    )

    created_pipeline_job = assert_job_cancel(pipeline_job, client)
    assert isinstance(created_pipeline_job.jobs["parallel_node"], ParallelFor)
    rest_job_dict = pipeline_job._to_rest_object().as_dict()
    assert rest_job_dict["properties"]["jobs"]["parallel_node"] == expected_node
    yaml_job_dict = pipeline_job._to_dict()
    yaml_node.pop("_source", None)
    assert yaml_job_dict["jobs"]["parallel_node"] == yaml_node


class TestParallelFor(TestConditionalNodeInPipeline):
    def test_simple_foreach_string_item(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/helloworld_parallel_for_pipeline_job.yaml"
        expected_node = {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_number": 1}, {"component_in_number": 2}]',
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }

        assert_foreach(client, randstr("job_name"), source, expected_node)

    def test_simple_foreach_list_item(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/helloworld_parallel_for_pipeline_job_list_input.yaml"
        expected_node = {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_number": 1}, {"component_in_number": 2}]',
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }
        assert_foreach(client, randstr("job_name"), source, expected_node)

    def test_simple_foreach_dict_item(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/helloworld_parallel_for_pipeline_job_dict_input.yaml"
        expected_node = {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '{"branch1": {"component_in_number": 1}, "branch2": ' '{"component_in_number": 2}}',
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }
        assert_foreach(client, randstr("job_name"), source, expected_node)

    def test_output_binding_foreach_node(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/helloworld_parallel_for_pipeline_job_output_binding.yaml"
        expected_node = {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_number": 1}, {"component_in_number": 2}]',
            "outputs": {"component_out_path": {"type": "literal", "value": "${{parent.outputs.component_out_path}}"}},
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }
        yaml_node = {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_number": 1}, {"component_in_number": 2}]',
            "outputs": {"component_out_path": "${{parent.outputs.component_out_path}}"},
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }
        assert_foreach(client, randstr("job_name"), source, expected_node, yaml_node)

    def test_assets_in_items(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/control_flow/parallel_for/assets_items.yaml"
        expected_node = {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_path": {"uri": '
            '"https://dprepdata.blob.core.windows.net/demo/Titanic.csv", '
            '"job_input_type": "uri_file"}}, {"component_in_path": {"uri": '
            '"https://dprepdata.blob.core.windows.net/demo/Titanic.csv", '
            '"job_input_type": "uri_file"}}]',
            "outputs": {"component_out_path": {"type": "literal", "value": "${{parent.outputs.component_out_path}}"}},
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }
        yaml_node = {
            "body": "${{parent.jobs.parallel_body}}",
            # items will become json string when dump to avoid removal of empty inputs
            "items": "[{\"component_in_path\": \"{'type': 'uri_file', 'path': "
            "'https://dprepdata.blob.core.windows.net/demo/Titanic.csv'}\"}, "
            "{\"component_in_path\": \"{'type': 'uri_file', 'path': "
            "'https://dprepdata.blob.core.windows.net/demo/Titanic.csv'}\"}]",
            "outputs": {"component_out_path": "${{parent.outputs.component_out_path}}"},
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }
        assert_foreach(client, randstr("job_name"), source, expected_node, yaml_node)

    def test_path_on_datastore_in_items(self, client: MLClient, randstr: Callable):
        source = "./tests/test_configs/pipeline_jobs/control_flow/parallel_for/path_on_ds_items.yaml"
        expected_node = {
            "body": "${{parent.jobs.parallel_body}}",
            "items": '[{"component_in_path": {"uri": '
            '"azureml://datastores/workspaceblobstore/paths/path/on/datastore/1", '
            '"job_input_type": "uri_folder"}}, {"component_in_path": {"uri": '
            '"azureml://datastores/workspaceblobstore/paths/path/on/datastore/2", '
            '"job_input_type": "uri_folder"}}]',
            "outputs": {"component_out_path": {"type": "literal", "value": "${{parent.outputs.component_out_path}}"}},
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }
        yaml_node = {
            "body": "${{parent.jobs.parallel_body}}",
            "items": "[{\"component_in_path\": \"{'type': 'uri_folder', 'path': "
            "'azureml://datastores/workspaceblobstore/paths/path/on/datastore/1'}\"}, "
            "{\"component_in_path\": \"{'type': 'uri_folder', 'path': "
            "'azureml://datastores/workspaceblobstore/paths/path/on/datastore/2'}\"}]",
            "outputs": {"component_out_path": "${{parent.outputs.component_out_path}}"},
            "type": "parallel_for",
            "_source": "YAML.JOB",
        }
        assert_foreach(client, randstr("job_name"), source, expected_node, yaml_node)


def assert_control_flow_in_pipeline_component(client, component_path, pipeline_path):
    params_override = [{"component": component_path}]
    pipeline_job = load_job(
        pipeline_path,
        params_override=params_override,
    )
    created_pipeline = assert_job_cancel(pipeline_job, client)
    pipeline_job_dict = created_pipeline._to_rest_object().as_dict()

    pipeline_job_dict = omit_with_wildcard(pipeline_job_dict, *omit_fields)
    assert pipeline_job_dict["properties"]["jobs"] == {}


class TestControlFLowPipelineComponent(TestConditionalNodeInPipeline):
    def test_if_else(self, client: MLClient, randstr: Callable[[], str]):
        assert_control_flow_in_pipeline_component(
            client=client,
            component_path="./if_else/simple_pipeline.yml",
            pipeline_path="./tests/test_configs/pipeline_jobs/control_flow/control_flow_with_pipeline_component.yml",
        )

    @pytest.mark.skip(reason="TODO(2177353): check why recorded tests failure.")
    def test_do_while(self, client: MLClient, randstr: Callable[[], str]):
        assert_control_flow_in_pipeline_component(
            client=client,
            component_path="./do_while/pipeline_component.yml",
            pipeline_path="./tests/test_configs/pipeline_jobs/control_flow/control_flow_with_pipeline_component.yml",
        )

    def test_foreach(self, client: MLClient, randstr: Callable[[], str]):
        assert_control_flow_in_pipeline_component(
            client=client,
            component_path="./parallel_for/simple_pipeline.yml",
            pipeline_path="./tests/test_configs/pipeline_jobs/control_flow/control_flow_with_pipeline_component.yml",
        )
