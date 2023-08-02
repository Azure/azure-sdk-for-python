# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Optional, Union

from typing_extensions import Literal

from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitoringSignalBase as RestMonitoringSignalBase,
    DataDriftMonitoringSignal as RestMonitoringDataDriftSignal,
    DataQualityMonitoringSignal as RestMonitoringDataQualitySignal,
    PredictionDriftMonitoringSignal as RestPredictionDriftMonitoringSignal,
    FeatureAttributionDriftMonitoringSignal as RestFeatureAttributionDriftMonitoringSignal,
    ModelPerformanceSignal as RestModelPerformanceSignal,
    CustomMonitoringSignal as RestCustomMonitoringSignal,
    MonitoringDataSegment as RestMonitoringDataSegment,
    MonitoringFeatureFilterBase as RestMonitoringFeatureFilterBase,
    TopNFeaturesByAttribution as RestTopNFeaturesByAttribution,
    AllFeatures as RestAllFeatures,
    FeatureSubset as RestFeatureSubset,
    MonitoringNotificationMode,
    MonitoringSignalType,
    MonitoringWorkspaceConnection as RestMonitoringWorkspaceConnection,
    MonitoringInputDataBase,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import to_iso_duration_format_days, from_iso_duration_format_days
from azure.ai.ml.constants._monitoring import MonitorSignalType, ALL_FEATURES, MonitorModelType, MonitorDatasetContext
from azure.ai.ml.entities._monitoring.input_data import (
    RestMonitoringInputData,
    MonitorInputData,
    FixedInputData,
    TrailingInputData,
    StaticInputData,
)
from azure.ai.ml.entities._monitoring.thresholds import (
    MetricThreshold,
    DataDriftMetricThreshold,
    DataQualityMetricThreshold,
    DataQualityMetricsCategorical,
    PredictionDriftMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    ModelPerformanceMetricThreshold,
    CustomMonitoringMetricThreshold,
    NumericalDataDriftMetrics,
    CategoricalDataDriftMetrics,
)


@experimental
class DataSegment(RestTranslatableMixin):
    """Monitor data segment

    :param feature_name: The feature to segment the data on
    :type feature_name: str
    :param feature_values: A list of values the given segmented feature to filter on
    :param feature_values: List[str]
    """

    def __init__(
        self,
        *,
        feature_name: str = None,
        feature_values: List[str] = None,
    ):
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

    :param top_n_feature_importance: The number of top features to include
    :type top_n_feature_importance: int
    """

    def __init__(
        self,
        *,
        top_n_feature_importance: int = 10,
    ):
        self.top_n_feature_importance = top_n_feature_importance

    def _to_rest_object(self) -> RestTopNFeaturesByAttribution:
        return RestTopNFeaturesByAttribution(
            top=self.top_n_feature_importance,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestTopNFeaturesByAttribution) -> "MonitorFeatureFilter":
        return cls(top_n_feature_importance=obj.top)

class TargetDataset:
    def __init__(self, dataset: MonitorInputData, data_window_size: str = None):
        self.dataset = dataset
        self.data_window_size = data_window_size

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

class ProductionData(RestTranslatableMixin):
    """Monitor production data

    :param dataset: Production dataset definition for monitor
    :type dataset: ~azure.ai.ml.entities.MonitorInputData
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
        uri = self.input_data.path
        job_type = self.input_data.type
        monitoring_input_data = TrailingInputData(
            data_context=self.data_context,
            target_columns=None,
            job_type=job_type,
            uri=uri,
            preocessing_component_id=self.pre_processing_component,
            window_size=self.data_window_size,
            window_offset= self.data_window_size,
        )
        return (
            monitoring_input_data._to_rest_object()
        )
    
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "ProductionData":
        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            pre_processing_component=obj.pre_processing_component_id,
            data_window_size=obj.window_size,
        )

