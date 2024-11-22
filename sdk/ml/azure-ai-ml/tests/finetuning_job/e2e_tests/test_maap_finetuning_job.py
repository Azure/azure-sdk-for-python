# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

import pytest
from azure.ai.ml.entities import CustomModelFineTuningJob
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.operations._run_history_constants import JobStatus


@pytest.mark.finetuning_job_test
# @pytest.mark.usefixtures("recorded_test")
# @pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
class TestCustomModelFineTuningJob_MaaP(AzureRecordedTestCase):

    def test_using_instance_types(
        self,
        finetuning_job_instance_types: CustomModelFineTuningJob,
        client: MLClient,
    ) -> None:

        # Act
        created_job = client.jobs.create_or_update(finetuning_job_instance_types)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_created_job(
            input_job=finetuning_job_instance_types,
            created_job=created_job,
            returned_job=returned_job,
        )

    def test_using_aml_compute(
        self,
        finetuning_job_amlcompute: CustomModelFineTuningJob,
        client: MLClient,
    ) -> None:
        # Act
        created_job = client.jobs.create_or_update(finetuning_job_amlcompute)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_created_job(
            input_job=finetuning_job_amlcompute,
            created_job=created_job,
            returned_job=returned_job,
        )

    def test_using_queue_settings(
        self,
        finetuning_job_queue_settings: CustomModelFineTuningJob,
        client: MLClient,
    ) -> None:

        # Act
        created_job = client.jobs.create_or_update(finetuning_job_queue_settings)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_created_job(
            input_job=finetuning_job_queue_settings,
            created_job=created_job,
            returned_job=returned_job,
        )


def validate_created_job(
    input_job: CustomModelFineTuningJob,
    created_job: CustomModelFineTuningJob,
    returned_job: CustomModelFineTuningJob,
    compute: Optional[str] = None,
) -> None:
    assert input_job is not None
    assert returned_job is not None
    assert created_job.id is not None
    assert created_job.name == input_job.name, f"Expected job name to be {created_job.name}"
    assert (
        input_job.display_name == created_job.display_name == returned_job.display_name
    ), f"Expected display name to be {input_job.display_name}"
    assert (
        input_job.experiment_name == created_job.experiment_name == returned_job.experiment_name
    ), "Expected experiment name to be {input_job.experiment_name}"
    assert created_job.status == JobStatus.RUNNING

    if input_job.resources:
        assert (
            input_job.resources.instance_types
            == created_job.resources.instance_types
            == returned_job.resources.instance_types
        )

    if input_job.queue_settings:
        assert (
            input_job.queue_settings.job_tier.lower()
            == created_job.queue_settings.job_tier.lower()
            == returned_job.queue_settings.job_tier.lower()
        )

    if compute:
        assert input_job.compute == created_job.compute == returned_job.compute
