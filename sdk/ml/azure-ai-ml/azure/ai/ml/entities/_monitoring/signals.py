# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Optional, Union
import datetime
import isodate

from typing_extensions import Literal

from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitoringInputDataBase as RestMonitoringInputData,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitoringSignalBase as RestMonitoringSignalBase,
    DataDriftMonitoringSignal as RestMonitoringDataDriftSignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    DataQualityMonitoringSignal as RestMonitoringDataQualitySignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    FeatureAttributionDriftMonitoringSignal as RestFeatureAttributionDriftMonitoringSignal,
    ModelPerformanceSignal as RestModelPerformanceSignal,
    CustomMonitoringSignal as RestCustomMonitoringSignal,
    MonitoringDataSegment as RestMonitoringDataSegment,
    MonitoringFeatureFilterBase as RestMonitoringFeatureFilterBase,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringNotificationMode
from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringSignalType
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    PredictionDriftMonitoringSignal as RestPredictionDriftMonitoringSignal,
)
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    TopNFeaturesByAttribution as RestTopNFeaturesByAttribution,
    AllFeatures as RestAllFeatures,
    FeatureSubset as RestFeatureSubset,
    MonitoringWorkspaceConnection as RestMonitoringWorkspaceConnection,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._monitoring import (
    MonitorSignalType,
    ALL_FEATURES,
    MonitorModelType,
    MonitorDatasetContext,
    MonitorFeatureDataType,
)
from azure.ai.ml.entities._monitoring.input_data import (
    FixedInputData,
    TrailingInputData,
    StaticInputData,
)
from azure.ai.ml.entities._monitoring.thresholds import (
    DataDriftMetricThreshold,
    DataQualityMetricThreshold,
    PredictionDriftMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    MetricThreshold,
    ModelPerformanceMetricThreshold,
    CustomMonitoringMetricThreshold,
)


@experimental
class DataSegment(RestTranslatableMixin):
    """Data segment for monitoring.

    :keyword feature_name: The feature to segment the data on.
    :paramtype feature_name: str
    :keyword feature_values: A list of values for the given segmented feature to filter.
    :paramtype feature_values: list[str]
    """

    def __init__(
        self,
        *,
        feature_name: str = None,
        feature_values: List[str] = None,
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


@experimental
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


@experimental
class BaselineDataRange:
    def __init__(
        self,
        *,
        window_start: str = None,
        window_end: str = None,
        trailing_window_size: str = None,
        trailing_window_offset: str = None,
    ):
        self.window_start = window_start
        self.window_end = window_end
        self.trailing_window_size = trailing_window_size
        self.trailing_window_offset = trailing_window_offset


@experimental
class ProductionData(RestTranslatableMixin):
    """Production Data
    :param input_data: The data for which drift will be calculated
    :type Input: ~azure.ai.ml.entities._input_outputs
    :param data_context: The data to calculate drift against
    :type MonitorDatasetContext: ~azure.ai.ml.constants._monitoring
    :param pre_processing_component :
    :type pre_processing_component: string
    :param data_window_size:
    :type data_window_size: string
    """

    def __init__(
        self,
        *,
        input_data: Input,
        data_context: MonitorDatasetContext = None,
        pre_processing_component: str = None,
        data_window_size: str = None,
    ):
        self.input_data = input_data
        self.data_context = data_context
        self.pre_processing_component = pre_processing_component
        self.data_window_size = data_window_size

    def _to_rest_object(self, **kwargs) -> RestMonitoringInputData:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.data_window_size is None:
            self.data_window_size = default_data_window_size
        uri = self.input_data.path
        job_type = self.input_data.type
        monitoring_input_data = TrailingInputData(
            data_context=self.data_context,
            target_columns=None,
            job_type=job_type,
            uri=uri,
            pre_processing_component_id=self.pre_processing_component,
            window_size=self.data_window_size,
            window_offset=self.data_window_size,
        )
        return monitoring_input_data._to_rest_object()

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "ProductionData":
        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            pre_processing_component=obj.preprocessing_component_id,
            data_window_size=isodate.duration_isoformat(obj.window_size),
        )


