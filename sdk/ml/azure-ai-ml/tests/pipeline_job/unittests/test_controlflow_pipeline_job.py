import pytest
from marshmallow import ValidationError

from azure.ai.ml import load_job
from azure.ai.ml.exceptions import ValidationException
from .._util import _PIPELINE_JOB_TIMEOUT_SECOND


@pytest.mark.timeout(_PIPELINE_JOB_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestControlFlowPipelineJobUT:
    pass


class TestParallelForPipelineJobUT(TestControlFlowPipelineJobUT):

    @pytest.mark.parametrize(
        "exception_cls, yaml_path, msg, location",
        [
            # items with invalid content type
            # (
            #     ValidationError,
            #     "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_invalid_value_type.yml",
            #     'Not a valid mapping type.',
            #     '"path": "jobs.parallelfor.items",'
            # ),
            # # items with empty dict as content
            # (
            #     ValidationException,
            #     "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_empty.yml",
            #     "Items is an empty list/dict.",
            #     '"path": "jobs.parallelfor.items",'
            # ),
            # item meta not match
            (
                ValidationException,
                "./tests/test_configs/pipeline_jobs/invalid/parallel_for/items_meta_mismatch.yml",
                "xxx",
                "xxx"
            ),
            # required field unprovided
            # body unsupported
        ]
    )
    def test_dsl_parallel_for_pipeline_illegal_cases(self, exception_cls, yaml_path, msg, location):
        with pytest.raises(exception_cls) as e:
            job = load_job(yaml_path)
            job._validate(raise_error=True)

        assert msg in str(e.value)
        assert location in str(e.value)


