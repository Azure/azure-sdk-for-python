# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access, too-many-lines

import datetime
from typing import Any, Dict, List, Optional, Union

import isodate
from typing_extensions import Literal

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_06_01_preview.models import AllFeatures as RestAllFeatures
from azure.ai.ml._restclient.v2023_06_01_preview.models import CustomMonitoringSignal as RestCustomMonitoringSignal
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    DataDriftMonitoringSignal as RestMonitoringDataDriftSignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    DataQualityMonitoringSignal as RestMonitoringDataQualitySignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    FeatureAttributionDriftMonitoringSignal as RestFeatureAttributionDriftMonitoringSignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import FeatureSubset as RestFeatureSubset
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    GenerationSafetyQualityMonitoringSignal as RestGenerationSafetyQualityMonitoringSignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    GenerationTokenStatisticsSignal as RestGenerationTokenStatisticsSignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import ModelPerformanceSignal as RestModelPerformanceSignal
from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringDataSegment as RestMonitoringDataSegment
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitoringFeatureFilterBase as RestMonitoringFeatureFilterBase,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringInputDataBase as RestMonitoringInputData
from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringNotificationMode
from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringSignalBase as RestMonitoringSignalBase
from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringSignalType
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitoringWorkspaceConnection as RestMonitoringWorkspaceConnection,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    PredictionDriftMonitoringSignal as RestPredictionDriftMonitoringSignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    TopNFeaturesByAttribution as RestTopNFeaturesByAttribution,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._monitoring import (
    ALL_FEATURES,
    MonitorDatasetContext,
    MonitorFeatureDataType,
    MonitorSignalType,
)
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_inputs_to_dataset_literal,
    to_rest_dataset_literal_inputs,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._monitoring.input_data import FixedInputData, StaticInputData, TrailingInputData
from azure.ai.ml.entities._monitoring.thresholds import (
    CustomMonitoringMetricThreshold,
    DataDriftMetricThreshold,
    DataQualityMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    GenerationSafetyQualityMonitoringMetricThreshold,
    GenerationTokenStatisticsMonitorMetricThreshold,
    MetricThreshold,
    ModelPerformanceMetricThreshold,
    PredictionDriftMetricThreshold,
)
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


class DataSegment(RestTranslatableMixin):
    """Data segment for monitoring.

    :keyword feature_name: The feature to segment the data on.
    :paramtype feature_name: str
    :keyword feature_values: A list of values for the given segmented feature to filter.
    :paramtype feature_values: List[str]
    """

    def __init__(
        self,
        *,
        feature_name: Optional[str] = None,
        feature_values: Optional[List[str]] = None,
    ) -> None:
        self.feature_name = feature_name
        self.feature_values = feature_values

    def _to_rest_object(self) -> RestMonitoringDataSegment:
        return RestMonitoringDataSegment(feature=self.feature_name, values=self.feature_values)

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataSegment) -> "DataSegment":
        return cls(
            feature_name=obj.feature,
            feature_values=obj.values,
        )


class MonitorFeatureFilter(RestTranslatableMixin):
    """Monitor feature filter

    :keyword top_n_feature_importance: The number of top features to include. Defaults to 10.
    :paramtype top_n_feature_importance: int
    """

    def __init__(
        self,
        *,
        top_n_feature_importance: int = 10,
    ) -> None:
        self.top_n_feature_importance = top_n_feature_importance

    def _to_rest_object(self) -> RestTopNFeaturesByAttribution:
        return RestTopNFeaturesByAttribution(
            top=self.top_n_feature_importance,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestTopNFeaturesByAttribution) -> "MonitorFeatureFilter":
        return cls(top_n_feature_importance=obj.top)


class BaselineDataRange:
    """Baseline data range for monitoring.

    This class is used when initializing a data_window for a ReferenceData object.
    For trailing input, set lookback_window_size and lookback_window_offset to a desired value.
    For static input, set window_start and window_end to a desired value.
    """

    def __init__(
        self,
        *,
        window_start: Optional[str] = None,
        window_end: Optional[str] = None,
        lookback_window_size: Optional[str] = None,
        lookback_window_offset: Optional[str] = None,
    ):
        self.window_start = window_start
        self.window_end = window_end
        self.lookback_window_size = lookback_window_size
        self.lookback_window_offset = lookback_window_offset


class ProductionData(RestTranslatableMixin):
    """Production Data

    :param input_data: The data for which drift will be calculated
    :type Input: ~azure.ai.ml.entities._input_outputs
    :param data_context: The context of the input dataset. Possible values
        include: model_inputs, model_outputs, training, test, validation, ground_truth
    :type MonitorDatasetContext: ~azure.ai.ml.constants.MonitorDatasetContext
    :param pre_processing_component: ARM resource ID of the component resource used to
        preprocess the data.
    :type pre_processing_component: string
    :param data_window: The number of days or a time frame that a singal monitor looks back over the target.
    :type data_window_size: BaselineDataRange
    """

    def __init__(
        self,
        *,
        input_data: Input,
        data_context: Optional[MonitorDatasetContext] = None,
        pre_processing_component: Optional[str] = None,
        data_window: Optional[BaselineDataRange] = None,
        data_column_names: Optional[Dict[str, str]] = None,
    ):
        self.input_data = input_data
        self.data_context = data_context
        self.pre_processing_component = pre_processing_component
        self.data_window = data_window
        self.data_column_names = data_column_names

    def _to_rest_object(self, **kwargs: Any) -> RestMonitoringInputData:
        self._validate()
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.data_window is None:
            self.data_window = BaselineDataRange(
                lookback_window_size=default_data_window_size, lookback_window_offset="P0D"
            )
        if self.data_window.lookback_window_size in ["default", None]:
            self.data_window.lookback_window_size = default_data_window_size
        uri = self.input_data.path
        job_type = self.input_data.type
        monitoring_input_data = TrailingInputData(
            data_context=self.data_context,
            target_columns=self.data_column_names,
            job_type=job_type,
            uri=uri,
            pre_processing_component_id=self.pre_processing_component,
            window_size=self.data_window.lookback_window_size,
            window_offset=(
                self.data_window.lookback_window_offset
                if self.data_window.lookback_window_offset is not None
                else "P0D"
            ),
        )
        return monitoring_input_data._to_rest_object()

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "ProductionData":
        data_window = BaselineDataRange(
            lookback_window_size=isodate.duration_isoformat(obj.window_size),
            lookback_window_offset=isodate.duration_isoformat(obj.window_offset),
        )
        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            pre_processing_component=obj.preprocessing_component_id,
            data_window=data_window,
            data_column_names=obj.columns,
        )

    def _validate(self) -> None:
        if self.data_window:
            if self.data_window.window_start or self.data_window.window_end:
                msg = "ProductionData only accepts lookback_window_size and lookback_window_offset."
                err = ValidationException(
                    message=msg,
                    target=ErrorTarget.MODEL_MONITORING,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.MISSING_FIELD,
                )
                log_and_raise_error(err)


