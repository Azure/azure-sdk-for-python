# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Union

from typing_extensions import Literal

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    MonitoringSignalBase as RestMonitoringSignalBase,
    DataDriftMonitoringSignal as RestMonitoringDataDriftSignal,
    DataQualityMonitoringSignal as RestMonitoringDataQualitySignal,
    PredictionDriftMonitoringSignal as RestPredictionDriftMonitoringSignal,
    FeatureAttributionDriftMonitoringSignal as RestFeatureAttributionDriftMonitoringSignal,
    ModelPerformanceSignalBase as RestModelPerformanceSignal,
    CustomMonitoringSignal as RestCustomMonitoringSignal,
    MonitoringDataSegment as RestMonitoringDataSegment,
    MonitoringFeatureFilterBase as RestMonitoringFeatureFilterBase,
    TopNFeaturesByAttribution as RestTopNFeaturesByAttribution,
    AllFeatures as RestAllFeatures,
    FeatureSubset as RestFeatureSubset,
    MonitoringNotificationMode,
    MonitoringSignalType,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import to_iso_duration_format_days, from_iso_duration_format_days
from azure.ai.ml.constants._monitoring import MonitorSignalType, ALL_FEATURES, MonitorModelType
from azure.ai.ml.entities._monitoring.input_data import MonitorInputData
from azure.ai.ml.entities._monitoring.thresholds import (
    MetricThreshold,
    DataDriftMetricThreshold,
    DataQualityMetricThreshold,
    PredictionDriftMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    ModelPerformanceMetricThreshold,
    CustomMonitoringMetricThreshold,
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


@experimental
class TargetDataset:
    """Monitor target dataset

    :param dataset: Target dataset definition for monitor
    :type dataset: ~azure.ai.ml.entities.MonitorInputData
    :param lookback_period: The number of days a single monitor looks back over the target
    :type lookback_period: int
    """

    def __init__(
        self,
        *,
        dataset: MonitorInputData,
        lookback_period: int = None,
    ):
        self.dataset = dataset
        self.lookback_period = lookback_period


@experimental
class MonitoringSignal(RestTranslatableMixin):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: Union[MetricThreshold, List[MetricThreshold]] = None,
        alert_enabled: bool = True,
    ):
        self.target_dataset = target_dataset
        self.baseline_dataset = baseline_dataset
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringSignalBase) -> "MonitoringSignal":
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


@experimental
class DataSignal(MonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[MetricThreshold] = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
        )
        self.features = features


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
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[DataDriftMetricThreshold],
        alert_enabled: bool = True,
        data_segment: DataSegment = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            features=features,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.DATA_DRIFT
        self.data_segment = data_segment

    def _to_rest_object(self) -> RestMonitoringDataDriftSignal:
        rest_features = _to_rest_features(self.features) if self.features else None
        return RestMonitoringDataDriftSignal(
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            features=rest_features,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.lookback_period)
            if self.target_dataset.lookback_period
            else None,
            data_segment=self.data_segment._to_rest_object() if self.data_segment else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataDriftSignal) -> "DataDriftSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                lookback_period=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
            ),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
            features=_from_rest_features(obj.features),
            metric_thresholds=[
                DataDriftMetricThreshold._from_rest_object(threshold) for threshold in obj.metric_thresholds
            ],
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
            data_segment=DataSegment._from_rest_object(obj.data_segment) if obj.data_segment else None,
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
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        metric_thresholds: List[PredictionDriftMetricThreshold],
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.PREDICTION_DRIFT

    def _to_rest_object(self) -> RestPredictionDriftMonitoringSignal:
        return RestPredictionDriftMonitoringSignal(
            # hack this to a random value since the service ignores it and it's mislabled as a required property
            model_type="classification",
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.lookback_period)
            if self.target_dataset.lookback_period
            else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestPredictionDriftMonitoringSignal) -> "PredictionDriftSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                lookback_period=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
            ),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
            metric_thresholds=[
                PredictionDriftMetricThreshold._from_rest_object(threshold) for threshold in obj.metric_thresholds
            ],
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
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
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[DataQualityMetricThreshold],
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            features=features,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.DATA_QUALITY

    def _to_rest_object(self) -> RestMonitoringDataQualitySignal:
        rest_features = _to_rest_features(self.features) if self.features else None
        return RestMonitoringDataQualitySignal(
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            features=rest_features,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.lookback_period)
            if self.target_dataset.lookback_period
            else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataQualitySignal) -> "DataDriftSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                lookback_period=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
            ),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
            features=_from_rest_features(obj.features),
            metric_thresholds=[
                DataDriftMetricThreshold._from_rest_object(threshold) for threshold in obj.metric_thresholds
            ],
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
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


@experimental
class FeatureAttributionDriftSignal(ModelSignal):
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
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        metric_thresholds: FeatureAttributionDriftMetricThreshold,
        model_type: MonitorModelType,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT

    def _to_rest_object(self) -> RestFeatureAttributionDriftMonitoringSignal:
        return RestFeatureAttributionDriftMonitoringSignal(
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            metric_threshold=self.metric_thresholds._to_rest_object(),
            model_type=self.model_type,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.lookback_period)
            if self.target_dataset.lookback_period
            else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestFeatureAttributionDriftMonitoringSignal) -> "FeatureAttributionDriftSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                lookback_period=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
            ),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
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

    def _to_rest_object(self) -> RestModelPerformanceSignal:
        return RestModelPerformanceSignal(
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            metric_threshold=self.metric_thresholds._to_rest_object(model_type=self.model_type),
            data_segment=self.data_segment._to_rest_object() if self.data_segment else None,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.lookback_period)
            if self.target_dataset.lookback_period
            else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestModelPerformanceSignal) -> "ModelPerformanceSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                lookback_period=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
            ),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
            metric_thresholds=ModelPerformanceMetricThreshold._from_rest_object(obj.metric_threshold),
            model_type=obj.metric_threshold.model_type.lower(),
            data_segment=DataSegment._from_rest_object(obj.data_segment) if obj.data_segment else None,
            alert_enabled=False
            if not obj.mode or (obj.mode and obj.mode == MonitoringNotificationMode.DISABLED)
            else MonitoringNotificationMode.ENABLED,
        )


@experimental
class CustomMonitoringSignal(RestTranslatableMixin):
    """Feature attribution drift signal

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
    """

    def __init__(
        self,
        *,
        input_datasets: Dict[str, MonitorInputData] = None,
        metric_thresholds: List[CustomMonitoringMetricThreshold],
        component_id: str,
        alert_enabled: bool = True,
    ):
        self.type = MonitorSignalType.CUSTOM
        self.input_datasets = input_datasets
        self.metric_thresholds = metric_thresholds
        self.component_id = component_id
        self.alert_enabled = alert_enabled

    def _to_rest_object(self) -> RestCustomMonitoringSignal:
        return RestCustomMonitoringSignal(
            component_id=self.component_id,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            input_assets={
                input_name: input_value._to_rest_object() for input_name, input_value in self.input_datasets.items()
            }
            if self.input_datasets
            else None,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestCustomMonitoringSignal) -> "CustomMonitoringSignal":
        return cls(
            input_datasets={
                input_name: MonitorInputData._from_rest_object(input_value)
                for input_name, input_value in obj.input_assets.items()
            }
            if obj.input_assets
            else None,
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
) -> Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]]:
    if isinstance(obj, RestTopNFeaturesByAttribution):
        return MonitorFeatureFilter(top_n_feature_importance=obj.top)
    if isinstance(obj, RestFeatureSubset):
        return obj.features
    if isinstance(obj, RestAllFeatures):
        return ALL_FEATURES


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
