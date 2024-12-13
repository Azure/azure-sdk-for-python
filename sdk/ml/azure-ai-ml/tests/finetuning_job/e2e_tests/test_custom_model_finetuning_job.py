# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
from typing import Dict, Optional, Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml._restclient.v2024_01_01_preview.models import FineTuningTaskType
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import CustomModelFineTuningJob
from azure.ai.ml.operations._run_history_constants import JobStatus


@pytest.mark.finetuning_job_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
class TestCustomModelFineTuningJob(AzureRecordedTestCase):
    def test_custom_model_finetuning_job(
        self, text_completion_dataset: Tuple[Input, Input], mlflow_model_llama: Input, client: MLClient
    ) -> None:
        # get classification task
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]
        training_data, validation_data = text_completion_dataset
        custom_model_finetuning_job = self._get_custom_model_finetuning_job(
            task=FineTuningTaskType.TEXT_COMPLETION,
            training_data=training_data,
            validation_data=validation_data,
            hyperparameters={
                "per_device_train_batch_size": "1",
                "learning_rate": "0.00002",
                "num_train_epochs": "1",
            },
            model=mlflow_model_llama,
            display_name=f"llama-display-name-{short_guid}",
            name=f"llama-{short_guid}",
            experiment_name="llama-finetuning-experiment",
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
            outputs={"registered_model": Output(type="mlflow_model", name=f"llama-finetune-registered-{short_guid}")},
        )
        # Trigger job
        created_job = client.jobs.create_or_update(custom_model_finetuning_job)
        returned_job = client.jobs.get(created_job.name)
        assert returned_job is not None
        # Assert created job
        assert created_job.id is not None
        assert created_job.name == f"llama-{short_guid}", f"Expected job name to be llama-{short_guid}"
        assert (
            created_job.display_name == f"llama-display-name-{short_guid}"
        ), f"Expected display name to be llama-display-name-{short_guid}"
        assert (
            created_job.experiment_name == "llama-finetuning-experiment"
        ), "Expected experiment name to be llama-finetuning-experiment"
        assert created_job.status == JobStatus.RUNNING
        # TODO: Need service side fixes - Assert completion - Need to check why ES SB handler is
        # not completing the run appropriately.
        # assert_final_job_status(created_job, client, ClassificationJob, JobStatus.COMPLETED)

    def _get_custom_model_finetuning_job(
        self,
        *,
        model: Input,
        task: str,
        training_data: Input,
        validation_data: Optional[Input] = None,
        hyperparameters: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> CustomModelFineTuningJob:
        custom_model_finetuning_job = CustomModelFineTuningJob(
            task=task,
            model=model,
            training_data=training_data,
            validation_data=validation_data,
            hyperparameters=hyperparameters,
            **kwargs,
        )
        return custom_model_finetuning_job
