# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import assert_final_job_status, get_automl_job_properties

from azure.ai.ml import MLClient
from azure.ai.ml.automl import ColumnTransformer, regression
from azure.ai.ml.entities import QueueSettings
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.tabular.regression_job import RegressionJob
from azure.ai.ml.operations._run_history_constants import JobStatus


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="Datasets downloaded by test are too large to record reliably")
class TestAutoMLRegression(AzureRecordedTestCase):
    def get_regression_task(
        self, dataset: Tuple[Input, str], experiment_name: str, add_validation: bool = False
    ) -> RegressionJob:
        # Get training data
        training_data, label_column_name = dataset

        regression_task = regression(
            training_data=training_data,
            target_column_name=label_column_name,
            primary_metric="R2Score",
            compute="automl-cpu-cluster",
            experiment_name=experiment_name,
            properties=get_automl_job_properties(),
        )

        if add_validation:
            regression_task.set_data(
                training_data=training_data, n_cross_validations=2, target_column_name=label_column_name
            )

        regression_task.set_limits(
            trial_timeout_minutes=10,
            timeout_minutes=600,
            max_trials=1,
            max_concurrent_trials=1,
            enable_early_termination=True,
        )

        regression_task.set_training(enable_stack_ensemble=False, enable_vote_ensemble=False)

        return regression_task

    def test_regression(
        self,
        machinedata_dataset: Tuple[Input, str],
        client: MLClient,
    ) -> None:
        # get regression task
        regression_task = self.get_regression_task(machinedata_dataset, "DPv2-regression")
        # Trigger job
        created_job = client.jobs.create_or_update(regression_task)
        # Assert completion
        assert_final_job_status(created_job, client, RegressionJob, JobStatus.COMPLETED)

    def test_regression_with_custom_featurization(
        self,
        machinedata_dataset: Tuple[Input, str],
        client: MLClient,
    ) -> None:
        # get regression task
        regression_task = self.get_regression_task(machinedata_dataset, "DPv2-regression-custom-featurization")

        # Set featurization
        # Drop columns, add mode, add transformer_params,add block_transformers
        transformer_params = {
            "imputer": [
                ColumnTransformer(fields=["MYCT"], parameters={"strategy": "mean"}),
            ],
        }
        regression_task.set_featurization(
            mode="custom",
            transformer_params=transformer_params,
            blocked_transformers=["WordEmbedding"],
        )

        # Trigger job
        created_job = client.jobs.create_or_update(regression_task)
        # Assert completion
        assert_final_job_status(created_job, client, RegressionJob, JobStatus.COMPLETED)

    def test_regression_fail_without_featurization(
        self,
        machinedata_dataset: Tuple[Input, str],
        client: MLClient,
    ) -> None:
        # get regression task
        regression_task = self.get_regression_task(machinedata_dataset, "DPv2-regression-fail-without-featurization")
        # Set featurization off
        regression_task.set_featurization(mode="off")
        # Trigger job
        created_job = client.jobs.create_or_update(regression_task)
        assert_final_job_status(created_job, client, RegressionJob, JobStatus.FAILED)

    def test_regression_with_training_settings_serverless(
        self,
        machinedata_dataset: Tuple[Input, str],
        client: MLClient,
    ) -> None:
        # get regression task with validation split
        regression_task = self.get_regression_task(
            machinedata_dataset, "DPv2-regression-training-settings", add_validation=True
        )
        regression_task.compute = None
        regression_task.queue_settings = QueueSettings(job_tier="standard")
        # Featurization set to auto by default
        # Set training
        blocked_models = ["ElasticNet", "XGBoostRegressor", "LightGBM"]
        regression_task.set_training(
            enable_model_explainability=True,
            enable_vote_ensemble=False,
            enable_stack_ensemble=False,
            blocked_training_algorithms=blocked_models,
        )
        # Trigger job
        created_job = client.jobs.create_or_update(regression_task)
        # Assert completion
        assert_final_job_status(created_job, client, RegressionJob, JobStatus.COMPLETED)