@experimental
class ReferenceData(RestTranslatableMixin):
    """Reference Data
    :param input_data: The data for which drift will be calculated
    :type Input: ~azure.ai.ml.entities._input_outputs
    :param data_context: The data to calculate drift against
    :type MonitorDatasetContext: ~azure.ai.ml.constants._monitoring
    :param pre_processing_component :
    :type pre_processing_component: string
    :param target_column_name:
    :type target_column_name: string
    :param data_window:
    :type data_window_size: BaselineDataRange
    """

    def __init__(
        self,
        *,
        input_data: Input,
        data_context: MonitorDatasetContext = None,
        pre_processing_component: Optional[str] = None,
        target_column_name: Optional[str] = None,
        data_window: Optional[BaselineDataRange] = None,
    ):
        self.input_data = input_data
        self.data_context = data_context
        self.pre_processing_component = pre_processing_component
        self.target_column_name = target_column_name
        self.data_window = data_window

    def _to_rest_object(self) -> RestMonitoringInputData:
        if self.data_window is not None:
            if self.data_window.trailing_window_size is not None:
                return TrailingInputData(
                    data_context=self.data_context,
                    target_columns={"target_column": self.target_column_name}
                    if self.target_column_name is not None
                    else None,
                    job_type=self.input_data.type,
                    uri=self.input_data.path,
                    pre_processing_component_id=self.pre_processing_component,
                    window_size=self.data_window.trailing_window_size,
                    window_offset=self.data_window.trailing_window_offset
                    if self.data_window.trailing_window_offset is not None
                    else self.data_window.trailing_window_size,
                )._to_rest_object()
            if self.data_window.window_start is not None and self.data_window.window_end is not None:
                return StaticInputData(
                    data_context=self.data_context,
                    target_columns={"target_column": self.target_column_name}
                    if self.target_column_name is not None
                    else None,
                    job_type=self.input_data.type,
                    uri=self.input_data.path,
                    pre_processing_component_id=self.pre_processing_component,
                    window_start=self.data_window.window_start,
                    window_end=self.data_window.window_end,
                )._to_rest_object()

        return FixedInputData(
            data_context=self.data_context,
            target_columns={"target_column": self.target_column_name} if self.target_column_name is not None else None,
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
                trailing_window_size=isodate.duration_isoformat(obj.window_size),
                trailing_window_offset=isodate.duration_isoformat(obj.window_offset),
            )

        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            pre_processing_component=obj.preprocessing_component_id if obj.input_data_type != "Fixed" else None,
            data_window=data_window,
            target_column_name=obj.columns["target_column"] if obj.columns is not None else None,
        )


