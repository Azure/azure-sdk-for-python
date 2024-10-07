from typing import Union

import pytest

from azure.ai.ml._restclient.v2024_01_01_preview.models import AutoNCrossValidations, CustomNCrossValidations, JobBase
from azure.ai.ml.automl import classification, forecasting, regression
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.automl.tabular.classification_job import ClassificationJob
from azure.ai.ml.entities._job.automl.tabular.forecasting_job import ForecastingJob
from azure.ai.ml.entities._job.automl.tabular.regression_job import RegressionJob


@pytest.mark.automl_test
@pytest.mark.unittest
class TestNCrossValidationSettings:
    JOBS = [classification, regression, forecasting]

    def get_job_rest_object(
        self,
        n_cross_validation: Union[str, int, None],
        automl_job: Union[classification, regression, forecasting],
        validation_data_size: float = None,
        from_rest_obj: bool = False,
    ) -> Union[JobBase, ClassificationJob, RegressionJob, ForecastingJob]:
        # Create an AutoML Job

        job = automl_job(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
            enable_model_explainability=True,
            n_cross_validations=n_cross_validation,
            validation_data_size=validation_data_size,
        )

        job.limits = {"timeout_minutes": 60, "max_trials": 100, "max_concurrent_trials": 4}

        if automl_job == forecasting:
            job.set_forecast_settings(
                time_column_name="time",
            )

        rest_obj = job._to_rest_object()

        if from_rest_obj:  # from rest obj
            rest_obj = AutoMLJob._from_rest_object(rest_obj)

        return rest_obj

    def test_auto_n_cv_to_rest(self):
        # Test with auto n cross validations (to_rest_object)
        rest_objs = [
            self.get_job_rest_object("auto", self.JOBS[0]),
            self.get_job_rest_object("auto", self.JOBS[1]),
            self.get_job_rest_object("auto", self.JOBS[2]),
        ]

        for obj in rest_objs:
            assert isinstance(
                obj.properties.task_details.n_cross_validations, AutoNCrossValidations
            ), "N cross validations not an object of AutoNCrossValidations in {} job".format(
                obj.properties.task_details.task_type
            )

    def test_auto_n_cv_from_rest(self):
        # Test with auto n cross validations (from_rest_object)
        rest_objs = [
            self.get_job_rest_object("auto", self.JOBS[0], from_rest_obj=True),
            self.get_job_rest_object("auto", self.JOBS[1], from_rest_obj=True),
            self.get_job_rest_object("auto", self.JOBS[2], from_rest_obj=True),
        ]

        for obj in rest_objs:
            assert obj.n_cross_validations == "auto", "N cross validations incorrectly deserializing in {} job".format(
                obj.task_type
            )

    def test_value_n_cv_to_rest(self):
        # Test with int value n cross validations (to_rest_obj)
        rest_objs = [
            self.get_job_rest_object(2, self.JOBS[0]),
            self.get_job_rest_object(2, self.JOBS[1]),
            self.get_job_rest_object(2, self.JOBS[2]),
        ]

        for obj in rest_objs:
            assert isinstance(
                obj.properties.task_details.n_cross_validations, CustomNCrossValidations
            ), "N cross validations not an object of CustomNCrossValidations in {} job".format(
                obj.properties.task_details.task_type
            )

    def test_value_n_cv_from_rest(self):
        # Test with auto n cross validations (from_rest_object)
        rest_objs = [
            self.get_job_rest_object(2, self.JOBS[0], from_rest_obj=True),
            self.get_job_rest_object(2, self.JOBS[1], from_rest_obj=True),
            self.get_job_rest_object(2, self.JOBS[2], from_rest_obj=True),
        ]

        for obj in rest_objs:
            assert obj.n_cross_validations == 2, "N cross validations incorrectly deserializing in {} job".format(
                obj.task_type
            )

    def test_none_n_cv_to_rest(self):
        # Test with None value n cross validations
        rest_objs = [
            self.get_job_rest_object(None, self.JOBS[0]),
            self.get_job_rest_object(None, self.JOBS[1]),
            self.get_job_rest_object(None, self.JOBS[2]),
        ]

        for obj in rest_objs:
            assert obj.properties.task_details.n_cross_validations is None, "N cross validations not None"

    def test_none_n_cv_from_rest(self):
        # Test with auto n cross validations (from_rest_object)
        rest_objs = [
            self.get_job_rest_object(None, self.JOBS[0], from_rest_obj=True),
            self.get_job_rest_object(None, self.JOBS[1], from_rest_obj=True),
            self.get_job_rest_object(None, self.JOBS[2], from_rest_obj=True),
        ]

        for obj in rest_objs:
            assert obj.n_cross_validations is None, "N cross validations not None in {} job".format(obj.task_type)

    def test_monte_carlo_cv(self):
        # Test with monte carlo cv
        rest_objs = [
            self.get_job_rest_object(10, self.JOBS[0], 0.2),
            self.get_job_rest_object(10, self.JOBS[1], 0.2),
            self.get_job_rest_object(10, self.JOBS[2], 0.2),
        ]

        for obj in rest_objs:
            assert isinstance(
                obj.properties.task_details.n_cross_validations, CustomNCrossValidations
            ), "N cross validations not an object of CustomNCrossValidations in {} job".format(
                obj.properties.task_details.task_type
            )
            assert (
                obj.properties.task_details.validation_data_size == 0.2
            ), "Validation data size not being assigned in {} job".format(obj.properties.task_details.task_type)
