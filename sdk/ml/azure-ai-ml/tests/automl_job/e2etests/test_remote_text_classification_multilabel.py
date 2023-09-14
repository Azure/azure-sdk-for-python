# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Tuple

import pytest
import copy
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import assert_final_job_status, get_automl_job_properties

from azure.ai.ml import MLClient
from azure.ai.ml.automl import text_classification_multilabel
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.nlp import TextClassificationMultilabelJob
from azure.ai.ml.operations._run_history_constants import JobStatus


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="Datasets downloaded by test are too large to record reliably")
class TestTextClassificationMultilabel(AzureRecordedTestCase):
    @pytest.mark.parametrize("components", [(False), (True)])
    def test_remote_run_text_classification_multilabel(
        self, paper_categorization: Tuple[Input, Input, str], client: MLClient, components: bool
    ) -> None:
        training_data, validation_data, target_column_name = paper_categorization

        job = text_classification_multilabel(
            training_data=training_data,
            validation_data=validation_data,
            target_column_name=target_column_name,
            compute="gpu-cluster",
            experiment_name="DPv2-text-classification-multilabel",
            properties=get_automl_job_properties(),
        )

        # use component specific model name so that the test fails if components are not run
        if components:
            job.set_training_parameters(model_name="microsoft/deberta-base")
            job_reuse = copy.deepcopy(job)

        job.set_limits(timeout_minutes=60, max_concurrent_trials=1)

        created_job = client.jobs.create_or_update(job)
        if components:
            created_job_reuse = client.jobs.create_or_update(job_reuse)
            assert_final_job_status(created_job_reuse, client, TextClassificationMultilabelJob, JobStatus.COMPLETED)

        assert_final_job_status(created_job, client, TextClassificationMultilabelJob, JobStatus.COMPLETED)
