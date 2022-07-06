# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest

from azure.ai.ml.constants import AssetTypes
from azure.ai.ml._restclient.v2022_02_01_preview.models import (       
    MLTableJobInput,
    UserIdentity,
)
from azure.ai.ml.automl import (
    forecasting,
    ForecastingModels,
    ShortSeriesHandlingConfiguration,
    ForecastingPrimaryMetrics,
)
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.tabular import ForecastingJob


@pytest.mark.unittest
class TestAutoMLForecasting:
    def test_forecasting_task(self):
        # Create AutoML Forecasting Task
        identity = UserIdentity()
        forecasting_job = forecasting(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
            primary_metric=ForecastingPrimaryMetrics.NORMALIZED_MEAN_ABSOLUTE_ERROR,
            enable_model_explainability=True,
            validation_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/valid.csv"),
            # Job attributes
            compute="cluster-forecasting",
            name="forecasting_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            identity = identity,
        )  # type: ForecastingJob
        forecasting_job.set_limits(timeout_minutes=60, max_trials=100, max_concurrent_trials=4)
        forecasting_job.set_training(
            enable_onnx_compatible_models=True, blocked_training_algorithms=[ForecastingModels.AVERAGE]
        )
        forecasting_job.set_featurization(enable_dnn_featurization=True)
        forecasting_job.set_forecast_settings(
            time_column_name="time",
            forecast_horizon=20,
            target_lags=[1, 2, 3],
            time_series_id_column_names=["tid1", "tid2", "tid2"],
            frequency="W-THU",
            target_rolling_window_size=4,
            short_series_handling_config=ShortSeriesHandlingConfiguration.DROP,
            use_stl="season",
            seasonality=3,
        )

        # check if stack ensemble was disabled
        assert forecasting_job.training.enable_stack_ensemble is False, "enable_stack_ensemble should default to False"

        # serialize and deserialize again and compare
        rest_obj = forecasting_job._to_rest_object()  # serialize to rest object
        assert rest_obj.properties.identity == identity
        assert isinstance(
            rest_obj.properties.task_details.data_settings.training_data.data, MLTableJobInput
        ), "Training data is not MLTableJobInput"
        assert isinstance(
            rest_obj.properties.task_details.data_settings.validation_data.data, MLTableJobInput
        ), "Validation data is not MLTableJobInput"

        original_obj = ForecastingJob._from_rest_object(rest_obj)  # deserialize from rest object
        assert forecasting_job == original_obj, "Conversion to/from rest object failed"
        assert (
            original_obj.primary_metric == ForecastingPrimaryMetrics.NORMALIZED_MEAN_ABSOLUTE_ERROR
        ), "Primary metric is not set"
        assert original_obj.compute == "cluster-forecasting", "Compute not set correctly"
        assert original_obj.name == "forecasting_job", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        # check if the original job inputs were restored
        assert isinstance(original_obj._data.training_data.data, Input), "Training data is not Input"
        assert original_obj._data.training_data.data.type == AssetTypes.MLTABLE, "Training data type not set correctly"
        assert original_obj.identity == identity
        assert (
            original_obj._data.training_data.data.path == "https://foo/bar/train.csv"
        ), "Training data path not set correctly"
        assert isinstance(original_obj._data.validation_data.data, Input), "Validation data is not Input"
        assert original_obj._data.validation_data.data.type == AssetTypes.MLTABLE, "Test data type not set correctly"
        assert (
            original_obj._data.validation_data.data.path == "https://foo/bar/valid.csv"
        ), "Test data path not set correctly"