class ReferenceData(RestTranslatableMixin):
    """Reference Data

    :param input_data: The data for which drift will be calculated
    :type Input: ~azure.ai.ml.entities._input_outputs
    :param data_context: The context of the input dataset. Possible values
        include: model_inputs, model_outputs, training, test, validation, ground_truth
    :type MonitorDatasetContext: ~azure.ai.ml.constants.MonitorDatasetContext
    :param pre_processing_component: ARM resource ID of the component resource used to
        preprocess the data.
    :type pre_processing_component: string
    :param target_column_name: The name of the target column in the dataset.
    :type target_column_name: string
    :param data_window: The number of days or a time frame that a single monitor looks back over the target.
    :type data_window_size: BaselineDataRange
    """

    def __init__(
        self,
        *,
        input_data: Input,
        data_context: Optional[MonitorDatasetContext] = None,
        pre_processing_component: Optional[str] = None,
        data_window: Optional[BaselineDataRange] = None,
        data_column_names: Optional[Dict[str, str]] = None,
    ):
        self.input_data = input_data
        self.data_context = data_context
        self.pre_processing_component = pre_processing_component
        self.data_window = data_window
        self.data_column_names = data_column_names

    def _to_rest_object(self, **kwargs: Any) -> RestMonitoringInputData:
        default_data_window = kwargs.get("default_data_window")
        ref_data_window_size = kwargs.get("ref_data_window_size")
        if self.data_window is not None:
            if self.data_window.lookback_window_size is not None:
                if self.data_window.lookback_window_size == "default":
                    self.data_window.lookback_window_size = ref_data_window_size
                if self.data_window.lookback_window_offset == "default":
                    self.data_window.lookback_window_offset = default_data_window
                return TrailingInputData(
                    data_context=self.data_context,
                    target_columns=self.data_column_names,
                    job_type=self.input_data.type,
                    uri=self.input_data.path,
                    pre_processing_component_id=self.pre_processing_component,
                    window_size=self.data_window.lookback_window_size,
                    window_offset=(
                        self.data_window.lookback_window_offset
                        if self.data_window.lookback_window_offset is not None
                        else "P0D"
                    ),
                )._to_rest_object()
            if self.data_window.window_start is not None and self.data_window.window_end is not None:
                return StaticInputData(
                    data_context=self.data_context,
                    target_columns=self.data_column_names,
                    job_type=self.input_data.type,
                    uri=self.input_data.path,
                    pre_processing_component_id=self.pre_processing_component,
                    window_start=self.data_window.window_start,
                    window_end=self.data_window.window_end,
                )._to_rest_object()

        return FixedInputData(
            data_context=self.data_context,
            target_columns=self.data_column_names,
            job_type=self.input_data.type,
            uri=self.input_data.path,
        )._to_rest_object()

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "ReferenceData":
        data_window = None
        if obj.input_data_type == "Static":
            data_window = BaselineDataRange(
                window_start=datetime.datetime.strftime(obj.window_start, "%Y-%m-%d"),
                window_end=datetime.datetime.strftime(obj.window_end, "%Y-%m-%d"),
            )
        if obj.input_data_type == "Trailing":
            data_window = BaselineDataRange(
                lookback_window_size=isodate.duration_isoformat(obj.window_size),
                lookback_window_offset=isodate.duration_isoformat(obj.window_offset),
            )

        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            pre_processing_component=obj.preprocessing_component_id if obj.input_data_type != "Fixed" else None,
            data_window=data_window,
            data_column_names=obj.columns,
        )


