# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import datetime
from typing import Dict
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_06_01_preview.models import(
    MonitoringInputDataBase as RestMonitoringInputData,
    FixedInputData as RestFixedInputData,
    TrailingInputData as RestTrailingInputData,
    StaticInputData as RestStaticInputData,
) 
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml._utils._experimental import experimental

from azure.ai.ml.constants._monitoring import MonitorDatasetContext
from azure.ai.ml.entities._inputs_outputs import Input


@experimental
class MonitorInputData(RestTranslatableMixin):
    """Monitor input data

    :param input_dataset: Input data used by the monitor
    :type input_dataset: ~azure.ai.ml.entities.Input
    :param dataset_context: The context of the input dataset. Possible values
        include: model_inputs, model_outputs, training, test, validation,
        ground_truth
    :type dataset_context: str or ~azure.ai.ml.constants.MonitorDatasetContext
    :param target_column_name: The target column in the given input dataset to leverage
    :type target_column_name: str
    :param pre_processing_component: ARM resource ID of the component resource used to
        preprocess the data.
    :type pre_processing_component: str
    """

    def __init__(
        self,
        *,
        input_type: str = None,
        data_context: MonitorDatasetContext = None,
        target_columns: Dict = None,
        job_type: str = None,
        uri: str = None,
    ):
        self.input_type = input_type
        self.data_context = data_context
        self.target_columns = target_columns
        self.job_type = job_type
        self.uri = uri

class FixedInputData(MonitorInputData):
    def __init(
        self,
        *,
        input_type: str = None,
        data_context: MonitorDatasetContext = None,
        target_columns: Dict = None,
        job_type: str = None,
        uri: str = None,
    ):
        super().__init__(
            input_type="Fixed",
            data_context=data_context,
            target_columns=target_columns,
            job_type=job_type,
            uri=uri,
        )

    def _to_rest_object(self) -> RestFixedInputData:
        return RestFixedInputData(
            data_context=snake_to_camel(self.data_context),
            columns=self.target_columns,
            job_input_type=self.job_type,
            uri=self.uri,
        )
    
    def _from_rest_object(cls, obj: RestFixedInputData) -> "FixedInputData":
        return cls(
            data_context=camel_to_snake(obj.data_context),
            target_columns=obj.columns,
            job_type=obj.job_input_type,
            uri=obj.uri,
        )
    
class TrailingInputData(MonitorInputData):
    def __init__(
        self,
        *,
        data_context: MonitorDatasetContext = None,
        target_columns: Dict = None,
        job_type: str = None,
        uri: str = None,
        window_size: datetime.timedelta = None,
        window_offset: datetime.timedelta = None,
        preocessing_component_id: str = None,
    ):
        super().__init__(
            input_type="Trailing",
            data_context=data_context,
            target_columns=target_columns,
            job_type=job_type,
            uri=uri,
        )
        self.window_size = window_size
        self.window_offset = window_offset
        self.preocessing_component_id = preocessing_component_id

    def _to_rest_object(self) -> RestTrailingInputData:
        return RestTrailingInputData(
            data_context=snake_to_camel(self.data_context),
            columns=self.target_columns,
            job_input_type=self.job_type,
            uri=self.uri,
            window_size=self.window_size,
            window_offset=self.window_offset,
            preprocessing_component_id=self.preocessing_component_id,
        )
    
    def _from_rest_object(cls, obj: RestTrailingInputData) -> "TrailingInputData":
        return cls(
            data_context=camel_to_snake(obj.data_context),
            target_columns=obj.columns,
            job_type=obj.job_input_type,
            uri=obj.uri,
            window_size=obj.window_size,
            window_offset=obj.window_offset,
            preocessing_component_id=obj.preprocessing_component_id,
        )
    
class StaticInputData(MonitorInputData):
    def __init__(
        self,
        *,
        data_context: MonitorDatasetContext = None,
        target_columns: Dict = None,
        job_type: str = None,
        uri: str = None,
        preocessing_component_id: str = None,
        window_start: datetime.datetime = None,
        window_end: datetime.datetime = None,
    ):
        super().__init__(
            input_type="Static",
            data_context=data_context,
            target_columns=target_columns,
            job_type=job_type,
            uri=uri,
        )
        self.preocessing_component_id = preocessing_component_id
        self.window_start = window_start
        self.window_end = window_end
    
    def _to_rest_object(self) -> RestStaticInputData:
        return RestStaticInputData(
            data_context=snake_to_camel(self.data_context),
            columns=self.target_columns,
            job_input_type=self.job_type,
            uri=self.uri,
            preprocessing_component_id=self.preocessing_component_id,
            window_start=self.window_start,
            window_end=self.window_end,
        )
    
    def _from_rest_object(cls, obj: RestStaticInputData) -> "StaticInputData":
        return cls(
            data_context=camel_to_snake(obj.data_context),
            target_columns=obj.columns,
            job_type=obj.job_input_type,
            uri=obj.uri,
            preocessing_component_id=obj.preprocessing_component_id,
            window_start=obj.window_start,
            window_end=obj.window_end,
        )