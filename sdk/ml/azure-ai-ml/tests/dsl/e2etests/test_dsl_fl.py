import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from .._util import _DSL_TIMEOUT_SECOND
from test_utilities.utils import _PYTEST_TIMEOUT_METHOD, assert_job_cancel, omit_with_wildcard, sleep_if_live

from typing import Callable

from azure.ai.ml import (
    MLClient,
)


@pytest.mark.timeout(timeout=_DSL_TIMEOUT_SECOND, method=_PYTEST_TIMEOUT_METHOD)
@pytest.mark.e2etest
@pytest.mark.core_sdk_test
class TestDSLPipeline(AzureRecordedTestCase):
    def test_fl_pipeline(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        pass
        '''Similarly to the unit test, we will need to audit the pipeline e2e tests to get a baseline understanding
        of what needs to be tested for decorators in a thourough e2e suite. In addition to that, some immediate
        FL-specific tests that come to mind are:
        
        - Behavior with silos across regions
        - Behavior with silos in air-gapped regions (if possible, I'm not sure if that's out perogative)
        - Behavior with 1 silo
        - Error behavior with 0 silos? (might just be a unit test case that shouldn't hit backend...)
        - Testing complex/optional scatter/gather options that effect backend behavior (if any exist).'''