import json
import os.path
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils import is_live
import pydash
import pytest
from marshmallow import ValidationError
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, assert_job_cancel, wait_until_done, sleep_if_live

from azure.ai.ml import Input, MLClient, load_component, load_data, load_job
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants import InputOutputModes
from azure.ai.ml.constants._job.pipeline import PipelineConstants
from azure.ai.ml.entities import Component, Job, PipelineJob
from azure.ai.ml.entities._builders import Command, Pipeline
from azure.ai.ml.entities._builders.do_while import DoWhile
from azure.ai.ml.entities._builders.parallel import Parallel
from azure.ai.ml.entities._builders.spark import Spark
from azure.ai.ml.exceptions import JobException
from azure.ai.ml.operations._run_history_constants import JobStatus
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND, DATABINDING_EXPRESSION_TEST_CASES, \
    DATABINDING_EXPRESSION_TEST_CASE_ENUMERATE


def assert_job_input_output_types(job: PipelineJob):
    from azure.ai.ml.entities._job.pipeline._io import NodeInput, NodeOutput, PipelineInput, PipelineOutput

    for _, input in job.inputs.items():
        assert isinstance(input, PipelineInput)
    for _, output in job.outputs.items():
        assert isinstance(output, PipelineOutput)
    for _, component in job.jobs.items():
        for _, input in component.inputs.items():
            assert isinstance(input, NodeInput)
        for _, output in component.outputs.items():
            assert isinstance(output, NodeOutput)


@pytest.fixture
def generate_weekly_fixed_job_name(variable_recorder) -> str:
    def create_or_record_weekly_fixed_job_name(job_name: str):
        """Add a week postfix to job name, make it a weekly fixed name."""
        c = datetime.utcnow().isocalendar()  # follow CI workspace generate rule
        return variable_recorder.get_or_record(job_name, f"{job_name}_{c[0]}W{c[1]}")

    return create_or_record_weekly_fixed_job_name