class MonitoringSignal(RestTranslatableMixin):
    """
    Base class for monitoring signals.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword baseline_dataset: The baseline dataset definition for monitor input.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: The metric thresholds for the signal.
    :paramtype metric_thresholds: Union[
        ~azure.ai.ml.entities.DataDriftMetricThreshold,
        ~azure.ai.ml.entities.DataQualityMetricThreshold,
        ~azure.ai.ml.entities.PredictionDriftMetricThreshold,
        ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold,
        ~azure.ai.ml.entities.CustomMonitoringMetricThreshold,
        ~azure.ai.ml.entities.GenerationSafetyQualityMonitoringMetricThreshold,
        List[Union[
            ~azure.ai.ml.entities.DataDriftMetricThreshold,
            ~azure.ai.ml.entities.DataQualityMetricThreshold,
            ~azure.ai.ml.entities.PredictionDriftMetricThreshold,
            ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold,
            ~azure.ai.ml.entities.CustomMonitoringMetricThreshold,
            ~azure.ai.ml.entities.GenerationSafetyQualityMonitoringMetricThreshold,

        ]]]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: Optional[ProductionData] = None,
        reference_data: Optional[ReferenceData] = None,
        metric_thresholds: Optional[Union[MetricThreshold, List[MetricThreshold]]],
        properties: Optional[Dict[str, str]] = None,
        alert_enabled: bool = False,
    ):
        self.production_data = production_data
        self.reference_data = reference_data
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled
        self.properties = properties

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringSignalBase) -> Optional[  # pylint: disable=too-many-return-statements
        Union[
            "DataDriftSignal",
            "DataQualitySignal",
            "PredictionDriftSignal",
            "ModelPerformanceSignal",
            "FeatureAttributionDriftSignal",
            "CustomMonitoringSignal",
            "GenerationSafetyQualitySignal",
            "GenerationTokenStatisticsSignal",
        ]
    ]:
        if obj.signal_type == MonitoringSignalType.DATA_DRIFT:
            return DataDriftSignal._from_rest_object(obj)
        if obj.signal_type == MonitoringSignalType.DATA_QUALITY:
            return DataQualitySignal._from_rest_object(obj)
        if obj.signal_type == MonitoringSignalType.PREDICTION_DRIFT:
            return PredictionDriftSignal._from_rest_object(obj)
        if obj.signal_type == "ModelPerformanceSignalBase":
            return ModelPerformanceSignal._from_rest_object(obj)
        if obj.signal_type == MonitoringSignalType.FEATURE_ATTRIBUTION_DRIFT:
            return FeatureAttributionDriftSignal._from_rest_object(obj)
        if obj.signal_type == MonitoringSignalType.CUSTOM:
            return CustomMonitoringSignal._from_rest_object(obj)
        if obj.signal_type == MonitoringSignalType.GENERATION_SAFETY_QUALITY:
            return GenerationSafetyQualitySignal._from_rest_object(obj)
        if obj.signal_type == MonitoringSignalType.MODEL_PERFORMANCE:
            return ModelPerformanceSignal._from_rest_object(obj)
        if obj.signal_type == MonitoringSignalType.GENERATION_TOKEN_STATISTICS:
            return GenerationTokenStatisticsSignal._from_rest_object(obj)

        return None


class DataSignal(MonitoringSignal):
    """Base class for data signals.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword baseline_dataset: The baseline dataset definition for monitor input.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword features: The features to include in the signal.
    :paramtype features: Union[List[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal[ALL_FEATURES]]
    :keyword metric_thresholds: The metric thresholds for the signal.
    :paramtype metric_thresholds: List[Union[
        ~azure.ai.ml.entities.DataDriftMetricThreshold,
        ~azure.ai.ml.entities.DataQualityMetricThreshold,
        ~azure.ai.ml.entities.PredictionDriftMetricThreshold,
        ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold,
        ~azure.ai.ml.entities.CustomMonitoringMetricThreshold,
        ~azure.ai.ml.entities.GenerationSafetyQualityMonitoringMetricThreshold,

    ]]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: Optional[ProductionData] = None,
        reference_data: Optional[ReferenceData] = None,
        features: Optional[Union[List[str], MonitorFeatureFilter, Literal["all_features"]]] = None,
        feature_type_override: Optional[Dict[str, Union[str, MonitorFeatureDataType]]] = None,
        metric_thresholds: Optional[Union[MetricThreshold, List[MetricThreshold]]],
        alert_enabled: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
            properties=properties,
        )
        self.features = features
        self.feature_type_override = feature_type_override


class DataDriftSignal(DataSignal):
    """Data drift signal.

    :ivar type: The type of the signal, set to "data_drift" for this class.
    :vartype type: str
    :param production_data: The data for which drift will be calculated
    :paramtype production_data: ~azure.ai.ml.entities.ProductionData
    :param reference_data: The data to calculate drift against
    :paramtype reference_data: ~azure.ai.ml.entities.ReferenceData
    :param metric_thresholds: Metrics to calculate and their associated thresholds
    :paramtype metric_thresholds: ~azure.ai.ml.entities.DataDriftMetricThreshold
    :param alert_enabled: The current notification mode for this signal
    :paramtype alert_enabled: bool
    :param data_segment: The data segment used for scoping on a subset of the data population.
    :paramtype data_segment: ~azure.ai.ml.entities.DataSegment
    :keyword features: The feature filter identifying which feature(s) to calculate drift over.
    :paramtype features: Union[List[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal['all_features']]
    :param feature_type_override: Dictionary of features and what they should be overridden to.
    :paramtype feature_type_override: dict[str, str]
    :param properties: Dictionary of additional properties.
    :paramtype properties: dict[str, str]
    """

    def __init__(
        self,
        *,
        production_data: Optional[ProductionData] = None,
        reference_data: Optional[ReferenceData] = None,
        features: Optional[Union[List[str], MonitorFeatureFilter, Literal["all_features"]]] = None,
        feature_type_override: Optional[Dict[str, Union[str, MonitorFeatureDataType]]] = None,
        metric_thresholds: Optional[Union[DataDriftMetricThreshold, List[MetricThreshold]]] = None,
        alert_enabled: bool = False,
        data_segment: Optional[DataSegment] = None,
        properties: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            features=features,
            feature_type_override=feature_type_override,
            alert_enabled=alert_enabled,
            properties=properties,
        )
        self.type = MonitorSignalType.DATA_DRIFT
        self.data_segment = data_segment

    def _to_rest_object(self, **kwargs: Any) -> RestMonitoringDataDriftSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        ref_data_window_size = kwargs.get("ref_data_window_size")
        if self.production_data is not None and self.production_data.data_window is None:
            self.production_data.data_window = BaselineDataRange(lookback_window_size=default_data_window_size)
        rest_features = _to_rest_features(self.features) if self.features else None
        return RestMonitoringDataDriftSignal(
            production_data=(
                self.production_data._to_rest_object(default_data_window_size=default_data_window_size)
                if self.production_data is not None
                else None
            ),
            reference_data=(
                self.reference_data._to_rest_object(
                    default_data_window=default_data_window_size, ref_data_window_size=ref_data_window_size
                )
                if self.reference_data is not None
                else None
            ),
            features=rest_features,
            feature_data_type_override=self.feature_type_override,
            metric_thresholds=(
                self.metric_thresholds._to_rest_object()
                if isinstance(self.metric_thresholds, MetricThreshold)
                else None
            ),
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            data_segment=self.data_segment._to_rest_object() if self.data_segment else None,
            properties=self.properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataDriftSignal) -> "DataDriftSignal":
        return cls(
            production_data=ProductionData._from_rest_object(obj.production_data),
            reference_data=ReferenceData._from_rest_object(obj.reference_data),
            features=_from_rest_features(obj.features),
            feature_type_override=obj.feature_data_type_override,
            metric_thresholds=DataDriftMetricThreshold._from_rest_object(obj.metric_thresholds),
            alert_enabled=(
                False
                if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
                else MonitoringNotificationMode.ENABLED
            ),
            data_segment=DataSegment._from_rest_object(obj.data_segment) if obj.data_segment else None,
            properties=obj.properties,
        )

    @classmethod
    def _get_default_data_drift_signal(cls) -> "DataDriftSignal":
        return cls(
            features=ALL_FEATURES,  # type: ignore[arg-type]
            metric_thresholds=DataDriftMetricThreshold._get_default_thresholds(),
        )


