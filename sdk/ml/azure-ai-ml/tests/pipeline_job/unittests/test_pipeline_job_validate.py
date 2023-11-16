import json
import re
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional
from unittest.mock import patch

import pytest
from marshmallow import ValidationError
from pytest_mock import MockFixture

from azure.ai.ml import Input, MLClient, Output, dsl, load_component, load_job
from azure.ai.ml.constants._common import AssetTypes, InputOutputModes
from azure.ai.ml.entities import Choice, CommandComponent, PipelineJob
from azure.ai.ml.entities._validate_funcs import validate_job
from azure.ai.ml.exceptions import UserErrorException, ValidationException

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND


def assert_the_same_path(actual_path, expected_path):
    if actual_path is None or expected_path is None:
        assert actual_path == expected_path
    else:
        assert Path(actual_path).resolve() == Path(expected_path).resolve()


tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_PIPELINE_JOB_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPipelineJobValidate:
    @pytest.mark.parametrize(
        "pipeline_job_path, expected_error",
        [
            pytest.param(
                "./tests/test_configs/pipeline_jobs/invalid/with_invalid_component.yml",
                # only type matched error message in "component
                r"Missing data for required field\.",
                id="missing_required_field",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/invalid/type_sensitive_component_error.yml",
                # not allowed type
                "Value 'unsupported' passed is not in set",
                id="not_allowed_type",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/job_with_incorrect_component_content/pipeline.yml",
                "In order to specify an existing codes, please provide",
                id="invalid_component_content",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/invalid/invalid_pipeline_referencing_component_file.yml",
                "In order to specify an existing components, please provide the correct registry",
                id="invalid_pipeline_referencing_component_file",
            ),
        ],
    )
    def test_pipeline_job_validation_on_load(self, pipeline_job_path: str, expected_error: str) -> None:
        with pytest.raises(ValidationError, match=expected_error):
            load_job(pipeline_job_path)

    @pytest.mark.parametrize(
        "pipeline_job_path, expected_validation_result",
        [
            pytest.param(
                "./tests/test_configs/pipeline_jobs/invalid/with_invalid_value_in_component.yml",
                # only type matched error message in "component
                {
                    "location": f"{Path('./tests/test_configs/components/invalid/combo.yml').absolute()}#line 35",
                    "message": "Not a valid "
                    "URL.; In order to specify a git path, please provide "
                    "the correct path prefixed with 'git+\n"
                    "; In order to specify an existing codes, please "
                    "provide the correct registry path prefixed with "
                    "'azureml://':\n",
                    "path": "jobs.hello_world_component.component.code",
                    "value": "azureml:name-only",
                },
                id="invalid_code_in_component",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/invalid/with_invalid_component.yml",
                # only type matched error message in "component
                {
                    "location": f"{Path('./tests/test_configs/components/invalid/no_environment.yml').absolute()}#line 1",
                    "message": "Missing data for required field.",
                    "path": "jobs.hello_world_component.component.environment",
                    "value": None,
                },
                id="missing_required_field",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/invalid/type_sensitive_component_error.yml",
                # not allowed type
                {
                    "location": f"{Path('./tests/test_configs/pipeline_jobs/invalid/type_sensitive_component_error.yml').absolute()}#line 24",
                    "message": "Value 'unsupported' passed is not in set " "['command', 'import', 'sweep', 'parallel'",
                    "path": "jobs.hello_world_unsupported_type.type",
                    "value": "unsupported",
                },
                id="not_allowed_type",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/job_with_incorrect_component_content/pipeline.yml",
                {
                    "location": f"{Path('./tests/test_configs/pipeline_jobs/job_with_incorrect_component_content/pipeline.yml').absolute()}#line 8",
                    "message": "Not a valid string.; Not a valid URL.; "
                    "In order to specify a git path, please provide "
                    "the correct path prefixed with 'git+\n"
                    "; In order to specify an existing codes, please "
                    "provide the correct registry path prefixed with "
                    "'azureml://':\n",
                    "path": "jobs.hello_python_world_job.component.code",
                    "value": None,
                },
                id="invalid_component_content",
            ),
        ],
    )
    def test_pipeline_job_schema_error(self, pipeline_job_path: str, expected_validation_result: dict) -> None:
        result = validate_job(path=pipeline_job_path)
        result_dict = result._to_dict()["errors"]
        assert len(result_dict) == 1
        assert expected_validation_result.pop("message") in result_dict[0].pop("message")
        assert result_dict[0] == expected_validation_result

    def test_pipeline_job_type_sensitive_error_message(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_type_sensitive_errors.yml"
        validation_result = validate_job(test_path)
        actual_dict = validation_result._to_dict()
        for error in actual_dict["errors"]:
            error.pop("location")
            error.pop("message")
        assert actual_dict == {
            "errors": [
                # error on type only for not supported value on type_field
                {
                    "path": "jobs.hello_world_unsupported_type.type",
                    "value": "unsupported",
                },
                # following errors are from SweepSchema
                {
                    "path": "jobs.hello_world_no_env.objective",
                    "value": None,
                },
                {
                    "path": "jobs.hello_world_no_env.limits",
                    "value": None,
                },
                {
                    "path": "jobs.hello_world_no_env.trial",
                    "value": None,
                },
            ],
            "result": "Failed",
        }

    def test_pipeline_node_name_validate(self):
        invalid_node_names = ["1", "a-c", "1abc", ":::", "hello.world", "Abc", "aBc"]
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job.yml"
        for invalid_name in invalid_node_names:
            params_override = [{"jobs": {invalid_name: {"type": "command", "command": "ls"}}}]
            with pytest.raises(ValidationError) as e:
                load_job(test_path, params_override=params_override)
            err_msg = "Pipeline node name should be a valid python identifier"
            assert err_msg in str(e.value)

        valid_component_names = ["_abc", "n", "name", "n_a_m_e", "name_1"]
        for valid_name in valid_component_names:
            params_override = [{"jobs": {valid_name: {"type": "command", "command": "ls"}}}]
            load_job(test_path, params_override=params_override)

    def test_pipeline_job_source_path_resolution(self):
        test_path = "./tests/test_configs/pipeline_jobs/inline_file_comp_base_path_sensitive/pipeline.yml"
        component_path = (
            "./tests/test_configs/pipeline_jobs/inline_file_comp_base_path_sensitive/component/component.yml"
        )

        pipeline_job: PipelineJob = load_job(test_path)
        assert_the_same_path(pipeline_job._source_path, test_path)
        for node_name in ["command_node", "command_node_file_ref"]:
            assert_the_same_path(pipeline_job.jobs[node_name].component._source_path, component_path)

            component = load_component(component_path)
            assert_the_same_path(component._source_path, component_path)

            assert_the_same_path(
                pipeline_job.jobs["command_node"].component.environment._source_path,
                "./tests/test_configs/environment/environment_docker_context.yml",
            )

    def test_pipeline_job_node_base_path_resolution(self, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/inline_file_comp_base_path_sensitive/pipeline.yml"
        pipeline_job: PipelineJob = load_job(test_path)
        pipeline_job._validate(raise_error=True)
        # return origin value as no base path change
        assert pipeline_job.jobs["command_node"].component.code == "../../../python"
        # return origin value before serialization
        assert pipeline_job.jobs["command_node"].code == "../../../python"

        code_path = "./tests/test_configs/python"
        pipeline_job_dict = pipeline_job._to_dict()
        # return rebased path after serialization
        assert_the_same_path(pipeline_job_dict["jobs"]["command_node"]["component"]["code"], code_path)
        assert_the_same_path(
            pipeline_job_dict["jobs"]["command_node"]["component"]["environment"]["build"]["path"],
            "./tests/test_configs/environment/environment_files",
        )

    def test_pipeline_job_base_path_resolution(self, mocker: MockFixture):
        job: PipelineJob = load_job("./tests/test_configs/pipeline_jobs/my_exp/azureml-job.yaml")
        assert job._validate().passed

    def test_pipeline_job_validate_compute(self) -> None:
        test_path = "./tests/test_configs/pipeline_jobs/invalid/combo.yml"
        pipeline_job: PipelineJob = load_job(test_path)
        assert pipeline_job._validate()._to_dict()["errors"][0]["message"] == "Compute not set"

        pipeline_job.settings.default_compute = "cpu-cluster"
        assert pipeline_job._validate().passed
        pipeline_job.settings.default_compute = None

        pipeline_job.compute = "cpu-cluster"
        assert pipeline_job._validate().passed
        pipeline_job.compute = None

        pipeline_job.jobs["command_node"].compute = "cpu-cluster"
        assert pipeline_job._validate().passed

    def test_pipeline_job_diagnostics_location_resolution(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/pipeline_jobs/invalid/combo.yml"
        pipeline_job: PipelineJob = load_job(test_path)
        result_dict = mock_machinelearning_client.jobs.validate(pipeline_job)._to_dict()
        assert result_dict == {
            "errors": [
                {
                    "location": f"{Path(test_path).resolve().absolute()}#line 21",
                    "message": "Compute not set",
                    "path": "jobs.command_node.compute",
                    "value": None,
                }
            ],
            "warnings": [
                {
                    "location": f"{Path(test_path).resolve().absolute()}#line 23",
                    "message": "Unknown field.",
                    "path": "jobs.command_node.jeff_special_option",
                    "value": {"joo": "bar"},
                }
            ],
            "result": "Failed",
        }

    @pytest.mark.parametrize(
        "pipeline_output_path, error_message",
        [
            pytest.param(
                "tests/test_configs/pipeline_jobs/helloworld_pipeline_job_register_pipeline_output_without_name.yaml",
                "Output name is required when output version is specified.",
                id="register_pipeline_output_without_name",
            ),
            pytest.param(
                "tests/test_configs/pipeline_jobs/helloworld_pipeline_job_register_node_output_without_name.yaml",
                "Output name is required when output version is specified.",
                id="register_node_output_without_name",
            ),
            pytest.param(
                "tests/test_configs/pipeline_jobs/helloworld_pipeline_job_register_pipeline_output_with_invalid_name.yaml",
                "The output name pipeline_output@ can only contain alphanumeric characters, dashes and underscores, with a limit of 255 characters.",
                id="register_pipeline_output_with_invalid_name",
            ),
        ],
    )
    def test_register_output_without_name_yaml(self, pipeline_output_path, error_message):
        with pytest.raises(UserErrorException) as e:
            pipeline = load_job(source=pipeline_output_path)
        assert error_message in str(e.value)

    @pytest.mark.parametrize(
        "test_case,expected_error_message",
        [
            # test matrix: <pipeline-default-compute> + <step-compute>
            pytest.param(
                "none_pipeline_default_compute_invalid",
                {
                    "jobs.vanilla_node.compute": "Compute not set",
                    "jobs.node_with_resources.compute": "Compute not set",
                    "jobs.pipeline_node.jobs.vanilla_node.compute": "Compute not set",
                    "jobs.pipeline_node.jobs.node_with_resources.compute": "Compute not set",
                },
                id="none_pipeline_default_compute_invalid",
            ),  # invalid: none + none / none + resources
            pytest.param(
                "none_pipeline_default_compute_valid",
                None,
                id="none_pipeline_default_compute_valid",
            ),  # valid: none + resources / none + serverless / none + compute target
            pytest.param(
                "serverless_pipeline_default_compute_valid",
                None,
                id="serverless_pipeline_default_compute_valid",
            ),  # valid serverless + <step-compute> (any combination should be valid)
        ],
    )
    def test_pipeline_job_with_serverless_compute(
        self, test_case: str, expected_error_message: Optional[List[str]]
    ) -> None:
        yaml_path = f"./tests/test_configs/pipeline_jobs/serverless_compute/{test_case}/pipeline.yml"
        pipeline_job = load_job(yaml_path)
        validation_result = pipeline_job._validate()
        if expected_error_message is None:
            assert validation_result.passed
        else:
            assert validation_result.error_messages == expected_error_message

    @pytest.mark.parametrize(
        "pipeline_output_path, error_message",
        [
            pytest.param(
                "./tests/test_configs/pipeline_jobs/data_transfer/invalid/import_data_invalid_output_type.yaml",
                "Outputs field only support type mltable for database and uri_folder for file_system",
                id="import_data_invalid_output_type",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/data_transfer/invalid/export_data_invalid_input_type.yaml",
                "Inputs field only support type uri_file for database and uri_folder for file_system",
                id="export_data_invalid_input_type",
            ),
        ],
    )
    def test_data_transfer_job(self, pipeline_output_path: str, error_message: str):
        pipeline = load_job(source=pipeline_output_path)
        validate_result = pipeline._validate()
        assert error_message in str(validate_result.error_messages)

    @pytest.mark.parametrize(
        "pipeline_output_path, error_message",
        [
            pytest.param(
                "./tests/test_configs/pipeline_jobs/data_transfer/invalid/import_data_with_reference_component_file."
                "yaml",
                "In order to specify an existing None, please provide the correct registry path prefixed with 'azureml",
                id="import_data_with_reference_component_file",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/data_transfer/invalid/export_data_with_reference_componen_file.yaml",
                "In order to specify an existing None, please provide the correct registry path prefixed with 'azureml",
                id="export_data_with_reference_component_file",
            ),
        ],
    )
    def test_load_data_transfer_job_with_reference_component_file(self, pipeline_output_path: str, error_message: str):
        with pytest.raises(ValidationError) as ex:
            load_job(pipeline_output_path)
            assert error_message in ex.__str__()


@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestDSLPipelineJobValidate:
    def test_pipeline_str(self):
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            component_func = load_component(path)
            component_func(component_in_number=component_in_number, component_in_path=component_in_path)

        test_job_input = Input(path="azureml:fake_data:1")
        pipeline1 = pipeline(10, test_job_input)
        assert str(pipeline1)
        pipeline2 = pipeline(None, None)
        validate_result = pipeline2._validate()
        assert validate_result.passed is False
        assert validate_result.error_messages == {
            "jobs.microsoftsamples_command_component_basic.compute": "Compute not set",
            "inputs.component_in_path": "Required input 'component_in_path' for pipeline 'pipeline' not provided.",
        }
        validate_result.resolve_location_for_diagnostics(source_path=pipeline2.component._source_path)

    def test_pipeline_with_none_parameter_no_default_optional_false(self) -> None:
        default_optional_func = load_component(str(components_dir / "default_optional_component.yml"))

        # None input is binding to a required input
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input,
            required_param,
            required_param_with_default,
        ):
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=None,
            required_param="hello",
            required_param_with_default=False,
        )
        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "inputs.required_input": "Required input 'required_input' for pipeline 'pipeline_with_default_optional_parameters' not provided."
        }

        # None input is not binding to a required input
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_param,
            required_param_with_default,
        ):
            default_optional_func(
                required_input=None,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_param="hello",
            required_param_with_default=False,
        )
        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "jobs.default_optional_component.inputs.required_input": "Required input 'required_input' for component 'default_optional_component' not provided."
        }

        # Not pass required parameter
        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_param,
            required_param_with_default,
        ):
            default_optional_func(
                required_param=required_param,
                required_param_with_default=required_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_param="hello",
            required_param_with_default=False,
        )

        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "jobs.default_optional_component.inputs.required_input": "Required input 'required_input' for component 'default_optional_component' not provided."
        }

    def test_pipeline_with_none_parameter_binding_to_two_component_inputs(self) -> None:
        default_optional_func = load_component(str(components_dir / "default_optional_component.yml"))

        # None pipeline parameter is binding to two component.

        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input, required_param, required_param_with_default, optional_param_with_default, optional_param
        ):
            # In the first component, optional_param_with_default is binding to two optional component inputs.
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param_with_default,
                optional_param_with_default=optional_param_with_default,
            )
            #  In the second component, optional_param_with_default is binding to one optional component input and one
            #  required component input.
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=optional_param_with_default,
                optional_param=optional_param,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param_with_default=None,
            optional_param="optional_param",
        )
        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "inputs.optional_param_with_default": "Required input 'optional_param_with_default' for pipeline 'pipeline_with_default_optional_parameters' not provided."
        }

    def test_dsl_pipeline_distribution_as_command_inputs(self) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline(name="train_with_sweep_in_pipeline")
        def train_with_sweep_in_pipeline(raw_data):
            component_to_sweep: CommandComponent = load_component(yaml_file)
            cmd_node1 = component_to_sweep(component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data)
            return {
                "pipeline_job_model": cmd_node1.outputs.component_out_path,
            }

        pipeline = train_with_sweep_in_pipeline(raw_data=Input(path="/a/path/on/ds"))
        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "jobs.cmd_node1.inputs.component_in_number": "Input of command cmd_node1 is a SweepDistribution, please use command.sweep to transform the command into a sweep node.",
            "jobs.cmd_node1.compute": "Compute not set",
        }

    @pytest.mark.usefixtures("enable_pipeline_private_preview_features")
    def test_dsl_pipeline_component_validate_compute(self) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)
        job_input = Input(
            type=AssetTypes.URI_FILE,
            path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
        )

        @dsl.pipeline()
        def sub_pipeline0(component_in_number: int, component_in_path: Input, node_compute_name="cpu-cluster"):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node2.compute = node_compute_name
            return node1.outputs

        @dsl.pipeline()
        def sub_pipeline1(component_in_number: int, component_in_path: Input):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            sub_pipeline0(component_in_number=component_in_number, component_in_path=component_in_path)
            return node1.outputs

        @dsl.pipeline()
        def root_pipeline(component_in_number, component_in_path):
            sub_graph = sub_pipeline0(component_in_number=component_in_number, component_in_path=component_in_path)
            sub_pipeline1(component_in_number=component_in_number, component_in_path=component_in_path)
            return sub_graph.outputs

        pipeline_job: PipelineJob = root_pipeline(10, job_input)
        validate_result = pipeline_job._validate()
        assert validate_result.error_messages == {
            "jobs.sub_graph.jobs.node1.compute": "Compute not set",
            "jobs.sub_pipeline1.jobs.node1.compute": "Compute not set",
            "jobs.sub_pipeline1.jobs.sub_pipeline0.jobs.node1.compute": "Compute not set",
        }
        pipeline_job.settings.default_compute = "cpu-cluster"
        validate_result = pipeline_job._validate()
        assert validate_result.passed is True

    @pytest.mark.usefixtures("enable_pipeline_private_preview_features")
    def test_pipeline_job_error_when_nested_component_has_no_concrete_type(self):
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)

        @dsl.pipeline
        def sub_pipeline(component_in_number, component_in_path):
            component_func1(component_in_number=component_in_number, component_in_path=component_in_path)

        @dsl.pipeline
        def root_pipeline(component_in_number, component_in_path):
            sub_pipeline(component_in_number=component_in_number, component_in_path=component_in_path)

        job_input = Input(
            type=AssetTypes.URI_FILE,
            path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
        )
        pipeline_job: PipelineJob = root_pipeline(10, job_input)
        validate_result = pipeline_job._validate()
        # Note: top level input will not raise type unknown error here
        assert validate_result.error_messages == {
            "jobs.sub_pipeline.inputs.component_in_number": "Parameter type unknown, "
            "please add type annotation or specify input default value.",
            "jobs.sub_pipeline.inputs.component_in_path": "Parameter type unknown, "
            "please add type annotation or specify input default value.",
            "jobs.sub_pipeline.jobs.microsoftsamples_command_component_basic.compute": "Compute not set",
        }

    def test_pipeline_optional_link_to_required(self):
        default_optional_func = load_component(str(components_dir / "default_optional_component.yml"))

        # None pipeline parameter is binding to two component.

        @dsl.pipeline(
            default_compute="cpu-cluster",
        )
        def pipeline_with_default_optional_parameters(
            required_input: Input(optional=True),
            required_param,
            required_param_with_default,
            optional_param_with_default,
            optional_param,
        ):
            # In the first component, optional_param_with_default is binding to two optional component inputs.
            default_optional_func(
                required_input=required_input,
                required_param=required_param,
                required_param_with_default=required_param_with_default,
                optional_param=optional_param_with_default,
                optional_param_with_default=optional_param_with_default,
            )

        pipeline = pipeline_with_default_optional_parameters(
            required_input=Input(path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
            required_param="hello",
            required_param_with_default="required_param_with_default",
            optional_param_with_default=None,
            optional_param="optional_param",
        )
        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "inputs.required_input": "Pipeline optional Input binding to required inputs: ['default_optional_component.inputs.required_input']"
        }

    def test_node_unknown_property_setting(self) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)
        job_input = Input(
            type=AssetTypes.URI_FILE,
            path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
        )

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)
            node1.jeff_special_option.foo = "bar"
            node1.compute = "cpu-cluster"

        dsl_pipeline: PipelineJob = pipeline(10, job_input)

        with patch("azure.ai.ml.entities._validation.core.module_logger.warning") as mock_logging:
            dsl_pipeline._validate(raise_error=True)
            mock_logging.assert_called_with("Warnings: [jobs.node1.jeff_special_option: Unknown field.]")

    def test_node_required_field_missing(self) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"
        component_func1 = load_component(path)
        job_input = Input(
            type=AssetTypes.URI_FILE,
            path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
        )

        @dsl.pipeline()
        def pipeline(component_in_number, component_in_path):
            node1 = component_func1(component_in_number=component_in_number, component_in_path=component_in_path)

            node2 = node1.sweep(
                goal="maximize",
                primary_metric="accuracy",
                sampling_algorithm="random",
            )
            node2.compute = "cpu-cluster"
            node2.jeff_special_option.foo = "bar"

        dsl_pipeline: PipelineJob = pipeline(10, job_input)

        validation_result = dsl_pipeline._validate()
        assert validation_result.error_messages == {"jobs.node2.limits": "Missing data for required field."}

    def test_node_schema_validation(self) -> None:
        path = "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml"
        batch_inference1 = load_component(path)

        # Construct pipeline
        @dsl.pipeline(default_compute="cpu-cluster", experiment_name="sdk-cli-v2")
        def parallel_in_pipeline(job_data_path):
            batch_inference_node1 = batch_inference1(job_data_path=job_data_path)
            batch_inference_node1.outputs.job_output_path.type = AssetTypes.MLTABLE

            return {"job_out_data": batch_inference_node1.outputs.job_output_path}

        pipeline = parallel_in_pipeline(
            job_data_path=Input(
                type=AssetTypes.MLTABLE,
                path="./tests/test_configs/dataset/mnist-data/",
                mode=InputOutputModes.EVAL_MOUNT,
            ),
        )

        with patch("azure.ai.ml.entities._validation.core.module_logger.info") as mock_logging:
            pipeline._validate()
            mock_logging.assert_not_called()

    def test_node_base_path_resolution(self):
        # load with a different root_base_path first as nested.schema will be initialized only once by default
        test_path = "./tests/test_configs/pipeline_jobs/inline_file_comp_base_path_sensitive/pipeline.yml"
        load_job(test_path)

        component_path = (
            "./tests/test_configs/pipeline_jobs/inline_file_comp_base_path_sensitive/component/component.yml"
        )

        @dsl.pipeline()
        def pipeline_no_arg():
            component_func = load_component(component_path)
            r_iris_example = component_func(iris=Input(path="/a/path/on/ds"))
            r_iris_example.compute = "cpu-cluster"

        pipeline_job = pipeline_no_arg()
        pipeline_job._validate(raise_error=True)
        # return origin value as no base path change
        assert pipeline_job.jobs["r_iris_example"].component.code == "../../../python"

    def test_dsl_pipeline_with_use_node_with_multiple_output_as_input(self):
        path = "./tests/test_configs/components/merge_outputs_component.yml"
        component_func1 = load_component(path)

        @dsl.pipeline(name="pipeline_with_use_node_with_multiple_output_as_input")
        def pipeline_with_use_node_with_multiple_output_as_input(component_in_number: int, component_in_path: str):
            node1 = component_func1(
                component_in_number=component_in_number,
                component_in_path_1=component_in_path,
                component_in_path_2=component_in_path,
            )
            node2 = component_func1(
                component_in_number=component_in_number,
                component_in_path_1=node1,
                component_in_path_2=node1,  # use a node as the input
            )
            return {"pipeline_out": node2.outputs.component_out_path_1}

        with pytest.raises(ValidationException) as ex:
            pipeline_with_use_node_with_multiple_output_as_input(10, "test")
            assert "Exactly 1 output is required, got 2. ({'component_out_path_1': <azure.ai.m" in ex.__str__()

    @pytest.mark.usefixtures("enable_pipeline_private_preview_features")
    def test_dsl_pipeline_with_compute_binding(self):
        path = "./tests/test_configs/components/merge_outputs_component.yml"
        component_func1 = load_component(path)

        @dsl.pipeline
        def sub_pipeline_with_compute_binding(compute_name: str):
            node1 = component_func1(
                component_in_number=1,
                component_in_path_1="test",
                component_in_path_2="test2",
            )
            node1.compute = compute_name

        @dsl.pipeline
        def pipeline_with_compute_binding(compute_name: str):
            node1 = component_func1(
                component_in_number=1,
                component_in_path_1="test",
                component_in_path_2="test2",
            )
            node1.compute = compute_name
            sub_pipeline_with_compute_binding(compute_name)

        pipeline_job = pipeline_with_compute_binding("cpu-cluster")
        # Assert compute binding validate not raise error when validate
        assert pipeline_job._validate().passed

    @pytest.mark.usefixtures(
        "enable_pipeline_private_preview_features",
        "enable_private_preview_pipeline_node_types",
        "enable_private_preview_schema_features",
    )
    def test_pipeline_with_invalid_do_while_node(self) -> None:
        with pytest.raises(ValidationError) as exception:
            load_job(
                "./tests/test_configs/pipeline_jobs/control_flow/do_while/invalid_pipeline.yml",
            )
        error_message_str = re.findall(r"(\{.*\})", exception.value.args[0].replace("\n", ""))[0]
        error_messages = json.loads(error_message_str)

        def assert_error_message(path, except_message, error_messages):
            msgs = next(filter(lambda item: item["path"] == path, error_messages))
            assert except_message == msgs["message"]

        assert_error_message("jobs.empty_mapping.mapping", "Missing data for required field.", error_messages["errors"])
        assert_error_message(
            "jobs.out_of_range_max_iteration_count.limits.max_iteration_count",
            "Must be greater than or equal to 1 and less than or equal to 1000.",
            error_messages["errors"],
        )
        assert_error_message(
            "jobs.invalid_max_iteration_count.limits.max_iteration_count",
            "Not a valid integer.",
            error_messages["errors"],
        )

    def test_arm_id_pipeline_node_compute(self) -> None:
        job = load_job("./tests/test_configs/pipeline_jobs/pipeline_job_with_registered_pipeline_component.yml")
        validation_result = job._validate_compute_is_set()
        assert validation_result.passed

    def test_dsl_data_transfer_import_pipeline_with_invalid_outputs(self) -> None:
        query_source_snowflake = "select * from TPCH_SF1000.PARTSUPP limit 10"
        connection_target_azuresql = "azureml:my_snowflake_connection"
        outputs = {
            "test": Output(
                type=AssetTypes.URI_FOLDER,
                path="azureml://datastores/workspaceblobstore_sas/paths/importjob/${{name}}/output_dir/snowflake/",
            ),
            "sink": Output(
                type=AssetTypes.URI_FOLDER,
                path="azureml://datastores/workspaceblobstore_sas/paths/importjob/${{name}}/output_dir/snowflake/",
            ),
        }

        @dsl.pipeline(description="submit a pipeline with data transfer import database job")
        def data_transfer_import_database_pipeline_from_builder(query_source_snowflake, connection_target_azuresql):
            from azure.ai.ml.data_transfer import Database, import_data

            source_snowflake = Database(query=query_source_snowflake, connection=connection_target_azuresql)
            snowflake_blob = import_data(
                source=source_snowflake,
                outputs=outputs,
            )

        pipeline = data_transfer_import_database_pipeline_from_builder(
            query_source_snowflake, connection_target_azuresql
        )
        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "jobs.snowflake_blob.compute": "Compute not set",
            "jobs.snowflake_blob.outputs.sink": "Outputs field only support one output called sink in import task",
            "jobs.snowflake_blob.outputs.sink.type": "Outputs field only support type mltable for database and uri_"
            "folder for file_system",
        }

    def test_dsl_data_transfer_export_pipeline_with_invalid_inputs(self) -> None:
        connection_target_azuresql = "azureml:my_export_azuresqldb_connection"
        table_name = "dbo.Persons"
        my_cosmos_folder = Input(type=AssetTypes.URI_FOLDER, path="/data/testFile_ForSqlDB.parquet")

        @dsl.pipeline(description="submit a pipeline with data transfer export database job")
        def data_transfer_export_database_pipeline_from_builder(table_name, connection_target_azuresql, cosmos_folder):
            from azure.ai.ml.data_transfer import Database, export_data

            source_snowflake = Database(table_name=table_name, connection=connection_target_azuresql)
            blob_azuresql = export_data(
                inputs={"source": cosmos_folder, "test": my_cosmos_folder}, sink=source_snowflake
            )

        pipeline = data_transfer_export_database_pipeline_from_builder(
            table_name, connection_target_azuresql, my_cosmos_folder
        )

        validate_result = pipeline._validate()
        assert validate_result.error_messages == {
            "jobs.blob_azuresql.compute": "Compute not set",
            "jobs.blob_azuresql.inputs.source": "Inputs field only support one input called source in export task",
        }
