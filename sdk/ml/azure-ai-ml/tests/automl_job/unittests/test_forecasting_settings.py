from typing import Any, List, Tuple

import pytest

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    AutoForecastHorizon,
    AutoSeasonality,
    AutoTargetLags,
    AutoTargetRollingWindowSize,
    CustomForecastHorizon,
    CustomSeasonality,
    CustomTargetLags,
    CustomTargetRollingWindowSize,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import ForecastingSettings as RestForecastingSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import ShortSeriesHandlingConfiguration
from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings


@pytest.mark.automl_test
@pytest.mark.unittest
class TestForecastingSettings:
    @pytest.mark.parametrize(
        "settings",
        [
            RestForecastingSettings(time_series_id_column_names=["xxx"]),
            RestForecastingSettings(time_series_id_column_names=[]),
            RestForecastingSettings(time_series_id_column_names=None),
        ],
    )
    def test_forecast_settings_from_object(self, settings: RestForecastingSettings):
        actual_obj = ForecastingSettings._from_rest_object(obj=settings)
        assert actual_obj.time_series_id_column_names == settings.time_series_id_column_names

    @pytest.mark.parametrize(
        "settings",
        [
            (ForecastingSettings(time_series_id_column_names=["xxx"]), ["xxx"]),
            (ForecastingSettings(time_series_id_column_names=[]), []),
            (ForecastingSettings(time_series_id_column_names=None), None),
            (ForecastingSettings(time_series_id_column_names="xxx"), ["xxx"]),
        ],
    )
    def test_forecast_settings_to_rest_object(self, settings: Tuple[ForecastingSettings, List[str]]):
        input_settings, expected = settings
        actual = input_settings._to_rest_object()
        assert actual.time_series_id_column_names == expected

    @pytest.mark.parametrize(
        "settings",
        [
            (RestForecastingSettings(forecast_horizon=CustomForecastHorizon(value=10)), 10),
            (RestForecastingSettings(forecast_horizon=AutoForecastHorizon()), "auto"),
            (RestForecastingSettings(forecast_horizon=None), None),
        ],
    )
    def test_forecast_horizon_from_rest(self, settings: Tuple[RestForecastingSettings, Any]):
        actual_obj = ForecastingSettings._from_rest_object(obj=settings[0])
        assert actual_obj.forecast_horizon == settings[1], "actual: {}, expected: {}".format(
            actual_obj.forecast_horizon, settings[1]
        )

    @pytest.mark.parametrize(
        "settings",
        [
            (ForecastingSettings(forecast_horizon=10), CustomForecastHorizon(value=10)),
            (ForecastingSettings(forecast_horizon="auto"), AutoForecastHorizon()),
            (ForecastingSettings(forecast_horizon=None), None),
        ],
    )
    def test_forecast_horizon_to_rest(self, settings: Tuple[ForecastingSettings, List[str]]):
        input_settings, expected = settings
        actual = input_settings._to_rest_object()
        assert actual.forecast_horizon == expected

    # test target_lags from rest
    @pytest.mark.parametrize(
        "settings",
        [
            (RestForecastingSettings(target_lags=CustomTargetLags(values=[10, 20])), [10, 20]),
            (RestForecastingSettings(target_lags=AutoTargetLags()), "auto"),
            (RestForecastingSettings(target_lags=None), None),
        ],
    )
    def test_target_lags_from_rest(self, settings: Tuple[RestForecastingSettings, Any]):
        actual_obj = ForecastingSettings._from_rest_object(obj=settings[0])
        assert actual_obj.target_lags == settings[1], "actual: {}, expected: {}".format(
            actual_obj.target_lags, settings[1]
        )

    @pytest.mark.parametrize(
        "settings",
        [
            (ForecastingSettings(target_lags=10), CustomTargetLags(values=[10])),
            (ForecastingSettings(target_lags=[10, 20, 30]), CustomTargetLags(values=[10, 20, 30])),
            (ForecastingSettings(target_lags="auto"), AutoTargetLags()),
        ],
    )
    def test_target_lags_to_rest(self, settings: Tuple[ForecastingSettings, List[int]]):
        input_settings, expected = settings
        actual = input_settings._to_rest_object()
        assert actual.target_lags == expected, "actual: {}, expected: {}".format(actual, expected)

    # test target_rolling_window_size from rest
    @pytest.mark.parametrize(
        "settings",
        [
            (RestForecastingSettings(target_rolling_window_size=CustomTargetRollingWindowSize(value=10)), 10),
            (RestForecastingSettings(target_rolling_window_size=AutoTargetRollingWindowSize()), "auto"),
            (RestForecastingSettings(target_rolling_window_size=None), None),
        ],
    )
    def test_target_rolling_window_size_from_rest(self, settings: Tuple[RestForecastingSettings, Any]):
        actual_obj = ForecastingSettings._from_rest_object(obj=settings[0])
        assert actual_obj.target_rolling_window_size == settings[1], "actual: {}, expected: {}".format(
            actual_obj.target_rolling_window_size, settings[1]
        )

    @pytest.mark.parametrize(
        "settings",
        [
            (ForecastingSettings(target_rolling_window_size=10), CustomTargetRollingWindowSize(value=10)),
            (ForecastingSettings(target_rolling_window_size="auto"), AutoTargetRollingWindowSize()),
        ],
    )
    def test_target_rolling_window_size_to_rest(self, settings: Tuple[ForecastingSettings, List[int]]):
        input_settings, expected = settings
        actual = input_settings._to_rest_object()
        assert actual.target_rolling_window_size == expected, "actual: {}, expected: {}".format(actual, expected)

    # test seasonality from rest
    @pytest.mark.parametrize(
        "settings",
        [
            (RestForecastingSettings(seasonality=CustomSeasonality(value=10)), 10),
            (RestForecastingSettings(seasonality=AutoSeasonality()), "auto"),
            (RestForecastingSettings(seasonality=None), None),
        ],
    )
    def test_seasonality_from_rest(self, settings: Tuple[RestForecastingSettings, Any]):
        actual_obj = ForecastingSettings._from_rest_object(obj=settings[0])
        assert actual_obj.seasonality == settings[1], "actual: {}, expected: {}".format(
            actual_obj.seasonality, settings[1]
        )

    @pytest.mark.parametrize(
        "settings",
        [
            (ForecastingSettings(seasonality=10), CustomSeasonality(value=10)),
            (ForecastingSettings(seasonality="auto"), AutoSeasonality()),
        ],
    )
    def test_seasonality_to_rest(self, settings: Tuple[ForecastingSettings, List[int]]):
        input_settings, expected = settings
        actual = input_settings._to_rest_object()
        assert actual.seasonality == expected, "actual: {}, expected: {}".format(actual, expected)

    def test_forecast_settings_equality(self):
        settings = ForecastingSettings(
            time_column_name="time",
            forecast_horizon=20,
            target_lags=[1, 2, 3],
            time_series_id_column_names=["tid1", "tid2", "tid2"],
            frequency="W-THU",
            target_rolling_window_size=4,
            short_series_handling_config=ShortSeriesHandlingConfiguration.DROP,
            use_stl="season",
            seasonality=3,
            features_unknown_at_forecast_time=["a"],
        )

        # serialize and deserialize again
        settings_rest = settings._to_rest_object()
        settings_rest_2 = ForecastingSettings._from_rest_object(obj=settings_rest)
        assert settings == settings_rest_2, "actual: {}, expected: {}".format(settings, settings_rest_2)
