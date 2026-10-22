# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

import pytest
from azure.ai.ml.entities import CustomModelFineTuningJob
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from test_common_functions import validate_job


@pytest.mark.finetuning_job_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
class TestCustomModelFineTuningJob_MaaP(AzureRecordedTestCase):

    @pytest.mark.e2etest
    def test_using_instance_types(
        self,
        finetuning_job_instance_types: CustomModelFineTuningJob,
        client: MLClient,
    ) -> None:

        # Act
        created_job = client.jobs.create_or_update(finetuning_job_instance_types)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_job(
            input_job=finetuning_job_instance_types,
            created_job=created_job,
            returned_job=returned_job,
        )

    @pytest.mark.e2etest
    def test_using_aml_compute(
        self,
        finetuning_job_compute: CustomModelFineTuningJob,
        client: MLClient,
    ) -> None:
        # Act
        created_job = client.jobs.create_or_update(finetuning_job_compute)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_job(
            input_job=finetuning_job_compute,
            created_job=created_job,
            returned_job=returned_job,
        )

    @pytest.mark.e2etest
    def test_using_queue_settings(
        self,
        finetuning_job_queue_settings: CustomModelFineTuningJob,
        client: MLClient,
    ) -> None:

        # Act
        created_job = client.jobs.create_or_update(finetuning_job_queue_settings)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_job(
            input_job=finetuning_job_queue_settings,
            created_job=created_job,
            returned_job=returned_job,
        )
