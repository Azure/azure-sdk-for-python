# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Tuple

import pytest
from test_utilities.utils import assert_final_job_status, get_automl_job_properties

from azure.ai.ml import MLClient
from azure.ai.ml.automl import text_ner
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.nlp import TextNerJob
from azure.ai.ml.operations._run_history_constants import JobStatus

from devtools_testutils import AzureRecordedTestCase, is_live


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(
    condition=not is_live(),
    reason="Datasets downloaded by test are too large to record reliably"
)
class TestTextNer(AzureRecordedTestCase):
    def test_remote_run_text_ner(
        self,
        conll: Tuple[Input, Input],
        client: MLClient,
    ) -> None:
        training_data, validation_data = conll
        job = text_ner(
            training_data=training_data,
            validation_data=validation_data,
            compute="gpu-cluster",
            experiment_name="DPv2-text-ner",
            properties=get_automl_job_properties(),
        )
        job.set_limits(timeout_minutes=60, max_concurrent_trials=1)

        created_job = client.jobs.create_or_update(job)

        assert_final_job_status(created_job, client, TextNerJob, JobStatus.COMPLETED)