@experimental
class MonitoringSignal(RestTranslatableMixin):
    """
    Base class for monitoring signals.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword target_dataset: The target dataset definition for monitor input.
    :paramtype target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The baseline dataset definition for monitor input.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: The metric thresholds for the signal.
    :paramtype metric_thresholds: Union[
        ~azure.ai.ml.entities.DataDriftMetricThreshold,
        ~azure.ai.ml.entities.DataQualityMetricThreshold,
        ~azure.ai.ml.entities.PredictionDriftMetricThreshold,
        ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold,
        ~azure.ai.ml.entities.CustomMonitoringMetricThreshold,
        list[Union[
            ~azure.ai.ml.entities.DataDriftMetricThreshold,
            ~azure.ai.ml.entities.DataQualityMetricThreshold,
            ~azure.ai.ml.entities.PredictionDriftMetricThreshold,
            ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold,
            ~azure.ai.ml.entities.CustomMonitoringMetricThreshold
        ]]]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        metric_thresholds: Union[MetricThreshold, List[MetricThreshold]],
        properties: Optional[Dict[str, str]] = None,
        alert_enabled: bool = True,
    ):
        self.production_data = production_data
        self.reference_data = reference_data
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled
        self.properties = properties

    @classmethod
    def _from_rest_object(  # pylint: disable=too-many-return-statements
        cls, obj: RestMonitoringSignalBase
    ) -> Optional["MonitoringSignal"]:
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

        return None


@experimental
class DataSignal(MonitoringSignal):
    """Base class for data signals.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword target_dataset: The target dataset definition for monitor input.
    :paramtype target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The baseline dataset definition for monitor input.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword features: The features to include in the signal.
    :paramtype features: Union[list[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal[ALL_FEATURES]]
    :keyword metric_thresholds: The metric thresholds for the signal.
    :paramtype metric_thresholds: list[Union[
        ~azure.ai.ml.entities.DataDriftMetricThreshold,
        ~azure.ai.ml.entities.DataQualityMetricThreshold,
        ~azure.ai.ml.entities.PredictionDriftMetricThreshold,
        ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold,
        ~azure.ai.ml.entities.CustomMonitoringMetricThreshold
    ]]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        features: Optional[Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]]] = None,
        feature_type_override: Optional[Dict[str, Union[str, MonitorFeatureDataType]]] = None,
        metric_thresholds: List[MetricThreshold],
        alert_enabled: bool = True,
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


@experimental
class DataDriftSignal(DataSignal):
    """Data drift signal.

    :ivar type: The type of the signal
    :vartype type: str
    :param production_data: The data for which drift will be calculated
    :type production_data: ~azure.ai.ml.entities.ProductionData
    :param reference_data: The data to calculate drift against
    :type reference_data: ~azure.ai.ml.entities.ReferenceData
    :param metric_thresholds :A list of metrics to calculate and their
        associated thresholds
    :type metric_thresholds: List[~azure.ai.ml.entities.DataDriftMetricThreshold]
    :param alert_enabled: The current notification mode for this signal
    :type alert_enabled: bool
    :keyword data_segment: The data segment used for scoping on a subset of the data population.
    :paramtype data_segment: ~azure.ai.ml.entities.DataSegment
    :keyword features: The feature filter identifying which feature(s) to
        calculate drift over.
    :paramtype features: Union[list[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal['all_features']]
    """

    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        features: Optional[Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]]] = None,
        feature_type_override: Optional[Dict[str, Union[str, MonitorFeatureDataType]]] = None,
        metric_thresholds: DataDriftMetricThreshold = None,
        alert_enabled: bool = True,
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

    def _to_rest_object(self, **kwargs) -> RestMonitoringDataDriftSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.production_data.data_window_size is None:
            self.production_data.data_window_size = default_data_window_size
        rest_features = _to_rest_features(self.features) if self.features else None
        return RestMonitoringDataDriftSignal(
            production_data=self.production_data._to_rest_object(),
            reference_data=self.reference_data._to_rest_object(),
            features=rest_features,
            feature_data_type_override=self.feature_type_override,
            metric_thresholds=self.metric_thresholds._to_rest_object(),
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
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
            data_segment=DataSegment._from_rest_object(obj.data_segment) if obj.data_segment else None,
            properties=obj.properties,
        )

    @classmethod
    def _get_default_data_drift_signal(cls) -> "DataDriftSignal":
        return cls(
            features=ALL_FEATURES,
            metric_thresholds=DataDriftMetricThreshold._get_default_thresholds(),
        )


