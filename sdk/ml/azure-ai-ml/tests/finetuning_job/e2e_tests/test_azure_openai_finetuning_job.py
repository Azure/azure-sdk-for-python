# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.operations._run_history_constants import JobStatus
from typing import Optional, Dict
from azure.ai.ml.entities._job.finetuning.azure_openai_finetuning_job import AzureOpenAIFineTuningJob
from azure.ai.ml.entities._job.finetuning.azure_openai_hyperparameters import AzureOpenAIHyperparameters
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    FineTuningTaskType,
)
import uuid


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="Datasets downloaded by test are too large to record reliably")
class TestAzureOpenAIFineTuningJob(AzureRecordedTestCase):
    def test_azure_openai_finetuning_job(
        self, text_completion_dataset: Tuple[Input, Input], mlflow_model_gpt4: Input, client: MLClient
    ) -> None:
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]
        training_data, validation_data = text_completion_dataset
        azure_openai_finetuning_job = self._get_azure_openai_finetuning_job(
            # TODO: Once backend is ready, update the task type to CHAT_COMPLETION
            task=FineTuningTaskType.TEXT_COMPLETION,
            training_data=training_data,
            validation_data=validation_data,
            hyperparameters=AzureOpenAIHyperparameters(batch_size=1, learning_rate_multiplier=0.00002, n_epochs=1),
            model=mlflow_model_gpt4,
            display_name=f"gpt4-display-name-{short_guid}",
            name=f"gpt4-{short_guid}",
            experiment_name="gpt4-finetuning-experiment",
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
            outputs={"registered_model": Output(type="mlflow_model", name=f"gpt4-finetune-registered-{short_guid}")},
        )
        # Trigger job
        created_job = client.jobs.create_or_update(azure_openai_finetuning_job)

        # Assert created job
        assert created_job.id is not None
        assert created_job.name == f"gpt4-{short_guid}", f"Expected job name to be gpt4-{short_guid}"
        assert (
            created_job.display_name == f"gpt4-display-name-{short_guid}"
        ), f"Expected display name to be gpt4-display-name-{short_guid}"
        assert (
            created_job.experiment_name == "gpt4-finetuning-experiment"
        ), "Expected experiment name to be gpt4-finetuning-experiment"
        assert created_job.status == JobStatus.RUNNING
        # TODO: Need service side fixes - Assert completion - Need to check why ES SB handler is
        # not completing the run appropriately.
        # assert_final_job_status(created_job, client, ClassificationJob, JobStatus.COMPLETED)

    def _get_azure_openai_finetuning_job(
        self,
        *,
        model: Input,
        task: str,
        training_data: Input,
        validation_data: Optional[Input] = None,
        hyperparameters: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> AzureOpenAIFineTuningJob:
        azure_openai_finetuning_job = AzureOpenAIFineTuningJob(
            task=task,
            model=model,
            training_data=training_data,
            validation_data=validation_data,
            hyperparameters=hyperparameters,
            **kwargs,
        )
        return azure_openai_finetuning_job
