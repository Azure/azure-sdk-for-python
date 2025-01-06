# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from test_common_functions import validate_job


@pytest.mark.finetuning_job_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
class TestCustomModelFineTuningJob(AzureRecordedTestCase):

    @pytest.mark.e2etest
    def test_custom_model_finetuning_job(
        self,
        finetuning_job_with_name_updated,
        client: MLClient,
    ) -> None:

        # Trigger job
        created_job = client.jobs.create_or_update(finetuning_job_with_name_updated)
        returned_job = client.jobs.get(created_job.name)

        validate_job(
            input_job=finetuning_job_with_name_updated,
            created_job=created_job,
            returned_job=returned_job,
        )
