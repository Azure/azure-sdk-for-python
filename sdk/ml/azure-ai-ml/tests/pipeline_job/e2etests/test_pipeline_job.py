import os.path
from pathlib import Path
from typing import Any, Callable, Dict

import pydash
import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, assert_job_cancel, sleep_if_live, wait_until_done

from azure.ai.ml import Input, MLClient, load_component, load_data, load_job
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId, is_singularity_id_for_resource
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.constants._job.pipeline import PipelineConstants
from azure.ai.ml.entities import Component, Job, PipelineJob
from azure.ai.ml.entities._builders import Command, Pipeline
from azure.ai.ml.entities._builders.parallel import Parallel
from azure.ai.ml.entities._builders.spark import Spark
from azure.ai.ml.exceptions import JobException
from azure.core.exceptions import HttpResponseError

from .._util import (
    _PIPELINE_JOB_LONG_RUNNING_TIMEOUT_SECOND,
    _PIPELINE_JOB_TIMEOUT_SECOND,
    DATABINDING_EXPRESSION_TEST_CASE_ENUMERATE,
    DATABINDING_EXPRESSION_TEST_CASES,
)


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


@pytest.mark.usefixtures(
    "recorded_test",
    "mock_code_hash",
    "enable_pipeline_private_preview_features",
    "mock_asset_name",
    "mock_component_hash",
    "mock_set_headers_with_user_aml_token",
    "enable_environment_id_arm_expansion",
    "mock_anon_component_version",
)
@pytest.mark.timeout(timeout=_PIPELINE_JOB_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.pipeline_test
class TestPipelineJob(AzureRecordedTestCase):
    # Please set ML_TENANT_ID in your environment variables when recording this test.
    # It will to help sanitize RequestBody.Studio.endpoint for job creation request.
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

    @pytest.mark.skipif(condition=not is_live(), reason="registry test, may fail in playback mode")
    def test_pipeline_job_create_with_registries(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/hello_pipeline_job_with_registries.yml",
            params_override=params_override,
        )
        # registry sdk-test may be sanitized as other name, so use two assertions to avoid this issue
        assert str(pipeline_job.jobs["a"].environment).startswith("azureml://registries/")
        assert str(pipeline_job.jobs["a"].environment).endswith("/environments/openMPIUbuntu/versions/1")
        job = assert_job_cancel(pipeline_job, client)
        assert job.name == params_override[0]["name"]
        assert str(job.jobs["a"].component).startswith("azureml://registries/")
        assert str(job.jobs["a"].component).endswith("/components/hello_world_asset/versions/1")

    @pytest.mark.skip("Skipping due to Spark version Upgrade")
    @pytest.mark.parametrize(
        "pipeline_job_path",
        [
            "tests/test_configs/dsl_pipeline/spark_job_in_pipeline/wordcount_pipeline.yml",
            "tests/test_configs/dsl_pipeline/spark_job_in_pipeline/sample_pipeline.yml",
            "tests/test_configs/dsl_pipeline/spark_job_in_pipeline/pipeline.yml",
            "tests/test_configs/dsl_pipeline/spark_job_in_pipeline/pipeline_inline_job.yml",
            "tests/test_configs/pipeline_jobs/shakespear_sample/pipeline.yml",
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
        ],
    )
    def test_pipeline_job_with_command_job(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        test_case_i,
        test_case_name,
        pipeline_samples_e2e_registered_train_components,  # Test depends on this being in the workspace
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
                            "environment_variables": {"FOO": "bar"},
                            "name": "hello_world_inline_commandjob_1",
                            "computeId": "cpu-cluster",
                            "inputs": {
                                "test1": {
                                    "mode": "ReadOnlyMount",
                                    "uri": "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv",
                                    "job_input_type": "uri_file",
                                },
                                "literal_input": {"job_input_type": "literal", "value": "2"},
                            },
                            "_source": "YAML.JOB",
                        },
                        "hello_world_inline_commandjob_2": {
                            "type": "command",
                            "name": "hello_world_inline_commandjob_2",
                            "_source": "YAML.JOB",
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
                    "services",
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
                            "name": "train_job",
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
                            "name": "score_job",
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
                            "_source": "YAML.JOB",
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
                    "services",
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

    @pytest.mark.parametrize(
        "pipeline_job_path",
        [
            "file_component_input_e2e.yml",
            "file_input_e2e.yml",
            "tabular_input_e2e.yml",
        ],
    )
    @pytest.mark.skip("Will renable when parallel e2e recording issue is fixed")
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

    @pytest.mark.parametrize(
        "pipeline_job_path",
        [
            "file_component_literal_input_e2e.yml",
        ],
    )
    @pytest.mark.skip("Will renable when parallel e2e recording issue is fixed")
    def test_pipeline_job_with_parallel_component_job_bind_to_literal_input(
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

    @pytest.mark.skip("Will renable when parallel e2e recording issue is fixed")
    def test_pipeline_job_with_parallel_job_with_input_bindings(self, client: MLClient, randstr: Callable[[str], str]):
        yaml_path = "tests/test_configs/pipeline_jobs/pipeline_job_with_parallel_job_with_input_bindings.yml"

        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source=yaml_path,
            params_override=params_override,
        )
        created_job = client.jobs.create_or_update(pipeline_job)
        assert created_job.jobs["hello_world"].resources.instance_count == "${{parent.inputs.instance_count}}"

    @pytest.mark.skip(
        reason="The task for fixing this is tracked by "
        "https://msdata.visualstudio.com/Vienna/_workitems/edit/2298433"
    )
    @pytest.mark.parametrize(
        "pipeline_job_path",
        [
            "file_literal_input_e2e.yml",
        ],
    )
    def test_pipeline_job_with_inline_parallel_job_bind_to_literal_input(
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

    @pytest.mark.skip("Will renable when parallel e2e recording issue is fixed")
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
    @pytest.mark.skipif(condition=not is_live(), reason="reuse test, target to verify service-side behavior")
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

    @pytest.mark.skip("TODO (2370129): Recording fails due to 'Cannot find pipeline run' error")
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

    @pytest.mark.skipif(condition=not is_live(), reason="registry test, may fail in playback mode")
    def test_pipeline_job_create_with_registry_model_as_input(self, client: MLClient, randstr: Callable[[str], str]):
        params_override = [{"name": randstr("name")}]
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/job_with_registry_model_as_input/pipeline.yml",
            params_override=params_override,
        )
        job = assert_job_cancel(pipeline_job, client)
        assert job.name == params_override[0]["name"]

    def test_pipeline_node_with_default_component(self, client: MLClient, randstr: Callable[[str], str]):
        params_override = [{"name": randstr("job_name")}]
        pipeline_job = load_job(
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_default_component.yml",
            params_override=params_override,
        )

        created_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert (
            created_pipeline_job.jobs["hello_world_component"].component
            == "microsoftsamples_command_component_basic@default"
        )

    @pytest.mark.skip("Skipping due to Spark version Upgrade")
    def test_register_output_yaml(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
    ):
        # only register pipeline output
        register_pipeline_output_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_register_pipeline_output_name_version.yaml"
        )
        pipeline = load_job(source=register_pipeline_output_path)
        pipeline_job = assert_job_cancel(pipeline, client)
        output = pipeline_job.outputs.component_out_path
        assert output.name == "pipeline_output"
        assert output.version == "1"

        # only register node output
        register_node_output_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_register_node_output_name_version.yaml"
        )
        pipeline = load_job(source=register_node_output_path)
        pipeline_job = assert_job_cancel(pipeline, client)
        output = pipeline_job.jobs["parallel_body"].outputs.component_out_path
        assert output.name == "node_output"
        assert output.version == "1"

        # register node output and pipeline output while the node output isn't binding to pipeline output
        register_both_output_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_register_pipeline_and_node_output.yaml"
        )
        pipeline = load_job(source=register_both_output_path)
        pipeline_job = assert_job_cancel(pipeline, client)

        pipeline_output = pipeline_job.outputs.pipeline_out_path
        assert pipeline_output.name == "pipeline_output"
        assert pipeline_output.version == "2"
        node_output = pipeline_job.jobs["parallel_body"].outputs.component_out_path
        assert node_output.name == "node_output"
        assert node_output.version == "1"

        # register node output and pipeline output while the node output is binding to pipeline output
        register_both_output_binding_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_register_pipeline_and_node_binding_output.yaml"
        )
        pipeline = load_job(source=register_both_output_binding_path)
        pipeline_job = assert_job_cancel(pipeline, client)

        pipeline_output = pipeline_job.outputs.pipeline_out_path
        assert pipeline_output.name == "pipeline_output"
        assert pipeline_output.version == "2"
        node_output = pipeline_job.jobs["parallel_body"].outputs.component_out_path
        assert node_output.name == "node_output"
        assert node_output.version == "1"

        # register spark node output
        register_spark_output_path = (
            "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/pipeline_inline_job_register_output.yml"
        )
        pipeline = load_job(source=register_spark_output_path)
        pipeline_job = assert_job_cancel(pipeline, client)

        node_output = pipeline_job.jobs["count_by_row"].outputs.output
        assert node_output.name == "spark_output"
        assert node_output.version == "12"

        # register sweep node output
        register_sweep_output_path = (
            "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_sweep_node_register_output.yml"
        )
        pipeline = load_job(source=register_sweep_output_path, params_override=[{"name": randstr("job_name")}])
        pipeline_job = assert_job_cancel(pipeline, client)

        node_output = pipeline_job.jobs["hello_sweep_inline_file_trial"].outputs.trained_model_dir
        assert node_output.name == "sweep_output"
        assert node_output.version == "123_sweep"

        # register parallel node output
        register_parallel_output_path = (
            "./tests/test_configs/dsl_pipeline/parallel_component_with_file_input/pipeline_register_output.yml"
        )
        pipeline = load_job(source=register_parallel_output_path)
        pipeline_job = assert_job_cancel(pipeline, client)

        node_output = pipeline_job.jobs["convert_data_node"].outputs.file_output_data
        assert node_output.name == "convert_data_node_output"
        assert node_output.version == "1"

    def test_pipeline_job_with_data_transfer_copy_urifolder(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/copy_files.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["copy_files"], fields_to_omit)

        assert actual_dict == {
            "_source": "YAML.COMPONENT",
            "data_copy_mode": "merge_with_overwrite",
            "inputs": {"folder1": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"}},
            "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
            "task": "copy_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_data_transfer_copy_urifile(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/copy_uri_files.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["copy_files"], fields_to_omit)

        assert actual_dict == {
            "_source": "YAML.COMPONENT",
            "data_copy_mode": "fail_if_conflict",
            "inputs": {"folder1": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"}},
            "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
            "task": "copy_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_data_transfer_copy_2urifolder(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/merge_files.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["merge_files"], fields_to_omit)

        assert actual_dict == {
            "_source": "YAML.COMPONENT",
            "data_copy_mode": "merge_with_overwrite",
            "inputs": {
                "folder1": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"},
                "folder2": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder_dup}}"},
            },
            "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
            "task": "copy_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_inline_data_transfer_copy_2urifolder(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/merge_files_job.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["merge_files_job"], fields_to_omit)

        assert actual_dict == {
            "_source": "YAML.JOB",
            "data_copy_mode": "merge_with_overwrite",
            "inputs": {
                "folder1": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"},
                "folder2": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder_dup}}"},
            },
            "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
            "task": "copy_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_inline_data_transfer_copy_mixtype_file(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/merge_mixtype_files.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["merge_files"], fields_to_omit)

        assert actual_dict == {
            "_source": "YAML.COMPONENT",
            "data_copy_mode": "merge_with_overwrite",
            "inputs": {
                "input1": {"job_input_type": "literal", "value": "${{parent.inputs.input1}}"},
                "input2": {"job_input_type": "literal", "value": "${{parent.inputs.input2}}"},
                "input3": {"job_input_type": "literal", "value": "${{parent.inputs.input3}}"},
            },
            "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
            "task": "copy_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_data_transfer_import_filesystem(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/import_file_system_to_blob.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["s3_blob"], fields_to_omit)

        # load from rest will get source from component, which will be REMOTE.REGISTRY since component now is
        # registry component
        assert actual_dict == {
            "_source": "BUILTIN",
            "outputs": {
                "sink": {
                    "job_output_type": "uri_folder",
                    "uri": "azureml://datastores/workspaceblobstore/paths/importjob/${{name}}/output_dir/s3//",
                }
            },
            "source": {
                "connection": "${{parent.inputs.connection_target}}",
                "path": "${{parent.inputs.path_source_s3}}",
                "type": "file_system",
            },
            "task": "import_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_data_transfer_import_filesystem_reference_component(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = (
            "./tests/test_configs/pipeline_jobs/data_transfer/" "import_file_system_to_blob_reference_component.yaml"
        )
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["s3_blob"], fields_to_omit)

        # load from rest will get source from component, which will be REMOTE.REGISTRY since component now is
        # registry component
        assert actual_dict == {
            "_source": "REMOTE.REGISTRY",
            "outputs": {
                "sink": {
                    "job_output_type": "uri_folder",
                    "uri": "azureml://datastores/workspaceblobstore/paths/importjob/${{name}}/output_dir/s3//",
                }
            },
            "source": {
                "connection": "${{parent.inputs.connection_target}}",
                "path": "${{parent.inputs.path_source_s3}}",
                "type": "file_system",
            },
            "task": "import_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_data_transfer_import_sql_database(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/import_sql_database_to_blob.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["snowflake_blob"], fields_to_omit)

        assert actual_dict == {
            "_source": "BUILTIN",
            "computeId": "serverless",
            "outputs": {"sink": {"job_output_type": "mltable"}},
            "source": {
                "connection": "azureml:my_azuresqldb_connection",
                "query": "${{parent.inputs.query_source_snowflake}}",
                "type": "database",
            },
            "task": "import_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_data_transfer_import_snowflake_database(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/import_database_to_blob.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["snowflake_blob"], fields_to_omit)

        assert actual_dict == {
            "_source": "BUILTIN",
            "computeId": "serverless",
            "outputs": {
                "sink": {
                    "job_output_type": "mltable",
                    "uri": "azureml://datastores/workspaceblobstore_sas/paths/importjob/${{name}}/output_dir/snowflake/",
                }
            },
            "source": {
                "connection": "azureml:my_snowflake_connection",
                "query": "${{parent.inputs.query_source_snowflake}}",
                "type": "database",
            },
            "task": "import_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_data_transfer_export_sql_database(self, client: MLClient, randstr: Callable[[str], str]):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/export_database_to_blob.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["blob_azuresql"], fields_to_omit)

        assert actual_dict == {
            "_source": "BUILTIN",
            "inputs": {"source": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"}},
            "sink": {
                "connection": "${{parent.inputs.connection_target_azuresql}}",
                "table_name": "${{parent.inputs.table_name}}",
                "type": "database",
            },
            "task": "export_data",
            "type": "data_transfer",
        }

    def test_pipeline_job_with_data_transfer_export_sql_database_reference_component(
        self, client: MLClient, randstr: Callable[[str], str]
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/export_database_to_blob_reference_component.yaml"
        pipeline: PipelineJob = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        created_pipeline = assert_job_cancel(pipeline, client)
        pipeline_dict = created_pipeline._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties", "componentId"]

        actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["blob_azuresql"], fields_to_omit)

        assert actual_dict == {
            "_source": "REMOTE.REGISTRY",
            "inputs": {"source": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"}},
            "sink": {
                "connection": "${{parent.inputs.connection_target_azuresql}}",
                "table_name": "${{parent.inputs.table_name}}",
                "type": "database",
            },
            "task": "export_data",
            "type": "data_transfer",
        }

    def test_register_output_yaml_succeed(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
    ):
        register_pipeline_path = (
            "./tests/test_configs/dsl_pipeline/pipeline_with_pipeline_component/pipeline_register_output.yml"
        )
        pipeline = load_job(source=register_pipeline_path)
        # overwrite version
        random_version = randstr("version")
        pipeline.outputs.pipeline_job_best_model.version = random_version
        pipeline.jobs["train_and_evaludate_model1"].outputs.trained_model.version = random_version
        pipeline.jobs["compare"].outputs.best_model.version = random_version
        pipeline.jobs["compare"].outputs.best_result.version = random_version
        pipeline.jobs["compare_2"].outputs.best_model.version = random_version
        pipeline.jobs["compare_2"].outputs.best_result.version = random_version

        pipeline_job = client.jobs.create_or_update(pipeline)
        client.jobs.stream(pipeline_job.name)

        def check_name_version_and_register_succeed(output, asset_name):
            assert output.name == asset_name
            assert output.version == random_version
            assert client.data.get(name=asset_name, version=random_version)

        check_name_version_and_register_succeed(pipeline_job.outputs.pipeline_job_best_model, "pipeline_output_a")
        check_name_version_and_register_succeed(
            pipeline_job.jobs["train_and_evaludate_model1"].outputs.trained_model, "model1_output"
        )
        check_name_version_and_register_succeed(pipeline_job.jobs["compare_2"].outputs.best_model, "best_model_2")
        check_name_version_and_register_succeed(pipeline_job.jobs["compare_2"].outputs.best_result, "best_result_2")

        # name and version are not rewritten, but the display content in page is the PipelineOutput
        assert pipeline_job.jobs["compare"].outputs.best_model.name == "best_model"
        assert pipeline_job.jobs["compare"].outputs.best_model.version == random_version

    @pytest.mark.skipif(condition=not is_live(), reason="Task 2177353: component version changes across tests.")
    @pytest.mark.parametrize(
        "test_path",
        [
            "command/pipeline_serverless_compute.yml",
            "command/node_serverless_compute.yml",
            "command/node_serverless_compute_no_default.yml",
            "sweep/pipeline_serverless_compute.yml",
            "sweep/node_serverless_compute.yml",
            "sweep/node_serverless_compute_no_default.yml",
            "pipeline/pipeline_serverless_compute.yml",
            "pipeline/node_serverless_compute.yml",
            "automl/pipeline_with_instance_type.yml",
            "automl/pipeline_without_instance_type.yml",
            "automl/pipeline_with_instance_type_no_default.yml",
            # "parallel/pipeline_serverless_compute.yml", TODO (2349832): azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33 uses deprecated Python
            "spark/pipeline_serverless_compute.yml",
            "spark/node_serverless_compute_no_default.yml",
        ],
    )
    def test_serverless_compute_in_pipeline(self, client: MLClient, test_path: str) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/serverless_compute/all_types/" + test_path
        pipeline_job = load_job(yaml_path)
        assert_job_cancel(pipeline_job, client)

    def test_pipeline_job_serverless_compute_with_job_tier(self, client: MLClient) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/serverless_compute/job_tier/pipeline_with_job_tier.yml"
        pipeline_job = load_job(yaml_path)
        created_pipeline_job = assert_job_cancel(pipeline_job, client)
        rest_obj = created_pipeline_job._to_rest_object()
        assert rest_obj.properties.jobs["spot_job_tier"]["queue_settings"] == {"job_tier": "Spot"}
        assert rest_obj.properties.jobs["standard_job_tier"]["queue_settings"] == {"job_tier": "Standard"}

    def test_pipeline_job_serverless_compute_sweep_in_pipeline_with_job_tier(self, client: MLClient) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/serverless_compute/job_tier/sweep_in_pipeline/pipeline.yml"
        pipeline_job = load_job(yaml_path)
        created_pipeline_job = assert_job_cancel(pipeline_job, client)
        rest_obj = created_pipeline_job._to_rest_object()
        assert rest_obj.properties.jobs["node"]["queue_settings"] == {"job_tier": "standard"}

    def test_pipeline_job_serverless_compute_automl_in_pipeline_with_job_tier(self, client: MLClient) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/serverless_compute/job_tier/automl_in_pipeline/pipeline.yml"
        pipeline_job = load_job(yaml_path)
        created_pipeline_job = assert_job_cancel(pipeline_job, client)
        rest_obj = created_pipeline_job._to_rest_object()
        assert rest_obj.properties.jobs["text_ner_node"]["queue_settings"] == {"job_tier": "spot"}

    @pytest.mark.disable_mock_code_hash
    def test_register_automl_output(self, client: MLClient, randstr: Callable[[str], str]):
        register_pipeline_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/automl_regression_with_command_node_register_output.yml"
        pipeline = load_job(source=register_pipeline_path, params_override=[{"name": randstr("name")}])
        pipeline_job = assert_job_cancel(pipeline, client)
        assert pipeline_job.jobs["regression_node"].outputs["best_model"].name == "regression_name"
        assert pipeline_job.jobs["regression_node"].outputs["best_model"].version == "1"

        # Current code won't copy NodeOutput to the binding PipelineOutput for yaml defined job.
        # To register a binding NodeOutput, define name and version in pipeline level is more expected.
        assert pipeline_job.outputs.regression_node_2.name == None
        assert pipeline_job.outputs.regression_node_2.version == None

    def test_pipeline_job_singularity_no_compute_in_yaml(self, client: MLClient, mock_singularity_arm_id: str) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/singularity/pipeline_job_no_compute.yml"
        pipeline_job = load_job(yaml_path)
        pipeline_job.settings.default_compute = mock_singularity_arm_id

        created_pipeline_job = assert_job_cancel(pipeline_job, client)
        rest_obj = created_pipeline_job._to_rest_object()
        assert rest_obj.properties.settings["default_compute"] == mock_singularity_arm_id
        assert rest_obj.properties.jobs["low_node"]["resources"] == {
            "instance_type": "Singularity.ND40rs_v2",
            "properties": {
                "AISuperComputer": {
                    "imageVersion": "",
                    "slaTier": "Basic",
                    "priority": "Low",
                }
            },
        }
        assert rest_obj.properties.jobs["medium_node"]["resources"] == {
            "instance_type": "Singularity.ND40rs_v2",
            "properties": {
                "AISuperComputer": {
                    "imageVersion": "",
                    "slaTier": "Standard",
                    "priority": "Medium",
                }
            },
        }
        assert rest_obj.properties.jobs["high_node"]["resources"] == {
            "instance_type": "Singularity.ND40rs_v2",
            "properties": {
                "AISuperComputer": {
                    "imageVersion": "",
                    "slaTier": "Premium",
                    "priority": "High",
                }
            },
        }

    @pytest.mark.skip(reason="Need to create SingularityTestVC cluster.")
    def test_pipeline_job_singularity_short_name(self, client: MLClient) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/singularity/pipeline_job_short_name.yml"
        pipeline_job = load_job(yaml_path)
        created_pipeline_job = assert_job_cancel(pipeline_job, client)
        rest_obj = created_pipeline_job._to_rest_object()
        default_compute = rest_obj.properties.settings["default_compute"]
        assert is_singularity_id_for_resource(default_compute)
        assert default_compute.endswith("SingularityTestVC")
        node_compute = rest_obj.properties.jobs["hello_world"]["computeId"]
        assert is_singularity_id_for_resource(node_compute)
        assert node_compute.endswith("centeuapvc")

    @pytest.mark.skipif(condition=not is_live(), reason="recording will expose Singularity information")
    def test_pipeline_job_singularity_live(self, client: MLClient, tmp_path: Path, singularity_vc):
        full_name = "azureml://subscriptions/{}/resourceGroups/{}/virtualclusters/{}".format(
            singularity_vc.subscription_id, singularity_vc.resource_group_name, singularity_vc.name
        )
        short_name = f"azureml://virtualclusters/{singularity_vc.name}"

        pipeline_yaml_template = """
$schema: https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json
type: pipeline
display_name: full name & short name
experiment_name: Singularity in pipeline
jobs:
  full_name:
    command: echo full name
    environment:
      image: singularitybase.azurecr.io/base/job/deepspeed/0.4-pytorch-1.7.0-cuda11.0-cudnn8-devel:20221017T152225334
    compute: {{singularity-full-name}}
    resources:
      instance_type: Singularity.ND40rs_v2
  short_name:
    command: echo short name
    environment:
      image: singularitybase.azurecr.io/base/job/deepspeed/0.4-pytorch-1.7.0-cuda11.0-cudnn8-devel:20221017T152225334
    compute: {{singularity-short-name}}
    resources:
      instance_type: Singularity.ND40rs_v2
        """
        pipeline_yaml_content = pipeline_yaml_template.replace("{{singularity-full-name}}", full_name).replace(
            "{{singularity-short-name}}", short_name
        )
        pipeline_yaml_path = tmp_path / "pipeline.yml"
        pipeline_yaml_path.write_text(pipeline_yaml_content)
        pipeline_job = load_job(pipeline_yaml_path)
        created_pipeline_job = assert_job_cancel(pipeline_job, client)
        rest_obj = created_pipeline_job._to_rest_object()

        assert is_singularity_id_for_resource(rest_obj.properties.jobs["full_name"]["computeId"])
        assert rest_obj.properties.jobs["full_name"]["computeId"].endswith(singularity_vc.name)
        assert is_singularity_id_for_resource(rest_obj.properties.jobs["short_name"]["computeId"])
        assert rest_obj.properties.jobs["short_name"]["computeId"].endswith(singularity_vc.name)

    def test_pipeline_with_param_group_in_command_component(
        self,
        client,
        randstr: Callable[[str], str],
    ):
        pipeline_job = load_job("./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_group_input_for_node.yml")
        created_pipeline_job = assert_job_cancel(pipeline_job, client)
        assert created_pipeline_job.jobs["dot_input_name"]._to_dict()["inputs"] == {
            "component_in_group.number": "10.99",
            "component_in_group.sub1.integer": "10",
            "component_in_group.sub1.number": "10.99",
            "component_in_group.sub2.number": "10.99",
            "component_in_path": {"path": "${{parent.inputs.job_in_path}}"},
        }

    def test_flow_node_skip_input_filtering(self, client: MLClient, randstr: Callable[[str], str]):
        flow_dag_path = "./tests/test_configs/flows/web_classification_with_additional_includes/flow.dag.yaml"
        anonymous_component = load_component(flow_dag_path)
        created_component = client.components.create_or_update(
            load_component(flow_dag_path, params_override=[{"name": randstr("component_name")}])
        )

        from azure.ai.ml.dsl._group_decorator import group

        @group
        class Connection:
            connection: str
            deployment_name: str

        init_args = {
            "inputs": {
                "data": Input(
                    type=AssetTypes.URI_FOLDER, path="./tests/test_configs/flows/data/web_classification.jsonl"
                ),
                "url": "${data.url}",
                "connections": {
                    "summarize_text_content": {
                        "connection": "azure_open_ai_connection",
                        "deployment_name": "text-davinci-003",
                    },
                    "classify_with_llm": Connection(
                        connection="azure_open_ai_connection",
                        deployment_name="llm-davinci-003",
                    ),
                },
            },
        }
        node_registered = Parallel(component=created_component, **init_args)
        node_anonymous = Parallel(component=anonymous_component, **init_args)

        registered_inputs = node_registered._to_rest_object()["inputs"]
        assert registered_inputs == {
            "connections.classify_with_llm.connection": {
                "job_input_type": "literal",
                "value": "azure_open_ai_connection",
            },
            "connections.classify_with_llm.deployment_name": {"job_input_type": "literal", "value": "llm-davinci-003"},
            "connections.summarize_text_content.connection": {
                "job_input_type": "literal",
                "value": "azure_open_ai_connection",
            },
            "connections.summarize_text_content.deployment_name": {
                "job_input_type": "literal",
                "value": "text-davinci-003",
            },
            "data": {"job_input_type": "uri_folder", "uri": "./tests/test_configs/flows/data/web_classification.jsonl"},
            "url": {"job_input_type": "literal", "value": "${data.url}"},
        }

        assert node_anonymous._to_rest_object()["inputs"] == registered_inputs

    @pytest.mark.parametrize(
        "test_path,expected_node_dict",
        [
            pytest.param(
                "./tests/test_configs/pipeline_jobs/pipeline_job_with_flow_from_dag.yml",
                {
                    "inputs": {
                        "connections.summarize_text_content.connection": "azure_open_ai_connection",
                        "connections.summarize_text_content.deployment_name": "text-davinci-003",
                        "data": {"path": "${{parent.inputs.data}}"},
                        "url": "${data.url}",
                    },
                    "outputs": {"flow_outputs": "${{parent.outputs.output_data}}"},
                    "type": "parallel",
                },
                id="dag",
            ),
            pytest.param(
                "./tests/test_configs/pipeline_jobs/pipeline_job_with_flow_from_run.yml",
                {
                    "inputs": {"data": {"path": "${{parent.inputs.data}}"}, "text": "${data.text}"},
                    "outputs": {"flow_outputs": "${{parent.outputs.output_data}}"},
                    "type": "parallel",
                },
                id="run",
            ),
        ],
    )
    def test_pipeline_job_with_flow(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        test_path: str,
        expected_node_dict: Dict[str, Any],
    ) -> None:
        # for some unclear reason, there will be unstable failure in playback mode when there are multiple
        # anonymous flow components in the same pipeline job. This is a workaround to avoid that.
        # the probable cause is that flow component creation request contains flow definition uri, which is
        # constructed based on response of code pending upload requests, and those requests have been normalized
        # in playback mode and mixed up.
        pipeline_job = load_job(source=test_path, params_override=[{"name": randstr("name")}])
        validation_result = client.jobs.validate(pipeline_job)
        assert validation_result.passed, validation_result

        created_pipeline_job = assert_job_cancel(pipeline_job, client)

        pipeline_job_dict = created_pipeline_job._to_dict()
        pipeline_job_dict["jobs"]["anonymous_node"].pop("component", None)

        assert pipeline_job_dict["jobs"]["anonymous_node"] == expected_node_dict


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.e2etest
@pytest.mark.pipeline_test
@pytest.mark.skipif(condition=not is_live(), reason="no need to run in playback mode")
@pytest.mark.timeout(timeout=_PIPELINE_JOB_LONG_RUNNING_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
class TestPipelineJobLongRunning:
    """Long-running tests that require pipeline job completed."""

    def test_pipeline_job_get_child_run(self, client: MLClient, randstr: Callable[[str], str]):
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_quick_with_output.yml",
            params_override=[{"name": randstr("name")}],
        )
        job = client.jobs.create_or_update(pipeline_job)
        print("pipeline job name:", job.name)
        wait_until_done(client, job)
        child_job = next(
            job
            for job in client.jobs.list(parent_job_name=job.name)
            if job.display_name == "hello_world_inline_commandjob_1"
        )
        retrieved_child_run = client.jobs.get(child_job.name)
        assert isinstance(retrieved_child_run, Job)
        assert retrieved_child_run.name == child_job.name

    def test_pipeline_job_download(self, client: MLClient, randstr: Callable[[str], str], tmp_path: Path) -> None:
        job = client.jobs.create_or_update(
            load_job(
                source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_quick_with_output.yml",
                params_override=[{"name": randstr("job_name")}],
            )
        )
        print("pipeline job name:", job.name)
        wait_until_done(client, job)
        client.jobs.download(name=job.name, download_path=tmp_path)
        artifact_dir = tmp_path / "artifacts"
        assert artifact_dir.exists()
        assert next(artifact_dir.iterdir(), None), "No artifacts were downloaded"

    def test_pipeline_job_child_run_download(
        self, client: MLClient, randstr: Callable[[str], str], tmp_path: Path
    ) -> None:
        job = client.jobs.create_or_update(
            load_job(
                source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_quick_with_output.yml",
                params_override=[{"name": randstr("job_name")}],
            )
        )
        print("pipeline job name:", job.name)
        wait_until_done(client, job)
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

    def test_reused_pipeline_child_job_download(
        self,
        client: MLClient,
        randstr: Callable[[str], str],
        tmp_path: Path,
    ) -> None:
        pipeline_spec_path = "./tests/test_configs/pipeline_jobs/reuse_child_job_download/pipeline.yml"

        # ensure previous job exists for reuse
        job_name = randstr("job_name")
        print("previous job name:", job_name)
        previous_job = client.jobs.create_or_update(
            load_job(source=pipeline_spec_path, params_override=[{"name": job_name}])
        )
        wait_until_done(client, previous_job)

        # submit a new job that will reuse previous job
        new_job_name = randstr("new_job_name")
        print("new job name:", new_job_name)
        new_job = client.jobs.create_or_update(
            load_job(pipeline_spec_path, params_override=[{"name": new_job_name}]),
        )
        wait_until_done(client, new_job)

        # ensure reuse behavior, get child job and check
        child_jobs = [
            job
            for job in client.jobs.list(parent_job_name=new_job_name)
            if job.display_name == "hello_world_component_inline"
        ]
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