class PredictionDriftSignal(MonitoringSignal):
    """Prediction drift signal.

    :ivar type: The type of the signal, set to "prediction_drift" for this class.
    :vartype type: str
    :param production_data: The data for which drift will be calculated
    :paramtype production_data: ~azure.ai.ml.entities.ProductionData
    :param reference_data: The data to calculate drift against
    :paramtype reference_data: ~azure.ai.ml.entities.ReferenceData
    :param metric_thresholds: Metrics to calculate and their associated thresholds
    :paramtype metric_thresholds: ~azure.ai.ml.entities.DataDriftMetricThreshold
    :param alert_enabled: The current notification mode for this signal
    :paramtype alert_enabled: bool
    :param properties: Dictionary of additional properties.
    :paramtype properties: dict[str, str]
    """

    def __init__(
        self,
        *,
        production_data: Optional[ProductionData] = None,
        reference_data: Optional[ReferenceData] = None,
        metric_thresholds: PredictionDriftMetricThreshold,
        alert_enabled: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
            properties=properties,
        )
        self.type = MonitorSignalType.PREDICTION_DRIFT

    def _to_rest_object(self, **kwargs: Any) -> RestPredictionDriftMonitoringSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        ref_data_window_size = kwargs.get("ref_data_window_size")
        if self.production_data is not None and self.production_data.data_window is None:
            self.production_data.data_window = BaselineDataRange(lookback_window_size=default_data_window_size)
        return RestPredictionDriftMonitoringSignal(
            production_data=(
                self.production_data._to_rest_object(default_data_window_size=default_data_window_size)
                if self.production_data is not None
                else None
            ),
            reference_data=(
                self.reference_data._to_rest_object(
                    default_data_window=default_data_window_size, ref_data_window_size=ref_data_window_size
                )
                if self.reference_data is not None
                else None
            ),
            metric_thresholds=(
                self.metric_thresholds._to_rest_object()
                if isinstance(self.metric_thresholds, MetricThreshold)
                else None
            ),
            properties=self.properties,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            model_type="classification",
        )

    @classmethod
    def _from_rest_object(cls, obj: RestPredictionDriftMonitoringSignal) -> "PredictionDriftSignal":
        return cls(
            production_data=ProductionData._from_rest_object(obj.production_data),
            reference_data=ReferenceData._from_rest_object(obj.reference_data),
            metric_thresholds=PredictionDriftMetricThreshold._from_rest_object(obj.metric_thresholds),
            alert_enabled=(
                False
                if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
                else MonitoringNotificationMode.ENABLED
            ),
            properties=obj.properties,
        )

    @classmethod
    def _get_default_prediction_drift_signal(cls) -> "PredictionDriftSignal":
        return cls(
            metric_thresholds=PredictionDriftMetricThreshold._get_default_thresholds(),
        )