@experimental
class PredictionDriftSignal(MonitoringSignal):
    """Prediction drift signal.

    :keyword baseline_dataset: The dataset to calculate drift against.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword target_dataset: The dataset for which drift will be calculated.
    :paramtype target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword metric_thresholds: A list of metrics to calculate and their associated thresholds
    :paramtype metric_thresholds: list[~azure.ai.ml.entities.PredictionDriftMetricThreshold]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        metric_thresholds: PredictionDriftMetricThreshold,
        alert_enabled: bool = True,
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

    def _to_rest_object(self, **kwargs) -> RestPredictionDriftMonitoringSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.production_data.data_window_size is None:
            self.production_data.data_window_size = default_data_window_size
        return RestPredictionDriftMonitoringSignal(
            production_data=self.production_data._to_rest_object(),
            reference_data=self.reference_data._to_rest_object(),
            metric_thresholds=self.metric_thresholds._to_rest_object(),
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
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
            properties=obj.properties,
        )

    @classmethod
    def _get_default_prediction_drift_signal(cls) -> "PredictionDriftSignal":
        return cls(
            metric_thresholds=PredictionDriftMetricThreshold._get_default_thresholds(),
        )


@experimental
class DataQualitySignal(DataSignal):
    """Data quality signal


    :keyword target_dataset: The data for which quality will be calculated.
    :paramtype target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The data to calculate quality against.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :paramtype metric_thresholds: list[~azure.ai.ml.entities.DataQualityMetricThreshold]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    :keyword features: The feature filter identifying which feature(s) to
        calculate quality over.
    :paramtype features: Union[list[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal['all_features']]
    """

    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        features: Optional[Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]]] = None,
        feature_type_override: Optional[Dict[str, Union[str, MonitorFeatureDataType]]] = None,
        metric_thresholds: [DataQualityMetricThreshold] = None,
        alert_enabled: bool = True,
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

    def _to_rest_object(self, **kwargs) -> RestMonitoringDataQualitySignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.production_data.data_window_size is None:
            self.production_data.data_window_size = default_data_window_size
        rest_features = _to_rest_features(self.features) if self.features else None
        rest_metrics = _to_rest_data_quality_metrics(
            self.metric_thresholds.numerical, self.metric_thresholds.categorical
        )
        return RestMonitoringDataQualitySignal(
            production_data=self.production_data._to_rest_object(),
            reference_data=self.reference_data._to_rest_object(),
            features=rest_features,
            feature_data_type_override=self.feature_type_override,
            metric_thresholds=rest_metrics,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            properties=self.properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataQualitySignal) -> "DataDriftSignal":
        return cls(
            production_data=ProductionData._from_rest_object(obj.production_data),
            reference_data=ReferenceData._from_rest_object(obj.reference_data),
            features=_from_rest_features(obj.features),
            feature_type_override=obj.feature_data_type_override,
            metric_thresholds=DataQualityMetricThreshold._from_rest_object(obj.metric_thresholds),
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
            properties=obj.properties,
        )

    @classmethod
    def _get_default_data_quality_signal(
        cls,
    ) -> "DataQualitySignal":
        return cls(
            features=ALL_FEATURES,
            metric_thresholds=DataQualityMetricThreshold._get_default_thresholds(),
        )


@experimental
class ModelSignal(MonitoringSignal):
    """Base class for model signals.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword target_dataset: The data for which quality will be calculated.
    :paramtype target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The data to calculate quality against.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :paramtype metric_thresholds: list[~azure.ai.ml.entities.MetricThreshold]
    :keyword model_type: The type of model to monitor.
    :paramtype model_type: ~azure.ai.ml.constants.MonitorModelType
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: ProductionData,
        reference_data: ReferenceData,
        metric_thresholds: List[MetricThreshold],
        model_type: MonitorModelType,
        alert_enabled: bool = True,
    ) -> None:
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
        )
        self.model_type = model_type


