# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Optional, Union

from typing_extensions import Literal

from azure.ai.ml._restclient.v2023_04_01_preview.models import AllFeatures as RestAllFeatures
from azure.ai.ml._restclient.v2023_04_01_preview.models import CustomMonitoringSignal as RestCustomMonitoringSignal
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    DataDriftMonitoringSignal as RestMonitoringDataDriftSignal,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    DataQualityMonitoringSignal as RestMonitoringDataQualitySignal,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    FeatureAttributionDriftMonitoringSignal as RestFeatureAttributionDriftMonitoringSignal,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import FeatureSubset as RestFeatureSubset
from azure.ai.ml._restclient.v2023_04_01_preview.models import ModelPerformanceSignalBase as RestModelPerformanceSignal
from azure.ai.ml._restclient.v2023_04_01_preview.models import MonitoringDataSegment as RestMonitoringDataSegment
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    MonitoringFeatureFilterBase as RestMonitoringFeatureFilterBase,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import MonitoringNotificationMode
from azure.ai.ml._restclient.v2023_04_01_preview.models import MonitoringSignalBase as RestMonitoringSignalBase
from azure.ai.ml._restclient.v2023_04_01_preview.models import MonitoringSignalType
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    PredictionDriftMonitoringSignal as RestPredictionDriftMonitoringSignal,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    TopNFeaturesByAttribution as RestTopNFeaturesByAttribution,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import from_iso_duration_format_days, to_iso_duration_format_days
from azure.ai.ml.constants._monitoring import ALL_FEATURES, MonitorModelType, MonitorSignalType
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._monitoring.input_data import MonitorInputData
from azure.ai.ml.entities._monitoring.thresholds import (
    CustomMonitoringMetricThreshold,
    DataDriftMetricThreshold,
    DataQualityMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    MetricThreshold,
    ModelPerformanceMetricThreshold,
    PredictionDriftMetricThreshold,
)


@experimental
class DataSegment(RestTranslatableMixin):
    """Data segment for monitoring.

    :keyword feature_name: The feature to segment the data on.
    :type feature_name: str
    :keyword feature_values: A list of values for the given segmented feature to filter.
    :type feature_values: list[str]
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
    :type top_n_feature_importance: int
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
class TargetDataset:
    """Monitor target dataset.

    :keyword dataset: The target dataset definition for monitor input.
    :type dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword data_window_size: The time window to select for the data, in days.
    :type data_window_size: Optional[int]
    """

    def __init__(
        self,
        *,
        dataset: MonitorInputData,
        data_window_size: int = None,
    ) -> None:
        self.dataset = dataset
        self.data_window_size = data_window_size


@experimental
class MonitoringSignal(RestTranslatableMixin):
    """
    Base class for monitoring signals.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword target_dataset: The target dataset definition for monitor input.
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The baseline dataset definition for monitor input.
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: The metric thresholds for the signal.
    :type metric_thresholds: Union[
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
    :type alert_enabled: bool
    """

    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: Union[MetricThreshold, List[MetricThreshold]] = None,
        alert_enabled: bool = True,
    ) -> None:
        self.target_dataset = target_dataset
        self.baseline_dataset = baseline_dataset
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled

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
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The baseline dataset definition for monitor input.
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword features: The features to include in the signal.
    :type features: Union[list[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal[ALL_FEATURES]]
    :keyword metric_thresholds: The metric thresholds for the signal.
    :type metric_thresholds: list[Union[
        ~azure.ai.ml.entities.DataDriftMetricThreshold,
        ~azure.ai.ml.entities.DataQualityMetricThreshold,
        ~azure.ai.ml.entities.PredictionDriftMetricThreshold,
        ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold,
        ~azure.ai.ml.entities.CustomMonitoringMetricThreshold
    ]]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :type alert_enabled: bool
    """

    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[MetricThreshold] = None,
        alert_enabled: bool = True,
    ) -> None:
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
        )
        self.features = features