class DataQualitySignal(DataSignal):
    """Data quality signal

    :ivar type: The type of the signal. Set to "data_quality" for this class.
    :vartype type: str
    :param production_data: The data for which drift will be calculated
    :paramtype production_data: ~azure.ai.ml.entities.ProductionData
    :param reference_data: The data to calculate drift against
    :paramtype reference_data: ~azure.ai.ml.entities.ReferenceData
    :param metric_thresholds: Metrics to calculate and their associated thresholds
    :paramtype metric_thresholds: ~azure.ai.ml.entities.DataDriftMetricThreshold
    :param alert_enabled: The current notification mode for this signal
    :paramtype alert_enabled: bool
    :keyword features: The feature filter identifying which feature(s) to calculate drift over.
    :paramtype features: Union[List[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal['all_features']]
    :param feature_type_override: Dictionary of features and what they should be overridden to.
    :paramtype feature_type_override: dict[str, str]
    :param properties: Dictionary of additional properties.
    :paramtype properties: dict[str, str]
    """

    def __init__(
        self,
        *,
        production_data: Optional[ProductionData] = None,
        reference_data: Optional[ReferenceData] = None,
        features: Optional[Union[List[str], MonitorFeatureFilter, Literal["all_features"]]] = None,
        feature_type_override: Optional[Dict[str, Union[str, MonitorFeatureDataType]]] = None,
        metric_thresholds: Optional[Union[MetricThreshold, List[MetricThreshold]]] = None,
        alert_enabled: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            features=features,
            feature_type_override=feature_type_override,
            alert_enabled=alert_enabled,
            properties=properties,
        )
        self.type = MonitorSignalType.DATA_QUALITY

    def _to_rest_object(self, **kwargs: Any) -> RestMonitoringDataQualitySignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        ref_data_window_size = kwargs.get("ref_data_window_size")
        if self.production_data is not None and self.production_data.data_window is None:
            self.production_data.data_window = BaselineDataRange(
                lookback_window_size=default_data_window_size,
            )
        rest_features = _to_rest_features(self.features) if self.features else None
        rest_metrics = (
            # TODO: Bug Item number: 2883365
            _to_rest_data_quality_metrics(
                self.metric_thresholds.numerical, self.metric_thresholds.categorical  # type: ignore
            )
            if isinstance(self.metric_thresholds, MetricThreshold)
            else None
        )
        return RestMonitoringDataQualitySignal(
            production_data=(
                self.production_data._to_rest_object(default_data_window_size=default_data_window_size)
                if self.production_data is not None
                else None
            ),
            reference_data=(
                self.reference_data._to_rest_object(
                    default_data_window=default_data_window_size, ref_data_window_size=ref_data_window_size
                )
                if self.reference_data is not None
                else None
            ),
            features=rest_features,
            feature_data_type_override=self.feature_type_override,
            metric_thresholds=rest_metrics,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            properties=self.properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataQualitySignal) -> "DataQualitySignal":
        return cls(
            production_data=ProductionData._from_rest_object(obj.production_data),
            reference_data=ReferenceData._from_rest_object(obj.reference_data),
            features=_from_rest_features(obj.features),
            feature_type_override=obj.feature_data_type_override,
            metric_thresholds=DataQualityMetricThreshold._from_rest_object(obj.metric_thresholds),
            alert_enabled=(
                False
                if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
                else MonitoringNotificationMode.ENABLED
            ),
            properties=obj.properties,
        )

    @classmethod
    def _get_default_data_quality_signal(
        cls,
    ) -> "DataQualitySignal":
        return cls(
            features=ALL_FEATURES,  # type: ignore[arg-type]
            metric_thresholds=DataQualityMetricThreshold._get_default_thresholds(),
        )


@experimental
class FADProductionData(RestTranslatableMixin):
    """Feature Attribution Production Data

    :keyword input_data: Input data used by the monitor.
    :paramtype input_data: ~azure.ai.ml.Input
    :keyword data_context: The context of the input dataset. Accepted values are "model_inputs",
        "model_outputs", "training", "test", "validation", and "ground_truth".
    :paramtype data_context: ~azure.ai.ml.constants._monitoring
    :keyword data_column_names: The names of the columns in the input data.
    :paramtype data_column_names: Dict[str, str]
    :keyword pre_processing_component: The ARM (Azure Resource Manager) resource ID of the component resource used to
        preprocess the data.
    :paramtype pre_processing_component: string
    :param data_window: The number of days or a time frame that a singal monitor looks back over the target.
    :type data_window: BaselineDataRange
    """

    def __init__(
        self,
        *,
        input_data: Input,
        data_context: Optional[MonitorDatasetContext] = None,
        data_column_names: Optional[Dict[str, str]] = None,
        pre_processing_component: Optional[str] = None,
        data_window: Optional[BaselineDataRange] = None,
    ):
        self.input_data = input_data
        self.data_context = data_context
        self.data_column_names = data_column_names
        self.pre_processing_component = pre_processing_component
        self.data_window = data_window

    def _to_rest_object(self, **kwargs: Any) -> RestMonitoringInputData:
        default_data_window_size = kwargs.get("default")
        if self.data_window is None:
            self.data_window = BaselineDataRange(
                lookback_window_size=default_data_window_size, lookback_window_offset="P0D"
            )
        if self.data_window.lookback_window_size == "default":
            self.data_window.lookback_window_size = default_data_window_size
        uri = self.input_data.path
        job_type = self.input_data.type
        monitoring_input_data = TrailingInputData(
            data_context=self.data_context,
            target_columns=self.data_column_names,
            job_type=job_type,
            uri=uri,
            pre_processing_component_id=self.pre_processing_component,
            window_size=self.data_window.lookback_window_size,
            window_offset=(
                self.data_window.lookback_window_offset
                if self.data_window.lookback_window_offset is not None
                else "P0D"
            ),
        )
        return monitoring_input_data._to_rest_object()

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "FADProductionData":
        data_window = BaselineDataRange(
            lookback_window_size=isodate.duration_isoformat(obj.window_size),
            lookback_window_offset=isodate.duration_isoformat(obj.window_offset),
        )
        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            data_column_names=obj.columns,
            pre_processing_component=obj.preprocessing_component_id,
            data_window=data_window,
        )


