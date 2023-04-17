# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,too-many-instance-attributes

from typing import List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    AutoForecastHorizon,
    AutoSeasonality,
    AutoTargetLags,
    AutoTargetRollingWindowSize,
    CustomForecastHorizon,
    CustomSeasonality,
    CustomTargetLags,
    CustomTargetRollingWindowSize,
    ForecastHorizonMode,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import ForecastingSettings as RestForecastingSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    SeasonalityMode,
    TargetLagsMode,
    TargetRollingWindowSizeMode,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ForecastingSettings(RestTranslatableMixin):
    """Forecasting settings for an AutoML Job.

    :param country_or_region_for_holidays: The country/region used to generate holiday features. These should be ISO
        3166 two-letter country/region code, for example 'US' or 'GB'.
    :type country_or_region_for_holidays: str
    :param forecast_horizon: The desired maximum forecast horizon in units of time-series frequency.
    :type forecast_horizon: int
    :param target_lags: The number of past periods to lag from the target column. Use 'auto' to use the automatic
        heuristic based lag.
    :type target_lags: Union[str, int, List[int]]
    :param target_rolling_window_size: The number of past periods used to create a rolling window average of the
        target column.
    :type target_rolling_window_size: int
    :param frequency: Forecast frequency. When forecasting, this parameter represents the period with which the
        forecast is desired, for example daily, weekly, yearly, etc.
    :type frequency: str
    :param feature_lags: Flag for generating lags for the numeric features with 'auto'
    :type feature_lags: str
    :param seasonality: Set time series seasonality as an integer multiple of the series frequency. Use 'auto' for
        automatic settings.
    :type seasonality: Union[str, int]
    :param use_stl: Configure STL Decomposition of the time-series target column. use_stl can take two values:
        'season' - only generate season component and 'season_trend' - generate both season and trend components.
    :type use_stl: str
    :param short_series_handling_config: The parameter defining how if AutoML should handle short time series.
    :type short_series_handling_config: str
    :param target_aggregate_function: The function to be used to aggregate the time series target column to conform
        to a user specified frequency. If the target_aggregation_function is set, but the freq parameter is not set,
        the error is raised. The possible target aggregation functions are: "sum", "max", "min" and "mean".
    :type target_aggregate_function: str
    :param time_column_name: The name of the time column.
    :type time_column_name: str
    :param time_series_id_column_names:  The names of columns used to group a timeseries.
    :type time_series_id_column_names: Union[str, List[str]]
    """

    def __init__(
        self,
        *,
        country_or_region_for_holidays: Optional[str] = None,
        cv_step_size: Optional[int] = None,
        forecast_horizon: Optional[Union[str, int]] = None,
        target_lags: Optional[Union[str, int, List[int]]] = None,
        target_rolling_window_size: Optional[Union[str, int]] = None,
        frequency: Optional[str] = None,
        feature_lags: Optional[str] = None,
        seasonality: Optional[Union[str, int]] = None,
        use_stl: Optional[str] = None,
        short_series_handling_config: Optional[str] = None,
        target_aggregate_function: Optional[str] = None,
        time_column_name: Optional[str] = None,
        time_series_id_column_names: Optional[Union[str, List[str]]] = None,
    ):
        self.country_or_region_for_holidays = country_or_region_for_holidays
        self.cv_step_size = cv_step_size
        self.forecast_horizon = forecast_horizon
        self.target_lags = target_lags
        self.target_rolling_window_size = target_rolling_window_size
        self.frequency = frequency
        self.feature_lags = feature_lags
        self.seasonality = seasonality
        self.use_stl = use_stl
        self.short_series_handling_config = short_series_handling_config
        self.target_aggregate_function = target_aggregate_function
        self.time_column_name = time_column_name
        self.time_series_id_column_names = time_series_id_column_names

    def _to_rest_object(self) -> RestForecastingSettings:
        forecast_horizon = None
        if isinstance(self.forecast_horizon, str):
            forecast_horizon = AutoForecastHorizon()
        elif self.forecast_horizon:
            forecast_horizon = CustomForecastHorizon(value=self.forecast_horizon)

        target_lags = None
        if isinstance(self.target_lags, str):
            target_lags = AutoTargetLags()
        elif self.target_lags:
            lags = [self.target_lags] if not isinstance(self.target_lags, list) else self.target_lags
            target_lags = CustomTargetLags(values=lags)

        target_rolling_window_size = None
        if isinstance(self.target_rolling_window_size, str):
            target_rolling_window_size = AutoTargetRollingWindowSize()
        elif self.target_rolling_window_size:
            target_rolling_window_size = CustomTargetRollingWindowSize(value=self.target_rolling_window_size)

        seasonality = None
        if isinstance(self.seasonality, str):
            seasonality = AutoSeasonality()
        elif self.seasonality:
            seasonality = CustomSeasonality(value=self.seasonality)

        time_series_id_column_names = self.time_series_id_column_names
        if isinstance(self.time_series_id_column_names, str) and self.time_series_id_column_names:
            time_series_id_column_names = [self.time_series_id_column_names]

        return RestForecastingSettings(
            country_or_region_for_holidays=self.country_or_region_for_holidays,
            cv_step_size=self.cv_step_size,
            forecast_horizon=forecast_horizon,
            time_column_name=self.time_column_name,
            target_lags=target_lags,
            target_rolling_window_size=target_rolling_window_size,
            seasonality=seasonality,
            frequency=self.frequency,
            feature_lags=self.feature_lags,
            use_stl=self.use_stl,
            short_series_handling_config=self.short_series_handling_config,
            target_aggregate_function=self.target_aggregate_function,
            time_series_id_column_names=time_series_id_column_names,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestForecastingSettings) -> "ForecastingSettings":
        forecast_horizon = None
        if obj.forecast_horizon and obj.forecast_horizon.mode == ForecastHorizonMode.AUTO:
            forecast_horizon = obj.forecast_horizon.mode.lower()
        elif obj.forecast_horizon:
            forecast_horizon = obj.forecast_horizon.value

        rest_target_lags = obj.target_lags
        target_lags = None
        if rest_target_lags and rest_target_lags.mode == TargetLagsMode.AUTO:
            target_lags = rest_target_lags.mode.lower()
        elif rest_target_lags:
            target_lags = rest_target_lags.values

        target_rolling_window_size = None
        if obj.target_rolling_window_size and obj.target_rolling_window_size.mode == TargetRollingWindowSizeMode.AUTO:
            target_rolling_window_size = obj.target_rolling_window_size.mode.lower()
        elif obj.target_rolling_window_size:
            target_rolling_window_size = obj.target_rolling_window_size.value

        seasonality = None
        if obj.seasonality and obj.seasonality.mode == SeasonalityMode.AUTO:
            seasonality = obj.seasonality.mode.lower()
        elif obj.seasonality:
            seasonality = obj.seasonality.value

        return cls(
            country_or_region_for_holidays=obj.country_or_region_for_holidays,
            cv_step_size=obj.cv_step_size,
            forecast_horizon=forecast_horizon,
            target_lags=target_lags,
            target_rolling_window_size=target_rolling_window_size,
            frequency=obj.frequency,
            feature_lags=obj.feature_lags,
            seasonality=seasonality,
            use_stl=obj.use_stl,
            short_series_handling_config=obj.short_series_handling_config,
            target_aggregate_function=obj.target_aggregate_function,
            time_column_name=obj.time_column_name,
            time_series_id_column_names=obj.time_series_id_column_names,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ForecastingSettings):
            return NotImplemented
        return (
            self.country_or_region_for_holidays == other.country_or_region_for_holidays
            and self.cv_step_size == other.cv_step_size
            and self.forecast_horizon == other.forecast_horizon
            and self.target_lags == other.target_lags
            and self.target_rolling_window_size == other.target_rolling_window_size
            and self.frequency == other.frequency
            and self.feature_lags == other.feature_lags
            and self.seasonality == other.seasonality
            and self.use_stl == other.use_stl
            and self.short_series_handling_config == other.short_series_handling_config
            and self.target_aggregate_function == other.target_aggregate_function
            and self.time_column_name == other.time_column_name
            and self.time_series_id_column_names == other.time_series_id_column_names
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
