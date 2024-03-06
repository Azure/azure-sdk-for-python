from functools import partial
from pathlib import Path
from typing import Callable, Union

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from mock import mock
from pytest_mock import MockFixture
from test_utilities.utils import (
    _PYTEST_TIMEOUT_METHOD,
    assert_job_cancel,
    omit_with_wildcard,
    submit_and_cancel_new_dsl_pipeline,
)

from azure.ai.ml import Input, MLClient, dsl, load_component
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.dsl._group_decorator import group
from azure.ai.ml.entities import (
    Choice,
    Command,
    CommandComponent,
    Component,
    Environment,
    PipelineComponent,
    PipelineJob,
    Sweep,
)
from azure.ai.ml.operations._operation_orchestrator import OperationOrchestrator

from .._util import _DSL_TIMEOUT_SECOND

tests_root_dir = Path(__file__).parent.parent.parent
components_dir = tests_root_dir / "test_configs/components/"
job_input = Input(
    type=AssetTypes.URI_FILE,
    path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
)
experiment_name = "dsl_pipeline_e2e"
common_omit_fields = [
    "properties",
    "display_name",
    "experiment_name",
    "jobs.*.componentId",
    "inputs.*.uri",
    "jobs.*._source",
    "jobs.*.properties",
    "settings._source",
    "source_job_id",
    "services",
]


def _get_component_in_first_child(_with_jobs: Union[PipelineJob, PipelineComponent], client: MLClient) -> Component:
    if not _with_jobs.jobs:
        raise ValueError("No jobs found in the pipeline")
    _result = next(iter(_with_jobs.jobs.values())).component.split(":")
    if len(_result) == 2:
        _name, _version = _result
    elif len(_result) == 3:
        _, _name, _version = _result
    else:
        raise ValueError("Invalid component arm string: {}".format(_result))
    return client.components.get(_name, _version)


@group
class SubGroup:
    integer: int = None
    number: float = None


@group
class Group:
    number: float = None
    sub1: SubGroup = None
    sub2: SubGroup = None