@experimental
class DataDriftSignal(DataSignal):
    """Data drift signal.

    :keyword target_dataset: The dataset for which drift will be calculated.
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The dataset to calculate drift against.
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :type metric_thresholds: list[~azure.ai.ml.entities.DataDriftMetricThreshold]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :type alert_enabled: bool
    :keyword data_segment: The data segment used for scoping on a subset of the data population.
    :type data_segment: ~azure.ai.ml.entities.DataSegment
    :keyword features: The feature filter identifying which feature(s) to
        calculate drift over.
    :type features: Union[list[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal['all_features']]
    """

    def __init__(
        self,
        *,
        baseline_dataset: MonitorInputData = None,
        target_dataset: TargetDataset = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[DataDriftMetricThreshold],
        alert_enabled: bool = True,
        data_segment: DataSegment = None,
    ) -> None:
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            features=features,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.DATA_DRIFT
        self.data_segment = data_segment

    def _to_rest_object(self, **kwargs) -> RestMonitoringDataDriftSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        rest_features = _to_rest_features(self.features) if self.features else None
        return RestMonitoringDataDriftSignal(
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            features=rest_features,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.data_window_size)
            if self.target_dataset.data_window_size
            else default_data_window_size,
            data_segment=self.data_segment._to_rest_object() if self.data_segment else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataDriftSignal) -> "DataDriftSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                data_window_size=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
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
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword target_dataset: The dataset for which drift will be calculated.
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword metric_thresholds: A list of metrics to calculate and their associated thresholds
    :type metric_thresholds: list[~azure.ai.ml.entities.PredictionDriftMetricThreshold]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :type alert_enabled: bool
    """

    def __init__(
        self,
        *,
        baseline_dataset: MonitorInputData = None,
        target_dataset: TargetDataset = None,
        metric_thresholds: List[PredictionDriftMetricThreshold],
        alert_enabled: bool = True,
    ) -> None:
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.PREDICTION_DRIFT

    def _to_rest_object(self, **kwargs) -> RestPredictionDriftMonitoringSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        return RestPredictionDriftMonitoringSignal(
            # hack this to a random value since the service ignores it and it's mislabled as a required property
            model_type="classification",
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.data_window_size)
            if self.target_dataset.data_window_size
            else default_data_window_size,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestPredictionDriftMonitoringSignal) -> "PredictionDriftSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                data_window_size=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
            ),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
            metric_thresholds=[
                PredictionDriftMetricThreshold._from_rest_object(threshold) for threshold in obj.metric_thresholds
            ],
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


    :keyword target_dataset: The data for which quality will be calculated.
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The data to calculate quality against.
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :type metric_thresholds: list[~azure.ai.ml.entities.DataQualityMetricThreshold]
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :type alert_enabled: bool
    :keyword features: The feature filter identifying which feature(s) to
        calculate quality over.
    :type features: Union[list[str], ~azure.ai.ml.entities.MonitorFeatureFilter, Literal['all_features']]
    """

    def __init__(
        self,
        *,
        baseline_dataset: MonitorInputData = None,
        target_dataset: TargetDataset = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[DataQualityMetricThreshold],
        alert_enabled: bool = True,
    ) -> None:
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            features=features,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.DATA_QUALITY

    def _to_rest_object(self, **kwargs) -> RestMonitoringDataQualitySignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        rest_features = _to_rest_features(self.features) if self.features else None
        return RestMonitoringDataQualitySignal(
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            features=rest_features,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.data_window_size)
            if self.target_dataset.data_window_size
            else default_data_window_size,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataQualitySignal) -> "DataDriftSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                data_window_size=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
            ),
            baseline_dataset=MonitorInputData._from_rest_object(obj.baseline_data),
            features=_from_rest_features(obj.features),
            metric_thresholds=[
                DataQualityMetricThreshold._from_rest_object(threshold) for threshold in obj.metric_thresholds
            ],
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
    """Base class for model signals.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword target_dataset: The data for which quality will be calculated.
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The data to calculate quality against.
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :type metric_thresholds: list[~azure.ai.ml.entities.MetricThreshold]
    :keyword model_type: The type of model to monitor.
    :type model_type: ~azure.ai.ml.constants.MonitorModelType
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :type alert_enabled: bool
    """

    def __init__(
        self,
        *,
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        metric_thresholds: List[MetricThreshold],
        model_type: MonitorModelType,
        alert_enabled: bool = True,
    ) -> None:
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

    :keyword target_dataset: The data for which drift will be calculated.
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The data to calculate drift against.
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :type metric_thresholds: ~azure.ai.ml.entities.FeatureAttributionDriftMetricThreshold
    :keyword model_type: The model type.
    :type model_type: ~azure.ai.ml.constants.MonitorModelType
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :type alert_enabled: bool
    """

    def __init__(
        self,
        *,
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        metric_thresholds: FeatureAttributionDriftMetricThreshold,
        model_type: MonitorModelType,
        alert_enabled: bool = True,
    ) -> None:
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT

    def _to_rest_object(self, **kwargs) -> RestFeatureAttributionDriftMonitoringSignal:
        default_data_window_size = kwargs.get("default_data_window_size")
        return RestFeatureAttributionDriftMonitoringSignal(
            target_data=self.target_dataset.dataset._to_rest_object(),
            baseline_data=self.baseline_dataset._to_rest_object(),
            metric_threshold=self.metric_thresholds._to_rest_object(),
            model_type=self.model_type,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.target_dataset.data_window_size)
            if self.target_dataset.data_window_size
            else default_data_window_size,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestFeatureAttributionDriftMonitoringSignal) -> "FeatureAttributionDriftSignal":
        return cls(
            target_dataset=TargetDataset(
                dataset=MonitorInputData._from_rest_object(obj.target_data),
                data_window_size=from_iso_duration_format_days(obj.lookback_period) if obj.lookback_period else None,
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
    """Model performance signal.

    :keyword target_dataset: The data for which performance will be calculated.
    :type target_dataset: ~azure.ai.ml.entities.TargetDataset
    :keyword baseline_dataset: The data to calculate performance against.
    :type baseline_dataset: ~azure.ai.ml.entities.MonitorInputData
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :type metric_thresholds: ~azure.ai.ml.entities.ModelPerformanceMetricThreshold
    :keyword model_type: The model type.
    :type model_type: ~azure.ai.ml.constants.MonitorModelType
    :keyword data_segment: The data segment to calculate performance against.
    :type data_segment: ~azure.ai.ml.entities.DataSegment
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :type alert_enabled: bool
    """

    def __init__(
        self,
        *,
        target_dataset: TargetDataset,
        baseline_dataset: MonitorInputData,
        metric_thresholds: ModelPerformanceMetricThreshold,
        model_type: MonitorModelType,
        data_segment: DataSegment = None,
        alert_enabled: bool = True,
    ) -> None:
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


@experimental
class CustomMonitoringSignal(RestTranslatableMixin):
    """Custom monitoring signal.

    :keyword input_datasets: A dictionary of input datasets for monitoring.
        Each key is the component input port name, and its value is the data asset.
    :type input_datasets: Optional[dict[str, ~azure.ai.ml.entities.MonitorInputData]]
    :keyword metric_thresholds: A list of metrics to calculate and their
        associated thresholds.
    :type metric_thresholds: list[~azure.ai.ml.entities.CustomMonitoringMetricThreshold]
    :keyword component_id: The ARM (Azure Resource Manager) ID of the component resource used to
        calculate the custom metrics.
    :type component_id: str
    :keyword alert_enabled: Whether or not to enable alerts for the signal. Defaults to True.
    :type alert_enabled: bool
    :keyword data_window_size: The number of days a single monitor looks back
        over the target
    :type data_window_size: Optional[int]
    """

    def __init__(
        self,
        *,
        input_datasets: Dict[str, MonitorInputData] = None,
        metric_thresholds: List[CustomMonitoringMetricThreshold],
        component_id: str,
        alert_enabled: bool = True,
        data_window_size: Optional[int] = None,
    ) -> None:
        self.type = MonitorSignalType.CUSTOM
        self.input_datasets = input_datasets
        self.metric_thresholds = metric_thresholds
        self.component_id = component_id
        self.alert_enabled = alert_enabled
        self.data_window_size = data_window_size

    def _to_rest_object(self, **kwargs) -> RestCustomMonitoringSignal:  # pylint:disable=unused-argument
        default_data_window_size = kwargs.get("default_data_window_size")
        return RestCustomMonitoringSignal(
            component_id=self.component_id,
            metric_thresholds=[threshold._to_rest_object() for threshold in self.metric_thresholds],
            input_assets={
                input_name: input_value._to_rest_object() for input_name, input_value in self.input_datasets.items()
            }
            if self.input_datasets
            else None,
            mode=MonitoringNotificationMode.ENABLED if self.alert_enabled else MonitoringNotificationMode.DISABLED,
            lookback_period=to_iso_duration_format_days(self.data_window_size)
            if self.data_window_size
            else default_data_window_size,
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
