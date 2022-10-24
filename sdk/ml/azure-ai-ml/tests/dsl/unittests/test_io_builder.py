from pathlib import Path

import pydash
import pytest

from azure.ai.ml import load_component, Input
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.entities._job.pipeline._io.base import _resolve_builders_2_data_bindings
from test_utilities.utils import omit_with_wildcard

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestInputOutputBuilder:
    def test_nested_input_output_builder(self):
        input1 = PipelineInput(name="input1", owner="pipeline", meta=None)
        input2 = PipelineInput(name="input2", owner="pipeline", meta=None)
        input3 = PipelineInput(name="input3", owner="pipeline", meta=None)
        test_data = {
            "data1": input1,
            "data2": {
                "1": input2,
            },
            "data3": [input3],
            "data4": [{"1": input1}, input2, [input3]],
            "data5": {"1": [input1], "2": {"1": input2}, "3": input3},
        }
        assert _resolve_builders_2_data_bindings(test_data) == {
            "data1": "${{parent.inputs.input1}}",
            "data2": {"1": "${{parent.inputs.input2}}"},
            "data3": ["${{parent.inputs.input3}}"],
            "data4": [{"1": "${{parent.inputs.input1}}"}, "${{parent.inputs.input2}}", ["${{parent.inputs.input3}}"]],
            "data5": {
                "1": ["${{parent.inputs.input1}}"],
                "2": {"1": "${{parent.inputs.input2}}"},
                "3": "${{parent.inputs.input3}}",
            },
        }

    def test_pipeline_input_result(self):
        component_yaml = components_dir / "helloworld_component.yml"
        component_func = load_component(source=component_yaml)

        @pipeline
        def my_pipeline(job_in_number, job_in_path):
            assert isinstance(job_in_number, PipelineInput)
            assert isinstance(job_in_path, PipelineInput)
            assert isinstance(job_in_number.result(), int)
            assert isinstance(job_in_path.result(), Input)
            node1 = component_func(component_in_number=job_in_number, component_in_path=job_in_path)
            # calling result() will convert pipeline input to actual value
            node2 = component_func(component_in_number=job_in_number.result(), component_in_path=job_in_path.result())
            return {
                "output1": node1.outputs.component_out_path,
                "output2": node2.outputs.component_out_path
            }

        pipeline_job1 = my_pipeline(
            job_in_number=1, job_in_path=Input(path="fake_path1")
        )

        common_omit_fields = [
            "jobs.*.componentId",
            "jobs.*._source",
            "jobs.*.properties",
        ]

        rest_pipeline_job = omit_with_wildcard(pipeline_job1._to_rest_object().properties.as_dict(),
                                               *common_omit_fields)
        expected_pipeline_job1 = {
            'node1': {
                'computeId': None,
                'display_name': None,
                'distribution': None,
                'environment_variables': {},
                'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                   'value': '${{parent.inputs.job_in_number}}'},
                           'component_in_path': {'job_input_type': 'literal',
                                                 'value': '${{parent.inputs.job_in_path}}'}},
                'limits': None,
                'name': 'node1',
                'outputs': {'component_out_path': {'type': 'literal',
                                                   'value': '${{parent.outputs.output1}}'}},
                'resources': None,
                'tags': {},
                'type': 'command'},
            'node2': {
                'computeId': None,
                'display_name': None,
                'distribution': None,
                'environment_variables': {},
                'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                   'value': '1'},
                           'component_in_path': {'job_input_type': 'uri_folder',
                                                 'uri': 'fake_path1'}},
                'limits': None,
                'name': 'node2',
                'outputs': {'component_out_path': {'type': 'literal',
                                                   'value': '${{parent.outputs.output2}}'}},
                'resources': None,
                'tags': {},
                'type': 'command'}
        }
        assert rest_pipeline_job["jobs"] == expected_pipeline_job1

        pipeline_job2 = my_pipeline(
            job_in_number=2, job_in_path=Input(path="fake_path2")
        )

        rest_pipeline_job = omit_with_wildcard(pipeline_job2._to_rest_object().properties.as_dict(),
                                               *common_omit_fields)

        expected_pipeline_job2 = {
            'node1': {'computeId': None,
                      'display_name': None,
                      'distribution': None,
                      'environment_variables': {},
                      'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                         'value': '${{parent.inputs.job_in_number}}'},
                                 'component_in_path': {'job_input_type': 'literal',
                                                       'value': '${{parent.inputs.job_in_path}}'}},
                      'limits': None,
                      'name': 'node1',
                      'outputs': {'component_out_path': {'type': 'literal',
                                                         'value': '${{parent.outputs.output1}}'}},
                      'resources': None,
                      'tags': {},
                      'type': 'command'},
            'node2': {'computeId': None,
                      'display_name': None,
                      'distribution': None,
                      'environment_variables': {},
                      'inputs': {'component_in_number': {'job_input_type': 'literal',
                                                         'value': '2'},
                                 'component_in_path': {'job_input_type': 'uri_folder',
                                                       'uri': 'fake_path2'}},
                      'limits': None,
                      'name': 'node2',
                      'outputs': {'component_out_path': {'type': 'literal',
                                                         'value': '${{parent.outputs.output2}}'}},
                      'resources': None,
                      'tags': {},
                      'type': 'command'}
        }
        assert rest_pipeline_job["jobs"] == expected_pipeline_job2

        # calling pipeline func again won't affect existing pipeline job
        pipeline_job1.jobs["node2"].inputs["component_in_number"] == 1
        pipeline_job1.jobs["node2"].inputs["component_in_path"].path == "fake_path1"

        rest_pipeline_job = omit_with_wildcard(pipeline_job1._to_rest_object().properties.as_dict(),
                                               *common_omit_fields)
        assert rest_pipeline_job["jobs"] == expected_pipeline_job1