@pytest.mark.usefixtures(
    "enable_environment_id_arm_expansion",
    "enable_pipeline_private_preview_features",
    "mock_code_hash",
    "mock_component_hash",
    "mock_set_headers_with_user_aml_token",
    "recorded_test",
)
@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestDSLPipelineWithSpecificNodes(AzureRecordedTestCase):
    @staticmethod
    def _generate_multi_layer_pipeline_func():
        path = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline
        def pipeline_leaf(component_in_path: Input):
            component_func1 = load_component(source=path)
            component_func1(component_in_path=component_in_path, component_in_number=1)

            component_func2 = load_component(
                source=path,
                params_override=[
                    {
                        "name": "another_component_name",
                        "version": "another_component_version",
                    }
                ],
            )
            component_func2(component_in_path=component_in_path, component_in_number=1)

            component_func3 = load_component(
                source=path, params_override=[{"environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:32"}]
            )
            component_func3(component_in_path=component_in_path, component_in_number=1)

            component_func4 = load_component(source=path)
            component_func4.command += " & echo updated1"
            component_func4(component_in_path=component_in_path, component_in_number=1)

        @dsl.pipeline
        def pipeline_mid(job_in_path: Input):
            pipeline_leaf(job_in_path)
            pipeline_leaf(job_in_path)

        @dsl.pipeline
        def pipeline_root(job_in_path: Input):
            pipeline_mid(job_in_path)
            pipeline_mid(job_in_path)

        return pipeline_root

    @staticmethod
    def _generate_pipeline_func_for_concurrent_component_registration_test(shared_input):
        path = "./tests/test_configs/components/helloworld_component.yml"
        conda_file_path = "./tests/test_configs/environment/environment_files/environment.yml"

        environment = Environment(
            name="test-environment",
            conda_file=conda_file_path,
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
            version="2",  # TODO: anonymous environment has potential version conflict?
            description="This is an anonymous environment",
        )

        @dsl.pipeline
        def pipeline_leaf():
            component_func1a = load_component(source=path)
            component_func1a.environment = environment
            component_func1a.command += " & echo updated1"
            component_func1a(component_in_path=shared_input, component_in_number=1)

            component_func1b = load_component(source=path)
            component_func1b.environment = environment
            component_func1b.command += " & echo updated1"
            component_func1b(component_in_path=shared_input, component_in_number=1)

            component_func2 = load_component(source=path)
            component_func2.command += " & echo updated2"
            component_func2.environment = environment
            component_func2(component_in_path=shared_input, component_in_number=1)

            component_func3 = load_component(source=path)
            component_func3.command += " & echo updated3"
            component_func3.environment = environment
            component_func3(component_in_path=shared_input, component_in_number=1)

        # TODO: test with multiple pipelines after server-side return jobs for pipeline component
        # @dsl.pipeline
        # def pipeline_mid():
        #     pipeline_leaf()
        #     pipeline_leaf()
        #
        # @dsl.pipeline
        # def pipeline_root():
        #     pipeline_mid()
        #     pipeline_mid()

        return pipeline_leaf

    def test_dsl_pipeline_sweep_node(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        yaml_file = "./tests/test_configs/components/helloworld_component.yml"

        @dsl.pipeline
        def train_with_sweep_in_pipeline(raw_data, primary_metric: str = "AUC", max_total_trials: int = 10):
            component_to_sweep: CommandComponent = load_component(source=yaml_file)
            # to check the logic to set default display name for components
            component_to_sweep.display_name = None

            cmd_node1: Command = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            )

            sweep_job1: Sweep = cmd_node1.sweep(
                primary_metric="AUC",  # primary_metric,
                goal="maximize",
                sampling_algorithm="random",
            )
            sweep_job1.compute = "gpu-cluster"
            sweep_job1.set_limits(max_total_trials=10)  # max_total_trials

            cmd_node2: Command = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            )
            sweep_job2: Sweep = cmd_node2.sweep(
                primary_metric="AUC",
                goal="minimize",
                sampling_algorithm="random",
                max_total_trials=10,
            )
            sweep_job2.compute = "gpu-cluster"

            sweep_job3: Sweep = component_to_sweep(
                component_in_number=Choice([2, 3, 4, 5]), component_in_path=raw_data
            ).sweep(
                primary_metric="accuracy",
                goal="maximize",
                sampling_algorithm="random",
                max_total_trials=10,
            )

            component_to_link = load_component(source=yaml_file, params_override=[{"name": "node_to_link"}])
            link_node = component_to_link(
                component_in_number=2, component_in_path=sweep_job1.outputs.component_out_path
            )

            return {
                "pipeline_job_best_model1": sweep_job1.outputs.component_out_path,
                "pipeline_job_best_model2": sweep_job2.outputs.component_out_path,
                "pipeline_job_best_model3": sweep_job3.outputs.component_out_path,
                "pipeline_model_test_result": link_node.outputs.component_out_path,
            }

        pipeline: PipelineJob = train_with_sweep_in_pipeline(
            raw_data=job_input, max_total_trials=100, primary_metric="accuracy"
        )
        pipeline.settings.default_compute = "cpu-cluster"
        created_pipeline = assert_job_cancel(pipeline, client)
        name, version = created_pipeline.jobs["sweep_job1"].trial.split(":")
        created_component = client.components.get(name, version)
        # keep original component display name to guarantee reuse
        assert created_component.display_name is None

    def test_dsl_pipeline_component_cache_in_resolver(self, client: MLClient) -> None:
        input_data_path = "./tests/test_configs/data/"
        pipeline_root = self._generate_multi_layer_pipeline_func()

        _submit_and_cancel = partial(
            submit_and_cancel_new_dsl_pipeline, client=client, job_in_path=Input(path=input_data_path)
        )

        def _mock_get_component_arm_id(_component: Component) -> str:
            # the logic has no diff comparing to original function other than always using show_progress=False
            # just to mock the function and check call information
            if not _component.id:
                _component._id = client.components.create_or_update(
                    _component, is_anonymous=True, show_progress=False
                ).id
            return _component.id

        with mock.patch.object(
            OperationOrchestrator, "_get_component_arm_id", side_effect=_mock_get_component_arm_id
        ) as mock_resolve:
            _submit_and_cancel(pipeline_root)
            # pipeline_leaf, pipeline_mid and 3 command components will be resolved
            assert mock_resolve.call_count == 5

        with mock.patch.object(
            OperationOrchestrator, "_get_component_arm_id", side_effect=_mock_get_component_arm_id
        ) as mock_resolve:
            _submit_and_cancel(pipeline_root)
            # no more requests to resolve components as local cache is hit
            assert mock_resolve.call_count == 0

        pipeline_job = pipeline_root(job_in_path=Input(path=input_data_path))
        pipeline_job.settings.default_compute = "cpu-cluster"
        leaf_subgraph = pipeline_job.jobs["pipeline_mid"].component.jobs["pipeline_leaf"].component
        leaf_subgraph.jobs["another_component_name"].component.command += " & echo updated2"
        with mock.patch.object(
            OperationOrchestrator, "_get_component_arm_id", side_effect=_mock_get_component_arm_id
        ) as mock_resolve:
            assert_job_cancel(pipeline_job, client)
            # updated command component and its parents (pipeline_leaf and pipeline_mid) will be resolved
            assert mock_resolve.call_count == 3

    def test_dsl_pipeline_concurrent_component_registration(self, client: MLClient, mocker: MockFixture) -> None:
        # disable on-disk cache to test concurrent component registration
        mocker.patch("azure.ai.ml._utils.utils.is_on_disk_cache_enabled", return_value=False)

        input_data_path = "./tests/test_configs/data/"
        pipeline_root = self._generate_pipeline_func_for_concurrent_component_registration_test(
            shared_input=Input(path=input_data_path)
        )

        _submit_and_cancel = partial(
            submit_and_cancel_new_dsl_pipeline,
            client=client,
        )

        treatment_pipeline_job = _submit_and_cancel(pipeline_root)

        with mock.patch("azure.ai.ml._utils.utils.is_concurrent_component_registration_enabled", return_value=False):
            base_pipeline_job = _submit_and_cancel(pipeline_root)

        # Server-side does not guarantee the same anonymous pipeline component share the same version
        # So omit name and version and do comparison layer by layer
        omit_fields = ["id", "name", "version", "creation_context", "services", "jobs.*.component"]

        base, treat = base_pipeline_job, treatment_pipeline_job
        # TODO: test with multiple pipelines after server-side return jobs for pipeline component
        for _ in range(0, 0):
            assert omit_with_wildcard(base._to_dict(), *omit_fields) == omit_with_wildcard(
                treat._to_dict(), *omit_fields
            )
            base = _get_component_in_first_child(base, client)
            treat = _get_component_in_first_child(treat, client)

        # The last layer contains the command components
        omit_fields.pop()
        assert omit_with_wildcard(base._to_dict(), *omit_fields) == omit_with_wildcard(treat._to_dict(), *omit_fields)

    @pytest.mark.parametrize(
        "group_param_input, use_remote_component",
        [
            pytest.param(
                Group(
                    number=1.0,
                    sub1=SubGroup(integer=1),
                ),
                False,
                id="strong-typed-group",
            ),
            pytest.param(
                {
                    "number": 1.0,
                    "sub1": {"integer": 1},
                },
                False,
                id="dict-group",
            ),
            pytest.param(
                Group(
                    number=1.0,
                    sub1=SubGroup(integer=1),
                ),
                True,
                id="strong-typed-group-remote",
            ),
            pytest.param(
                {
                    "number": 1.0,
                    "sub1": {"integer": 1},
                },
                True,
                id="dict-group-remote",
            ),
        ],
    )
    def test_dsl_pipeline_with_param_group_in_command_component(
        self,
        client,
        group_param_input,
        use_remote_component: bool,
        randstr: Callable[[str], str],
    ):
        command_func = load_component("./tests/test_configs/components/helloworld_component_with_parameter_group.yml")
        input_data_path = "./tests/test_configs/data/"

        if use_remote_component:
            command_func.name = randstr("component_name")
            command_func = client.components.create_or_update(
                command_func,
            )

        @dsl.pipeline
        def pipeline_with_command(input_data):
            command_node = command_func(
                component_in_path=input_data,
                component_in_group=group_param_input,
            )
            return command_node.outputs

        pipeline: PipelineJob = pipeline_with_command(
            input_data=Input(
                path=input_data_path,
                type=AssetTypes.URI_FOLDER,
            ),
        )
        pipeline.settings.default_compute = "cpu-cluster"
        created_pipeline = client.jobs.create_or_update(pipeline)
        assert created_pipeline.jobs["command_node"]._to_rest_inputs() == {
            "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.input_data}}"},
            "component_in_group.number": {"job_input_type": "literal", "value": "1.0"},
            "component_in_group.sub1.integer": {"job_input_type": "literal", "value": "1"},
        }

    @pytest.mark.skipif(not is_live(), reason="Met some problem in recording")
    def test_dsl_pipeline_component_with_static_local_data_input(self, client: MLClient) -> None:
        path = "./tests/test_configs/components/helloworld_component.yml"
        input_data_path = "./tests/test_configs/data/"

        @dsl.pipeline()
        def pipeline_no_arg():
            component_func = load_component(source=path)
            component_func(
                component_in_path=Input(
                    path=input_data_path,
                    type=AssetTypes.URI_FOLDER,
                ),
                component_in_number=1,
            )

        @dsl.pipeline
        def pipeline_func():
            pipeline_no_arg()

        pipeline_job: PipelineJob = pipeline_func()
        pipeline_job.settings.default_compute = "cpu-cluster"
        client.jobs.create_or_update(pipeline_job)
