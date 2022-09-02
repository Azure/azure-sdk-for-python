# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .automl_job import AutoMLJobSchema
from .automl_vertical import AutoMLVerticalSchema
from .featurization_settings import FeaturizationSettingsSchema, TableFeaturizationSettingsSchema
from .forecasting_settings import ForecastingSettingsSchema
from .table_vertical.classification import AutoMLClassificationSchema
from .table_vertical.forecasting import AutoMLForecastingSchema
from .table_vertical.regression import AutoMLRegressionSchema
from .table_vertical.table_vertical import AutoMLTableVerticalSchema
from .table_vertical.table_vertical_limit_settings import AutoMLTableLimitsSchema
from .training_settings import TrainingSettingsSchema

__all__ = [
    "AutoMLJobSchema",
    "AutoMLVerticalSchema",
    "FeaturizationSettingsSchema",
    "TableFeaturizationSettingsSchema",
    "ForecastingSettingsSchema",
    "AutoMLClassificationSchema",
    "AutoMLForecastingSchema",
    "AutoMLRegressionSchema",
    "AutoMLTableVerticalSchema",
    "AutoMLTableLimitsSchema",
    "TrainingSettingsSchema",
]
