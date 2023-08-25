# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import FeatureLags as FeatureLagsMode
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ForecastHorizonMode,
    SeasonalityMode,
    ShortSeriesHandlingConfiguration,
    TargetAggregationFunction,
    TargetLagsMode,
    TargetRollingWindowSizeMode,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import UseStl as STLMode
from azure.ai.ml._schema.core.fields import StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


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
    features_unknown_at_forecast_time = UnionField([fields.Str(), fields.List(fields.Str())])

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings

        return ForecastingSettings(**data)
