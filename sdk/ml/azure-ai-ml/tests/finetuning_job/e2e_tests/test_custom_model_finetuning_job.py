# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.operations._run_history_constants import JobStatus
from azure.ai.ml.entities._inputs_outputs import Input
from typing import Optional, Dict
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import CustomModelFineTuningJob
import pytest
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    FineTuningTaskType,
)
import uuid


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
# @pytest.mark.skipif(condition=not is_live(), reason="Datasets downloaded by test are too large to record reliably")
class TestCustomModelFineTuningJob(AzureRecordedTestCase):

    def test_custom_model_finetuning_job(
        self, text_completion_dataset: Tuple[Input, Input], mlflow_model_llama: Input, client: MLClient
    ) -> None:
        # get classification task
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]
        training_data, validation_data = text_completion_dataset
        classification_task = self._get_custom_model_finetuning_job(
            task=FineTuningTaskType.TEXT_COMPLETION,
            training_data=training_data,
            validation_data=validation_data,
            # hyperparameters={"foo": "bar"},
            model=mlflow_model_llama,
            name=f"llama-{short_guid}",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
        )
        # Trigger job
        created_job = client.jobs.create_or_update(classification_task)
        assert created_job.id is not None
        assert created_job.name is not None
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