class ReferenceData(RestTranslatableMixin):
    """Monitor reference data

    """

    def __init__(
        self,
        *,
        input_data: Input,
        data_context: MonitorDatasetContext = None,
        pre_processing_component: str = None,
        target_column_name: str = None,
        data_window: BaselineDataRange = None,
    ):
        self.input_data = input_data
        self.data_context = data_context
        self.pre_processing_component = pre_processing_component
        self.target_column_name = target_column_name
        self.data_window = data_window

    def _to_rest_object(self) -> RestMonitoringInputData:
        uri = self.input_data.path, 
        jobInputType = self.input_data.type
        if self.target_column_name:
            target_column = {"target_column_name": self.target_column_name}
        else:
            target_column = None
        if self.data_window is not None:
            if self.data_window.trailing_window_size is not None:
                return(
                    TrailingInputData(
                        input_type="Trailing",
                        data_context=self.data_context,
                        target_columns=target_column,
                        job_type=jobInputType,
                        uri=uri,
                        preocessing_component_id=self.pre_processing_component,
                        window_size=self.data_window.trailing_window_size,
                        window_offset=self.data_window.trailing_window_size,
                    )._to_rest_object()
                )
            elif self.data_window.window_start is not None and self.data_window.window_end is not None:
                return(
                    StaticInputData(
                        input_type="Static",
                        data_context=self.data_context,
                        target_columns=target_column,
                        job_type=jobInputType,
                        uri=uri,
                        preocessing_component_id=self.pre_processing_component,
                        window_start=self.data_window.window_start,
                        window_end=self.data_window.window_end,
                    )._to_rest_object()
                ) 
        return(
            FixedInputData(
                input_type="Fixed",
                data_context=self.data_context,
                target_columns=target_column,
                job_type=jobInputType,
                uri=uri,
            )._to_rest_object()
        )
        
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "ReferenceData":
        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            pre_processing_component=obj.pre_processing_component_id,
            target_column=obj.target_column,
            data_window=BaselineDataRange(
                window_start=obj.window_start,
                window_end=obj.window_end,
                trailing_window_size=obj.window_size,
                trailing_window_offset=obj.window_offset,
            ),
        )
    
@experimental
class MonitoringSignal(RestTranslatableMixin):
    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        metric_thresholds: Union[MetricThreshold, List[MetricThreshold]] = None,
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
    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        feature_type_override: Dict[str, str] = None,
        metric_thresholds: List[MetricThreshold] = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
        )
        self.features = features
        self.feature_type_override = feature_type_override


@experimental
class DataDriftSignal(DataSignal):
    """Data drift signal

    :ivar type: The type of the signal
    :vartype type: str
    :param target_dataset: The data for which drift will be calculated
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :param baseline_dataset: The data to calculate drift against
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :param metric_thresholds :A list of metrics to calculate and their
        associated thresholds
    :type metric_thresholds: List[~azure.ai.ml.entities.DataDriftMetricThreshold]
    :param alert_enabled: The current notification mode for this signal
    :type alert_enabled: bool
    :param data_segment: The data segment used for scoping on a subset of the
        data population
    :type data_segment: ~azure.ai.ml.entities.DataSegment
    :param features: The feature filter identifying which feature(s) to
        calculate drift over
    :type features: Union[List[str], ~azure.ai.ml.entities.MonitorFeatureFilter
        , Literal['all_features']]
    """

    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        feature_type_override: Dict[str, str] = None,
        metric_thresholds: DataDriftMetricThreshold = None,
        alert_enabled: bool = True,
        data_segment: DataSegment = None,
    ):
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            features=features,
            feature_type_override=feature_type_override,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.DATA_DRIFT
        self.data_segment = data_segment

    def _to_rest_object(self, **kwargs) -> RestMonitoringDataDriftSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.production_data.data_window_size is None:
            self.production_data.data_window_size = default_data_window_size
        rest_features = _to_rest_features(self.features) if self.features else None
        rest_metrics = _to_rest_num_cat_metrics(self.metric_thresholds.numerical, self.metric_thresholds.categorical)
        return RestMonitoringDataDriftSignal(
            production_data=self.production_data._to_rest_object(),
            reference_data=self.reference_data._to_rest_object(),
            features=rest_features,
            feature_data_type_override=self.feature_type_override,
            metric_thresholds=rest_metrics,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            data_segment=self.data_segment._to_rest_object() if self.data_segment else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataDriftSignal) -> "DataDriftSignal":
        return cls(
            production_data=None,
            reference_data=None,
            features=_from_rest_features(obj.features),
            metric_thresholds=_from_rest_num_cat_metrics(obj.metric_thresholds.numerical,obj.metric_thresholds.categorical),
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
            data_segment=DataSegment._from_rest_object(obj.data_segment) if obj.data_segment else None,
        )

    @classmethod
    def _get_default_data_drift_signal(cls) -> "DataDriftSignal":
        return cls(
            features=ALL_FEATURES,
            metric_thresholds=DataDriftMetricThreshold._get_default_thresholds(),
        )


