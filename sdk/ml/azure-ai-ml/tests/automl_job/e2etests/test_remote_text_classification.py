from typing import Tuple

import pytest
from test_utilities.utils import assert_final_job_status, get_automl_job_properties

from azure.ai.ml import MLClient
from azure.ai.ml.automl import text_classification
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.nlp import TextClassificationJob
from azure.ai.ml.operations._run_history_constants import JobStatus


@pytest.mark.automle2etest
class TestTextClassification:
    def test_remote_run_text_classification(
        self,
        newsgroup: Tuple[Input, Input, str],
        client: MLClient,
    ) -> None:
        training_data, validation_data, target_column_name = newsgroup
        job = text_classification(
            training_data=training_data,
            validation_data=validation_data,
            target_column_name=target_column_name,
            compute="gpu-cluster",
            experiment_name="DPv2-text-classification",
            properties=get_automl_job_properties(),
        )
        job.set_limits(timeout_minutes=60, max_concurrent_trials=1)
        job.set_featurization(dataset_language="eng")

        created_job = client.jobs.create_or_update(job)

        assert_final_job_status(created_job, client, TextClassificationJob, JobStatus.COMPLETED)
