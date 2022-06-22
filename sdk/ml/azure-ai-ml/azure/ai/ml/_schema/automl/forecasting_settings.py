# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from azure.ai.ml._schema import PatchedSchemaMeta, UnionField, StringTransformedEnum
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    FeatureLags as FeatureLagsMode,
    TargetLagsMode,
    TargetRollingWindowSizeMode,
    ForecastHorizonMode,
    ShortSeriesHandlingConfiguration,
    TargetAggregationFunction,
    SeasonalityMode,
    UseStl as STLMode,
)


class ForecastingSettingsSchema(metaclass=PatchedSchemaMeta):
    country_or_region_for_holidays = fields.Str()
    cv_step_size = fields.Int()
    forecast_horizon = UnionField(
        [
            StringTransformedEnum(allowed_values=[ForecastHorizonMode.AUTO]),
            fields.Int(),
        ]
    )
    target_lags = UnionField(
        [
            StringTransformedEnum(allowed_values=[TargetLagsMode.AUTO]),
            fields.Int(),
            fields.List(fields.Int()),
        ]
    )
    target_rolling_window_size = UnionField(
        [
            StringTransformedEnum(allowed_values=[TargetRollingWindowSizeMode.AUTO]),
            fields.Int(),
        ]
    )
    time_column_name = fields.Str()
    time_series_id_column_names = UnionField([fields.Str(), fields.List(fields.Str())])
    frequency = fields.Str()
    feature_lags = StringTransformedEnum(allowed_values=[FeatureLagsMode.NONE, FeatureLagsMode.AUTO])
    seasonality = UnionField(
        [
            StringTransformedEnum(allowed_values=[SeasonalityMode.AUTO]),
            fields.Int(),
        ]
    )
    short_series_handling_config = StringTransformedEnum(
        allowed_values=[o.value for o in ShortSeriesHandlingConfiguration]
    )
    use_stl = StringTransformedEnum(allowed_values=[STLMode.NONE, STLMode.SEASON, STLMode.SEASON_TREND])
    target_aggregate_function = StringTransformedEnum(allowed_values=[o.value for o in TargetAggregationFunction])

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings

        return ForecastingSettings(**data)
