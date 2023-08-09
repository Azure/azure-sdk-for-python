# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import assert_final_job_status, get_automl_job_properties

from azure.ai.ml import MLClient
from azure.ai.ml.automl import ForecastingSettings, forecasting
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.tabular.forecasting_job import ForecastingJob
from azure.ai.ml.operations._run_history_constants import JobStatus


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="Datasets downloaded by test are too large to record reliably")
class TestAutoMLForecasting(AzureRecordedTestCase):
    def get_forecasting_task(
        self,
        dataset: Tuple[Input, ForecastingSettings, str],
        experiment_name: str,
        add_validation: bool = False,
    ) -> ForecastingJob:
        # Get training data
        training_data, forecasting_settings, label_column_name = dataset

        forecasting_task = forecasting(
            training_data=training_data,
            target_column_name=label_column_name,
            forecasting_settings=forecasting_settings,
            primary_metric="NormalizedRootMeanSquaredError",
            compute="automl-cpu-cluster",
            experiment_name=experiment_name,
            properties=get_automl_job_properties(),
        )

        if add_validation:
            forecasting_task.set_data(
                training_data=training_data, n_cross_validations=2, target_column_name=label_column_name
            )

        forecasting_task.set_limits(
            trial_timeout_minutes=10,
            timeout_minutes=600,
            max_trials=3,
            max_concurrent_trials=2,
            enable_early_termination=True,
        )

        forecasting_task.set_training(enable_stack_ensemble=False, enable_vote_ensemble=False)

        return forecasting_task

    def test_forecasting(
        self,
        beer_forecasting_dataset: Tuple[Input, ForecastingSettings, str],
        client: MLClient,
    ) -> None:
        # get forecasting task
        forecasting_task = self.get_forecasting_task(beer_forecasting_dataset, "DPv2-forecasting", add_validation=True)
        # Trigger job
        created_job = client.jobs.create_or_update(forecasting_task)
        # Assert completion
        assert_final_job_status(created_job, client, ForecastingJob, JobStatus.COMPLETED)

    def test_forecasting_with_training_settings(
        self,
        beer_forecasting_dataset: Tuple[Input, ForecastingSettings, str],
        client: MLClient,
    ) -> None:
        # get forecasting task with validation split
        forecasting_task = self.get_forecasting_task(
            beer_forecasting_dataset, "DPv2-forecasting-training-settings", add_validation=True
        )
        # Featurization set to auto by default
        # Set training
        forecasting_task.set_training(
            enable_model_explainability=True, enable_vote_ensemble=False, enable_stack_ensemble=False
        )
        # Trigger job
        created_job = client.jobs.create_or_update(forecasting_task)
        # Assert completion
        assert_final_job_status(created_job, client, ForecastingJob, JobStatus.COMPLETED)