# previous bodiless_matcher fixture doesn't take effect because of typo, please add it in method level if needed


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "enable_pipeline_private_preview_features",
    "mock_asset_name",
    "mock_component_hash",
    "enable_environment_id_arm_expansion",
)
@pytest.mark.timeout(timeout=_PIPELINE_JOB_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestPipelineJob(AzureRecordedTestCase):
    def test_pipeline_job_create(
        self,
        client: MLClient,
        hello_world_component_no_paths: Component,
        randstr: Callable[[str], str],
    ) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_no_paths_e2e.yml",
            params_override=params_override,
        )
        job = client.jobs.create_or_update(pipeline_job)
        assert job.name == params_override[0]["name"]
        # Test update
        new_tag_name = randstr("new_tag_name")
        new_tag_value = randstr("new_tag_value")
        job.tags[new_tag_name] = new_tag_value
        updated_job = client.jobs.create_or_update(job)
        assert new_tag_name in updated_job.tags
        assert updated_job.tags[new_tag_name] == new_tag_value

    def test_pipeline_job_create_with_registries(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
    ) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/hello_pipeline_job_with_registries.yml",
            params_override=params_override,
        )
        assert pipeline_job.jobs.get("a").environment == "azureml://registries/testFeed/environments/sklearn-10-ubuntu2004-py38-cpu/versions/19.dev6"
        job = client.jobs.create_or_update(pipeline_job)
        assert job.name == params_override[0]["name"]
        assert job.jobs.get("a").component == "azureml://registries/testFeed/components/my_hello_world_asset_2/versions/1"

    @pytest.mark.skip("Skip for compute reaource not ready.")
    @pytest.mark.parametrize(
        "pipeline_job_path",
        [
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/wordcount_pipeline.yml",
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/sample_pipeline.yml",
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/pipeline.yml",
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/pipeline_inline_job.yml",
            "./tests/test_configs/pipeline_jobs/shakespear-sample-and-word-count-using-spark/pipeline.yml",
        ],
    )
    def test_pipeline_job_with_spark_job(
        self, client: MLClient, randstr: Callable[[], str], pipeline_job_path: str
    ) -> None:
        # todo: run failed
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            pipeline_job_path,
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)

        for job in created_job.jobs.values():
            # The spark job must be translated to component job in the pipeline job.
            assert isinstance(job, Spark)

    @pytest.mark.skip(reason="TODO: 1795498, test will fail if create new job and immediately cancel it.")
    def test_pipeline_job_get_child_run(self, client: MLClient, generate_weekly_fixed_job_name: Callable[[str], str]):
        job_name = "{}_{}".format(
            generate_weekly_fixed_job_name(job_name="helloworld_pipeline_job_quick_with_output"),
            "test_pipeline_job_get_child_run",
        )
        try:
            job = client.jobs.get(job_name)
        except ResourceNotFoundError:
            job = assert_job_cancel(
                load_job(
                    source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_quick_with_output.yml",
                    params_override=[{"name": job_name}],
                ),
                client=client,
            )

        child_job = next(
            job
            for job in client.jobs.list(parent_job_name=job.name)
            if job.display_name == "hello_world_inline_commandjob_1"
        )

        retrieved_child_run = client.jobs.get(child_job.name)

        assert isinstance(retrieved_child_run, Job)
        assert retrieved_child_run.name == child_job.name

    @pytest.mark.parametrize(
        "pipeline_job_path",
        [
            # flaky parameterization
            # "non_existent_remote_component.yml",
            "non_existent_remote_version.yml",
            "non_existent_compute.yml",
        ],
    )
    def test_pipeline_job_validation_remote(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        pipeline_job_path: str,
    ) -> None:
        base_dir = "./tests/test_configs/pipeline_jobs/invalid/"
        pipeline_job: PipelineJob = load_job(
            source=os.path.join(base_dir, pipeline_job_path),
            params_override=[{"name": randstr("name")}],
        )
        with pytest.raises(
            Exception,
            # hide this as server side error message is not consistent
            # match=str(expected_error),
        ):
            client.jobs.create_or_update(pipeline_job)

    def test_pipeline_job_with_inline_component_create(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_comps.yml",
            params_override=params_override,
        )
        assert pipeline_job.jobs["hello_world_component_inline"].component._schema is None
        assert pipeline_job.jobs["hello_world_component_inline_with_schema"].component._schema
        job_sources = {key: job._source for key, job in pipeline_job.jobs.items()}
        assert job_sources == {
            "hello_world_component_inline": "YAML.JOB",
            "hello_world_component_inline_with_schema": "YAML.JOB",
        }
        client.jobs.create_or_update(pipeline_job)
        created_component_id = pipeline_job.jobs["hello_world_component_inline"].component
        rest_job_sources = {key: job._source for key, job in pipeline_job.jobs.items()}
        self.assert_component_is_anonymous(client, created_component_id)
        assert rest_job_sources == job_sources

    def test_pipeline_job_with_inline_component_file_create(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        # Create the component used in the job
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_file_comps.yml",
            params_override=params_override,
        )
        client.jobs.create_or_update(pipeline_job)
        created_component_id = pipeline_job.jobs["hello_world_component_inline_file"].component
        self.assert_component_is_anonymous(client, created_component_id)

    def test_pipeline_job__with_inline_component_file_in_component_folder(
        self,
        client: MLClient,
        hello_world_component_no_paths: Component,
        randstr: Callable[[str], str],
    ) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/dsl_pipeline/basic_component_with_component_in_folder/pipeline.yml",
            params_override=params_override,
        )
        client.jobs.create_or_update(pipeline_job)
        created_component_id = pipeline_job.jobs["hello_python_world_job"].component
        self.assert_component_is_anonymous(client, created_component_id)

    def test_pipeline_job_with_component_arm_id_create(
        self,
        client: MLClient,
        hello_world_component: Component,
        randstr: Callable[[str], str],
    ) -> None:
        # Generate pipeline with component defined by arm id
        pipeline_spec_path = Path("./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_file_comps.yml")
        pipeline_dict = load_yaml(pipeline_spec_path)
        pipeline_jobs = pipeline_dict["jobs"]
        for job in pipeline_jobs.values():
            job["component"] = f"azureml:{hello_world_component.id}"

        # Create the component used in the job
        params_override = [{"name": randstr("name")}]
        pipeline_job = Job._load(
            data=pipeline_dict,
            yaml_path=pipeline_spec_path,
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)
        assert (
            created_job.jobs["hello_world_component_inline_file"].component
            == f"{hello_world_component.name}:{hello_world_component.version}"
        )

    def test_pipeline_job_create_with_resolve_reuse(
        self,
        client: MLClient,
        hello_world_component_no_paths: Component,
        randstr: Callable[[str], str],
    ) -> None:
        # Generate pipeline with component defined by arm id
        pipeline_spec_path = Path("./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_resolve_reuse.yml")

        # Create the component used in the job
        params_override = [{"name": randstr("name")}]
        pipeline_job: PipelineJob = load_job(source=pipeline_spec_path, params_override=params_override)
        assert isinstance(
            pipeline_job.jobs["hello_world_component_1"].component, str
        ), "named component must be in str instead of component object to avoid arm id resolving"
        assert isinstance(pipeline_job.jobs["hello_world_component_2"].component, str)

        assert id(pipeline_job.jobs["hello_world_component_inline_file_1"]) != id(
            pipeline_job.jobs["hello_world_component_inline_file_2"]
        ), "In load_job, components load from the same path shouldn't share the same Command instance."

        assert id(pipeline_job.jobs["hello_world_component_inline_file_1"].component) == id(
            pipeline_job.jobs["hello_world_component_inline_file_2"].component
        ), "In load_job, components load from the same path should share the same Component instance."

        # name & version in a local component yml will be ignored if it's a sub-job of a pipeline job
        _ = client.jobs.create_or_update(pipeline_job)

    def test_pipeline_job_with_output(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_component_output.yml",
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)

        # Some sanity checking of the outputs. Unit tests already extensively cover the translation to/from REST of outputs. If the job finishes successfully,
        # that means all of the outputs were set properly by the CLI.
        job_out_1 = created_job.outputs.get("job_out_path_1", None)
        assert job_out_1 is not None
        assert job_out_1.mode == InputOutputModes.RW_MOUNT

        job_out_2 = created_job.outputs.get("job_out_path_2", None)
        assert job_out_2 is not None
        assert job_out_2.mode == InputOutputModes.UPLOAD

        hello_world_component_1_outputs = created_job.jobs["hello_world_component_1"].outputs
        assert hello_world_component_1_outputs.component_out_path_1.mode == InputOutputModes.RW_MOUNT

        hello_world_component_2_outputs = created_job.jobs["hello_world_component_2"].outputs
        assert hello_world_component_2_outputs.component_out_path_1.mode == InputOutputModes.RW_MOUNT

    def test_pipeline_job_with_path_inputs(
        self,
        client: MLClient,
        helloworld_component_with_paths: Component,
        randstr: Callable[[str], str],
    ) -> None:
        # Create a data asset to put in the PipelineJob inputs
        data_override = [{"name": randstr("data_override_name")}]
        data = load_data(
            source="./tests/test_configs/dataset/data_local_path_with_datastore.yaml",
            params_override=data_override,
        )
        data_asset = client.data.create_or_update(data)

        params_override = [
            {"name": randstr("job_name")},
            {"inputs.job_in_path_other.path": data_asset.path},
        ]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_paths.yml",
            params_override=params_override,
        )
        client.jobs.create_or_update(pipeline_job)
        assert pipeline_job.inputs["job_in_path_other"].path.startswith("azureml")
        assert pipeline_job.inputs["job_in_path"].path.startswith("azureml")

    def assert_component_is_anonymous(self, client: MLClient, component_id: str) -> None:
        # extract component name, version from arm id
        arm_id = AMLVersionedArmId(component_id)
        created_component = client.components.get(arm_id.asset_name, arm_id.asset_version)
        assert created_component._is_anonymous

    def test_pipeline_job_default_datastore_compute(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_e2e.yml",
            params_override=params_override,
        )
        origin_pipeline_job_settings = vars(pipeline_job.settings).copy()
        created_job: PipelineJob = client.jobs.create_or_update(pipeline_job)
        created_job_settings = vars(created_job.settings)
        created_job_dict = created_job._to_dict()

        for key in [
            PipelineConstants.CONTINUE_ON_STEP_FAILURE,
            PipelineConstants.DEFAULT_COMPUTE,
            PipelineConstants.DEFAULT_DATASTORE,
        ]:
            input_val = origin_pipeline_job_settings.get(key, None)
            assert (
                created_job_settings.get(key, None) == input_val
            ), "client created job " "setting is mismatched with loaded job setting on {}: {} != {}".format(
                key, created_job_settings.get(key, None), input_val
            )
            if key == PipelineConstants.CONTINUE_ON_STEP_FAILURE:
                assert created_job_dict["settings"][key] == input_val
            else:
                assert created_job_dict["settings"][key] == f"azureml:{input_val}"
            # TODO: note that client.jobs.create_or_update will update the input pipeline job object
            # assert input_val == pipeline_job_settings.get(key, None)

        # Compute for components stays as None, the backend will leverage the default
        for job_name, job in created_job.jobs.items():
            if not pipeline_job.jobs[job_name].compute:
                assert not job.compute
            else:
                assert job.compute in pipeline_job.jobs[job_name].compute

    @pytest.mark.parametrize(
        "test_case_i,test_case_name",
        [
            # TODO: enable this after identity support released to canary
            # (0, "helloworld_pipeline_job_with_component_output"),
            (1, "helloworld_pipeline_job_with_paths"),
        ]
    )
    def test_pipeline_job_with_command_job(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        test_case_i,
        test_case_name,
    ) -> None:
        params = [
            (
                "tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_with_command_job_e2e.yml",
                2,
                {
                    "description": "The hello world pipeline job with inline command job",
                    "tags": {"tag": "tagvalue", "owner": "sdkteam"},
                    "compute_id": "cpu-cluster",
                    "is_archived": False,
                    "job_type": "Pipeline",
                    "inputs": {
                        "job_data_path": {
                            "mode": "ReadOnlyMount",
                            "uri": "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                            "job_input_type": "uri_file",
                        }
                    },
                    "jobs": {
                        "hello_world_inline_commandjob_1": {
                            "type": "command",
                            "resources": None,
                            "distribution": None,
                            "limits": None,
                            "environment_variables": {"FOO": "bar"},
                            "name": "hello_world_inline_commandjob_1",
                            "display_name": None,
                            "tags": {},
                            "computeId": "cpu-cluster",
                            "inputs": {
                                "test1": {
                                    "mode": "ReadOnlyMount",
                                    "uri": "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                                    "job_input_type": "uri_file",
                                },
                                "literal_input": {"job_input_type": "literal", "value": "2"},
                            },
                            "outputs": {},
                            "_source": "REMOTE.WORKSPACE.COMPONENT",
                        },
                        "hello_world_inline_commandjob_2": {
                            "type": "command",
                            "resources": None,
                            "distribution": None,
                            "limits": None,
                            "environment_variables": {},
                            "name": "hello_world_inline_commandjob_2",
                            "display_name": None,
                            "tags": {},
                            "computeId": None,
                            "inputs": {},
                            "outputs": {},
                            "_source": "REMOTE.WORKSPACE.COMPONENT",
                        },
                    },
                    "outputs": {"job_out_path_1": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}},
                    "settings": {
                        "default_compute": "cpu-cluster",
                        "default_datastore": "workspacefilestore",
                        "continue_on_step_failure": True,
                        "_source": "YAML.JOB",
                    },
                },
                [
                    "properties",
                    "display_name",
                    "experiment_name",
                    "jobs.hello_world_inline_commandjob_1.componentId",
                    "jobs.hello_world_inline_commandjob_2.componentId",
                    "jobs.hello_world_inline_commandjob_1.properties",
                    "jobs.hello_world_inline_commandjob_2.properties",
                    "source_job_id",
                ],
            ),
            (
                "tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_registered_component_literal_output_binding_to_inline_job_input.yml",
                2,
                {
                    "description": "E2E dummy train-score-eval pipeline with registered components",
                    "tags": {},
                    "compute_id": "cpu-cluster",
                    "display_name": "e2e_registered_components",
                    "is_archived": False,
                    "job_type": "Pipeline",
                    "inputs": {
                        "pipeline_job_training_input": {"mode": "ReadOnlyMount", "job_input_type": "uri_folder"},
                        "pipeline_job_test_input": {"mode": "ReadOnlyMount", "job_input_type": "uri_folder"},
                        "pipeline_job_training_max_epocs": {"job_input_type": "literal", "value": "20"},
                        "pipeline_job_training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                        "pipeline_job_learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
                    },
                    "jobs": {
                        "train_job": {
                            "type": "command",
                            "resources": None,
                            "distribution": None,
                            "limits": None,
                            "environment_variables": {},
                            "name": "train_job",
                            "display_name": None,
                            "tags": {},
                            "computeId": None,
                            "inputs": {
                                "training_data": {
                                    "job_input_type": "literal",
                                    "value": "${{parent.inputs.pipeline_job_training_input}}",
                                },
                                "max_epocs": {
                                    "job_input_type": "literal",
                                    "value": "${{parent.inputs.pipeline_job_training_max_epocs}}",
                                },
                                "learning_rate": {
                                    "job_input_type": "literal",
                                    "value": "${{parent.inputs.pipeline_job_training_learning_rate}}",
                                },
                                "learning_rate_schedule": {
                                    "job_input_type": "literal",
                                    "value": "${{parent.inputs.pipeline_job_learning_rate_schedule}}",
                                },
                            },
                            "outputs": {
                                "model_output": {
                                    "value": "${{parent.outputs.pipeline_job_trained_model}}",
                                    "type": "literal",
                                }
                            },
                            "_source": "REMOTE.WORKSPACE.COMPONENT",
                            "componentId": "Train:31",
                        },
                        "score_job": {
                            "type": "command",
                            "resources": None,
                            "distribution": None,
                            "limits": None,
                            "environment_variables": {},
                            "name": "score_job",
                            "display_name": None,
                            "tags": {},
                            "computeId": None,
                            "inputs": {
                                "model_input": {
                                    "job_input_type": "literal",
                                    "value": "${{parent.jobs.train_job.outputs.model_output}}",
                                },
                                "test_data": {
                                    "job_input_type": "literal",
                                    "value": "${{parent.inputs.pipeline_job_test_input}}",
                                },
                            },
                            "outputs": {},
                            "_source": "REMOTE.WORKSPACE.COMPONENT",
                        },
                    },
                    "outputs": {
                        "pipeline_job_trained_model": {"mode": "Upload", "job_output_type": "uri_folder"},
                        "pipeline_job_scored_data": {"mode": "Upload", "job_output_type": "uri_folder"},
                    },
                    "settings": {"_source": "YAML.JOB"},
                },
                [
                    "properties",
                    "experiment_name",
                    "inputs.pipeline_job_training_input.uri",
                    "inputs.pipeline_job_test_input.uri",
                    "jobs.score_job.componentId",
                    "jobs.train_job.properties",
                    "jobs.score_job.properties",
                    "source_job_id",
                ],
            ),
        ]
        pipeline_job_path, converted_jobs, expected_dict, fields_to_omit = params[test_case_i]

        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source=pipeline_job_path,
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)

        for job in created_job.jobs.values():
            # The command job must be translated to component job in the pipeline job.
            assert isinstance(job, Command)

        # assert on the number of converted jobs to make sure we didn't drop the command job
        assert len(created_job.jobs.items()) == converted_jobs

        pipeline_dict = created_job._to_rest_object().as_dict()
        actual_dict = pydash.omit(pipeline_dict["properties"], *fields_to_omit)
        assert actual_dict == expected_dict

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="need further investigation for these cases unreliability under none live mode")
    @pytest.mark.parametrize(
        "pipeline_job_path",
        [
            "file_component_input_e2e.yml",
            "file_input_e2e.yml",
            "tabular_input_e2e.yml",
        ],
    )
    def test_pipeline_job_with_parallel_job(
        self, client: MLClient, randstr: Callable[[str], str], pipeline_job_path: str
    ) -> None:
        base_file_name = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_with_parallel_job_"
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source=base_file_name + pipeline_job_path,
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)

        for job in created_job.jobs.values():
            # The parallel job must be translated to component job in the pipeline job.
            assert isinstance(job, Parallel)

        # assert on the number of converted jobs to make sure we didn't drop the parallel job
        assert len(created_job.jobs.items()) == 1

    def test_pipeline_job_with_multiple_parallel_job(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/pipeline.yml",
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)

        # assert on the number of converted jobs to make sure we didn't drop the parallel job
        assert len(created_job.jobs.items()) == 3

    def test_pipeline_job_with_command_job_with_dataset_short_uri(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:

        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_with_command_job_e2e_short_uri.yml",
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)

        for job in created_job.jobs.values():
            # The command job must be translated to component job in the pipeline job.
            assert isinstance(job, Command)

        # assert on the number of converted jobs to make sure we didn't drop the command job
        assert len(created_job.jobs.items()) == 2

    def test_pipeline_job_without_component_snapshot(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_without_component_snapshot.yml",
            params_override=params_override,
        )
        client.jobs.create_or_update(pipeline_job)
        created_component_id = pipeline_job.jobs["hello_world_component_inline"].component
        self.assert_component_is_anonymous(client, created_component_id)

    def test_pipeline_job_create_with_distribution_component(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_distribution_component.yml",
            params_override=params_override,
        )
        _ = pipeline_job._to_dict()
        created_job: PipelineJob = client.jobs.create_or_update(pipeline_job)
        created_job_dict = created_job._to_dict()

        created_component_id = pipeline_job.jobs["hello_world_component_mpi"].component
        self.assert_component_is_anonymous(client, created_component_id)

        for job_name, key, value in [
            ("hello_world_component_mpi", "process_count_per_instance", 3),
            ("hello_world_component_pytorch", "process_count_per_instance", 4),
            ("hello_world_component_tensorflow", "worker_count", 5),
        ]:
            instance_count = pydash.get(created_job_dict, "jobs.{}.resources.instance_count".format(job_name))
            assert instance_count == value, "{} resource attr is not set: {} != {}".format(
                job_name, instance_count, value
            )
            process_count_per_instance = pydash.get(created_job_dict, "jobs.{}.distribution.{}".format(job_name, key))
            assert process_count_per_instance == value, "{} distribution attr is not set: {} != {}".format(
                job_name, process_count_per_instance, value
            )

    @pytest.mark.disable_mock_code_hash
    def test_pipeline_job_anonymous_component_reuse(
        self,
        client: MLClient,
        hello_world_component: Component,
        randstr: Callable[[str], str],
    ) -> None:
        # create a pipeline job
        params_override = [{"name": randstr("job_name_1")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_comps.yml",
            params_override=params_override,
        )
        created_job1 = client.jobs.create_or_update(pipeline_job)

        # create another pipeline job
        params_override = [{"name": randstr("job_name_2")}]
        pipeline_job2 = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_comps.yml",
            params_override=params_override,
        )
        created_job2 = client.jobs.create_or_update(pipeline_job2)

        for job_name, job in created_job1.jobs.items():
            inline_component1 = created_job1.jobs[job_name].component
            inline_component2 = created_job2.jobs[job_name].component
            assert inline_component1 == inline_component2

    def test_pipeline_job_dependency_label_resolution(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        component_name = randstr("component_name")
        component_versions = ["foo", "bar", "baz", "foobar"]

        # Create the component used in the job
        for version in component_versions:
            created_component = client.components.create_or_update(
                load_component(
                    "./tests/test_configs/components/helloworld_component.yml",
                    params_override=[{"name": component_name}, {"version": version}],
                )
            )
            assert created_component.version == version
            assert created_component.name == component_name

        # Generate pipeline with component defined by arm id
        pipeline_spec_path = Path("./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_inline_file_comps.yml")
        pipeline_dict = load_yaml(pipeline_spec_path)

        # Check to see that component label gets resolved to an actual version
        job_key = "hello_world_component_inline_file"
        pipeline_dict["jobs"][job_key]["component"] = f"azureml:{component_name}@latest"

        pipeline_job = Job._load(
            data=pipeline_dict,
            yaml_path=pipeline_spec_path,
            params_override=[{"name": randstr("job_name")}],
        )
        # sleep for some time to so more likely to resolve the correct component latest version
        sleep_if_live(10)
        created_job = client.jobs.create_or_update(pipeline_job)
        assert created_job.jobs[job_key].component == f"{component_name}:{component_versions[-1]}"

    @pytest.mark.skip(reason="migration skip: refactor for download.")
    def test_pipeline_job_download(
        self, client: MLClient, tmp_path: Path, generate_weekly_fixed_job_name: Callable[[str], str]
    ) -> None:
        job_name = "{}_{}".format(
            generate_weekly_fixed_job_name(job_name="helloworld_pipeline_job_quick_with_output"),
            "test_pipeline_job_download",
        )
        try:
            job = client.jobs.get(job_name)
        except ResourceNotFoundError:
            job = client.jobs.create_or_update(
                load_job(
                    source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_quick_with_output.yml",
                    params_override=[{"name": job_name}],
                )
            )
        job_status = wait_until_done(client, job, timeout=60)
        client.jobs.download(name=job.name, download_path=tmp_path)
        if job_status != JobStatus.CANCELED:
            artifact_dir = tmp_path / "artifacts"
            assert artifact_dir.exists()
            assert next(artifact_dir.iterdir(), None), "No artifacts were downloaded"
        else:
            print("Job is canceled, not execute downloaded artifacts assertion.")

    def test_pipeline_job_child_run_download(
        self, client: MLClient, tmp_path: Path, generate_weekly_fixed_job_name: Callable[[str], str]
    ) -> None:
        job_name = "{}_{}".format(
            generate_weekly_fixed_job_name(job_name="helloworld_pipeline_job_quick_with_output"),
            "test_pipeline_job_child_run_download",
        )
        try:
            job = client.jobs.get(job_name)
        except ResourceNotFoundError:
            job = client.jobs.create_or_update(
                load_job(
                    source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_quick_with_output.yml",
                    params_override=[{"name": job_name}],
                )
            )

        job_status = wait_until_done(client, job, timeout=300)
        if job_status == JobStatus.CANCELED:
            print("Job is canceled, not execute downloaded artifacts assertion.")
            return

        child_job = next(
            job
            for job in client.jobs.list(parent_job_name=job.name)
            if job.display_name == "hello_world_inline_commandjob_1"
        )
        client.jobs.download(name=child_job.name, download_path=tmp_path)
        client.jobs.download(
            name=child_job.name,
            download_path=tmp_path,
            output_name="component_out_path_1",
        )
        artifact_dir = tmp_path / "artifacts"
        output_dir = tmp_path / "named-outputs" / "component_out_path_1"
        assert artifact_dir.exists()
        assert next(artifact_dir.iterdir(), None), "No artifacts were downloaded"
        assert output_dir.exists()
        assert next(output_dir.iterdir(), None), "No artifacts were downloaded"

    def test_sample_job_dump(self, client: MLClient, randstr: Callable[[str], str]):
        job = client.jobs.create_or_update(
            load_job(
                source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_quick_with_output.yml",
                params_override=[{"name": randstr("name")}],
            )
        )
        job_dict = job._to_dict()
        expected_keys = ["status", "properties", "tags", "creation_context"]
        assert all(key in job_dict.keys() for key in expected_keys), f"failed to get expected keys in {job_dict}"

        # original job did not change
        assert_job_input_output_types(job)

    def test_pipeline_job_with_sweep_node(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_sweep_node.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline: PipelineJob = client.jobs.create_or_update(pipeline)
        created_pipeline_dict = created_pipeline._to_dict()
        for dot_key, expected_value in [
            (
                "jobs.hello_sweep_inline_trial.objective",
                {
                    "goal": "maximize",
                    "primary_metric": "accuracy",
                },
            ),
            ("jobs.hello_sweep_inline_trial.sampling_algorithm", "random"),
            (
                "jobs.hello_sweep_inline_trial.limits",
                {
                    "max_concurrent_trials": 10,
                    "max_total_trials": 20,
                    "timeout": 7200,
                },
            ),
            (
                "jobs.hello_sweep_inline_trial.early_termination",
                {
                    "delay_evaluation": 200,
                    "type": "median_stopping",
                    "evaluation_interval": 100,
                },
            ),
            (
                "jobs.hello_sweep_inline_remote_trial.objective",
                {
                    "goal": "maximize",
                    "primary_metric": "accuracy",
                },
            ),
            (
                "jobs.hello_sweep_inline_remote_trial.trial",
                "azureml:microsoftsamplescommandcomponentbasic_nopaths_test:1",
            ),
            ("jobs.hello_sweep_inline_trial.compute", "azureml:gpu-cluster"),
            # test using compute from pipeline default compute
            ("jobs.hello_sweep_inline_file_trial.compute", None),
        ]:
            loaded_value = pydash.get(created_pipeline_dict, dot_key, None)
            assert loaded_value == expected_value, f"{dot_key} isn't as expected: {loaded_value} != {expected_value}"

    @pytest.mark.parametrize(
        "policy_yaml_dict",
        [
            {
                "type": "median_stopping",
                "delay_evaluation": 200,
                "evaluation_interval": 100,
            },
            {
                "type": "bandit",
                "delay_evaluation": 1,
                "evaluation_interval": 2,
                "slack_factor": 0.1,
            },
            {
                "type": "bandit",
                "delay_evaluation": 1,
                "evaluation_interval": 2,
                "slack_amount": 0.1,
            },
            {
                "type": "truncation_selection",
                "delay_evaluation": 1,
                "evaluation_interval": 2,
                "truncation_percentage": 20,
            },
        ],
    )
    def test_pipeline_job_with_sweep_node_early_termination_policy(
        self, client: MLClient, randstr: Callable[[str], str], policy_yaml_dict: Dict[str, Any]
    ):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_sweep_node.yml"
        pipeline: PipelineJob = load_job(
            source=test_path,
            params_override=[
                {"name": randstr("randstr")},
                {"jobs.hello_sweep_inline_trial.early_termination": policy_yaml_dict},
            ],
        )
        created_pipeline: PipelineJob = client.jobs.create_or_update(pipeline)
        created_pipeline_dict = created_pipeline._to_dict()
        assert pydash.get(created_pipeline_dict, "jobs.hello_sweep_inline_trial.early_termination") == policy_yaml_dict

    @pytest.mark.parametrize(
        "test_case_i, test_case_name",
        DATABINDING_EXPRESSION_TEST_CASE_ENUMERATE,
    )
    def test_pipeline_job_with_data_binding_expression(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        test_case_i: int,
        test_case_name: str,
    ):
        pipeline_job_path, expected_error = DATABINDING_EXPRESSION_TEST_CASES[test_case_i]

        pipeline: PipelineJob = load_job(source=pipeline_job_path, params_override=[{"name": randstr("name")}])
        if expected_error is None:
            assert_job_cancel(pipeline, client)
        elif isinstance(expected_error, HttpResponseError):
            with pytest.raises(HttpResponseError):
                client.jobs.create_or_update(pipeline)
        elif isinstance(expected_error, JobException):
            assert_job_cancel(pipeline, client)
        else:
            raise Exception("Unexpected error type {}".format(type(expected_error)))

    def test_pipeline_job_with_automl_regression(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_regression.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "training_data", "validation_data", "experiment_name", "properties"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["hello_automl_regression"], fields_to_omit)

        assert actual_dict == {
            "featurization": {"mode": "off"},
            "limits": {"max_concurrent_trials": 1, "max_trials": 1},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "r2_score",
            "tags": {},
            "target_column_name": "SalePrice",
            "task": "regression",
            "test_data": "${{parent.inputs.automl_test_data}}",
            "training": {"enable_stack_ensemble": False, "enable_vote_ensemble": False},
            "type": "automl",
        }

    def test_pipeline_job_with_automl_classification(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_classification.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["hello_automl_classification"], fields_to_omit)

        assert actual_dict == {
            "featurization": {"mode": "auto"},
            "limits": {"max_concurrent_trials": 1, "max_trials": 1},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "y",
            "task": "classification",
            "training": {"enable_stack_ensemble": False, "enable_vote_ensemble": False},
            "training_data": "${{parent.inputs.classification_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.classification_validate_data}}",
            "test_data": "${{parent.inputs.classification_test_data}}",
        }

    def test_pipeline_job_with_automl_forecasting(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_forecasting.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()

        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["hello_automl_forecasting"], fields_to_omit)

        assert actual_dict == {
            "featurization": {"mode": "auto"},
            "limits": {"max_concurrent_trials": 1, "max_trials": 1},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "normalized_root_mean_squared_error",
            "tags": {},
            "target_column_name": "BeerProduction",
            "task": "forecasting",
            "training": {"enable_stack_ensemble": False, "enable_vote_ensemble": False},
            "training_data": "${{parent.inputs.forecasting_train_data}}",
            "n_cross_validations": 2,
            "type": "automl",
            "forecasting": {"forecast_horizon": 12, "time_column_name": "DATE", "frequency": "MS"},
        }

    def test_pipeline_job_with_automl_text_classification(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_classification.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()

        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["automl_text_classification"], fields_to_omit)

        assert actual_dict == {
            "featurization": {"dataset_language": "eng"},
            "limits": {"max_trials": 1, "max_nodes": 1, "timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "y",
            "task": "text_classification",
            "training_data": "${{parent.inputs.text_classification_training_data}}",
            "validation_data": "${{parent.inputs.text_classification_validation_data}}",
            "type": "automl",
        }

    def test_pipeline_job_with_automl_text_classification_multilabel(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = (
            "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_classification_multilabel.yml"
        )
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()

        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(
            pipeline_dict["properties"]["jobs"]["automl_text_classification_multilabel"], fields_to_omit
        )

        assert actual_dict == {
            "limits": {"max_trials": 1, "max_nodes": 1, "timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "terms",
            "task": "text_classification_multilabel",
            "training_data": "${{parent.inputs.text_classification_multilabel_training_data}}",
            "validation_data": "${{parent.inputs.text_classification_multilabel_validation_data}}",
            "type": "automl",
        }

    def test_pipeline_job_with_automl_text_ner(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_ner.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()

        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["automl_text_ner"], fields_to_omit)

        assert actual_dict == {
            "limits": {"max_trials": 1, "max_nodes": 1, "timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "task": "text_ner",
            "training_data": "${{parent.inputs.text_ner_training_data}}",
            "validation_data": "${{parent.inputs.text_ner_validation_data}}",
            "type": "automl",
        }

    def test_pipeline_job_with_automl_image_multiclass_classification(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multiclass_classification.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(
            pipeline_dict["properties"]["jobs"]["hello_automl_image_multiclass_classification"], fields_to_omit
        )

        assert actual_dict == {
            "limits": {"timeout_minutes": 60, "max_concurrent_trials": 4, "max_trials": 20},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "label",
            "task": "image_classification",
            "training_data": "${{parent.inputs.image_multiclass_classification_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_multiclass_classification_validate_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "training_parameters": {
                "checkpoint_frequency": 1,
                "early_stopping": True,
                "early_stopping_delay": 2,
                "early_stopping_patience": 2,
                "evaluation_frequency": 1,
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.005,0.05)",
                    "model_name": "choice('vitb16r224')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "warmup_cosine_lr_warmup_epochs": "choice(0,3)",
                }
            ],
        }

    def test_pipeline_job_with_automl_image_multilabel_classification(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multilabel_classification.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(
            pipeline_dict["properties"]["jobs"]["hello_automl_image_multilabel_classification"], fields_to_omit
        )

        assert actual_dict == {
            "limits": {"timeout_minutes": 60, "max_concurrent_trials": 4, "max_trials": 20},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "iou",
            "tags": {},
            "target_column_name": "label",
            "task": "image_classification_multilabel",
            "training_data": "${{parent.inputs.image_multilabel_classification_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_multilabel_classification_validate_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "training_parameters": {
                "checkpoint_frequency": 1,
                "early_stopping": True,
                "early_stopping_delay": 2,
                "early_stopping_patience": 2,
                "evaluation_frequency": 1,
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.005,0.05)",
                    "model_name": "choice('vitb16r224')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "warmup_cosine_lr_warmup_epochs": "choice(0,3)",
                }
            ],
        }

    def test_pipeline_job_with_automl_image_object_detection(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_object_detection.yml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(
            pipeline_dict["properties"]["jobs"]["hello_automl_image_object_detection"], fields_to_omit
        )

        assert actual_dict == {
            "limits": {"timeout_minutes": 60, "max_concurrent_trials": 4, "max_trials": 20},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "mean_average_precision",
            "tags": {},
            "target_column_name": "label",
            "task": "image_object_detection",
            "training_data": "${{parent.inputs.image_object_detection_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_object_detection_validate_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "training_parameters": {
                "checkpoint_frequency": 1,
                "early_stopping": True,
                "early_stopping_delay": 2,
                "early_stopping_patience": 2,
                "evaluation_frequency": 1,
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.005,0.05)",
                    "model_name": "choice('fasterrcnn_resnet50_fpn')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "warmup_cosine_lr_warmup_epochs": "choice(0,3)",
                    "min_size": "choice(600,800)",
                }
            ],
        }

    def test_pipeline_job_with_automl_image_instance_segmentation(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = (
            "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_instance_segmentation.yml"
        )
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        actual_dict = pydash.omit(
            pipeline_dict["properties"]["jobs"]["hello_automl_image_instance_segmentation"], fields_to_omit
        )

        assert actual_dict == {
            "limits": {"timeout_minutes": 60, "max_concurrent_trials": 4, "max_trials": 20},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "mean_average_precision",
            "tags": {},
            "target_column_name": "label",
            "task": "image_instance_segmentation",
            "training_data": "${{parent.inputs.image_instance_segmentation_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_instance_segmentation_validate_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "training_parameters": {
                "checkpoint_frequency": 1,
                "early_stopping": True,
                "early_stopping_delay": 2,
                "early_stopping_patience": 2,
                "evaluation_frequency": 1,
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.005,0.05)",
                    "model_name": "choice('maskrcnn_resnet50_fpn')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "warmup_cosine_lr_warmup_epochs": "choice(0,3)",
                    "min_size": "choice(600,800)",
                }
            ],
        }

    def test_pipeline_without_setting_binding_node(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_without_setting_binding_node.yml",
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)
        trained_model = created_job.outputs.get("trained_model", None)
        assert trained_model is not None
        assert trained_model.mode == InputOutputModes.RW_MOUNT

        training_input = created_job.inputs.get("training_input", None)
        assert training_input is not None
        assert training_input.mode == InputOutputModes.RO_MOUNT

        train_job = created_job.jobs["train_job"]
        assert train_job.outputs.model_output.mode is None

        assert train_job.inputs.training_data.mode is None

    def test_pipeline_with_only_setting_pipeline_level(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_with_only_setting_pipeline_level.yml",
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)
        trained_model = created_job.outputs.get("trained_model", None)
        assert trained_model is not None
        assert trained_model.mode == InputOutputModes.UPLOAD

        training_input = created_job.inputs.get("training_input", None)
        assert training_input is not None
        assert training_input.mode == InputOutputModes.RO_MOUNT

        train_job = created_job.jobs["train_job"]
        assert train_job.outputs.model_output.mode is None

        assert train_job.inputs.training_data.mode is None

    def test_pipeline_with_only_setting_binding_node(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_with_only_setting_binding_node.yml",
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)
        trained_model = created_job.outputs.get("trained_model", None)
        assert trained_model is not None
        assert trained_model.mode == InputOutputModes.RW_MOUNT

        training_input = created_job.inputs.get("training_input", None)
        assert training_input is not None
        assert training_input.mode == InputOutputModes.RO_MOUNT

        train_job = created_job.jobs["train_job"]
        assert train_job.outputs.model_output.mode is InputOutputModes.UPLOAD

        assert train_job.inputs.training_data.mode is InputOutputModes.RO_MOUNT

    def test_pipeline_with_setting_binding_node_and_pipeline_level(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_with_setting_binding_node_and_pipeline_level.yml",
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)
        trained_model = created_job.outputs.get("trained_model", None)
        assert trained_model is not None
        assert trained_model.mode == InputOutputModes.RW_MOUNT

        training_input = created_job.inputs.get("training_input", None)
        assert training_input is not None
        assert training_input.mode == InputOutputModes.DOWNLOAD

        train_job = created_job.jobs["train_job"]
        assert train_job.outputs.model_output.mode is InputOutputModes.UPLOAD

        assert train_job.inputs.training_data.mode is InputOutputModes.RO_MOUNT

    def test_pipeline_with_inline_job_setting_binding_node_and_pipeline_level(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_with_inline_job_setting_binding_node_and_pipeline_level.yml",
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)
        trained_model = created_job.outputs.get("trained_model", None)
        assert trained_model is not None
        assert trained_model.mode == InputOutputModes.RW_MOUNT

        training_input = created_job.inputs.get("training_input", None)
        assert training_input is not None
        assert training_input.mode == InputOutputModes.DOWNLOAD

        train_job = created_job.jobs["train_job"]
        assert train_job.outputs.model_output.mode is InputOutputModes.UPLOAD

        assert train_job.inputs.training_data.mode is InputOutputModes.RO_MOUNT

    def test_pipeline_with_pipeline_component(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            "./tests/test_configs/dsl_pipeline/pipeline_with_pipeline_component/pipeline.yml",
            params_override=params_override,
        )
        created_pipeline = assert_job_cancel(pipeline_job, client)
        assert isinstance(created_pipeline.jobs["train_and_evaludate_model1"], Pipeline)
        assert isinstance(created_pipeline.jobs["train_and_evaludate_model2"], Pipeline)
        assert isinstance(created_pipeline.jobs["compare"], Command)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["settings"] == {
            "default_compute": "cpu-cluster",
            "default_datastore": "workspaceblobstore",
            "continue_on_step_failure": False,
            "force_rerun": True,
            "_source": "YAML.JOB",
        }

    def test_pipeline_component_job(self, client: MLClient):
        test_path = "./tests/test_configs/pipeline_jobs/pipeline_component_job.yml"
        job: PipelineJob = load_job(source=test_path)
        rest_job = assert_job_cancel(job, client)
        pipeline_dict = rest_job._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["component_id"]
        assert pipeline_dict["inputs"] == {
            "component_in_number": {"job_input_type": "literal", "value": "10"},
            "component_in_path": {
                "mode": "ReadOnlyMount",
                "uri": "https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
                "job_input_type": "uri_file",
            },
        }
        assert pipeline_dict["outputs"] == {"output_path": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}}
        assert pipeline_dict["settings"] == {"default_compute": "cpu-cluster", "_source": "REMOTE.WORKSPACE.JOB"}

    def test_remote_pipeline_component_job(self, client: MLClient, randstr: Callable[[str], str]):
        params_override = [{"name": randstr("component_name")}]
        test_path = "./tests/test_configs/components/helloworld_pipeline_component.yml"
        component = load_component(source=test_path, params_override=params_override)
        rest_component = client.components.create_or_update(component)
        pipeline_node = rest_component(
            component_in_number=10,
            component_in_path=Input(type="uri_file", path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
        )
        pipeline_node.settings.default_compute = "cpu-cluster"
        rest_job = assert_job_cancel(pipeline_node, client)
        pipeline_dict = rest_job._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["component_id"]
        assert pipeline_dict["inputs"] == {
            "component_in_number": {"job_input_type": "literal", "value": "10"},
            "component_in_path": {
                "mode": "ReadOnlyMount",
                "uri": "https://dprepdata.blob.core.windows.net/demo/Titanic.csv",
                "job_input_type": "uri_file",
            },
        }
        # No job output now, https://msdata.visualstudio.com/Vienna/_workitems/edit/1993701/
        # assert pipeline_dict["outputs"] == {"output_path": {"mode": "ReadWriteMount", "job_output_type": "uri_folder"}}
        assert pipeline_dict["settings"] == {"default_compute": "cpu-cluster", "_source": "REMOTE.WORKSPACE.COMPONENT"}

    @pytest.mark.skip(reason="request body still exits when re-record and will raise error "
                             "'Unable to find a record for the request' in playback mode")
    def test_pipeline_job_create_with_registry_model_as_input(
        self,
        client: MLClient,
        registry_client: MLClient,
        randstr: Callable[[str], str],
    ) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/pipeline.yml",
            params_override=params_override,
        )
        job = client.jobs.create_or_update(pipeline_job)
        assert job.name == params_override[0]["name"]

    def test_pipeline_node_with_default_component(self, client: MLClient, randstr: Callable[[str], str]):
        params_override = [{"name": randstr("job_name")}]
        pipeline_job = load_job(
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_default_component.yml",
            params_override=params_override,
        )

        created_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert created_pipeline_job.jobs["hello_world_component"].component == \
               "microsoftsamples_command_component_basic@default"


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "enable_pipeline_private_preview_features",
    "mock_asset_name",
    "mock_component_hash",
)
@pytest.mark.timeout(timeout=_PIPELINE_JOB_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestPipelineJobReuse(AzureRecordedTestCase):
    @pytest.mark.skip(reason="flaky test")
    def test_reused_pipeline_child_job_download(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        tmp_path: Path,
        generate_weekly_fixed_job_name: Callable[[str], str],
    ) -> None:
        pipeline_spec_path = "./tests/test_configs/pipeline_jobs/reuse_child_job_download/pipeline.yml"
        # ensure previous job exists for reuse
        job_name = "{}_{}".format(
            generate_weekly_fixed_job_name(job_name="hello_world_pipeline_job"),
            "test_reused_pipeline_child_job_download",
        )
        print(f"expected reused job name: {job_name}")
        try:
            previous_job = client.jobs.get(job_name)
        except ResourceNotFoundError:
            previous_job = client.jobs.create_or_update(
                load_job(source=pipeline_spec_path, params_override=[{"name": job_name}])
            )
        wait_until_done(client, previous_job)
        # submit a new job that will reuse previous job
        new_job_name = randstr("new_job_name")
        new_job = client.jobs.create_or_update(
            load_job(pipeline_spec_path, params_override=[{"name": new_job_name}]),
        )
        print(f"new submitted job name: {new_job_name}")
        wait_until_done(client, new_job)
        # ensure reuse behavior, get child job and check
        child_jobs = [
            job
            for job in client.jobs.list(parent_job_name=new_job_name)
            if job.display_name == "hello_world_component_inline"
        ]
        assert len(child_jobs) == 1  # expected number of child job
        child_job = child_jobs[0]
        assert child_job.properties.get(PipelineConstants.REUSED_FLAG_FIELD) == PipelineConstants.REUSED_FLAG_TRUE
        # download and check artifacts and named-outputs existence
        client.jobs.download(name=child_job.name, download_path=tmp_path)
        client.jobs.download(name=child_job.name, download_path=tmp_path, output_name="component_out_path")
        artifact_dir = tmp_path / "artifacts"
        output_dir = tmp_path / "named-outputs" / "component_out_path"
        assert artifact_dir.exists()
        assert next(artifact_dir.iterdir(), None), "No artifacts were downloaded"
        assert output_dir.exists()
        assert next(output_dir.iterdir(), None), "No outputs were downloaded"