@experimental
class FADProductionData(RestTranslatableMixin):
    def __init__(
        self,
        *,
        input_data: Input,
        data_context: MonitorDatasetContext = None,
        data_column_names: Dict = None,
        pre_processing_component: str = None,
        data_window_size: str = None,
    ):
        self.input_data = input_data
        self.data_context = data_context
        self.data_column_names = data_column_names
        self.pre_processing_component = pre_processing_component
        self.data_window_size = data_window_size

    def _to_rest_object(self, **kwargs) -> RestMonitoringInputData:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.data_window_size is None:
            self.data_window_size = default_data_window_size
        uri = self.input_data.path
        job_type = self.input_data.type
        monitoring_input_data = TrailingInputData(
            data_context=self.data_context,
            target_columns=self.data_column_names,
            job_type=job_type,
            uri=uri,
            pre_processing_component_id=self.pre_processing_component,
            window_size=self.data_window_size,
            window_offset=self.data_window_size,
        )
        return monitoring_input_data._to_rest_object()

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "FADProductionData":
        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            data_column_names=obj.columns,
            pre_processing_component=obj.preprocessing_component_id,
            data_window_size=obj.window_size,
        )


@experimental
class FeatureAttributionDriftSignal(RestTranslatableMixin):
    """Feature attribution drift signal

    :keyword target_dataset: The data for which drift will be calculated.
    :paramtype target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The data to calculate drift against.
    :paramtype baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :paramtype metric_thresholds: ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold
    :keyword model_type: The model type.
    :paramtype model_type: ~azure.ai.ml.constants.MonitorModelType
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: List[FADProductionData],
        reference_data: ReferenceData,
        metric_thresholds: FeatureAttributionDriftMetricThreshold,
        alert_enabled: bool = True,
        properties: Optional[Dict[str, str]] = None,
    ):
        self.production_data = production_data
        self.reference_data = reference_data
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled
        self.properties = properties
        self.type = MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT

    def _to_rest_object(
        self, **kwargs
    ) -> RestFeatureAttributionDriftMonitoringSignal:  # pylint: disable=unused-argument
        return RestFeatureAttributionDriftMonitoringSignal(
            production_data=[data._to_rest_object() for data in self.production_data],
            reference_data=self.reference_data._to_rest_object(),
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
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
            properties=obj.properties,
        )


@experimental
class ModelPerformanceSignal(ModelSignal):
    """Model performance signal.

    :keyword target_dataset: The data for which performance will be calculated.
    :paramtype target_dataset: ~azure.ai.ml.entities.TargetDataset
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
        model_type: MonitorModelType,
        data_segment: DataSegment = None,
        alert_enabled: bool = True,
    ) -> None:
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            model_type=model_type,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.MODEL_PERFORMANCE
        self.data_segment = data_segment

    def _to_rest_object(self, **kwargs) -> RestModelPerformanceSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.production_data.data_window_size is None:
            self.production_data.data_window_size = default_data_window_size
        return RestModelPerformanceSignal(
            production_data=self.production_data._to_rest_object(),
            reference_data=self.reference_data._to_rest_object(),
            metric_threshold=self.metric_thresholds._to_rest_object(model_type=self.model_type),
            data_segment=self.data_segment._to_rest_object() if self.data_segment else None,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestModelPerformanceSignal) -> "ModelPerformanceSignal":
        return cls(
            production_data=ProductionData._from_rest_object(obj.production_data),
            reference_data=ReferenceData._from_rest_object(obj.reference_data),
            metric_thresholds=ModelPerformanceMetricThreshold._from_rest_object(obj.metric_threshold),
            model_type=obj.metric_threshold.model_type.lower(),
            data_segment=DataSegment._from_rest_object(obj.data_segment) if obj.data_segment else None,
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
        )


@experimental
class WorkspaceConnection(RestTranslatableMixin):
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
    def _from_rest_object(cls, obj: RestMonitoringWorkspaceConnection) -> "WorkspaceConnection":
        return cls(
            environment_variables=obj.environment_variables,
            secret_config=obj.secrets,
        )


