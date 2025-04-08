# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Optional
import uuid

import pytest
from azure.ai.ml.entities import CustomModelFineTuningJob
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.ai.ml.entities._load_functions import load_job
from azure.ai.ml import MLClient
from test_common_functions import validate_job


@pytest.mark.finetuning_job_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
class TestFineTuningJob_MaaP_Yaml(AzureRecordedTestCase):

    @pytest.mark.e2etest
    def test_using_instance_types(
        self,
        finetuning_job_instance_types_yaml: Path,
        client: MLClient,
    ) -> None:

        # Arrange
        guid = uuid.uuid4()
        short_guid = str(guid)[:4]
        finetuning_job_instance_types = load_job(finetuning_job_instance_types_yaml)
        finetuning_job_instance_types.name = finetuning_job_instance_types.name + f"-{short_guid}"
        finetuning_job_instance_types.display_name = finetuning_job_instance_types.display_name + f"-{short_guid}"

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
        finetuning_job_compute_yaml: Path,
        client: MLClient,
    ) -> None:
        # Arrange
        guid = uuid.uuid4()
        short_guid = str(guid)[:4]
        finetuning_job_amlcompute = load_job(finetuning_job_compute_yaml)
        finetuning_job_amlcompute.name = finetuning_job_amlcompute.name + f"-{short_guid}"
        finetuning_job_amlcompute.display_name = finetuning_job_amlcompute.display_name + f"-{short_guid}"

        # Act
        created_job = client.jobs.create_or_update(finetuning_job_amlcompute)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_job(
            input_job=finetuning_job_amlcompute,
            created_job=created_job,
            returned_job=returned_job,
        )

    @pytest.mark.e2etest
    def test_using_queue_settings(
        self,
        finetuning_job_queue_settings_yaml: CustomModelFineTuningJob,
        client: MLClient,
    ) -> None:
        # Arrange
        guid = uuid.uuid4()
        short_guid = str(guid)[:4]
        finetuning_job_queue_settings = load_job(finetuning_job_queue_settings_yaml)
        finetuning_job_queue_settings.name = finetuning_job_queue_settings.name + f"-{short_guid}"
        finetuning_job_queue_settings.display_name = finetuning_job_queue_settings.display_name + f"-{short_guid}"

        # Act
        created_job = client.jobs.create_or_update(finetuning_job_queue_settings)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_job(
            input_job=finetuning_job_queue_settings,
            created_job=created_job,
            returned_job=returned_job,
        )