@experimental
class PredictionDriftSignal(MonitoringSignal):
    """Prediction drift signal

    :ivar type: The type of the signal
    :vartype type: str
    :param target_dataset: The data for which drift will be calculated
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :param baseline_dataset: The data to calculate drift against
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :param metric_thresholds :A list of metrics to calculate and their
        associated thresholds
    :type metric_thresholds: List[~azure.ai.ml.entities.PredictionDriftMetricThreshold]
    :param alert_enabled: The current notification mode for this signal
    :type alert_enabled: bool
    """

    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        metric_thresholds: PredictionDriftMetricThreshold,
        alert_enabled: bool = True,
    ):
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.PREDICTION_DRIFT

    def _to_rest_object(self, **kwargs) -> RestPredictionDriftMonitoringSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.production_data.data_window_size is None:
            self.production_data.data_window_size = default_data_window_size
        rest_metric_thresholds = _to_rest_num_cat_metrics(self.metric_thresholds.numerical, self.metric_thresholds.categorical)
        return RestPredictionDriftMonitoringSignal(
            # hack this to a random value since the service ignores it and it's mislabled as a required property
            model_type="classification",
            production_data=self.production_data._to_rest_object(),
            reference_data=self.reference_data._to_rest_object(),
            metric_thresholds=rest_metric_thresholds,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestPredictionDriftMonitoringSignal) -> "PredictionDriftSignal":
        return cls(
            production_data=ProductionData._from_rest_object(obj.production_data),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
            metric_thresholds=_from_rest_num_cat_metrics(obj.metric_thresholds.numerical,obj.metric_thresholds.categorical),
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
        )

    @classmethod
    def _get_default_prediction_drift_signal(cls) -> "PredictionDriftSignal":
        return cls(
            metric_thresholds=PredictionDriftMetricThreshold._get_default_thresholds(),
        )


