# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional
import uuid

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.finetuning import FineTuningTaskType
from azure.ai.ml.finetuning import create_finetuning_job
from azure.ai.ml.operations._run_history_constants import JobStatus


@pytest.mark.finetuning_job_test
# @pytest.mark.usefixtures("recorded_test")
# @pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
class TestCustomModelFineTuningJob_MaaP(AzureRecordedTestCase):

    def test_using_instance_types(
        self,
        text_completion_train_data: str,
        text_completion_validation_data: str,
        mlflow_model_llama3_8B: str,
        output_model_name_prefix: str,
        client: MLClient,
    ) -> None:
        # Arrange
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]
        display_name = f"llama-3-8B-display-name-{short_guid}"
        name = f"llama-3-8B-{short_guid}"
        experiment_name = "llama-3-8B-finetuning-experiment"
        instance_types = ["Standard_NC96ads_A100_v4", "Standard_E4s_v3"]

        custom_model_finetuning_job = create_finetuning_job(
            task=FineTuningTaskType.TEXT_COMPLETION,
            training_data=text_completion_train_data,
            validation_data=text_completion_validation_data,
            hyperparameters={
                "per_device_train_batch_size": "1",
                "learning_rate": "0.00002",
                "num_train_epochs": "1",
            },
            model=mlflow_model_llama3_8B,
            instance_types=instance_types,
            display_name=display_name,
            name=name,
            experiment_name=experiment_name,
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
            output_model_name_prefix=output_model_name_prefix,
        )

        # Act
        created_job = client.jobs.create_or_update(custom_model_finetuning_job)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_created_job(
            created_job,
            returned_job,
            name,
            display_name,
            experiment_name,
            short_guid,
            instance_types=instance_types,
        )

    def test_using_aml_compute(
        self,
        text_completion_train_data: str,
        text_completion_validation_data: str,
        mlflow_model_llama3_8B: str,
        output_model_name_prefix: str,
        client: MLClient,
    ) -> None:
        # Arrange
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]
        display_name = f"llama-3-8B-display-name-{short_guid}"
        name = f"llama-3-8B-{short_guid}"
        experiment_name = "llama-3-8B-finetuning-experiment"
        compute_name = "gpu-compute-low-pri"
        custom_model_finetuning_job = create_finetuning_job(
            task=FineTuningTaskType.TEXT_COMPLETION,
            training_data=text_completion_train_data,
            validation_data=text_completion_validation_data,
            hyperparameters={
                "per_device_train_batch_size": "1",
                "learning_rate": "0.00002",
                "num_train_epochs": "1",
            },
            model=mlflow_model_llama3_8B,
            compute=compute_name,
            display_name=display_name,
            name=name,
            experiment_name=experiment_name,
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
            output_model_name_prefix=output_model_name_prefix,
        )

        # Act
        created_job = client.jobs.create_or_update(custom_model_finetuning_job)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_created_job(
            created_job,
            returned_job,
            name,
            display_name,
            experiment_name,
            short_guid,
            compute=compute_name,
        )

    def test_using_queue_settings(
        self,
        text_completion_train_data: str,
        text_completion_validation_data: str,
        mlflow_model_llama3_8B: str,
        output_model_name_prefix: str,
        client: MLClient,
    ) -> None:
        # Arrange
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]
        display_name = f"llama-3-8B-display-name-{short_guid}"
        name = f"llama-3-8B-{short_guid}"
        experiment_name = "llama-3-8B-finetuning-experiment"
        compute_name = "gpu-compute-low-pri"
        job_tier = "Standard"

        custom_model_finetuning_job = create_finetuning_job(
            task=FineTuningTaskType.TEXT_COMPLETION,
            training_data=text_completion_train_data,
            validation_data=text_completion_validation_data,
            hyperparameters={
                "per_device_train_batch_size": "1",
                "learning_rate": "0.00002",
                "num_train_epochs": "1",
            },
            model=mlflow_model_llama3_8B,
            compute=compute_name,
            job_tier=job_tier,
            display_name=display_name,
            name=name,
            experiment_name=experiment_name,
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
            output_model_name_prefix=output_model_name_prefix,
        )

        # Act
        created_job = client.jobs.create_or_update(custom_model_finetuning_job)
        returned_job = client.jobs.get(created_job.name)

        # Assert
        validate_created_job(
            created_job,
            returned_job,
            name,
            display_name,
            experiment_name,
            short_guid,
            compute=compute_name,
            job_tier=job_tier,
        )


def validate_created_job(
    created_job,
    returned_job,
    name,
    display_name,
    experiment_name,
    short_guid,
    instance_types: Optional[List[str]] = None,
    job_tier: Optional[str] = None,
    priority: Optional[str] = None,
    compute: Optional[str] = None,
) -> None:
    assert returned_job is not None
    assert created_job.id is not None
    assert created_job.name == name, f"Expected job name to be llama-{short_guid}"
    assert (
        created_job.display_name == display_name
    ), f"Expected display name to be llama-display-name-{short_guid}"
    assert (
        created_job.experiment_name == experiment_name
    ), "Expected experiment name to be llama-finetuning-experiment"
    assert created_job.status == JobStatus.RUNNING

    if instance_types:
        assert created_job.resources is not None
        assert created_job.resources.instance_types == instance_types

    if job_tier:
        assert created_job.queue_settings is not None
        assert created_job.queue_settings.job_tier.lower() == job_tier.lower()

    if compute:
        assert created_job.compute == compute
