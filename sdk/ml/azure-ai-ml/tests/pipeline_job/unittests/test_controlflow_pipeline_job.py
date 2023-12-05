import pytest
from marshmallow import ValidationError

from azure.ai.ml import load_job
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities._job.to_rest_functions import to_rest_job_object
from azure.ai.ml.exceptions import ValidationException

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND


@pytest.mark.timeout(_PIPELINE_JOB_TIMEOUT_SECOND)
@pytest.mark.usefixtures(
    "enable_pipeline_private_preview_features",
    "enable_private_preview_schema_features",
    "enable_private_preview_pipeline_node_types",
)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestControlFlowPipelineJobUT:
    pass


class TestIfElseUI(TestControlFlowPipelineJobUT):
    @pytest.mark.parametrize(
        "exception_cls, yaml_path, msg, location",
        [
            # None true & None false
            (
                ValidationError,
                "./tests/test_configs/pipeline_jobs/invalid/if_else/none_true_none_false.yml",
                "True block and false block cannot be empty at the same time.",
                "",
            ),
            # None true & empty false
            (
                ValidationError,
                "./tests/test_configs/pipeline_jobs/invalid/if_else/none_true_empty_false.yml",
                "True block and false block cannot be empty at the same time.",
                "",
            ),
            # true & false intersection
            (
                ValidationError,
                "./tests/test_configs/pipeline_jobs/invalid/if_else/true_false_intersection.yml",
                "True block and false block cannot contain same nodes:",
                "",
            ),
            # invalid binding
            (
                ValidationException,
                "./tests/test_configs/pipeline_jobs/invalid/if_else/invalid_binding.yml",
                "of dsl.condition has invalid binding expression",
                '"path": "jobs.conditionnode.true_block",',
            ),
        ],
    )
    def test_if_else_validate(self, exception_cls, yaml_path, msg, location):
        with pytest.raises(exception_cls) as e:
            job = load_job(yaml_path)
            job._validate(raise_error=True)

        assert msg in str(e.value)
        assert location in str(e.value)


class TestDoWhilePipelineJobUT(TestControlFlowPipelineJobUT):
    def test_do_while_true_pipeline_omit_condition(self):
        yaml_path = "./tests/test_configs/pipeline_jobs/control_flow/do_while/pipeline.yml"
        pipeline_job = load_job(yaml_path)
        rest_job_resource = to_rest_job_object(pipeline_job)
        assert "condition" in rest_job_resource.properties.jobs["do_while_job_with_pipeline_job"]
        assert "condition" not in rest_job_resource.properties.jobs["do_while_true_job_with_pipeline_job"]

    def test_do_while_pipeline_illegal_cases(self):
        yaml_path = "./tests/test_configs/pipeline_jobs/control_flow/do_while/invalid_pipeline.yml"
        expected_validation_result = [
            # bool type is illegal for field condition
            (
                "Not a valid string.; Not a valid string.",
                "jobs.invalid_condition.condition",
            ),
            (
                "Missing data for required field.",
                "jobs.empty_mapping.mapping",
            ),
            (
                "Must be greater than or equal to 1 and less than or equal to 1000.",
                "jobs.out_of_range_max_iteration_count.limits.max_iteration_count",
            ),
            (
                "Missing data for required field.",
                "jobs.empty_max_iteration_count.limits",
            ),
            (
                "Not a valid integer.",
                "jobs.invalid_max_iteration_count.limits.max_iteration_count",
            ),
        ]
        with pytest.raises(ValidationError) as e:
            load_job(yaml_path)
        error_message = str(e.value)
        # use count of "invalid_pipeline.yml#line" to get number of error messages
        assert error_message.count("invalid_pipeline.yml#line") == len(expected_validation_result)
        for msg, location in expected_validation_result:
            assert msg in error_message
            assert location in error_message


class TestParallelForPipelineJobUT(TestControlFlowPipelineJobUT):
    @pytest.mark.parametrize(
        "exception_cls, yaml_path, msg, location",
        [
            pytest.param(
                ValidationError,
                "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_invalid_value_type.yml",
                "Not a valid mapping type.",
                '"path": "jobs.parallelfor.items",',
                id="items_invalid_content_type",
            ),
            pytest.param(
                ValidationException,
                "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_empty.yml",
                "Items is an empty list/dict.",
                '"path": "jobs.parallelfor.items",',
                id="items_empty_dict_content",
            ),
            pytest.param(
                ValidationException,
                "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_meta_mismatch.yml",
                '"message": "Items should have same keys',
                '"path": "jobs.parallelfor.items"',
                id="items_meta_mismatch",
            ),
            pytest.param(
                ValidationException,
                "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_not_exist.yml",
                "got unmatched inputs with loop body component",
                '"path": "jobs.parallelfor.items"',
                id="items_not_exist",
            ),
            pytest.param(
                ValidationException,
                "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_invalid_json.yml",
                '"message": "Items is neither a valid JSON',
                '"path": "jobs.parallelfor.items"',
                id="items_invalid_json",
            ),
            pytest.param(
                ValidationError,
                "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_unprovided.yml",
                '"message": "Missing data for required field',
                "items_unprovided.yml#line 7",
                id="required_field_unprovided",
            ),
            pytest.param(
                ValidationException,
                "./tests/test_configs/pipeline_jobs/invalid/parallel_for/body_not_supported.yml",
                " got <class 'azure.ai.ml.entities._builders.parallel.Parallel'> instead.",
                "",
                id="body_not_supported",
            ),
        ],
    )
    def test_dsl_parallel_for_pipeline_illegal_cases(self, exception_cls, yaml_path, msg, location):
        with pytest.raises(exception_cls) as e:
            job = load_job(yaml_path)
            job._validate(raise_error=True)

        assert msg in str(e.value)
        assert location in str(e.value)