@experimental
class DataQualitySignal(DataSignal):
    """Data quality signal

    :ivar type: The type of the signal
    :vartype type: str
    :param target_dataset: The data for which quality will be calculated
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :param baseline_dataset: The data to calculate quality against
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :param metric_thresholds :A list of metrics to calculate and their
        associated thresholds
    :type metric_thresholds: List[~azure.ai.ml.entities.DataQualityMetricThreshold]
    :param alert_enabled: The current notification mode for this signal
    :type alert_enabled: bool
    :param features: The feature filter identifying which feature(s) to
        calculate quality over
    :type features: Union[List[str], ~azure.ai.ml.entities.MonitorFeatureFilter
        , Literal['all_features']]
    """

    def __init__(
        self,
        *,
        production_data: ProductionData = None,
        reference_data: ReferenceData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: DataQualityMetricThreshold,
        alert_enabled: bool = True,
    ):
        super().__init__(
            production_data=production_data,
            reference_data=reference_data,
            metric_thresholds=metric_thresholds,
            features=features,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.DATA_QUALITY

    def _to_rest_object(self, **kwargs) -> RestMonitoringDataQualitySignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        if self.production_data.data_window_size is None:
            self.production_data.data_window_size = default_data_window_size
        rest_features = _to_rest_features(self.features) if self.features else None
        rest_mertrics = _to_rest_data_quality_metrics(self.metric_thresholds.numerical, self.metric_thresholds.categorical)
        return RestMonitoringDataQualitySignal(
            production_data=self.production_data._to_rest_object(),
            reference_data=self.reference_data._to_rest_object(),
            features=rest_features,
            metric_thresholds=rest_mertrics,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataQualitySignal) -> "DataDriftSignal":
        return cls(
            target_dataset=ProductionData._from_rest_object(obj.production_data),
            reference_data=ReferenceData._from_rest_object(obj.ref),
            features=_from_rest_features(obj.features),
            metric_thresholds=[DataQualityMetricsCategorical._from_rest_object(threshold) for threshold in obj.metric_thresholds.categorical],
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
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
    def __init__(
        self,
        *,
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        metric_thresholds: List[MetricThreshold],
        model_type: MonitorModelType,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
        )
        self.model_type = model_type

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
    
    def _to_rest_object(self) -> RestMonitoringInputData:
        if self.data_window_size is None:
            self.data_window_size = "P7D"
        uri = self.input_data.path
        job_type = self.input_data.type
        monitoring_input_data = TrailingInputData(
            data_context=self.data_context,
            target_columns=self.data_column_names,
            job_type=job_type,
            uri=uri,
            preocessing_component_id=self.pre_processing_component,
            window_size=self.data_window_size,
            window_offset= self.data_window_size,
        )
        return (
            monitoring_input_data._to_rest_object()
        )
    
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "FADProductionData":
        return cls(
            input_data=Input(
                path=obj.uri,
                type=obj.job_input_type,
            ),
            data_context=obj.data_context,
            target_columns=obj.data_column_names,
            pre_processing_component=obj.pre_processing_component_id,
            data_window_size=obj.window_size,
        )

    
@experimental
class FeatureAttributionDriftSignal(RestTranslatableMixin):
    """Feature attribution drift signal

    :ivar type: The type of the signal
    :vartype type: str
    :param target_dataset: The data for which quality will be calculated
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :param baseline_dataset: The data to calculate quality against
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :param metric_thresholds :A list of metrics to calculate and their
        associated thresholds
    :type metric_thresholds: ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold
    :param alert_enabled: The current notification mode for this signal
    :type alert_enabled: bool
    :param model_type: The type of task the model performs. Possible values
        include: "classification", "regression"
    :type model_type: str or ~azure.ai.ml.constants.MonitorModelType
    """

    def __init__(
        self,
        *,
        production_data: List[FADProductionData],
        reference_data: ReferenceData,
        metric_thresholds: FeatureAttributionDriftMetricThreshold,
        alert_enabled: bool = True,
    ):
        self.production_data = production_data
        self.reference_data = reference_data
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled
        self.type = MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT

    def _to_rest_object(self, **kwargs) -> RestFeatureAttributionDriftMonitoringSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        return RestFeatureAttributionDriftMonitoringSignal(
            production_data=[data._to_rest_object() for data in self.production_data],
            reference_data=self.reference_data._to_rest_object(),
            metric_threshold=self.metric_thresholds._to_rest_object(),
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestFeatureAttributionDriftMonitoringSignal) -> "FeatureAttributionDriftSignal":
        return cls(
            production_data=[FADProductionData._from_rest_object(data) for data in obj.production_data],
            reference_data=ReferenceData._from_rest_object(obj.baseline_data),
            metric_thresholds=FeatureAttributionDriftMetricThreshold._from_rest_object(obj.metric_threshold),
            model_type=obj.model_type.lower(),
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
        )


@experimental
class ModelPerformanceSignal(ModelSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        metric_thresholds: ModelPerformanceMetricThreshold,
        model_type: MonitorModelType,
        data_segment: DataSegment = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.MODEL_PERFORMANCE
        self.data_segment = data_segment

    def _to_rest_object(self, **kwargs) -> RestModelPerformanceSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        return RestModelPerformanceSignal(
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            metric_threshold=self.metric_thresholds._to_rest_object(model_type=self.model_type),
            data_segment=self.data_segment._to_rest_object() if self.data_segment else None,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.data_window_size)
            if self.target_dataset.data_window_size
            else default_data_window_size,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestModelPerformanceSignal) -> "ModelPerformanceSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                data_window_size=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
            ),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
            metric_thresholds=ModelPerformanceMetricThreshold._from_rest_object(obj.metric_threshold),
            model_type=obj.metric_threshold.model_type.lower(),
            data_segment=DataSegment._from_rest_object(obj.data_segment) if obj.data_segment else None,
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
        )

