# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import datetime
from typing import Dict, Optional

from azure.ai.ml._restclient.arm_ml_service.models import FixedInputData as RestFixedInputData
from azure.ai.ml._restclient.arm_ml_service.models import MonitoringInputDataBase as RestMonitorInputBase
from azure.ai.ml._restclient.arm_ml_service.models import RollingInputData as RestRollingInputData
from azure.ai.ml._restclient.arm_ml_service.models import StaticInputData as RestStaticInputData
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml.constants._monitoring import MonitorDatasetContext, MonitorInputDataType
from azure.ai.ml.entities._mixins import RestTranslatableMixin


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
        type: Optional[MonitorInputDataType] = None,
        data_context: Optional[MonitorDatasetContext] = None,
        target_columns: Optional[Dict] = None,
        job_type: Optional[str] = None,
        uri: Optional[str] = None,
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


class FixedInputData(MonitorInputData):
    """
    :ivar type: Specifies the type of monitoring input data. Set automatically to "Fixed" for this class.
    :var type: MonitorInputDataType
    """

    def __init__(
        self,
        *,
        data_context: Optional[MonitorDatasetContext] = None,
        target_columns: Optional[Dict] = None,
        job_type: Optional[str] = None,
        uri: Optional[str] = None,
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


class TrailingInputData(MonitorInputData):
    """
    :ivar type: Specifies the type of monitoring input data. Set automatically to "Trailing" for this class.
    :var type: MonitorInputDataType
    """

    def __init__(
        self,
        *,
        data_context: Optional[MonitorDatasetContext] = None,
        target_columns: Optional[Dict] = None,
        job_type: Optional[str] = None,
        uri: Optional[str] = None,
        window_size: Optional[str] = None,
        window_offset: Optional[str] = None,
        pre_processing_component_id: Optional[str] = None,
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

    def _to_rest_object(self) -> RestRollingInputData:
        # ``TrailingInputData`` was renamed to ``RollingInputData`` (inputDataType "Rolling") in the
        # shared arm_ml_service model. The migration pins api-version 2023-06-01-preview, whose service
        # contract still expects inputDataType "Trailing", so override the wire discriminator to preserve it.
        rest_object = RestRollingInputData(
            data_context=camel_to_snake(self.data_context),
            columns=self.target_columns,
            job_input_type=self.job_type,
            uri=self.uri,
            window_size=self.window_size,
            window_offset=self.window_offset,
            preprocessing_component_id=self.pre_processing_component_id,
        )
        rest_object["inputDataType"] = "Trailing"
        return rest_object

    @classmethod
    def _from_rest_object(cls, obj: RestRollingInputData) -> "TrailingInputData":
        # ``inputDataType: "Trailing"`` is not a known arm discriminator (arm uses "Rolling"), so the
        # object deserializes to the base ``MonitoringInputDataBase``; read the rolling fields, which are
        # already ISO-8601 strings on the wire, via their camelCase mapping keys.
        return cls(
            data_context=snake_to_camel(obj["dataContext"]),
            target_columns=obj.get("columns"),
            job_type=obj["jobInputType"],
            uri=obj["uri"],
            window_size=obj["windowSize"],
            window_offset=obj["windowOffset"],
            pre_processing_component_id=obj.get("preprocessingComponentId"),
        )


class StaticInputData(MonitorInputData):
    """
    :ivar type: Specifies the type of monitoring input data. Set automatically to "Static" for this class.
    :var type: MonitorInputDataType
    """

    def __init__(
        self,
        *,
        data_context: Optional[MonitorDatasetContext] = None,
        target_columns: Optional[Dict] = None,
        job_type: Optional[str] = None,
        uri: Optional[str] = None,
        pre_processing_component_id: Optional[str] = None,
        window_start: Optional[str] = None,
        window_end: Optional[str] = None,
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
        window_start = datetime.datetime.strptime(str(self.window_start), "%Y-%m-%d")
        window_end = datetime.datetime.strptime(str(self.window_end), "%Y-%m-%d")
        rest_object = RestStaticInputData(
            data_context=camel_to_snake(self.data_context),
            columns=self.target_columns,
            job_input_type=self.job_type,
            uri=self.uri,
            preprocessing_component_id=self.pre_processing_component_id,
            window_start=window_start,
            window_end=window_end,
        )
        # The arm_ml_service encoder drops sub-second precision (``...00:00:00Z``); the 2023-06-01-preview
        # msrest client emitted millisecond precision (``...00:00:00.000Z``). Override the wire keys to
        # preserve the exact byte form.
        rest_object["windowStart"] = window_start.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        rest_object["windowEnd"] = window_end.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return rest_object

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
