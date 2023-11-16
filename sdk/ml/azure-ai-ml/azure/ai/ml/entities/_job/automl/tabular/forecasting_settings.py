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
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ForecastingSettings as RestForecastingSettings,
)
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
    :type country_or_region_for_holidays: Optional[str]
    :param cv_step_size:
        Number of periods between the origin_time of one CV fold and the next fold. For
        example, if `n_step` = 3 for daily data, the origin time for each fold will be
        three days apart.
    :type cv_step_size: Optional[int]
    :param forecast_horizon:
        The desired maximum forecast horizon in units of time-series frequency. The default value is 1.

        Units are based on the time interval of your training data, e.g., monthly, weekly that the forecaster
        should predict out. When task type is forecasting, this parameter is required. For more information on
        setting forecasting parameters, see `Auto-train a time-series forecast model <https://docs.microsoft.com/
        azure/machine-learning/how-to-auto-train-forecast>`_.
    :type forecast_horizon: Optional[Union[int, str]]
    :param target_lags:
        The number of past periods to lag from the target column. By default the lags are turned off.

        When forecasting, this parameter represents the number of rows to lag the target values based
        on the frequency of the data. This is represented as a list or single integer. Lag should be used
        when the relationship between the independent variables and dependent variable do not match up or
        correlate by default. For example, when trying to forecast demand for a product, the demand in any
        month may depend on the price of specific commodities 3 months prior. In this example, you may want
        to lag the target (demand) negatively by 3 months so that the model is training on the correct
        relationship. For more information, see `Auto-train a time-series forecast model
        <https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-forecast>`_.

        **Note on auto detection of target lags and rolling window size.
        Please see the corresponding comments in the rolling window section.**
        We use the next algorithm to detect the optimal target lag and rolling window size.

        #. Estimate the maximum lag order for the look back feature selection. In our case it is the number of
           periods till the next date frequency granularity i.e. if frequency is daily, it will be a week (7),
           if it is a week, it will be month (4). That values multiplied by two is the largest
           possible values of lags/rolling windows. In our examples, we will consider the maximum lag
           order of 14 and 8 respectively).
        #. Create a de-seasonalized series by adding trend and residual components. This will be used
           in the next step.
        #. Estimate the PACF - Partial Auto Correlation Function on the on the data from (2)
           and search for points, where the auto correlation is significant i.e. its absolute
           value is more then 1.96/square_root(maximal lag value), which correspond to significance of 95%.
        #. If all points are significant, we consider it being strong seasonality
           and do not create look back features.
        #. We scan the PACF values from the beginning and the value before the first insignificant
           auto correlation will designate the lag. If first significant element (value correlate with
           itself) is followed by insignificant, the lag will be 0 and we will not use look back features.
    :type target_lags: Union[str, int, List[int]]
    :param target_rolling_window_size:
        The number of past periods used to create a rolling window average of the target column.

        When forecasting, this parameter represents `n` historical periods to use to generate forecasted values,
        <= training set size. If omitted, `n` is the full training set size. Specify this parameter
        when you only want to consider a certain amount of history when training the model.
        If set to 'auto', rolling window will be estimated as the last
        value where the PACF is more then the significance threshold. Please see target_lags section for details.
    :type target_rolling_window_size: Optional[Union[str, int]]
    :param frequency: Forecast frequency.

        When forecasting, this parameter represents the period with which the forecast is desired,
        for example daily, weekly, yearly, etc. The forecast frequency is dataset frequency by default.
        You can optionally set it to greater (but not lesser) than dataset frequency.
        We'll aggregate the data and generate the results at forecast frequency. For example,
        for daily data, you can set the frequency to be daily, weekly or monthly, but not hourly.
        The frequency needs to be a pandas offset alias.
        Please refer to pandas documentation for more information:
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
    :type frequency: Optional[str]
    :param feature_lags: Flag for generating lags for the numeric features with 'auto' or None.
    :type feature_lags: Optional[str]
    :param seasonality: Set time series seasonality as an integer multiple of the series frequency.
                If seasonality is set to 'auto', it will be inferred.
                If set to None, the time series is assumed non-seasonal which is equivalent to seasonality=1.
    :type seasonality: Optional[Union[int, str]]
    :param use_stl: Configure STL Decomposition of the time-series target column.
                use_stl can take three values: None (default) - no stl decomposition, 'season' - only generate
                season component and season_trend - generate both season and trend components.
    :type use_stl: Optional[str]
    :param short_series_handling_config:
        The parameter defining how if AutoML should handle short time series.

        Possible values: 'auto' (default), 'pad', 'drop' and None.
        * **auto** short series will be padded if there are no long series,
        otherwise short series will be dropped.
        * **pad** all the short series will be padded.
        * **drop**  all the short series will be dropped".
        * **None** the short series will not be modified.
        If set to 'pad', the table will be padded with the zeroes and
        empty values for the regressors and random values for target with the mean
        equal to target value median for given time series id. If median is more or equal
        to zero, the minimal padded value will be clipped by zero.
        Input:

        +------------+---------------+----------+--------+
        | Date       | numeric_value | string   | target |
        +============+===============+==========+========+
        | 2020-01-01 | 23            | green    | 55     |
        +------------+---------------+----------+--------+

        Output assuming minimal number of values is four:

        +------------+---------------+----------+--------+
        | Date       | numeric_value | string   | target |
        +============+===============+==========+========+
        | 2019-12-29 | 0             | NA       | 55.1   |
        +------------+---------------+----------+--------+
        | 2019-12-30 | 0             | NA       | 55.6   |
        +------------+---------------+----------+--------+
        | 2019-12-31 | 0             | NA       | 54.5   |
        +------------+---------------+----------+--------+
        | 2020-01-01 | 23            | green    | 55     |
        +------------+---------------+----------+--------+

        **Note:** We have two parameters short_series_handling_configuration and
        legacy short_series_handling. When both parameters are set we are
        synchronize them as shown in the table below (short_series_handling_configuration and
        short_series_handling for brevity are marked as handling_configuration and handling
        respectively).

        +------------+--------------------------+----------------------+-----------------------------+
        | | handling | | handling configuration | | resulting handling | | resulting handling        |
        |            |                          |                      | | configuration             |
        +============+==========================+======================+=============================+
        | True       | auto                     | True                 | auto                        |
        +------------+--------------------------+----------------------+-----------------------------+
        | True       | pad                      | True                 | auto                        |
        +------------+--------------------------+----------------------+-----------------------------+
        | True       | drop                     | True                 | auto                        |
        +------------+--------------------------+----------------------+-----------------------------+
        | True       | None                     | False                | None                        |
        +------------+--------------------------+----------------------+-----------------------------+
        | False      | auto                     | False                | None                        |
        +------------+--------------------------+----------------------+-----------------------------+
        | False      | pad                      | False                | None                        |
        +------------+--------------------------+----------------------+-----------------------------+
        | False      | drop                     | False                | None                        |
        +------------+--------------------------+----------------------+-----------------------------+
        | False      | None                     | False                | None                        |
        +------------+--------------------------+----------------------+-----------------------------+

    :type short_series_handling_config: Optional[str]
    :param target_aggregate_function: The function to be used to aggregate the time series target
                                      column to conform to a user specified frequency. If the
                                      target_aggregation_function is set, but the freq parameter
                                      is not set, the error is raised. The possible target
                                      aggregation functions are: "sum", "max", "min" and "mean".

            * The target column values are aggregated based on the specified operation.
              Typically, sum is appropriate for most scenarios.
            * Numerical predictor columns in your data are aggregated by sum, mean, minimum value,
              and maximum value. As a result, automated ML generates new columns suffixed with the
              aggregation function name and applies the selected aggregate operation.
            * For categorical predictor columns, the data is aggregated by mode,
              the most prominent category in the window.
            * Date predictor columns are aggregated by minimum value, maximum value and mode.

            +----------------+-------------------------------+--------------------------------------+
            |     | freq     | | target_aggregation_function | | Data regularity                    |
            |                |                               | | fixing mechanism                   |
            +================+===============================+======================================+
            | None (Default) | None (Default)                | | The aggregation is not             |
            |                |                               | | applied. If the valid              |
            |                |                               | | frequency can not be               |
            |                |                               | | determined the error will          |
            |                |                               | | be raised.                         |
            +----------------+-------------------------------+--------------------------------------+
            | Some Value     | None (Default)                | | The aggregation is not             |
            |                |                               | | applied. If the number             |
            |                |                               | | of data points compliant           |
            |                |                               | | to given frequency grid            |
            |                |                               | | is less then 90% these points      |
            |                |                               | | will be removed, otherwise         |
            |                |                               | | the error will be raised.          |
            +----------------+-------------------------------+--------------------------------------+
            | None (Default) | Aggregation function          | | The error about missing            |
            |                |                               | | frequency parameter                |
            |                |                               | | is raised.                         |
            +----------------+-------------------------------+--------------------------------------+
            | Some Value     | Aggregation function          | | Aggregate to frequency using       |
            |                |                               | | provided aggregation function.     |
            +----------------+-------------------------------+--------------------------------------+
    :type target_aggregate_function: str
    :param time_column_name:
        The name of the time column. This parameter is required when forecasting to specify the datetime
        column in the input data used for building the time series and inferring its frequency.
    :type time_column_name: Optional[str]
    :param time_series_id_column_names:
        The names of columns used to group a timeseries.
        It can be used to create multiple series. If time series id column names is not defined or
        the identifier columns specified do not identify all the series in the dataset, the time series identifiers
        will be automatically created for your dataset.
    :type time_series_id_column_names: Union[str, List[str]]
    :param features_unknown_at_forecast_time:
        The feature columns that are available for training but unknown at the time of forecast/inference.
        If features_unknown_at_forecast_time is set to an empty list, it is assumed that
        all the feature columns in the dataset are known at inference time. If this parameter is not set
        the support for future features is not enabled.
    :type features_unknown_at_forecast_time: Optional[Union[str, List[str]]]
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
        features_unknown_at_forecast_time: Optional[Union[str, List[str]]] = None,
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
        self.features_unknown_at_forecast_time = features_unknown_at_forecast_time

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

        features_unknown_at_forecast_time = self.features_unknown_at_forecast_time
        if isinstance(self.features_unknown_at_forecast_time, str) and self.features_unknown_at_forecast_time:
            features_unknown_at_forecast_time = [self.features_unknown_at_forecast_time]

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
            features_unknown_at_forecast_time=features_unknown_at_forecast_time,
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
            features_unknown_at_forecast_time=obj.features_unknown_at_forecast_time,
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
            and self.features_unknown_at_forecast_time == other.features_unknown_at_forecast_time
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
