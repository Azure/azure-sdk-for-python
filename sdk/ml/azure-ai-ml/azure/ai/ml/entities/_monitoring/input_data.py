# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import datetime
from typing import Dict, Optional
import isodate

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitoringInputDataBase as RestMonitorInputBase,
    FixedInputData as RestFixedInputData,
    TrailingInputData as RestTrailingInputData,
    StaticInputData as RestStaticInputData,
)

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml.constants._monitoring import MonitorDatasetContext, MonitorInputDataType


@experimental
class MonitorInputData(RestTranslatableMixin):
    """Monitor input data.

    :keyword type: Specifies the type of monitoring input data.
    :paramtype type: MonitorInputDataType
    :keyword input_dataset: Input data used by the monitor
    :paramtype input_dataset: Optional[~azure.ai.ml.Input]
    :keyword dataset_context: The context of the input dataset. Accepted values are "model_inputs",
        "model_outputs", "training", "test", "validation", and "ground_truth".
    :paramtype dataset_context: Optional[Union[str, ~azure.ai.ml.constants.MonitorDatasetContext]]
    :keyword target_column_name: The target column in the given input dataset.
    :paramtype target_column_name: Optional[str]
    :keyword pre_processing_component: The ARM (Azure Resource Manager) resource ID of the component resource used to
        preprocess the data.
    :paramtype pre_processing_component: Optional[str]
    """

    def __init__(
        self,
        *,
        type: MonitorInputDataType = None,
        data_context: MonitorDatasetContext = None,
        target_columns: Dict = None,
        job_type: str = None,
        uri: str = None,
    ):
        self.type = type
        self.data_context = data_context
        self.target_columns = target_columns
        self.job_type = job_type
        self.uri = uri

    @classmethod
    def _from_rest_object(cls, obj: RestMonitorInputBase) -> Optional["MonitorInputData"]:
        if obj.input_data_type == MonitorInputDataType.FIXED:
            return FixedInputData._from_rest_object(obj)
        if obj.input_data_type == MonitorInputDataType.TRAILING:
            return TrailingInputData._from_rest_object(obj)
        if obj.input_data_type == MonitorInputDataType.STATIC:
            return StaticInputData._from_rest_object(obj)

        return None


@experimental
class FixedInputData(MonitorInputData):
    """
    :ivar type: Specifies the type of monitoring input data. Set automatically to "Fixed" for this class.
    :var type: MonitorInputDataType
    """

    def __init__(
        self,
        *,
        data_context: MonitorDatasetContext = None,
        target_columns: Dict = None,
        job_type: str = None,
        uri: str = None,
    ):
        super().__init__(
            type=MonitorInputDataType.FIXED,
            data_context=data_context,
            target_columns=target_columns,
            job_type=job_type,
            uri=uri,
        )

    def _to_rest_object(self) -> RestFixedInputData:
        return RestFixedInputData(
            data_context=camel_to_snake(self.data_context),
            columns=self.target_columns,
            job_input_type=self.job_type,
            uri=self.uri,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestFixedInputData) -> "FixedInputData":
        return cls(
            data_context=camel_to_snake(obj.data_context),
            target_columns=obj.columns,
            job_type=obj.job_input_type,
            uri=obj.uri,
        )


@experimental
class TrailingInputData(MonitorInputData):
    """
    :ivar type: Specifies the type of monitoring input data. Set automatically to "Trailing" for this class.
    :var type: MonitorInputDataType
    """

    def __init__(
        self,
        *,
        data_context: MonitorDatasetContext = None,
        target_columns: Dict = None,
        job_type: str = None,
        uri: str = None,
        window_size: str = None,
        window_offset: str = None,
        pre_processing_component_id: str = None,
    ):
        super().__init__(
            type=MonitorInputDataType.TRAILING,
            data_context=data_context,
            target_columns=target_columns,
            job_type=job_type,
            uri=uri,
        )
        self.window_size = window_size
        self.window_offset = window_offset
        self.pre_processing_component_id = pre_processing_component_id

    def _to_rest_object(self) -> RestTrailingInputData:
        return RestTrailingInputData(
            data_context=camel_to_snake(self.data_context),
            columns=self.target_columns,
            job_input_type=self.job_type,
            uri=self.uri,
            window_size=self.window_size,
            window_offset=self.window_offset,
            preprocessing_component_id=self.pre_processing_component_id,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestTrailingInputData) -> "TrailingInputData":
        return cls(
            data_context=snake_to_camel(obj.data_context),
            target_columns=obj.columns,
            job_type=obj.job_input_type,
            uri=obj.uri,
            window_size=str(isodate.duration_isoformat(obj.window_size)),
            window_offset=str(isodate.duration_isoformat(obj.window_offset)),
            pre_processing_component_id=obj.preprocessing_component_id,
        )


@experimental
class StaticInputData(MonitorInputData):
    """
    :ivar type: Specifies the type of monitoring input data. Set automatically to "Static" for this class.
    :var type: MonitorInputDataType
    """

    def __init__(
        self,
        *,
        data_context: MonitorDatasetContext = None,
        target_columns: Dict = None,
        job_type: str = None,
        uri: str = None,
        pre_processing_component_id: str = None,
        window_start: str = None,
        window_end: str = None,
    ):
        super().__init__(
            type=MonitorInputDataType.STATIC,
            data_context=data_context,
            target_columns=target_columns,
            job_type=job_type,
            uri=uri,
        )
        self.pre_processing_component_id = pre_processing_component_id
        self.window_start = window_start
        self.window_end = window_end

    def _to_rest_object(self) -> RestStaticInputData:
        return RestStaticInputData(
            data_context=camel_to_snake(self.data_context),
            columns=self.target_columns,
            job_input_type=self.job_type,
            uri=self.uri,
            preprocessing_component_id=self.pre_processing_component_id,
            window_start=datetime.datetime.strptime(str(self.window_start), "%Y-%m-%d"),
            window_end=datetime.datetime.strptime(str(self.window_end), "%Y-%m-%d"),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestStaticInputData) -> "StaticInputData":
        return cls(
            data_context=snake_to_camel(obj.data_context),
            target_columns=obj.columns,
            job_type=obj.job_input_type,
            uri=obj.uri,
            pre_processing_component_id=obj.preprocessing_component_id,
            window_start=str(datetime.datetime.strftime(obj.window_start, "%Y-%m-%d")),
            window_end=datetime.datetime.strftime(obj.window_end, "%Y-%m-%d"),
        )