@experimental
class FeatureAttributionDriftSignal(RestTranslatableMixin):
    """Feature attribution drift signal

    :ivar type: The type of the signal. Set to "feature_attribution_drift" for this class.
    :vartype type: str
    :keyword production_data: The data for which drift will be calculated.
    :paratype production_data: ~azure.ai.ml.entities.FADProductionData
    :keyword reference_data: The data to calculate drift against.
    :paramtype reference_data: ~azure.ai.ml.entities.ReferenceData
    :keyword metric_thresholds: Metrics to calculate and their
        associated thresholds.
    :paramtype metric_thresholds: ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: Optional[List[FADProductionData]] = None,
        reference_data: ReferenceData,
        metric_thresholds: FeatureAttributionDriftMetricThreshold,
        alert_enabled: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ):
        self.production_data = production_data
        self.reference_data = reference_data
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled
        self.properties = properties
        self.type = MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT

    def _to_rest_object(
        self, **kwargs: Any  # pylint: disable=unused-argument
    ) -> RestFeatureAttributionDriftMonitoringSignal:
        default_window_size = kwargs.get("default_data_window_size")
        ref_data_window_size = kwargs.get("ref_data_window_size")
        return RestFeatureAttributionDriftMonitoringSignal(
            production_data=(
                [data._to_rest_object(default=default_window_size) for data in self.production_data]
                if self.production_data is not None
                else None
            ),
            reference_data=self.reference_data._to_rest_object(
                default_data_window=default_window_size, ref_data_window_size=ref_data_window_size
            ),
            metric_threshold=self.metric_thresholds._to_rest_object(),
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            properties=self.properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestFeatureAttributionDriftMonitoringSignal) -> "FeatureAttributionDriftSignal":
        return cls(
            production_data=[FADProductionData._from_rest_object(data) for data in obj.production_data],
            reference_data=ReferenceData._from_rest_object(obj.reference_data),
            metric_thresholds=FeatureAttributionDriftMetricThreshold._from_rest_object(obj.metric_threshold),
            alert_enabled=(
                False
                if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
                else MonitoringNotificationMode.ENABLED
            ),
            properties=obj.properties,
        )


@experimental
class ModelPerformanceSignal(RestTranslatableMixin):
    """Model performance signal.

    :keyword baseline_dataset: The data to calculate performance against.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :paramtype metric_thresholds: ~azure.ai.ml.entities.ModelPerformanceMetricThreshold
    :keyword model_type: The model type.
    :paramtype model_type: ~azure.ai.ml.constants.MonitorModelType
    :keyword data_segment: The data segment to calculate performance against.
    :paramtype data_segment: ~azure.ai.ml.entities.DataSegment
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: ProductionData,
        reference_data: ReferenceData,
        metric_thresholds: ModelPerformanceMetricThreshold,
        data_segment: Optional[DataSegment] = None,
        alert_enabled: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ) -> None:
        self.production_data = production_data
        self.reference_data = reference_data
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled
        self.type = MonitorSignalType.MODEL_PERFORMANCE
        self.data_segment = data_segment
        self.properties = properties

    def _to_rest_object(self, **kwargs: Any) -> RestModelPerformanceSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        ref_data_window_size = kwargs.get("ref_data_window_size")
        if self.properties is None:
            self.properties = {}
        self.properties["azureml.modelmonitor.model_performance_thresholds"] = self.metric_thresholds._to_str_object()
        if self.production_data.data_window is None:
            self.production_data.data_window = BaselineDataRange(
                lookback_window_size=default_data_window_size,
            )
        return RestModelPerformanceSignal(
            production_data=[self.production_data._to_rest_object(default_data_window_size=default_data_window_size)],
            reference_data=self.reference_data._to_rest_object(
                default_data_window_size=default_data_window_size, ref_data_window_size=ref_data_window_size
            ),
            metric_threshold=self.metric_thresholds._to_rest_object(),
            data_segment=self.data_segment._to_rest_object() if self.data_segment else None,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            properties=self.properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestModelPerformanceSignal) -> "ModelPerformanceSignal":
        return cls(
            production_data=ProductionData._from_rest_object(obj.production_data[0]),
            reference_data=ReferenceData._from_rest_object(obj.reference_data),
            metric_thresholds=ModelPerformanceMetricThreshold._from_rest_object(obj.metric_threshold),
            data_segment=DataSegment._from_rest_object(obj.data_segment) if obj.data_segment else None,
            alert_enabled=(
                False
                if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
                else MonitoringNotificationMode.ENABLED
            ),
        )


@experimental
class Connection(RestTranslatableMixin):
    """Monitoring Connection

    :param environment_variables: A dictionary of environment variables to set for the workspace.
    :paramtype environment_variables: Optional[dict[str, str]]
    :param secret_config: A dictionary of secrets to set for the workspace.
    :paramtype secret_config: Optional[dict[str, str]]
    """

    def __init__(
        self,
        *,
        environment_variables: Optional[Dict[str, str]] = None,
        secret_config: Optional[Dict[str, str]] = None,
    ):
        self.environment_variables = environment_variables
        self.secret_config = secret_config

    def _to_rest_object(self) -> RestMonitoringWorkspaceConnection:
        return RestMonitoringWorkspaceConnection(
            environment_variables=self.environment_variables,
            secrets=self.secret_config,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringWorkspaceConnection) -> "Connection":
        return cls(
            environment_variables=obj.environment_variables,
            secret_config=obj.secrets,
        )