class WorkspaceConnection(RestTranslatableMixin):
    def __init__(
        self,
        *,
        environment_variables: Dict[str,str],
        secret_config: Dict[str,str],
    ):
        self.environment_variables = environment_variables
        self.secret_config = secret_config

    def _to_rest_object(self) -> RestMonitoringWorkspaceConnection:
        return RestMonitoringWorkspaceConnection(
            environment_variables=self.environment_variables,
            secret_config=self.secret_config,
        )
    
    def _from_rest_object(cls, obj: RestMonitoringWorkspaceConnection) -> "WorkspaceConnection":
        return cls(
            environment_variables=obj.environment_variables,
            secret_config=obj.secret_config,
        )
@experimental
class CustomMonitoringSignal(RestTranslatableMixin):
    """Custom signal

    :ivar type: The type of the signal
    :vartype type: str
    :param input_datasets: Diction of input datasets for monitoring.
        Key is the component input port name, value is the data asset.
    :type input_datasets: Dict[str, ~azure.ai.ml.entities.MonitorInputData]
    :param metric_thresholds :A list of metrics to calculate and their
        associated thresholds
    :type metric_thresholds: List[~azure.ai.ml.entities.CustomMonitoringMetricThreshold]
    :param alert_enabled: The current notification mode for this signal
    :type alert_enabled: bool
    :param component_id: ARM ID of the component resource used to
        calculate the custom metrics.
    :type component_id: str
    :param data_window_size: The number of days a single monitor looks back
        over the target
    :type data_window_size: int
    """

    def __init__(
        self,
        *,
        input_data: Dict[str, Input] = None,
        metric_thresholds: List[CustomMonitoringMetricThreshold],
        component_id: str,
        workspace_connection: WorkspaceConnection,
        input_literals: Dict[str, MonitoringInputDataBase],
        alert_enabled: bool = True,
    ):
        self.type = MonitorSignalType.CUSTOM
        self.input_data = input_data
        self.metric_thresholds = metric_thresholds
        self.component_id = component_id
        self.alert_enabled = alert_enabled
        self.inpit_literals = input_literals
        self.workspace_connection = workspace_connection

    def _to_rest_object(self, **kwargs) -> RestCustomMonitoringSignal:  # pylint:disable=unused-argument
        default_data_window_size = kwargs.get("default_data_window_size")
        return RestCustomMonitoringSignal(
            component_id=self.component_id,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            inputs={
                input_name: input_value._to_rest_object() for input_name, input_value in self.input_data.items()
            }
            if self.input_data
            else None,
            input_assets={
                port_name: asset_value._to_rest_object() for port_name, asset_value in self.input_literals.items()
            }
            if self.inpit_literals
            else None,
            workspace_connection=self.workspace_connection._to_rest_object() 
            if self.workspace_connection else None,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestCustomMonitoringSignal) -> "CustomMonitoringSignal":
        return cls(
            input_data={
                input_name: Input._from_rest_object(input_value)
                for input_name, input_value in obj.input_data.items()
            }
            if obj.input_assets
            else None,
            input_literals={
                input_name: Input._from_rest_object(input_value)
                for input_name, input_value in obj.input_data.items()
            },
            metric_thresholds=[
                CustomMonitoringMetricThreshold._from_rest_object(metric) for metric in obj.metric_thresholds
            ],
            component_id=obj.component_id,
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
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

def _from_rest_num_cat_metrics(numerical_metrics, categorical_metrics):
    metrics = []
    if numerical_metrics is not None:
        metrics.append(NumericalDataDriftMetrics._from_rest_object(numerical_metrics))
    
    if categorical_metrics is not None:
        metrics.append(CategoricalDataDriftMetrics._from_rest_object(categorical_metrics))
    
    return metrics

def _to_rest_data_quality_metrics(numerical_metrics, categorical_metrics):
    metric_thresholds = []
    if numerical_metrics is not None:
        metric_thresholds = metric_thresholds + numerical_metrics._to_rest_object()
    
    if categorical_metrics is not None:
        metric_thresholds = metric_thresholds +  categorical_metrics._to_rest_object()
    
    return metric_thresholds