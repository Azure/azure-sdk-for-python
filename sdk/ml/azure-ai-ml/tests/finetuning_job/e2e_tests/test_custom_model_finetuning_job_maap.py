# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

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
class TestCustomModelFineTuningJob(AzureRecordedTestCase):
    def test_custom_model_finetuning_job_maap(
        self,
        text_completion_train_data: str,
        text_completion_validation_data: str,
        mlflow_model_llama3_8B: str,
        output_model_name_prefix: str,
        client: MLClient,
    ) -> None:
        # get classification task
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]
        display_name = f"llama-3-8B-display-name-{short_guid}"
        name = f"llama-3-8B-{short_guid}"
        experiment_name = "llama-3-8B-finetuning-experiment"
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
            instance_types=["Standard_NC96ads_A100_v4", "Standard_E4s_v3"],
            display_name=display_name,
            name=name,
            experiment_name=experiment_name,
            tags={"foo_tag": "bar"},
            properties={"my_property": True},
            output_model_name_prefix=output_model_name_prefix,
        )
        # Trigger job
        created_job = client.jobs.create_or_update(custom_model_finetuning_job)
        returned_job = client.jobs.get(created_job.name)
        assert returned_job is not None
        # Assert created job
        assert created_job.id is not None
        assert created_job.name == name, f"Expected job name to be llama-{short_guid}"
        assert (
            created_job.display_name == display_name
        ), f"Expected display name to be llama-display-name-{short_guid}"
        assert (
            created_job.experiment_name == experiment_name
        ), "Expected experiment name to be llama-finetuning-experiment"
        assert created_job.status == JobStatus.RUNNING
        assert created_job.resources is not None
        assert created_job.resources.instance_types == [
            "Standard_NC96ads_A100_v4",
            "Standard_E4s_v3",
        ]
        # TODO: Need service side fixes - Assert completion - Need to check why ES SB handler is
        # not completing the run appropriately.
        # assert_final_job_status(created_job, client, ClassificationJob, JobStatus.COMPLETED)