@experimental
class CustomMonitoringSignal(RestTranslatableMixin):
    """Custom monitoring signal.

    :ivar type: The type of the signal. Set to "custom" for this class.
    :vartype type: str
    :keyword input_data: A dictionary of input datasets for monitoring.
        Each key is the component input port name, and its value is the data asset.
    :paramtype input_data: Optional[dict[str, ~azure.ai.ml.entities.ReferenceData]]
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :paramtype metric_thresholds: List[~azure.ai.ml.entities.CustomMonitoringMetricThreshold]
    :keyword inputs:
    :paramtype inputs: Optional[dict[str, ~azure.ai.ml.entities.Input]]
    :keyword component_id: The ARM (Azure Resource Manager) ID of the component resource used to
        calculate the custom metrics.
    :paramtype component_id: str
    :keyword connection: Specify connection with environment variables and secret configs.
    :paramtype connection: Optional[~azure.ai.ml.entities.WorkspaceConnection]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    :keyword properties: A dictionary of custom properties for the signal.
    :paramtype properties: Optional[dict[str, str]]
    """

    def __init__(
        self,
        *,
        inputs: Optional[Dict[str, Input]] = None,
        metric_thresholds: List[CustomMonitoringMetricThreshold],
        component_id: str,
        connection: Optional[Connection] = None,
        input_data: Optional[Dict[str, ReferenceData]] = None,
        alert_enabled: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ):
        self.type = MonitorSignalType.CUSTOM
        self.inputs = inputs
        self.metric_thresholds = metric_thresholds
        self.component_id = component_id
        self.alert_enabled = alert_enabled
        self.input_data = input_data
        self.properties = properties
        self.connection = connection

    def _to_rest_object(self, **kwargs: Any) -> RestCustomMonitoringSignal:  # pylint:disable=unused-argument
        if self.connection is None:
            self.connection = Connection()
        return RestCustomMonitoringSignal(
            component_id=self.component_id,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            inputs=to_rest_dataset_literal_inputs(self.inputs, job_type=None) if self.inputs else None,
            input_assets=(
                {asset_name: asset_value._to_rest_object() for asset_name, asset_value in self.input_data.items()}
                if self.input_data
                else None
            ),
            workspace_connection=self.connection._to_rest_object(),
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            properties=self.properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestCustomMonitoringSignal) -> "CustomMonitoringSignal":
        return cls(
            inputs=from_rest_inputs_to_dataset_literal(obj.inputs) if obj.inputs else None,
            input_data={key: ReferenceData._from_rest_object(data) for key, data in obj.input_assets.items()},
            metric_thresholds=[
                CustomMonitoringMetricThreshold._from_rest_object(metric) for metric in obj.metric_thresholds
            ],
            component_id=obj.component_id,
            alert_enabled=(
                False
                if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
                else MonitoringNotificationMode.ENABLED
            ),
            properties=obj.properties,
            connection=Connection._from_rest_object(obj.workspace_connection),
        )


@experimental
class LlmData(RestTranslatableMixin):
    """LLM Request Response Data

    :param input_data: Input data used by the monitor.
    :paramtype input_data: ~azure.ai.ml.entities.Input
    :param data_column_names: The names of columns in the input data.
    :paramtype data_column_names: Dict[str, str]
    :param data_window: The number of days or a time frame that a singal monitor looks back over the target.
    :type data_window_size: BaselineDataRange
    """

    def __init__(
        self,
        *,
        input_data: Input,
        data_column_names: Optional[Dict[str, str]] = None,
        data_window: Optional[BaselineDataRange] = None,
    ):
        self.input_data = input_data
        self.data_column_names = data_column_names
        self.data_window = data_window

    def _to_rest_object(self, **kwargs: Any) -> RestMonitoringInputData:
        if self.data_window is None:
            self.data_window = BaselineDataRange(
                lookback_window_size=kwargs.get("default"),
            )
        return TrailingInputData(
            target_columns=self.data_column_names,
            job_type=self.input_data.type,
            uri=self.input_data.path,
            window_size=self.data_window.lookback_window_size,
            window_offset=(
                self.data_window.lookback_window_offset
                if self.data_window.lookback_window_offset is not None
                else "P0D"
            ),
        )._to_rest_object()

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "LlmData":
        data_window = BaselineDataRange(
            lookback_window_size=isodate.duration_isoformat(obj.window_size),
            lookback_window_offset=isodate.duration_isoformat(obj.window_offset),
        )
        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_column_names=obj.columns,
            data_window=data_window,
        )


@experimental
class GenerationSafetyQualitySignal(RestTranslatableMixin):
    """Generation Safety Quality monitoring signal.

    :ivar type: The type of the signal. Set to "generationsafetyquality" for this class.
    :vartype type: str
    :keyword production_data: A list of input datasets for monitoring.
    :paramtype input_datasets: Optional[dict[str, ~azure.ai.ml.entities.LlmData]]
    :keyword metric_thresholds: Metrics to calculate and their associated thresholds.
    :paramtype metric_thresholds: ~azure.ai.ml.entities.GenerationSafetyQualityMonitoringMetricThreshold
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    :keyword connection_id: Gets or sets the connection ID used to connect to the
        content generation endpoint.
    :paramtype connection_id: str
    :keyword properties: The properties of the signal
    :paramtype properties: Dict[str, str]
    :keyword sampling_rate: The sample rate of the target data, should be greater
        than 0 and at most 1.
    :paramtype sampling_rate: float
    """

    def __init__(
        self,
        *,
        production_data: Optional[List[LlmData]] = None,
        connection_id: Optional[str] = None,
        metric_thresholds: GenerationSafetyQualityMonitoringMetricThreshold,
        alert_enabled: bool = False,
        properties: Optional[Dict[str, str]] = None,
        sampling_rate: Optional[float] = None,
    ):
        self.type = MonitorSignalType.GENERATION_SAFETY_QUALITY
        self.production_data = production_data
        self.connection_id = connection_id
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled
        self.properties = properties
        self.sampling_rate = sampling_rate

    def _to_rest_object(self, **kwargs: Any) -> RestGenerationSafetyQualityMonitoringSignal:
        data_window_size = kwargs.get("default_data_window_size")
        return RestGenerationSafetyQualityMonitoringSignal(
            production_data=(
                [data._to_rest_object(default=data_window_size) for data in self.production_data]
                if self.production_data is not None
                else None
            ),
            workspace_connection_id=self.connection_id,
            metric_thresholds=self.metric_thresholds._to_rest_object(),
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            properties=self.properties,
            sampling_rate=self.sampling_rate,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestGenerationSafetyQualityMonitoringSignal) -> "GenerationSafetyQualitySignal":
        return cls(
            production_data=[LlmData._from_rest_object(data) for data in obj.production_data],
            connection_id=obj.workspace_connection_id,
            metric_thresholds=GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object(obj.metric_thresholds),
            alert_enabled=(
                False
                if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
                else MonitoringNotificationMode.ENABLED
            ),
            properties=obj.properties,
            sampling_rate=obj.sampling_rate,
        )


