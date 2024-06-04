import json
import re
from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional

import pydash
import pytest
import yaml
from marshmallow import ValidationError
from pytest_mock import MockFixture

from azure.ai.ml import MLClient, load_job
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobOutput as RestJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import MLTableJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import PipelineJob as RestPipelineJob
from azure.ai.ml._restclient.v2023_04_01_preview.models import UriFolderJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models._azure_machine_learning_workspaces_enums import (
    LearningRateScheduler,
    StochasticOptimizer,
)
from azure.ai.ml._utils.utils import camel_to_snake, dump_yaml_to_file, is_data_binding_expression, load_yaml
from azure.ai.ml.constants._common import ARM_ID_PREFIX, AssetTypes, InputOutputModes
from azure.ai.ml.constants._component import ComponentJobConstants
from azure.ai.ml.constants._job.pipeline import PipelineConstants
from azure.ai.ml.entities import CommandComponent, Component, Job, PipelineJob, SparkComponent
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._component.datatransfer_component import DataTransferComponent
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.entities._credentials import UserIdentityConfiguration
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    INPUT_MOUNT_MAPPING_FROM_REST,
    validate_pipeline_input_key_characters,
)
from azure.ai.ml.entities._job.automl.search_space_utils import _convert_sweep_dist_dict_to_str_dict
from azure.ai.ml.entities._job.job_service import (
    JobService,
    JupyterLabJobService,
    SshJobService,
    TensorBoardJobService,
    VsCodeJobService,
)
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, PipelineOutput
from azure.ai.ml.exceptions import UserErrorException, ValidationException

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND, DATABINDING_EXPRESSION_TEST_CASES


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_PIPELINE_JOB_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPipelineJobSchema:
    def test_validate_pipeline_job_keys(self):
        def validator(key, assert_valid=True):
            if assert_valid:
                validate_pipeline_input_key_characters(key)
                return
            with pytest.raises(Exception):
                validate_pipeline_input_key_characters(key)

        validator("a.vsd2..", assert_valid=False)
        validator("a..b", assert_valid=False)
        validator("00a", assert_valid=False)
        validator("0.a.v", assert_valid=False)
        validator("a.", assert_valid=False)
        validator("a.b0.", assert_valid=False)
        validator("a.b.0", assert_valid=False)
        validator("0.a.v", assert_valid=False)
        validator("bba")
        validator("__")
        validator("b_ba")
        validator("_.__.___")
        validator("b0._ba")
        validator("a.b.c0")

    def test_simple_deserialize(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_no_paths.yml"
        yaml_obj = load_yaml(test_path)
        job: PipelineJob = load_job(test_path)
        # Expected REST overrides and settings are in a JSON file "settings_overrides.json"
        with open(
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_no_paths_expected_settings_override.json"
        ) as f:
            expected_rest_settings_overrides = json.load(f)
        # assert that inputs put in "values" get bubbled up to top level
        expected_inputs = {
            "job_in_number": 10,
            "job_in_other_number": 15,
            "job_in_string": "a_random_string",
        }
        assert job._build_inputs() == expected_inputs
        settings = job.settings._to_dict()
        settings = {k: v for k, v in settings.items() if v is not None and k != "force_rerun"}
        assert settings == yaml_obj["settings"]
        # check that components were loaded correctly
        hello_world_component = job.jobs["hello_world_component"]
        rest_hello_world_component = hello_world_component._to_rest_object()
        hello_world_component_yaml = yaml_obj["jobs"]["hello_world_component"]
        assert hello_world_component_yaml["type"] == hello_world_component.type
        assert hello_world_component_yaml["component"][len(ARM_ID_PREFIX) :] == hello_world_component.component
        assert rest_hello_world_component["inputs"] == {
            "component_in_number": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_number}}",
            }
        }
        hello_world_component_2 = job.jobs["hello_world_component_2"]
        rest_hello_world_component_2 = hello_world_component_2._to_rest_object()
        hello_world_component_2_yaml = yaml_obj["jobs"]["hello_world_component_2"]
        assert hello_world_component_2_yaml["type"] == hello_world_component_2.type
        assert hello_world_component_2_yaml["component"][len(ARM_ID_PREFIX) :] == hello_world_component_2.component
        assert rest_hello_world_component_2["inputs"] == {
            "component_in_number": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_other_number}}",
            }
        }
        assert expected_rest_settings_overrides["expected_rest_overrides"]["distribution"] == (
            hello_world_component_2.distribution._to_rest_object().as_dict()
        )
        assert {"FOO": "bar"} == hello_world_component_2.environment_variables
        assert {"nested_override": 5} == hello_world_component_2.additional_override

        # hello_world_component_3 = job.jobs["hello_world_component_3"]
        # rest_hello_world_component_3 = hello_world_component_3._to_rest_object()
        # hello_world_component_3_yaml = yaml_obj["jobs"]["hello_world_component_3"]
        # assert hello_world_component_3_yaml["type"] == hello_world_component_3.type
        # assert rest_hello_world_component_3["inputs"] == {
        #     "job_data_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_data_path}}"},
        #     "score_model": {"job_input_type": "literal", "value": "${{parent.inputs.score_model}}"},
        # }

        # Check that REST conversion works
        rest_job = job._to_rest_object()
        rest_pipeline_properties = rest_job.properties
        # Check inputs were properly serialized
        for input_name, input_value in yaml_obj["inputs"].items():
            assert input_name in rest_pipeline_properties.inputs
            if isinstance(input_value, dict):
                input_value = input_value.get("value", None)
            if not isinstance(rest_pipeline_properties.inputs[input_name], (MLTableJobInput, UriFolderJobInput)):
                assert str(input_value) == rest_pipeline_properties.inputs[input_name].value

        # Check settings
        assert (
            rest_pipeline_properties.settings["continue_on_step_failure"]
            == expected_rest_settings_overrides["expected_rest_settings"]["continue_on_step_failure"]
        )

        # Check that components were properly serialized:
        input_component_jobs = yaml_obj["jobs"]
        for job_name, component_job in input_component_jobs.items():
            # Check that the input component job is in the REST representation
            assert job_name in rest_pipeline_properties.jobs
            rest_component_job = rest_pipeline_properties.jobs[job_name]
            if "component" in rest_pipeline_properties.jobs[job_name]:
                assert component_job["component"][len(ARM_ID_PREFIX) :] == rest_component_job["componentId"]
            # Check the inputs are properly placed
            rest_component_job_inputs = rest_component_job["inputs"]
            for input_name, input_value in component_job["inputs"].items():
                # skip check data bindings
                if not re.match(ComponentJobConstants.INPUT_PATTERN, input_value):
                    # If given input is a literal
                    assert input_name in rest_component_job_inputs
                    # If the given input is a literal value
                    assert rest_component_job_inputs[input_name].data.value == str(input_value)
            overrides = component_job.get("overrides", None)
            if overrides:
                assert rest_component_job["overrides"]
                assert expected_rest_settings_overrides["expected_rest_overrides"] == rest_component_job["overrides"]
            # Check that the compute is properly serialized
            if "component" in rest_component_job:
                assert rest_component_job["computeId"]
                assert rest_component_job["computeId"] == component_job["compute"][len(ARM_ID_PREFIX) :]

    def test_pipeline_job_settings_compute_dump(self, mock_machinelearning_client: MLClient):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_no_paths.yml"
        job = load_job(test_path)
        job.settings.default_compute = "cpu-cluster"
        dump_str = StringIO()
        yaml.dump(job._to_dict(), dump_str)
        dump_str = dump_str.getvalue()
        # assert settings.default_compute dumped as arm str
        assert "continue_on_step_failure: true" in dump_str
        assert "default_compute: azureml:cpu-cluster" in dump_str

    def test_literal_input_types(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_comps.yml"
        job = load_job(test_path)
        expected_inputs = {"job_in_number": 10.01, "job_in_other_number": 15}
        assert job._build_inputs() == expected_inputs
        assert isinstance(job.inputs["job_in_number"], PipelineInput)
        assert isinstance(job.inputs.job_in_number._data, float)
        assert isinstance(job.inputs["job_in_other_number"], PipelineInput)
        assert isinstance(job.inputs.job_in_other_number._data, int)

    def test_sweep_node(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_sweep_node.yml"
        pipeline: PipelineJob = load_job(test_path)
        pipeline_dict = pipeline._to_dict()
        for key, expected_value in [
            ("jobs.hello_sweep_inline_trial.objective.goal", "maximize"),
            ("jobs.hello_sweep_inline_remote_trial.objective.goal", "maximize"),
            (
                "jobs.hello_sweep_inline_remote_trial.trial",
                "azureml:microsoftsamplescommandcomponentbasic_nopaths_test:1",
            ),
        ]:
            loaded_value = pydash.get(pipeline_dict, key, None)
            assert loaded_value == expected_value, f"{key} isn't as expected: {loaded_value} != {expected_value}"

    def test_literal_inputs_fidelity_in_yaml_dump(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_no_paths.yml"
        job = load_job(test_path)

        reconstructed_yaml = job._to_dict()
        assert reconstructed_yaml["inputs"] == job._build_inputs()

    def test_pipeline_job_with_inputs(self, mock_machinelearning_client: MLClient, mocker: MockFixture) -> None:
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_data_options_no_outputs.yml"
        yaml_obj = load_yaml(test_path)
        job = load_job(test_path)

        # Check that all inputs are present and are of type Input
        for input_name in yaml_obj["inputs"].keys():
            job_obj_input = job.inputs.get(input_name, None)
            assert job_obj_input is not None
            assert isinstance(job_obj_input, PipelineInput)
            assert isinstance(job_obj_input._data, Input)

        # "Upload" the dependencies so that the dataset serialization behavior can be verified
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mocker.patch(
            "azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri",
            return_value="yyy",
        )
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
        # Convert to REST object and check that all inputs were turned into data inputs
        rest_job = job._to_rest_object()
        for input_name, input_value in yaml_obj["inputs"].items():
            rest_input = rest_job.properties.inputs.get(input_name, None)
            assert rest_input
            # Test that the dataset fields get populated
            job_input = job.inputs[input_name]._data
            assert rest_input.uri == job_input.path
            # Test that mode was properly serialized
            # TODO: https://msdata.visualstudio.com/Vienna/_workitems/edit/1318153/ For now, check that mode is present until new delivery types are supported.
            # yaml_input_mode = input_value.get("mode", InputDataDeliveryMode.READ_WRITE_MOUNT)
            if rest_input.mode:
                assert INPUT_MOUNT_MAPPING_FROM_REST[rest_input.mode] == job_input.mode
            else:
                assert job_input.mode is None

        # Test that translating from REST preserves the inputs
        from_rest_job = PipelineJob._from_rest_object(rest_job)
        for input_name, input_value in rest_job.properties.inputs.items():
            from_rest_input = from_rest_job.inputs[input_name]
            assert from_rest_input is not None
            assert isinstance(from_rest_input, PipelineInput)
            assert isinstance(from_rest_input._data, Input)

            assert from_rest_input._data.path == input_value.uri
            # For now, just check that there is a mode present until new data delivery types are supported.
            # TODO: https://msdata.visualstudio.com/Vienna/_workitems/edit/1318153/ For now, check that mode is present until new delivery types are supported.
            if from_rest_input.mode is None:
                assert input_value.mode is None
            else:
                assert from_rest_input.mode == INPUT_MOUNT_MAPPING_FROM_REST[input_value.mode]

    def test_pipeline_job_with_inputs_dataset(self, mock_machinelearning_client: MLClient, mocker: MockFixture) -> None:
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_dataset_options_no_outputs.yml"
        yaml_obj = load_yaml(test_path)
        job = load_job(test_path)  # type: PipelineJob

        # Check that all inputs are present and are of type InputOutputEntry
        for input_name in yaml_obj["inputs"].keys():
            job_obj_input = job.inputs.get(input_name, None)
            assert job_obj_input is not None
            assert isinstance(job_obj_input, PipelineInput)
            assert isinstance(job_obj_input._data, Input) or isinstance(job_obj_input._data, Input)

        # "Upload" the depedencies so that the dataset serialization behavior can be verified
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
        # Convert to REST object and check that all inputs were turned into data inputs
        rest_job = job._to_rest_object()
        for input_name, input_value in yaml_obj["inputs"].items():
            rest_input = rest_job.properties.inputs.get(input_name, None)
            assert rest_input is not None
            # Test that the dataset fields get populated
            assert rest_input.uri == job.inputs[input_name]._data.path
            # Test that mode was properly serialized
            # TODO: https://msdata.visualstudio.com/Vienna/_workitems/edit/1318153/ For now, check that mode is present until new delivery types are supported.
            # yaml_input_mode = input_value.get("mode", InputDataDeliveryMode.READ_WRITE_MOUNT)
            if rest_input.mode:
                assert INPUT_MOUNT_MAPPING_FROM_REST[rest_input.mode] == job.inputs[input_name]._data.mode
            else:
                assert job.inputs[input_name]._data.mode is None

        # Test that translating from REST preserves the inputs
        from_rest_job = PipelineJob._from_rest_object(rest_job)
        for input_name, input_value in rest_job.properties.inputs.items():
            from_rest_input = from_rest_job.inputs[input_name]
            assert from_rest_input is not None
            assert isinstance(from_rest_input, PipelineInput)
            from_rest_input = from_rest_input._to_job_input()

            if isinstance(from_rest_input, Input):
                assert from_rest_input.path == input_value.uri
            else:
                raise AssertionError("must be InputOutputEntry or Input")
            # For now, just check that there is a mode present until new data delivery types are supported.
            # TODO: https://msdata.visualstudio.com/Vienna/_workitems/edit/1318153/ For now, check that mode is present until new delivery types are supported.
            if from_rest_input.mode is None:
                assert input_value.mode is None
            else:
                assert from_rest_input.mode == INPUT_MOUNT_MAPPING_FROM_REST[input_value.mode]

    def test_pipeline_job_components_with_inputs(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ) -> None:
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_comps_data_options_no_outputs.yml"
        yaml_obj = load_yaml(test_path)
        job = load_job(test_path)

        # Check that all inputs are present in the jobs
        for job_name, job_value in yaml_obj["jobs"].items():
            job_obj = job.jobs.get(job_name, None)
            assert job_obj is not None
            for input_name, input_value in job_value["inputs"].items():
                job_input = job_obj.inputs[input_name]._to_job_input()
                if isinstance(input_value, str):
                    if isinstance(job_input, Input) and is_data_binding_expression(job_input.path):
                        job_input = job_input.path
                    assert isinstance(job_input, str)
                else:
                    assert isinstance(job_input, Input)

        # "Upload" the depedencies so that the dataset serialization behavior can be verified
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
        # Convert to REST object and check that all inputs were turned into data inputs
        rest_job = job._to_rest_object()
        # Test that each job's inputs were serialized properly in the REST translation
        expected_inputs = {
            "component_in_3": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.inputvalue}}",
            }
        }
        assert rest_job.properties.jobs["multiple_data_component"]["inputs"] == expected_inputs

        # Test that translating from REST preserves the inputs for each job. In this case, they are all bindings
        from_rest_job = PipelineJob._from_rest_object(rest_job)
        from_rest_job.jobs["multiple_data_component"]["inputs"] == expected_inputs

    def test_pipeline_job_components_with_inline_dataset(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ) -> None:
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_component_output.yml"
        yaml_obj = load_yaml(test_path)
        job = load_job(test_path)
        # Check that all inputs are present in the jobs are of type str or Input
        for job_name, job_value in yaml_obj["jobs"].items():
            job_obj = job.jobs.get(job_name, None)
            assert job_obj is not None
            for input_name, input_value in job_value["inputs"].items():
                job_input = job_obj.inputs[input_name]._to_job_input()
                if isinstance(input_value, str):
                    if isinstance(job_input, Input) and is_data_binding_expression(job_input.path):
                        job_input = job_input.path
                    assert isinstance(job_input, str)
                else:
                    assert isinstance(job_input, Input)

    def test_pipeline_component_job_with_outputs(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ) -> None:
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_data_options.yml"
        yaml_obj = load_yaml(test_path)
        job = load_job(test_path)

        # Check that all outputs are present and are of type Input
        for output_name in yaml_obj["outputs"].keys():
            job_obj_output = job.outputs.get(output_name, None)
            assert job_obj_output is not None
            assert isinstance(job_obj_output, PipelineOutput)
            job_obj_output = job_obj_output._to_job_output()
            assert isinstance(job_obj_output, Output)

        # Check that all outputs for the component jobs are present or of type string or Input
        for job_name, job_value in yaml_obj["jobs"].items():
            component_job = job.jobs.get(job_name, None)
            assert component_job is not None
            for output_name, output_value in job_value["outputs"].items():
                component_job_output = component_job.outputs.get(output_name, None)
                assert component_job_output is not None
                if isinstance(output_value, dict):
                    # case where user specifies inline output
                    assert output_value["mode"] == component_job_output.mode
                else:
                    # case where user specifies an input binding
                    assert output_value == component_job_output._data

        # Convert to REST object and check that all outputs were correctly turned into REST format
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mocker.patch(
            "azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri",
            return_value="yyy",
        )
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
        rest_job = job._to_rest_object()
        rest_component_jobs = rest_job.properties.jobs

        # Check serialization of top-level job
        for output_name, output_value in yaml_obj["outputs"].items():
            output_data = output_value.get("data", None)
            if output_data:
                rest_job_obj_output = rest_job.properties.outputs.get(output_name, None)
                assert rest_job_obj_output
                assert isinstance(rest_job_obj_output, RestJobOutput)
                # TODO https://msdata.visualstudio.com/Vienna/_workitems/edit/1318153: Put this check back once outputs work again
                # self._check_data_output_rest_formatting(rest_job_obj_output, output_value)

        # Check the serialization behavior of each ComponentJob
        expected_outputs = {
            "component_out_1": {
                "type": "literal",
                "value": "${{parent.outputs.job_in_data_name}}",
            },
            "component_out_2": {
                "type": "literal",
                "value": "${{parent.outputs.job_in_data_name_upload}}",
            },
            "component_out_3": {
                "type": "literal",
                "value": "${{parent.outputs.job_in_data_name_mount}}",
            },
            "component_out_4": {
                "type": "literal",
                "value": "${{parent.outputs.job_out_data_name_apart}}",
            },
            "component_out_5": {
                "type": "literal",
                "value": "${{parent.outputs.job_out_data_path}}",
            },
            "component_out_6": {
                "type": "literal",
                "value": "${{parent.outputs.job_out_data_store_path_upload}}",
            },
            "component_out_7": {
                "type": "literal",
                "value": "${{parent.outputs.job_out_data_store_path_mount}}",
            },
            "component_out_8": {
                "type": "literal",
                "value": "${{parent.outputs.job_out_data_store_url}}",
            },
            "component_out_9": {"job_output_type": "uri_folder", "mode": "Upload"},
        }
        expected_inputs = {
            "component_in_1": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_name_version_def_mode}}",
            },
            "component_in_2": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_name_version_mode_mount}}",
            },
            "component_in_3": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_name_version_mode_download}}",
            },
            "component_in_4": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_by_name}}",
            },
            "component_in_5": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_by_armid}}",
            },
            "component_in_6": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_by_store_path}}",
            },
            "component_in_7": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_by_path_default_store}}",
            },
            "component_in_8": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_by_store_path_and_mount}}",
            },
            "component_in_9": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_by_store_path_and_download}}",
            },
            "component_in_10": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_by_blob_dir}}",
            },
            "component_in_11": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_by_blob_file}}",
            },
            "component_in_12": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_local_dir}}",
            },
            "component_in_13": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_local_file}}",
            },
            "component_in_14": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_local_yaml_definition}}",
            },
            "component_in_15": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.job_in_data_uri}}",
            },
        }
        assert rest_component_jobs["multiple_data_component"]["outputs"] == expected_outputs
        assert rest_component_jobs["multiple_data_component"]["inputs"] == expected_inputs

        # Check the from REST behavior
        from_rest_job = PipelineJob._from_rest_object(rest_job)

        # Check that outputs were properly converted from REST format to SDK format
        for output_name, output_value in rest_job.properties.outputs.items():
            from_rest_output = from_rest_job.outputs.get(output_name, None)
            assert from_rest_output is not None
            assert isinstance(from_rest_output, PipelineOutput)
            from_rest_output = from_rest_output._to_job_output()
            assert isinstance(from_rest_output, Output)

        # Check that outputs were properly converted from REST format to SDK format for each ComponentJob
        from_rest_component_job = from_rest_job.jobs.get("multiple_data_component", None)
        assert from_rest_component_job is not None

        from_rest_component_job = from_rest_component_job._to_rest_object()
        assert from_rest_component_job["outputs"] == expected_outputs
        assert from_rest_component_job["inputs"] == expected_inputs

    def _check_data_output_rest_formatting(self, rest_output: RestJobOutput, yaml_output: Dict[str, Any]) -> None:
        rest_output_data = rest_output.data
        assert rest_output_data
        yaml_output_data = yaml_output["data"]
        assert rest_output_data
        assert rest_output_data.datapath == yaml_output_data.get("path", None)
        if yaml_output_data.get("datastore", None):
            assert rest_output_data.default_datastore == "xxx"

        if yaml_output_data.get("name"):
            assert rest_output_data.dataset_name == yaml_output_data.get("name")
        else:
            # If yaml name was None, assert that no name is present in REST output
            assert not rest_output_data.dataset_name

        mode = yaml_output.get("mode", None)
        if mode:
            assert rest_output_data.mode.lower() == mode.lower()

    def _check_data_output_from_rest_formatting(self, rest_output_data: RestJobOutput, from_rest_output: Input) -> None:
        from_rest_output_data = from_rest_output.data
        assert from_rest_output_data
        assert from_rest_output_data.path == rest_output_data.datapath
        assert from_rest_output_data.default_datastore == rest_output_data.datastore

        if rest_output_data.dataset_name:
            assert from_rest_output_data.name == rest_output_data.dataset_name
        else:
            # If rest name was None, assert neither name nor version are present in from_rest_output_data
            assert not from_rest_output_data.name
            assert not from_rest_output_data.version

        if rest_output_data.mode:
            assert from_rest_output.mode == rest_output_data.mode

    def assert_inline_component(self, component_job, component_dict):
        assert isinstance(
            component_job.component, (CommandComponent, ParallelComponent, SparkComponent, DataTransferComponent)
        )
        component = component_job.component or component_job.trial
        assert component._is_anonymous
        # hash will be generated before create_or_update, so can't check it in unit tests
        assert list(component.inputs.keys()) == list(component_dict.get("inputs", {}).keys())
        assert list(component.outputs.keys()) == list(component_dict.get("outputs", {}).keys())

    def test_pipeline_job_inline_component(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_comps.yml"
        job = load_job(test_path)
        # make sure inline component is parsed into component entity
        hello_world_component = job.jobs["hello_world_component_inline"]
        component_dict = load_yaml(test_path)["jobs"]["hello_world_component_inline"]["component"]
        self.assert_inline_component(hello_world_component, component_dict)

    def test_pipeline_job_inline_component_file(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_file_comps.yml"
        job = load_job(test_path)
        # make sure inline component is parsed into component entity
        hello_world_component = job.jobs["hello_world_component_inline_file"]
        component_dict = load_yaml("./tests/test_configs/components/helloworld_component.yml")
        self.assert_inline_component(hello_world_component, component_dict)

        test_path = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/pipeline.yml"
        job = load_job(test_path)
        # make sure inline component is parsed into component entity
        spark_component = job.jobs["add_greeting_column"]
        component_dict = load_yaml(
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/add_greeting_column_component.yml"
        )
        self.assert_inline_component(spark_component, component_dict)

        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/merge_files_job.yaml"
        job = load_job(test_path)
        # make sure inline component is parsed into component entity
        spark_component = job.jobs["merge_files_job"]
        component_dict = load_yaml("./tests/test_configs/components/data_transfer/merge_files.yaml")
        self.assert_inline_component(spark_component, component_dict)

        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/copy_files.yaml"
        job = load_job(test_path)
        # make sure inline component is parsed into component entity
        spark_component = job.jobs["copy_files"]
        component_dict = load_yaml("./tests/test_configs/components/data_transfer/copy_files.yaml")
        self.assert_inline_component(spark_component, component_dict)

    def test_pipeline_job_inline_component_file_with_complex_path(self):
        # parallel component
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_file_parallel.yml"
        job = load_job(test_path)
        # make sure inline component is parsed into component entity
        hello_world_component = job.jobs["hello_world_inline_paralleljob"]
        component_dict = load_yaml("./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/score.yml")
        self.assert_inline_component(hello_world_component, component_dict)

    def test_pipeline_job_inline_component_file_parallel_with_user_identity(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_file_parallel.yml"
        job = load_job(test_path)
        assert isinstance(job.jobs["hello_world_inline_paralleljob"].identity, UserIdentityConfiguration)

    @classmethod
    def assert_settings_field(
        cls,
        pipeline_job: PipelineJob,
        mock_machinelearning_client: MLClient,
        mocker: MockFixture,
    ):
        def mock_get_asset_arm_id(*args, **kwargs):
            if len(args) > 0:
                arg = args[0]
                if isinstance(arg, str):
                    return arg
                elif isinstance(arg, Code):
                    return arg.path
                elif isinstance(arg, Component):
                    # instead of returning a fake arm id here, we return the internal object for later value check
                    return arg
            return "xxx"

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            side_effect=mock_get_asset_arm_id,
        )
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(pipeline_job)

        # Check that if compute was specified, it was resolved
        # Otherwise, it should be left unset since the backend will apply the default
        for job_name, job in pipeline_job.jobs.items():
            if job_name == "hello_world_component_with_compute":
                assert job.compute == "cpu-cluster"
            else:
                assert job.compute == "xxx"

        rest_job = pipeline_job._to_rest_object()

        # Check that default datastore is filled in

        def assert_setting(rest_job, key, value):
            assert rest_job.properties.settings.get(key, None) == value

        assert_setting(rest_job, PipelineConstants.DEFAULT_DATASTORE, "workspacefilestore")
        assert_setting(rest_job, PipelineConstants.DEFAULT_COMPUTE, "cpu-cluster-1")
        assert_setting(rest_job, PipelineConstants.CONTINUE_ON_STEP_FAILURE, True)

        # check that default dictionary is created when translating from REST
        from_rest_job = PipelineJob._from_rest_object(rest_job)
        assert from_rest_job.settings
        assert from_rest_job.settings.default_datastore == "workspacefilestore"
        assert from_rest_job.settings.default_compute == "cpu-cluster-1"
        assert from_rest_job.settings.continue_on_step_failure is True

    def test_pipeline_job_settings_field(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults.yml"

        job = load_job(test_path)
        self.assert_settings_field(job, mock_machinelearning_client, mocker)
        # Test the case the compute is only defined in the top-level
        rest_job = job._to_rest_object()
        assert rest_job.properties.compute_id == "cpu-cluster"
        assert rest_job.properties.compute_id == job.compute

    def test_set_unknown_pipeline_job_settings(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults.yml"

        job: PipelineJob = load_job(
            test_path,
            params_override=[
                {
                    "settings._yaml_unknown": "_xxx",
                    "settings.yaml_unknown": "xxx",
                }
            ],
        )
        job.settings.unknown_setting = "unknown"
        job.settings._enable_dataset_mode = True
        job.settings.foo.bar = "xxx"
        # job.settings._foo.bar = "xxx" is not supported
        expected_dict = {
            "_source": "YAML.JOB",
            "default_datastore": "workspacefilestore",
            "default_compute": "cpu-cluster-1",
            "continue_on_step_failure": True,
            "unknown_setting": "unknown",
            "_enable_dataset_mode": True,
            "foo": {
                "bar": "xxx",
            },
            "_yaml_unknown": "_xxx",
            "yaml_unknown": "xxx",
        }
        assert job._to_rest_object().properties.settings == expected_dict

    def test_pipeline_job_settings_field_inline_commandjob(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_with_command_job_e2e.yml"
        pipeline_job = load_job(test_path)

        def mock_get_asset_arm_id(*args, **kwargs):
            if len(args) > 0:
                arg = args[0]
                if isinstance(arg, str):
                    return arg
                elif isinstance(arg, Code):
                    return arg.local_path
                elif isinstance(arg, (Component, Job)):
                    # instead of returning a fake arm id here, we return the internal object for later value check
                    return arg
            return "xxx"

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            side_effect=mock_get_asset_arm_id,
        )
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(pipeline_job)

        # Check that if compute was specified, it was resolved
        # Otherwise, it should be left unset since the backend will apply the default
        for job_name, job in pipeline_job.jobs.items():
            if job_name == "hello_world_inline_commandjob_1":
                assert job.compute == "cpu-cluster"
            else:
                assert job.compute == "xxx"

    @pytest.mark.parametrize(
        "test_path,expected_inputs",
        [
            pytest.param(
                "tests/test_configs/pipeline_jobs/pipeline_job_with_sweep_job_with_input_bindings.yml",
                {
                    "hello_world": {
                        "test1": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_data_path}}",
                        },
                    },
                    "hello_world_inline_commandjob_2": {
                        "input_from_previous_node": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.hello_world.outputs.job_output}}",
                        },
                        "test2": {"job_input_type": "literal", "value": "${{parent.inputs.job_data_path}}"},
                    },
                },
                id="pipeline_job_with_sweep_job_with_input_bindings",
            ),
            pytest.param(
                "tests/test_configs/pipeline_jobs/pipeline_job_with_command_job_with_input_bindings.yml",
                {
                    "hello_world": {
                        "literal_input": {"job_input_type": "literal", "value": "2"},
                        "test1": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_data_path}}",
                        },
                        "test2": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_data_path}}",
                        },
                    },
                    "hello_world_inline_commandjob_2": {
                        "input_from_previous_node": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.hello_world.outputs.job_output}}",
                        },
                        "test2": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_data_path}}",
                        },
                    },
                },
                id="pipeline_job_with_command_job_with_input_bindings",
            ),
            pytest.param(
                "tests/test_configs/pipeline_jobs/pipeline_job_with_parallel_job_with_input_bindings.yml",
                {
                    "hello_world": {
                        "job_data_path": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.job_data_path}}",
                        }
                    },
                },
                id="pipeline_job_with_parallel_job_with_input_bindings",
            ),
            pytest.param(
                "tests/test_configs/pipeline_jobs/pipeline_job_with_spark_job_with_input_bindings.yml",
                {
                    "hello_world": {
                        "test1": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.iris_data}}",
                        },
                        "file_input2": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.iris_data}}",
                        },
                    }
                },
                id="pipeline_job_with_spark_job_with_input_bindings",
            ),
        ],
    )
    def test_pipeline_job_with_input_bindings(
        self,
        mock_machinelearning_client: MLClient,
        mocker: MockFixture,
        test_path: str,
        expected_inputs: Dict[str, Any],
    ):
        yaml_obj = load_yaml(test_path)
        job = load_job(test_path)

        # no on-load check for sweep for now
        if "sweep" not in test_path:
            # check when top level input not exist
            with pytest.raises(Exception) as e:
                load_job(
                    test_path,
                    params_override=[{"jobs.hello_world.inputs.test1": "${{parent.inputs.not_found}}"}],
                )
            assert "Failed to find top level definition for input binding" in str(e.value)

        # Check that all inputs are present and are of type Input or are literals
        for input_name, input_yaml in yaml_obj["inputs"].items():
            job_obj_input = job.inputs.get(input_name, None)
            assert job_obj_input is not None, f"Input {input_name} not found in loaded job"
            assert isinstance(job_obj_input, PipelineInput)
            job_obj_input = job_obj_input._to_job_input()
            if isinstance(input_yaml, dict):
                assert isinstance(job_obj_input, Input)
            else:
                assert isinstance(job_obj_input, int)
        # Check that all inputs are present in the jobs
        for job_name, job_value in yaml_obj["jobs"].items():
            job_obj = job.jobs.get(job_name, None)
            assert job_obj is not None
            for input_name, input_value in job_obj._build_inputs().items():
                # check for input ports or literal
                if isinstance(input_value, str):
                    assert isinstance(job_obj.inputs[input_name]._data, str)
                if isinstance(input_value, int):
                    assert isinstance(job_obj.inputs[input_name]._data, int)

        # "Upload" the dependencies so that the dataset serialization behavior can be verified
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
        # Convert to REST object and check that all inputs were turned into data inputs
        rest_job = job._to_rest_object()
        rest_job_properties: RestPipelineJob = rest_job.properties
        rest_component_jobs = rest_job_properties.jobs

        # Test that each job's inputs were serialized properly in the REST translation
        for job_name, job_value in yaml_obj["jobs"].items():
            component_job = rest_component_jobs[job_name]
            assert isinstance(component_job, dict)
            # Check that each input in the yaml is properly serialized in the REST translation
            assert component_job["inputs"] == expected_inputs[job_name]
        # Test that translating from REST preserves the inputs for each job
        from_rest_job = PipelineJob._from_rest_object(rest_job)
        rest_job = job._to_rest_object()
        for job_name, job_value in from_rest_job.jobs.items():
            rest_component = rest_job.properties.jobs[job_name]
            assert expected_inputs[job_name] == rest_component["inputs"]

    @pytest.mark.parametrize(
        "pipeline_path,expected_input_outputs",
        [
            (
                "helloworld_pipeline_job_with_command_job_with_inputs_outputs.yml",
                {
                    "hello_world_inline_commandjob_1": {
                        "inputs": {
                            "literal_input": {
                                "job_input_type": "literal",
                                "value": "7",
                            },
                            "test1": {
                                "job_input_type": "uri_file",
                                "mode": "ReadOnlyMount",
                                "uri": "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                            },
                            "test2": {
                                "job_input_type": "uri_file",
                                "mode": "ReadOnlyMount",
                                "uri": "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                            },
                        }
                    },
                    "hello_world_inline_commandjob_2": {
                        "inputs": {
                            "test1": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.job_data}}",
                            },
                            "test2": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.hello_world_inline_commandjob_1.outputs.test1}}",
                            },
                            "test3": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.hello_world_inline_commandjob_3.outputs.test1}}",
                            },
                        }
                    },
                },
            ),
            ("type_contract/mltable.yml", {}),
            ("type_contract/mlflow_model.yml", {}),
            ("type_contract/custom_model.yml", {}),
            (
                "type_contract/path.yml",
                {
                    "hello_world_component": {
                        "inputs": {
                            "component_in_file": {
                                "job_input_type": "uri_file",
                                "uri": "azureml://datastores/mydatastore/paths/data/iris.csv",
                            },
                            "component_in_folder": {
                                "job_input_type": "uri_folder",
                                "uri": "azureml://datastores/mydatastore/paths/data/",
                            },
                            "component_in_path": {
                                "job_input_type": "uri_file",
                                "uri": "azureml://datastores/mydatastore/paths/data/iris.csv",
                            },
                        }
                    },
                    "hello_world_component_2": {
                        "inputs": {
                            "component_in_file": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.outputs.component_out_file}}",
                            },
                            "component_in_folder": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.outputs.component_out_folder}}",
                            },
                            "component_in_path": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.outputs.component_out_folder}}",
                            },
                        }
                    },
                },
            ),
            (
                "pipeline_job_number_type.yml",
                {
                    "hello_world_inline_commandjob_1": {
                        "inputs": {
                            "integer_input": {
                                "job_input_type": "literal",
                                "value": "7",
                            },
                            "test1": {
                                "job_input_type": "uri_file",
                                "mode": "ReadOnlyMount",
                                "uri": "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                            },
                            "test2": {
                                "job_input_type": "uri_file",
                                "mode": "ReadOnlyMount",
                                "uri": "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                            },
                            "float_input": {
                                "job_input_type": "literal",
                                "value": "1.0",
                            },
                            "boolean1": {"job_input_type": "literal", "value": "True"},
                            "boolean2": {"job_input_type": "literal", "value": "False"},
                            "boolean3": {"job_input_type": "literal", "value": "True"},
                        }
                    },
                    "hello_world_inline_commandjob_2": {
                        "inputs": {
                            "test1": {
                                "job_input_type": "literal",
                                "value": "${{parent.inputs.job_data}}",
                            },
                            "test2": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.hello_world_inline_commandjob_1.outputs.test1}}",
                            },
                            "test3": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.hello_world_inline_commandjob_3.outputs.test1}}",
                            },
                        }
                    },
                },
            ),
        ],
    )
    def test_pipeline_job_command_job_with_input_outputs(
        self,
        mock_machinelearning_client: MLClient,
        mocker: MockFixture,
        pipeline_path: str,
        expected_input_outputs: dict,
    ) -> None:
        # "Upload" the dependencies so that the dataset serialization behavior can be verified
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )

        test_path = "./tests/test_configs/pipeline_jobs/{}".format(pipeline_path)
        yaml_obj = load_yaml(test_path)
        job: PipelineJob = load_job(test_path)

        # Check that all inputs are present and are of type Input or are literals
        for name in yaml_obj["inputs"].keys():
            job_obj_input_output = job.inputs.get(name, None)
            assert job_obj_input_output is not None
            assert isinstance(job_obj_input_output, PipelineInput)
            job_input_output = job_obj_input_output._to_job_input()
            if name.endswith("literal_input"):
                assert isinstance(job_input_output, int)
            else:
                assert isinstance(job_input_output, Input)

        # Check that all outputs are present and are of type Input or are literals
        for name in yaml_obj["outputs"].keys():
            job_obj_input_output = job.outputs.get(name, None)
            assert job_obj_input_output is not None
            assert isinstance(job_obj_input_output, PipelineOutput)
            job_input_output = job_obj_input_output._to_job_output()
            if name.endswith("literal_input"):
                assert isinstance(job_input_output, int)
            else:
                assert isinstance(job_input_output, Output)

        for job_name, job_value in yaml_obj["jobs"].items():
            job_obj = job.jobs.get(job_name, None)
            assert job_obj is not None
            for name, input_value in job_obj._build_inputs().items():
                # check for input ports or literal
                if isinstance(input_value, str):
                    assert isinstance(job_obj.inputs[name]._data, str)
                if isinstance(input_value, int):
                    assert isinstance(job_obj.inputs[name]._data, int)

        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
        # Convert to REST object and check that all inputs were turned into data inputs
        rest_job = job._to_rest_object()
        rest_job_properties: RestPipelineJob = rest_job.properties
        rest_component_jobs = rest_job_properties.jobs

        _ = PipelineJob._from_rest_object(job._to_rest_object())

        for job_name, job_value in yaml_obj["jobs"].items():
            for io_type in ["inputs", "outputs"]:
                if job_name not in expected_input_outputs or io_type not in expected_input_outputs[job_name]:
                    continue
                expected_values = expected_input_outputs[job_name][io_type]

                # Test that each job's inputs were serialized properly in the REST translation
                component_job = rest_component_jobs[job_name]
                assert isinstance(component_job, dict)
                # Check that each input in the yaml is properly serialized in the REST translation
                assert component_job[io_type] == expected_values

                # Test that translating from REST preserves the inputs for each job
                rest_component = rest_job.properties.jobs[job_name]
                assert expected_values == rest_component[io_type]

    def test_pipeline_job_str(self):
        test_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_command_job_with_inputs_outputs.yml"
        )
        pipeline_entity = load_job(source=test_path)
        pipeline_str = str(pipeline_entity)
        assert pipeline_entity.name in pipeline_str

    def test_pipeline_job_with_environment_variables(self) -> None:
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_environment_variable.yml",
        )

        pipeline_job_dict = pipeline_job._to_rest_object().as_dict()
        assert "environment_variables" in pipeline_job_dict["properties"]["jobs"]["world_job"]
        assert pipeline_job_dict["properties"]["jobs"]["world_job"]["environment_variables"] == {
            "AZUREML_COMPUTE_USE_COMMON_RUNTIME": "false",
            "abc": "def",
        }

    def test_dump_distribution(self):
        # pipeline level test is in test_pipeline_job_create_with_distribution_component
        from azure.ai.ml import TensorFlowDistribution
        from azure.ai.ml._schema.job.distribution import PyTorchDistributionSchema, TensorFlowDistributionSchema

        distribution_dict = {
            "type": "tensorflow",
            # "distribution_type": 'tensorflow',
            "parameter_server_count": 0,
            "worker_count": 5,
        }
        # msrest has been removed from public interface
        distribution_obj = TensorFlowDistribution(**distribution_dict)

        with pytest.raises(
            ValidationError, match=r"Cannot dump non-PyTorchDistribution object into PyTorchDistributionSchema"
        ):
            _ = PyTorchDistributionSchema(context={"base_path": "./"}).dump(distribution_dict)
        with pytest.raises(
            ValidationError, match=r"Cannot dump non-PyTorchDistribution object into PyTorchDistributionSchema"
        ):
            _ = PyTorchDistributionSchema(context={"base_path": "./"}).dump(distribution_obj)

        after_dump_correct = TensorFlowDistributionSchema(context={"base_path": "./"}).dump(distribution_obj)
        assert after_dump_correct == distribution_dict

    def test_job_defaults(self, mocker: MockFixture):
        pipeline_job = load_job(source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_e2e.yml")
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        rest_job = pipeline_job._to_rest_object()
        assert rest_job.properties.settings == {
            "_source": "YAML.JOB",
            "continue_on_step_failure": True,
            "default_compute": "cpu-cluster",
            "default_datastore": "workspacefilestore",
            "force_rerun": False,
        }

    @pytest.mark.parametrize(
        "test_path, expected_components",
        [
            (
                "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_command_job_with_inputs_outputs.yml",
                {
                    "hello_world_inline_commandjob_1": {
                        "_source": "YAML.JOB",
                        "command": "pip freeze && echo " "${{inputs.literal_input}}",
                        "description": "Train a model on the Iris " "dataset-1.",
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {
                            "literal_input": {"default": "7", "type": "integer"},
                            "test1": {"mode": "ro_mount", "type": "uri_file"},
                            "test2": {"mode": "ro_mount", "type": "uri_file"},
                        },
                        "is_deterministic": True,
                        "outputs": {"test1": {"type": "uri_file"}},
                        "type": "command",
                        "version": "1",
                    },
                    "hello_world_inline_commandjob_2": {
                        "_source": "YAML.JOB",
                        "command": "echo Hello World",
                        "description": "Train a model on the Iris dataset-2.",
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {
                            "test1": {"mode": "ro_mount", "type": "uri_file"},
                            "test2": {"type": "uri_file"},
                            "test3": {"type": "uri_folder"},
                        },
                        "is_deterministic": True,
                        "type": "command",
                        "version": "1",
                    },
                    "hello_world_inline_commandjob_3": {
                        "_source": "YAML.JOB",
                        "command": "pip freeze && echo ${{inputs.test1}}",
                        "description": "Train a model on the Iris dataset-1.",
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {"test1": {"type": "uri_file", "mode": "ro_mount"}},
                        "is_deterministic": True,
                        "outputs": {"test1": {"type": "uri_folder"}},
                        "type": "command",
                        "version": "1",
                    },
                },
            ),
            (
                "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_command_job_with_inputs_outputs_2.yml",
                {
                    "hello_world_inline_commandjob_1": {
                        "_source": "YAML.JOB",
                        "command": "pip freeze && echo " "${{inputs.literal_input}}",
                        "description": "Train a model on the Iris " "dataset-1.",
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {
                            "literal_input": {"default": "7", "type": "integer"},
                            "test1": {"mode": "ro_mount", "type": "uri_file"},
                            "test2": {"mode": "ro_mount", "type": "uri_file"},
                        },
                        "is_deterministic": True,
                        "outputs": {"test1": {"type": "uri_file"}},
                        "type": "command",
                        "version": "1",
                    },
                    "hello_world_inline_commandjob_2": {
                        "_source": "YAML.JOB",
                        "command": "echo Hello World",
                        "description": "Train a model on the Iris dataset-2.",
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {
                            "test1": {"mode": "ro_mount", "type": "uri_file"},
                            "test2": {"type": "uri_file"},
                            "test3": {"type": "uri_folder"},
                        },
                        "is_deterministic": True,
                        "type": "command",
                        "version": "1",
                    },
                    "hello_world_inline_commandjob_3": {
                        "_source": "YAML.JOB",
                        "command": "pip freeze && echo ${{inputs.test1}}",
                        "description": "Train a model on the Iris dataset-1.",
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {"test1": {"type": "uri_file", "mode": "ro_mount"}},
                        "is_deterministic": True,
                        "outputs": {"test1": {"type": "uri_folder", "mode": "mount"}},
                        "type": "command",
                        "version": "1",
                    },
                },
            ),
        ],
    )
    def test_command_job_in_pipeline_to_component(self, test_path, expected_components):
        pipeline_entity = load_job(source=test_path)
        # check component of pipeline job is expected
        for name, expected_dict in expected_components.items():
            actual_dict = pipeline_entity.jobs[name].component._to_rest_object().as_dict()
            omit_fields = [
                "name",
                # dumped code will be an absolute path, tested in other tests
                "code",
            ]

            actual_dict = pydash.omit(actual_dict["properties"]["component_spec"], omit_fields)
            assert actual_dict == expected_dict

    def test_command_job_in_pipeline_deep_reference(self):
        test_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_command_job_with_deep_reference.yml"
        )
        pipeline_entity = load_job(source=test_path)
        expected_components = {
            "hello_world_inline_commandjob_1": {
                "_source": "YAML.JOB",
                "command": "pip freeze && echo ${{inputs.literal_input}}",
                "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                "inputs": {
                    "literal_input": {"type": "integer"},
                    "test1": {"type": "uri_file", "mode": "ro_mount"},
                    "test2": {"type": "uri_file", "mode": "ro_mount"},
                },
                "is_deterministic": True,
                "outputs": {"test1": {"type": "uri_folder", "mode": "mount"}},
                "type": "command",
                "version": "1",
            },
            "hello_world_inline_commandjob_2": {
                "_source": "YAML.JOB",
                "command": "pip freeze && echo ${{inputs.test1}}",
                "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                "inputs": {
                    "test1": {"mode": "ro_mount", "type": "uri_file"},
                    "test2": {"type": "uri_folder"},
                    "test3": {"type": "uri_file"},
                },
                "is_deterministic": True,
                "type": "command",
                "version": "1",
            },
            "hello_world_inline_commandjob_3": {
                "_source": "YAML.JOB",
                "command": "pip freeze && echo ${{inputs.test1}}",
                "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                "inputs": {
                    "test1": {"mode": "ro_mount", "type": "uri_file"},
                    "test2": {"type": "uri_file"},
                    "test3": {"type": "mltable"},
                },
                "is_deterministic": True,
                "outputs": {"test1": {"type": "uri_file"}},
                "type": "command",
                "version": "1",
            },
        }
        for name, expected_dict in expected_components.items():
            actual_dict = pipeline_entity.jobs[name].component._to_rest_object().as_dict()
            omit_fields = [
                "name",
            ]

            actual_dict = pydash.omit(actual_dict["properties"]["component_spec"], omit_fields)
            assert actual_dict == expected_dict

    def test_command_job_referenced_component_no_meta(self):
        test_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_command_job_with_deep_reference.yml"
        )
        params_override = [{"jobs.hello_world_component_before.component": "azureml:fake_component_arm_id:1"}]
        # when component is provided as arm id, won't able to get referenced component input/output type
        with pytest.raises(Exception) as e:
            load_job(source=test_path, params_override=params_override)
        err_msg = "Failed to find referenced source for input binding ${{parent.jobs.hello_world_component_before.outputs.test1}}"
        assert err_msg in str(e.value)

    @pytest.mark.parametrize(
        "test_path, job_key",
        [
            # AutoML Tabular component
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/automl_regression_with_pipeline_level_output.yml",
                "regression_node",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/automl_regression_with_command_node.yml",
                "regression_node",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_regression.yml",
                "hello_automl_regression",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_classification.yml",
                "hello_automl_classification",
            ),
            # AutoML NLP component
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_classification.yml",
                "automl_text_classification",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_classification_multilabel.yml",
                "automl_text_classification_multilabel",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_ner.yml",
                "automl_text_ner",
            ),
            # AutoML Vision component
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multiclass_classification.yml",
                "hello_automl_image_multiclass_classification",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multilabel_classification.yml",
                "hello_automl_image_multilabel_classification",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_object_detection.yml",
                "hello_automl_image_object_detection",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_instance_segmentation.yml",
                "hello_automl_image_instance_segmentation",
            ),
        ],
    )
    def test_automl_node_in_pipeline_load_dump(
        self, test_path, job_key, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        pipeline: PipelineJob = load_job(source=test_path)

        with open(test_path) as f:
            original_dict = yaml.safe_load(f)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(pipeline)

        automl_job = pipeline.jobs[job_key]
        automl_job_dict = automl_job._to_dict(inside_pipeline=True)
        pipeline_job_dict = json.loads(json.dumps(automl_job_dict))
        original_job_dict = json.loads(json.dumps(original_dict["jobs"][job_key]))
        omit_fields = ["display_name", "experiment_name", "log_verbosity", "name", "outputs", "properties", "tags"]
        pipeline_job_dict = pydash.omit(pipeline_job_dict, omit_fields)
        original_job_dict = pydash.omit(original_job_dict, omit_fields)
        if job_key == "automl_text_ner":
            # 1779366 target column not required for NER, remove when model gets updated
            pipeline_job_dict = pydash.omit(pipeline_job_dict, ["target_column_name"])
        if "image" in job_key:
            # sweep comparison won't match as pipeline dict will contain default values
            pipeline_job_dict = pydash.omit(pipeline_job_dict, ["sweep"])
            original_job_dict = pydash.omit(original_job_dict, ["sweep"])

            for i, search_space_item in enumerate(original_job_dict.get("search_space", [])):
                original_job_dict["search_space"][i] = _convert_sweep_dist_dict_to_str_dict(search_space_item)
        assert pipeline_job_dict == original_job_dict

    def _raise_error_on_wrong_schema(self, test_path, original_dict, job_key, mock_machinelearning_client, mocker):
        dump_yaml_to_file(test_path, original_dict)
        with pytest.raises(ValidationError):
            self.test_automl_node_in_pipeline_load_dump(test_path, job_key, mock_machinelearning_client, mocker)

    @pytest.mark.parametrize(
        "test_path, job_key",
        [
            # AutoML Vision component
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multiclass_classification.yml",
                "hello_automl_image_multiclass_classification",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multilabel_classification.yml",
                "hello_automl_image_multilabel_classification",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_object_detection.yml",
                "hello_automl_image_object_detection",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_instance_segmentation.yml",
                "hello_automl_image_instance_segmentation",
            ),
        ],
    )
    def test_automl_image_node_in_pipeline_load_dump(
        self, test_path, job_key, mock_machinelearning_client: MLClient, mocker: MockFixture, tmp_path: Path
    ):
        with open(test_path) as f:
            original_dict = yaml.safe_load(f)

        test_yaml_path = tmp_path / f"{job_key}_job.yml"
        # Test Invalid number_of_epochs
        original_dict_copy = deepcopy(original_dict)
        original_dict_copy["jobs"][job_key]["search_space"][0]["number_of_epochs"] = {
            "type": "choice",
            "values": [1.5, 2.5],
        }

        self._raise_error_on_wrong_schema(
            test_yaml_path, original_dict_copy, job_key, mock_machinelearning_client, mocker
        )

        # # Test AMS Gradient
        original_dict_copy = deepcopy(original_dict)
        original_dict_copy["jobs"][job_key]["search_space"][0]["ams_gradient"] = {
            "type": "choice",
            "values": [1.2, 2.5],
        }
        self._raise_error_on_wrong_schema(
            test_yaml_path, original_dict_copy, job_key, mock_machinelearning_client, mocker
        )

        original_dict_copy["jobs"][job_key]["search_space"][0]["ams_gradient"] = True
        dump_yaml_to_file(test_yaml_path, original_dict_copy)
        self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

        # test LRSChedular Enum
        original_dict_copy = deepcopy(original_dict)
        original_dict_copy["jobs"][job_key]["search_space"][0]["learning_rate_scheduler"] = {
            "type": "choice",
            "values": ["random_lr_scheduler1", "random_lr_scheduler2"],
        }
        self._raise_error_on_wrong_schema(
            test_yaml_path, original_dict_copy, job_key, mock_machinelearning_client, mocker
        )

        original_dict_copy["jobs"][job_key]["search_space"][0]["learning_rate_scheduler"] = camel_to_snake(
            LearningRateScheduler.WARMUP_COSINE
        )
        dump_yaml_to_file(test_yaml_path, original_dict_copy)
        self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

        original_dict_copy["jobs"][job_key]["search_space"][0]["learning_rate_scheduler"] = {
            "type": "choice",
            "values": [camel_to_snake(LearningRateScheduler.WARMUP_COSINE), camel_to_snake(LearningRateScheduler.STEP)],
        }
        dump_yaml_to_file(test_yaml_path, original_dict_copy)
        self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

        # test Optimizer
        original_dict_copy = deepcopy(original_dict)
        original_dict_copy["jobs"][job_key]["search_space"][0]["optimizer"] = {
            "type": "choice",
            "values": ["random1", "random2"],
        }
        self._raise_error_on_wrong_schema(
            test_yaml_path, original_dict_copy, job_key, mock_machinelearning_client, mocker
        )

        original_dict_copy["jobs"][job_key]["search_space"][0]["optimizer"] = camel_to_snake(StochasticOptimizer.ADAM)
        dump_yaml_to_file(test_yaml_path, original_dict_copy)
        self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

        original_dict_copy["jobs"][job_key]["search_space"][0]["optimizer"] = {
            "type": "choice",
            "values": [camel_to_snake(StochasticOptimizer.SGD), camel_to_snake(StochasticOptimizer.ADAM)],
        }
        dump_yaml_to_file(test_yaml_path, original_dict_copy)
        self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

        # Test Model Name
        original_dict_copy = deepcopy(original_dict)
        original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = 1
        self._raise_error_on_wrong_schema(
            test_yaml_path, original_dict_copy, job_key, mock_machinelearning_client, mocker
        )

        original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = 100.5
        self._raise_error_on_wrong_schema(
            test_yaml_path, original_dict_copy, job_key, mock_machinelearning_client, mocker
        )

        original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = True
        self._raise_error_on_wrong_schema(
            test_yaml_path, original_dict_copy, job_key, mock_machinelearning_client, mocker
        )

        if "image_" in job_key and "classification" in job_key:
            original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = {
                "type": "choice",
                "values": ["vitb16r224"],
            }
            dump_yaml_to_file(test_yaml_path, original_dict_copy)
            self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

            original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = "vitb16r224"
            dump_yaml_to_file(test_yaml_path, original_dict_copy)
            self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

        elif "object_detection" in job_key:
            original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = {
                "type": "choice",
                "values": ["yolov5", "fasterrcnn_resnet50_fpn"],
            }
            dump_yaml_to_file(test_yaml_path, original_dict_copy)
            self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

            original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = "fasterrcnn_resnet50_fpn"
            dump_yaml_to_file(test_yaml_path, original_dict_copy)
            self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

        elif "instance_segmentation" in job_key:
            original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = {
                "type": "choice",
                "values": ["maskrcnn_resnet152_fpn", "maskrcnn_resnet18_fpn"],
            }
            dump_yaml_to_file(test_yaml_path, original_dict_copy)
            self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

            original_dict_copy["jobs"][job_key]["search_space"][0]["model_name"] = "maskrcnn_resnet18_fpn"
            dump_yaml_to_file(test_yaml_path, original_dict_copy)
            self.test_automl_node_in_pipeline_load_dump(test_yaml_path, job_key, mock_machinelearning_client, mocker)

    @pytest.mark.parametrize(
        "params_override, error_field, expecting_field",
        [
            (
                [{"jobs.train_job.inputs.training_data": "${{inputs.pipeline_job_training_input}}"}],
                "${{inputs.pipeline_job_training_input}}",
                "${{parent.inputs.pipeline_job_training_input}}",
            ),
            (
                [{"jobs.score_job.inputs.model_input": "${{jobs.train_job.outputs.model_output}}"}],
                "${{jobs.train_job.outputs.model_output}}",
                "${{parent.jobs.train_job.outputs.model_output}}",
            ),
        ],
    )
    def test_legacy_data_binding_error_msg(self, params_override, error_field, expecting_field):
        test_path = "./tests/test_configs/dsl_pipeline/e2e_local_components/pipeline.yml"
        job: PipelineJob = load_job(source=test_path, params_override=params_override)
        with pytest.raises(ValidationException) as e:
            job._to_rest_object()
        err_msg = "{} has changed to {}, please change to use new format.".format(error_field, expecting_field)
        assert err_msg in str(e.value)

    @pytest.mark.parametrize(
        "test_path",
        [
            "./tests/test_configs/pipeline_jobs/pipeline_job_with_parallel_job_with_input_bindings.yml",
        ],
    )
    def test_parallel_pipeline_not_private_preview_features(self, test_path, mocker: MockFixture):
        mocker.patch("azure.ai.ml.entities._job.pipeline.pipeline_job.is_private_preview_enabled", return_value=False)
        job: PipelineJob = load_job(source=test_path)
        try:
            job._to_rest_object()
        except UserErrorException as e:
            assert False, f"parallel in pipeline is public preview feature, but raised exception {e.value}"

    def test_pipeline_yaml_job_node_source(self, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job.yml"
        job: PipelineJob = load_job(source=test_path)
        assert job.component._job_sources == {"REMOTE.WORKSPACE.COMPONENT": 2}
        assert job.component._source == "YAML.JOB"

        test_path = "./tests/test_configs/pipeline_jobs/component_from_registry.yml"
        job: PipelineJob = load_job(source=test_path)
        assert job.component._job_sources == {"REMOTE.REGISTRY": 1}
        assert job.component._source == "YAML.JOB"

    def test_command_job_node_services_in_pipeline_with_properties(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_node_services_with_properties.yml"
        job: PipelineJob = load_job(source=test_path)
        node_services = job.jobs["hello_world_component_inline"].services

        assert isinstance(node_services.get("my_ssh"), SshJobService)
        assert isinstance(node_services.get("my_tensorboard"), TensorBoardJobService)
        assert isinstance(node_services.get("my_jupyterlab"), JupyterLabJobService)
        assert isinstance(node_services.get("my_vscode"), VsCodeJobService)

        job_rest_obj = job._to_rest_object()
        rest_services = job_rest_obj.properties.jobs["hello_world_component_inline"]["services"]
        # rest object of node in pipeline should be pure dict
        assert rest_services == {
            "my_ssh": {
                "job_service_type": "SSH",
                "properties": {"sshPublicKeys": "xyz123"},
            },
            "my_tensorboard": {
                "job_service_type": "TensorBoard",
                "properties": {"logDir": "~/tblog"},
            },
            "my_jupyterlab": {
                "job_service_type": "JupyterLab",
            },
            "my_vscode": {
                "job_service_type": "VSCode",
            },
        }

    def test_command_job_node_services_in_pipeline(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_node_services.yml"
        job: PipelineJob = load_job(source=test_path)
        node_services = job.jobs["hello_world_component_inline"].services

        assert isinstance(node_services.get("my_ssh"), SshJobService)
        assert isinstance(node_services.get("my_tensorboard"), TensorBoardJobService)
        assert isinstance(node_services.get("my_jupyterlab"), JupyterLabJobService)
        assert isinstance(node_services.get("my_vscode"), VsCodeJobService)

        assert node_services.get("my_ssh").ssh_public_keys == "xyz123"
        assert node_services.get("my_tensorboard").log_dir == "~/tblog"

        job_rest_obj = job._to_rest_object()
        rest_services = job_rest_obj.properties.jobs["hello_world_component_inline"]["services"]
        # rest object of node in pipeline should be pure dict
        assert rest_services == {
            "my_ssh": {
                "job_service_type": "SSH",
                "properties": {"sshPublicKeys": "xyz123"},
            },
            "my_tensorboard": {
                "job_service_type": "TensorBoard",
                "properties": {"logDir": "~/tblog"},
            },
            "my_jupyterlab": {
                "job_service_type": "JupyterLab",
            },
            "my_vscode": {
                "job_service_type": "VSCode",
            },
        }

    def test_command_job_node_services_in_pipeline_with_no_component(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_node_services_inline_job.yml"
        job: PipelineJob = load_job(source=test_path)
        node_services = job.jobs["hello_world_component_inline"].services

        assert isinstance(node_services.get("my_ssh"), SshJobService)
        assert isinstance(node_services.get("my_tensorboard"), TensorBoardJobService)
        assert isinstance(node_services.get("my_jupyterlab"), JupyterLabJobService)
        assert isinstance(node_services.get("my_vscode"), VsCodeJobService)

        job_rest_obj = job._to_rest_object()

        # rest object of node in pipeline should be pure dict
        assert job_rest_obj.properties.jobs["hello_world_component_inline"]["services"] == {
            "my_ssh": {
                "job_service_type": "SSH",
                "properties": {"sshPublicKeys": "xyz123"},
            },
            "my_tensorboard": {
                "job_service_type": "TensorBoard",
                "properties": {"logDir": "~/tblog"},
            },
            "my_jupyterlab": {
                "job_service_type": "JupyterLab",
            },
            "my_vscode": {
                "job_service_type": "VSCode",
            },
        }

    def test_command_job_node_services_in_pipeline_with_no_component_with_properties(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_node_services_inline_job_with_properties.yml"
        job: PipelineJob = load_job(source=test_path)
        node_services = job.jobs["hello_world_component_inline"].services

        assert isinstance(node_services.get("my_ssh"), SshJobService)
        assert isinstance(node_services.get("my_tensorboard"), TensorBoardJobService)
        assert isinstance(node_services.get("my_jupyterlab"), JupyterLabJobService)
        assert isinstance(node_services.get("my_vscode"), VsCodeJobService)

        job_rest_obj = job._to_rest_object()

        # rest object of node in pipeline should be pure dict
        assert job_rest_obj.properties.jobs["hello_world_component_inline"]["services"] == {
            "my_ssh": {
                "job_service_type": "SSH",
                "properties": {"sshPublicKeys": "xyz123"},
            },
            "my_tensorboard": {
                "job_service_type": "TensorBoard",
                "properties": {"logDir": "~/tblog"},
            },
            "my_jupyterlab": {
                "job_service_type": "JupyterLab",
            },
            "my_vscode": {
                "job_service_type": "VSCode",
            },
        }

    def test_dump_pipeline_inputs(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_comps.yml"
        expected_inputs = {
            "float_input": 10.01,
            "integer_input": 15,
            "bool_input": False,
            "string_input": "hello",
            "string_integer_input": "43",
        }

        job = load_job(test_path, params_override=[{"inputs": expected_inputs}])

        assert job._to_dict()["inputs"] == expected_inputs

    def test_pipeline_job_with_pipeline_component(self):
        test_path = "./tests/test_configs/pipeline_jobs/pipeline_job_with_pipeline_component.yml"
        job: PipelineJob = load_job(source=test_path)
        nodes = job._to_dict()["jobs"]
        expected_node1_input_dict = {
            "component_in_number": {"path": "${{parent.inputs.int_param}}"},
            "component_in_path": {"path": "${{parent.inputs.data_input}}"},
        }
        assert nodes["node1"]["inputs"] == expected_node1_input_dict
        expected_node2_input_dict = {
            "component_in_number": 20,
            "component_in_path": {
                "type": "uri_file",
                "path": "azureml:https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
            },
        }
        assert nodes["node2"]["inputs"] == expected_node2_input_dict
        expected_node3_input_dict = {
            "component_in_number": 30,
            "component_in_path": {"path": "${{parent.jobs.node1.outputs.output_path}}"},
        }
        assert nodes["node3"]["inputs"] == expected_node3_input_dict

    def test_pipeline_component_job(self):
        test_path = "./tests/test_configs/pipeline_jobs/remote_pipeline_component_job.yml"
        job: PipelineJob = load_job(source=test_path)
        assert job._validate().passed
        expected_job_dict = {
            "component": "azureml://subscriptions/d511f82f-71ba-49a4-8233-d7be8a3650f4/resourceGroups/RLTesting/providers/Microsoft.MachineLearningServices/workspaces/AnkitWS/jobs/test_617704734544",
            "description": "The hello world pipeline job",
            "inputs": {
                "data_input": {
                    "path": "azureml:https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
                    "type": "uri_file",
                },
                "int_param": 10,
            },
            "settings": {"default_compute": "azureml:cpu-cluster"},
            "tags": {"owner": "sdkteam", "tag": "tagvalue"},
            "type": "pipeline",
        }
        assert job._to_dict() == expected_job_dict

        test_path = "./tests/test_configs/pipeline_jobs/pipeline_component_job.yml"
        job: PipelineJob = load_job(source=test_path)
        assert job._validate().passed
        job_dict = job._to_dict()
        assert "component" not in job_dict
        assert "jobs" in job_dict
        assert "component_a_job" in job_dict["jobs"]

        test_path = "./tests/test_configs/pipeline_jobs/pipeline_component_job_with_overrides.yml"
        job: PipelineJob = load_job(source=test_path)
        assert job._validate().passed
        job_dict = job._to_dict()
        assert job_dict["outputs"] == {
            "not_exists": {"path": "azureml://datastores/mock/paths/not_exists.txt", "type": "uri_file"},
            "output_path": {"path": "azureml://datastores/mock/paths/my_output_file.txt", "type": "uri_file"},
        }

        # Assert the output_path:None not override original component output value
        test_path = "./tests/test_configs/pipeline_jobs/pipeline_component_job_with_overrides2.yml"
        job: PipelineJob = load_job(source=test_path)
        assert job._validate().passed
        job_dict = job._to_dict()
        assert job_dict["outputs"] == {
            "not_exists": {"path": "azureml://datastores/mock/paths/not_exists.txt", "type": "uri_file"},
            "output_path": {"type": "uri_folder"},  # uri_folder from component output
        }

    def test_invalid_pipeline_component_job(self):
        test_path = "./tests/test_configs/pipeline_jobs/invalid/invalid_pipeline_component_job.yml"
        with pytest.raises(Exception) as e:
            load_job(source=test_path)
        assert "'jobs' and 'component' are mutually exclusive fields in pipeline job" in str(e.value)

    @pytest.mark.parametrize(
        "pipeline_job_path, expected_error",
        DATABINDING_EXPRESSION_TEST_CASES,
    )
    def test_pipeline_job_with_data_binding_expression(
        self, client: MLClient, pipeline_job_path: str, expected_error: Optional[Exception]
    ):
        pipeline: PipelineJob = load_job(source=pipeline_job_path)
        pipeline._to_rest_object()

    def test_pipeline_job_with_spark_component(self):
        yaml_path = r"./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_spark_component.yml"
        load_job(yaml_path)
