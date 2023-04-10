# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_04_01_preview.models import MonitoringInputData as RestMonitoringInputData
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml._utils._experimental import experimental

from azure.ai.ml.constants._monitoring import MonitorDatasetContext
from azure.ai.ml.entities._inputs_outputs import Input


@experimental
class MonitorInputData(RestTranslatableMixin):
    def __init__(
        self,
        *,
        input_dataset: Input = None,
        dataset_context: MonitorDatasetContext = None,
        target_column_name: str = None,
        pre_processing_component: str = None,
    ):
        self.input_dataset = input_dataset
        self.dataset_context = dataset_context
        self.target_column_name = target_column_name
        self.pre_processing_component = pre_processing_component

    def _to_rest_object(self) -> RestMonitoringInputData:
        return RestMonitoringInputData(
            data_context=snake_to_camel(self.dataset_context),
            asset=self.input_dataset._to_rest_object(),
            preprocessing_component_id=self.pre_processing_component,
            target_column_name=self.target_column_name
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringInputData) -> "MonitorInputData":
        return cls(
            dataset_context=camel_to_snake(obj.data_context),
            target_column_name=obj.target_column_name,
            pre_processing_component=obj.preprocessing_component_id
        )