@experimental
class GenerationTokenStatisticsSignal(RestTranslatableMixin):
    """Generation token statistics signal definition.

    :ivar type: The type of the signal. Set to "generationtokenstatisticssignal" for this class.
    :vartype type: str
    :keyword production_data: input dataset for monitoring.
    :paramtype input_dataset: Optional[~azure.ai.ml.entities.LlmData]
    :keyword metric_thresholds: Metrics to calculate and their associated thresholds. Defaults to App Traces
    :paramtype metric_thresholds: Optional[~azure.ai.ml.entities.GenerationTokenStatisticsMonitorMetricThreshold]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    :keyword properties: The properties of the signal
    :paramtype properties: Optional[Dict[str, str]]
    :keyword sampling_rate: The sample rate of the target data, should be greater
        than 0 and at most 1.
    :paramtype sampling_rate: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_genAI_monitors_configuration.py
                :start-after: [START default_monitoring]
                :end-before: [END default_monitoring]
                :language: python
                :dedent: 8
                :caption: Set Token Statistics Monitor.
    """

    def __init__(
        self,
        *,
        production_data: Optional[LlmData] = None,
        metric_thresholds: Optional[GenerationTokenStatisticsMonitorMetricThreshold] = None,
        alert_enabled: bool = False,
        properties: Optional[Dict[str, str]] = None,
        sampling_rate: Optional[float] = None,
    ):
        self.type = MonitorSignalType.GENERATION_TOKEN_STATISTICS
        self.production_data = production_data
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled
        self.properties = properties
        self.sampling_rate = sampling_rate

    def _to_rest_object(self, **kwargs: Any) -> RestGenerationTokenStatisticsSignal:
        data_window_size = kwargs.get("default_data_window_size")
        return RestGenerationTokenStatisticsSignal(
            production_data=(
                self.production_data._to_rest_object(default=data_window_size)
                if self.production_data is not None
                else None
            ),
            metric_thresholds=(
                self.metric_thresholds._to_rest_object()
                if self.metric_thresholds
                else GenerationTokenStatisticsMonitorMetricThreshold._get_default_thresholds()._to_rest_object()
            ),  # pylint: disable=line-too-long
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            properties=self.properties,
            sampling_rate=self.sampling_rate if self.sampling_rate else 0.1,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestGenerationTokenStatisticsSignal) -> "GenerationTokenStatisticsSignal":
        return cls(
            production_data=LlmData._from_rest_object(obj.production_data),
            metric_thresholds=GenerationTokenStatisticsMonitorMetricThreshold._from_rest_object(obj.metric_thresholds),
            alert_enabled=(
                False
                if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
                else MonitoringNotificationMode.ENABLED
            ),
            properties=obj.properties,
            sampling_rate=obj.sampling_rate,
        )

    @classmethod
    def _get_default_token_statistics_signal(cls) -> "GenerationTokenStatisticsSignal":
        return cls(
            metric_thresholds=GenerationTokenStatisticsMonitorMetricThreshold._get_default_thresholds(),
            sampling_rate=0.1,
        )


def _from_rest_features(
    obj: RestMonitoringFeatureFilterBase,
) -> Optional[Union[List[str], MonitorFeatureFilter, Literal["all_features"]]]:
    if isinstance(obj, RestTopNFeaturesByAttribution):
        return MonitorFeatureFilter(top_n_feature_importance=obj.top)
    if isinstance(obj, RestFeatureSubset):
        _restFeatureSubset: List[str] = obj.features
        return _restFeatureSubset
    if isinstance(obj, RestAllFeatures):
        _restAllFeatures: Literal["all_features"] = ALL_FEATURES  # type: ignore[assignment]
        return _restAllFeatures

    return None


def _to_rest_features(
    features: Union[List[str], MonitorFeatureFilter, Literal["all_features"]]
) -> RestMonitoringFeatureFilterBase:
    rest_features = None
    if isinstance(features, list):
        rest_features = RestFeatureSubset(features=features)
    elif isinstance(features, MonitorFeatureFilter):
        rest_features = features._to_rest_object()
    elif isinstance(features, str) and features == ALL_FEATURES:
        rest_features = RestAllFeatures()
    return rest_features


def _to_rest_num_cat_metrics(numerical_metrics: Any, categorical_metrics: Any) -> List:
    metrics = []
    if numerical_metrics is not None:
        metrics.append(numerical_metrics._to_rest_object())

    if categorical_metrics is not None:
        metrics.append(categorical_metrics._to_rest_object())

    return metrics


def _to_rest_data_quality_metrics(numerical_metrics: Any, categorical_metrics: Any) -> List:
    metric_thresholds: List = []
    if numerical_metrics is not None:
        metric_thresholds = metric_thresholds + numerical_metrics._to_rest_object()

    if categorical_metrics is not None:
        metric_thresholds = metric_thresholds + categorical_metrics._to_rest_object()

    return metric_thresholds
