# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import Forecasting as RestForecasting
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ForecastingPrimaryMetrics,
    JobBaseData,
    StackEnsembleSettings,
    TaskType,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AutoMLConstants
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.automl.tabular.automl_tabular import AutoMLTabular
from azure.ai.ml.entities._job.automl.tabular.featurization_settings import TabularFeaturizationSettings
from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings
from azure.ai.ml.entities._job.automl.tabular.limit_settings import TabularLimitSettings
from azure.ai.ml.entities._job.automl.training_settings import ForecastingTrainingSettings
from azure.ai.ml.entities._util import load_from_dict


@experimental
class ForecastingJob(AutoMLTabular):
    """Configuration for AutoML Forecasting Task."""

    _DEFAULT_PRIMARY_METRIC = ForecastingPrimaryMetrics.NORMALIZED_ROOT_MEAN_SQUARED_ERROR

    def __init__(
        self,
        *,
        primary_metric: str = None,
        forecasting_settings: ForecastingSettings = None,
        **kwargs,
    ) -> None:
        # Extract any task specific settings
        data = kwargs.pop("data", None)
        featurization = kwargs.pop("featurization", None)
        limits = kwargs.pop("limits", None)
        training = kwargs.pop("training", None)

        super().__init__(
            task_type=TaskType.FORECASTING,
            data=data,
            featurization=featurization,
            limits=limits,
            training=training,
            **kwargs,
        )

        self.primary_metric = primary_metric or ForecastingJob._DEFAULT_PRIMARY_METRIC
        self._forecasting_settings = forecasting_settings

    @property
    def primary_metric(self):
        return self._primary_metric

    @primary_metric.setter
    def primary_metric(self, value: Union[str, ForecastingPrimaryMetrics]):
        if is_data_binding_expression(str(value), ["parent"]):
            self._primary_metric = value
            return
        self._primary_metric = (
            ForecastingJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else ForecastingPrimaryMetrics[camel_to_snake(value).upper()]
        )

    @AutoMLTabular.training.getter
    def training(self) -> ForecastingTrainingSettings:
        return self._training or ForecastingTrainingSettings()

    @property
    def forecasting_settings(self) -> ForecastingSettings:
        return self._forecasting_settings

    def set_forecast_settings(
        self,
        *,
        time_column_name: str = None,
        forecast_horizon: Union[str, int] = None,
        time_series_id_column_names: Union[str, List[str]] = None,
        target_lags: Union[str, int, List[int]] = None,
        feature_lags: str = None,
        target_rolling_window_size: Union[str, int] = None,
        country_or_region_for_holidays: str = None,
        use_stl: str = None,
        seasonality: Union[str, int] = None,
        short_series_handling_config: str = None,
        frequency: str = None,
        target_aggregate_function: str = None,
        cv_step_size: int = None,
    ) -> None:
        """Manage parameters used by forecasting tasks.

        :param time_column_name:
            The name of the time column. This parameter is required when forecasting to specify the datetime
            column in the input data used for building the time series and inferring its frequency.
        :type time_column_name: str
        :param forecast_horizon:
            The desired maximum forecast horizon in units of time-series frequency. The default value is 1.

            Units are based on the time interval of your training data, e.g., monthly, weekly that the forecaster
            should predict out. When task type is forecasting, this parameter is required. For more information on
            setting forecasting parameters, see `Auto-train a time-series forecast model <https://docs.microsoft.com/
            azure/machine-learning/how-to-auto-train-forecast>`_.
        :type forecast_horizon: int or str
        :param time_series_id_column_names:
            The names of columns used to group a timeseries.
            It can be used to create multiple series. If time series id column names is not defined or
            the identifier columns specified do not identify all the series in the dataset, the time series identifiers
            will be automatically created for your dataset.
        :type time_series_id_column_names: str or list(str)
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
        :type target_lags: int, str, or list(int)
        :param feature_lags: Flag for generating lags for the numeric features with 'auto' or None.
        :type feature_lags: str or None
        :param target_rolling_window_size:
            The number of past periods used to create a rolling window average of the target column.

            When forecasting, this parameter represents `n` historical periods to use to generate forecasted values,
            <= training set size. If omitted, `n` is the full training set size. Specify this parameter
            when you only want to consider a certain amount of history when training the model.
            If set to 'auto', rolling window will be estimated as the last
            value where the PACF is more then the significance threshold. Please see target_lags section for details.
        :type target_rolling_window_size: int, str or None
        :param country_or_region_for_holidays: The country/region used to generate holiday features.
            These should be ISO 3166 two-letter country/region codes, for example 'US' or 'GB'.
        :type country_or_region_for_holidays: str or None
        :param use_stl: Configure STL Decomposition of the time-series target column.
                    use_stl can take three values: None (default) - no stl decomposition, 'season' - only generate
                    season component and season_trend - generate both season and trend components.
        :type use_stl: str or None
        :param seasonality: Set time series seasonality as an integer multiple of the series frequency.
                    If seasonality is set to 'auto', it will be inferred.
                    If set to None, the time series is assumed non-seasonal which is equivalent to seasonality=1.
        :type seasonality: int, str or None
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
            to zero, the minimal padded value will be clipped by zero:
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

            +-----------+------------------------+--------------------+----------------------------------+
            |  handling | handling_configuration | resulting handling | resulting handling_configuration |
            +===========+========================+====================+==================================+
            | True      | auto                   | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | pad                    | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | drop                   | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | None                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | auto                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | pad                    | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | drop                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | None                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+

        :type short_series_handling_config: str or None
        :param frequency: Forecast frequency.

            When forecasting, this parameter represents the period with which the forecast is desired,
            for example daily, weekly, yearly, etc. The forecast frequency is dataset frequency by default.
            You can optionally set it to greater (but not lesser) than dataset frequency.
            We'll aggregate the data and generate the results at forecast frequency. For example,
            for daily data, you can set the frequency to be daily, weekly or monthly, but not hourly.
            The frequency needs to be a pandas offset alias.
            Please refer to pandas documentation for more information:
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
        :type frequency: str or None
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

                +----------------+-----------------------------+---------------------------------------------+
                |      freq      | target_aggregation_function |      Data regularity fixing mechanism       |
                +================+=============================+=============================================+
                | None (Default) | None (Default)              | The aggregation is not applied.             |
                |                |                             | If the valid frequency can not be           |
                |                |                             | determined the error will be raised.        |
                +----------------+-----------------------------+---------------------------------------------+
                | Some Value     | None (Default)              | The aggregation is not applied.             |
                |                |                             | If the number of data points compliant      |
                |                |                             | to given frequency grid is less then 90%    |
                |                |                             | these points will be removed, otherwise     |
                |                |                             | the error will be raised.                   |
                +----------------+-----------------------------+---------------------------------------------+
                | None (Default) | Aggregation function        | The error about missing frequency parameter |
                |                |                             | is raised.                                  |
                +----------------+-----------------------------+---------------------------------------------+
                | Some Value     | Aggregation function        | Aggregate to frequency using provided       |
                |                |                             | aggregation function.                       |
                +----------------+-----------------------------+---------------------------------------------+

        :type target_aggregate_function: str or None
        :param cv_step_size:
            Number of periods between the origin_time of one CV fold and the next fold. For
            example, if `n_step` = 3 for daily data, the origin time for each fold will be
            three days apart.
        :type cv_step_size: int or None
        """
        self._forecasting_settings = self._forecasting_settings or ForecastingSettings()

        self._forecasting_settings.country_or_region_for_holidays = (
            country_or_region_for_holidays
            if country_or_region_for_holidays is not None
            else self._forecasting_settings.country_or_region_for_holidays
        )
        self._forecasting_settings.cv_step_size = (
            cv_step_size if cv_step_size is not None else self._forecasting_settings.cv_step_size
        )
        self._forecasting_settings.forecast_horizon = (
            forecast_horizon if forecast_horizon is not None else self._forecasting_settings.forecast_horizon
        )
        self._forecasting_settings.target_lags = (
            target_lags if target_lags is not None else self._forecasting_settings.target_lags
        )
        self._forecasting_settings.target_rolling_window_size = (
            target_rolling_window_size
            if target_rolling_window_size is not None
            else self._forecasting_settings.target_rolling_window_size
        )
        self._forecasting_settings.frequency = (
            frequency if frequency is not None else self._forecasting_settings.frequency
        )
        self._forecasting_settings.feature_lags = (
            feature_lags if feature_lags is not None else self._forecasting_settings.feature_lags
        )
        self._forecasting_settings.seasonality = (
            seasonality if seasonality is not None else self._forecasting_settings.seasonality
        )
        self._forecasting_settings.use_stl = use_stl if use_stl is not None else self._forecasting_settings.use_stl
        self._forecasting_settings.short_series_handling_config = (
            short_series_handling_config
            if short_series_handling_config is not None
            else self._forecasting_settings.short_series_handling_config
        )
        self._forecasting_settings.target_aggregate_function = (
            target_aggregate_function
            if target_aggregate_function is not None
            else self._forecasting_settings.target_aggregate_function
        )
        self._forecasting_settings.time_column_name = (
            time_column_name if time_column_name is not None else self._forecasting_settings.time_column_name
        )
        self._forecasting_settings.time_series_id_column_names = (
            time_series_id_column_names
            if time_series_id_column_names is not None
            else self._forecasting_settings.time_series_id_column_names
        )

    # override
    def set_training(
        self,
        *,
        enable_onnx_compatible_models: bool = None,
        enable_dnn_training: bool = None,
        enable_model_explainability: bool = None,
        enable_stack_ensemble: bool = None,
        enable_vote_ensemble: bool = None,
        stack_ensemble_settings: StackEnsembleSettings = None,
        ensemble_model_download_timeout: int = None,
        allowed_training_algorithms: List[str] = None,
        blocked_training_algorithms: List[str] = None,
    ) -> None:
        super().set_training(
            enable_onnx_compatible_models=enable_onnx_compatible_models,
            enable_dnn_training=enable_dnn_training,
            enable_model_explainability=enable_model_explainability,
            enable_stack_ensemble=enable_stack_ensemble,
            enable_vote_ensemble=enable_vote_ensemble,
            stack_ensemble_settings=stack_ensemble_settings,
            ensemble_model_download_timeout=ensemble_model_download_timeout,
            allowed_training_algorithms=allowed_training_algorithms,
            blocked_training_algorithms=blocked_training_algorithms,
        )

        # Disable stack ensemble by default, since it is currently not supported for forecasting tasks
        if enable_stack_ensemble is None:
            self._training.enable_stack_ensemble = False

    def _to_rest_object(self) -> JobBaseData:
        self._resolve_data_inputs()
        self._validation_data_to_rest()

        forecasting_task = RestForecasting(
            data_settings=self._data,
            featurization_settings=self._featurization._to_rest_object() if self._featurization else None,
            limit_settings=self._limits._to_rest_object() if self._limits else None,
            training_settings=self._training._to_rest_object() if self._training else None,
            primary_metric=self.primary_metric,
            allowed_models=self._training.allowed_training_algorithms if self._training else None,
            blocked_models=self._training.blocked_training_algorithms if self._training else None,
            log_verbosity=self.log_verbosity,
            forecasting_settings=self._forecasting_settings._to_rest_object(),
        )

        properties = RestAutoMLJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            tags=self.tags,
            compute_id=self.compute,
            properties=self.properties,
            environment_id=self.environment_id,
            environment_variables=self.environment_variables,
            services=self.services,
            outputs=to_rest_data_outputs(self.outputs),
            resources=self.resources,
            task_details=forecasting_task,
            identity=self.identity,
        )

        result = JobBaseData(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _from_rest_object(cls, obj: JobBaseData) -> "ForecastingJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestForecasting = properties.task_details

        job_args_dict = {
            "id": obj.id,
            "name": obj.name,
            "description": properties.description,
            "tags": properties.tags,
            "properties": properties.properties,
            "experiment_name": properties.experiment_name,
            "services": properties.services,
            "status": properties.status,
            "creation_context": obj.system_data,
            "display_name": properties.display_name,
            "compute": properties.compute_id,
            "outputs": from_rest_data_outputs(properties.outputs),
            "resources": properties.resources,
            "identity": properties.identity,
        }

        forecasting_job = cls(
            data=task_details.data_settings,
            featurization=TabularFeaturizationSettings._from_rest_object(task_details.featurization_settings)
            if task_details.featurization_settings
            else None,
            limits=TabularLimitSettings._from_rest_object(task_details.limit_settings)
            if task_details.limit_settings
            else None,
            training=ForecastingTrainingSettings._from_rest_object(task_details.training_settings)
            if task_details.training_settings
            else None,
            primary_metric=task_details.primary_metric,
            forecasting_settings=ForecastingSettings._from_rest_object(task_details.forecasting_settings)
            if task_details.forecasting_settings
            else None,
            log_verbosity=task_details.log_verbosity,
            **job_args_dict,
        )

        forecasting_job._restore_data_inputs()
        forecasting_job._training_settings_from_rest(
            task_details.allowed_models,
            task_details.blocked_models,
        )
        forecasting_job._validation_data_from_rest()

        return forecasting_job

    @classmethod
    def _load_from_dict(
        cls,
        data: Dict,
        context: Dict,
        additional_message: str,
        inside_pipeline=False,
        **kwargs,
    ) -> "ForecastingJob":
        from azure.ai.ml._schema.automl.table_vertical.forecasting import AutoMLForecastingSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLForecastingNodeSchema

        if inside_pipeline:
            loaded_data = load_from_dict(AutoMLForecastingNodeSchema, data, context, additional_message, **kwargs)
        else:
            loaded_data = load_from_dict(AutoMLForecastingSchema, data, context, additional_message, **kwargs)
        job_instance = cls._create_instance_from_schema_dict(loaded_data)
        return job_instance

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "ForecastingJob":
        loaded_data.pop(AutoMLConstants.TASK_TYPE_YAML, None)
        data_settings = {
            "training_data": loaded_data.pop("training_data"),
            "target_column_name": loaded_data.pop("target_column_name"),
            "weight_column_name": loaded_data.pop("weight_column_name", None),
            "validation_data": loaded_data.pop("validation_data", None),
            "validation_data_size": loaded_data.pop("validation_data_size", None),
            "cv_split_column_names": loaded_data.pop("cv_split_column_names", None),
            "n_cross_validations": loaded_data.pop("n_cross_validations", None),
            "test_data": loaded_data.pop("test_data", None),
            "test_data_size": loaded_data.pop("test_data_size", None),
        }
        job = ForecastingJob(**loaded_data)
        job.set_data(**data_settings)
        return job

    def _to_dict(self, inside_pipeline=False) -> Dict:
        from azure.ai.ml._schema.automl.table_vertical.forecasting import AutoMLForecastingSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLForecastingNodeSchema

        if inside_pipeline:
            schema_dict = AutoMLForecastingNodeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        else:
            schema_dict = AutoMLForecastingSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return schema_dict

    def __eq__(self, other):
        if not isinstance(other, ForecastingJob):
            return NotImplemented

        if not super(ForecastingJob, self).__eq__(other):
            return False

        return self.primary_metric == other.primary_metric and self._forecasting_settings == other._forecasting_settings

    def __ne__(self, other):
        return not self.__eq__(other)
