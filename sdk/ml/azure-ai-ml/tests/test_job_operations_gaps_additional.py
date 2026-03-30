from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestJobOperationsGaps(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_download_named_outputs_and_batch_branches_live(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Calling download with a non-existent job name should raise ResourceNotFoundError."""
        job_name = f"e2etest_{randstr('job')}_for_download"
        with pytest.raises(ResourceNotFoundError):
            client.jobs.download(job_name, download_path="./", all=True)
