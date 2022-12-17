import pytest

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND


@pytest.mark.timeout(_PIPELINE_JOB_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestControlFlowPipelineJobUT:
    pass


class TestParallelForPipelineJobUT(TestControlFlowPipelineJobUT):
    def test_dsl_parallel_for_pipeline_illegal_cases(self):
        # required field unprovided
        # body unsupported
        # items unsupported
        pass