@experimental
class CustomMonitoringSignal(RestTranslatableMixin):
    """Custom monitoring signal.

    :keyword input_datasets: A dictionary of input datasets for monitoring.
        Each key is the component input port name, and its value is the data asset.
    :paramtype input_datasets: Optional[dict[str, ~azure.ai.ml.entities.MonitorInputData]]
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :paramtype metric_thresholds: list[~azure.ai.ml.entities.CustomMonitoringMetricThreshold]
    :keyword component_id: The ARM (Azure Resource Manager) ID of the component resource used to
        calculate the custom metrics.
    :paramtype component_id: str
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :paramtype alert_enabled: bool
    :keyword data_window_size: The number of days a single monitor looks back
        over the target
    :paramtype data_window_size: Optional[int]
    """

    def __init__(
        self,
        *,
        input_literals: Optional[Dict[str, Input]] = None,
        metric_thresholds: List[CustomMonitoringMetricThreshold],
        component_id: str,
        workspace_connection: Optional[WorkspaceConnection] = None,
        input_datasets: Optional[Dict[str, ProductionData]] = None,
        alert_enabled: bool = True,
        properties: Optional[Dict[str, str]] = None,
    ):
        self.type = MonitorSignalType.CUSTOM
        self.input_literals = input_literals
        self.metric_thresholds = metric_thresholds
        self.component_id = component_id
        self.alert_enabled = alert_enabled
        self.input_datasets = input_datasets
        self.properties = properties
        self.workspace_connection = workspace_connection

    def _to_rest_object(self, **kwargs) -> RestCustomMonitoringSignal:  # pylint:disable=unused-argument
        if self.workspace_connection is None:
            self.workspace_connection = WorkspaceConnection()
        return RestCustomMonitoringSignal(
            component_id=self.component_id,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            inputs={
                input_name: input_value._to_rest_object() for input_name, input_value in self.input_literals.items()
            }
            if self.input_literals
            else None,
            input_assets={
                asset_name: asset_value._to_rest_object() for asset_name, asset_value in self.input_datasets.items()
            }
            if self.input_datasets
            else None,
            workspace_connection=self.workspace_connection._to_rest_object(),
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            properties=self.properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestCustomMonitoringSignal) -> "CustomMonitoringSignal":
        return cls(
            input_literals={
                input_name: Input._from_rest_object(input_value) for input_name, input_value in obj.inputs.items()
            }
            if obj.inputs
            else None,
            input_datasets={
                input_name: ProductionData._from_rest_object(input_value)
                for input_name, input_value in obj.input_assets.items()
            },
            metric_thresholds=[
                CustomMonitoringMetricThreshold._from_rest_object(metric) for metric in obj.metric_thresholds
            ],
            component_id=obj.component_id,
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
            properties=obj.properties,
            workspace_connection=WorkspaceConnection._from_rest_object(obj.workspace_connection),
        )


def _from_rest_features(
    obj: RestMonitoringFeatureFilterBase,
) -> Optional[Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]]]:
    if isinstance(obj, RestTopNFeaturesByAttribution):
        return MonitorFeatureFilter(top_n_feature_importance=obj.top)
    if isinstance(obj, RestFeatureSubset):
        return obj.features
    if isinstance(obj, RestAllFeatures):
        return ALL_FEATURES

    return None


def _to_rest_features(
    features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]]
) -> RestMonitoringFeatureFilterBase:
    rest_features = None
    if isinstance(features, list):
        rest_features = RestFeatureSubset(features=features)
    elif isinstance(features, MonitorFeatureFilter):
        rest_features = features._to_rest_object()
    elif isinstance(features, str) and features == ALL_FEATURES:
        rest_features = RestAllFeatures()
    return rest_features


def _to_rest_num_cat_metrics(numerical_metrics, categorical_metrics):
    metrics = []
    if numerical_metrics is not None:
        metrics.append(numerical_metrics._to_rest_object())

    if categorical_metrics is not None:
        metrics.append(categorical_metrics._to_rest_object())

    return metrics


def _to_rest_data_quality_metrics(numerical_metrics, categorical_metrics):
    metric_thresholds = []
    if numerical_metrics is not None:
        metric_thresholds = metric_thresholds + numerical_metrics._to_rest_object()

    if categorical_metrics is not None:
        metric_thresholds = metric_thresholds + categorical_metrics._to_rest_object()

    return metric_thresholds
