# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_04_01_preview.models import MonitoringInputData as RestMonitoringInputData
from azure.ai.ml._utils._experimental import experimental

from azure.ai.ml.constants._monitoring import MonitorDatasetContext


@experimental
class MonitorInputData(RestTranslatableMixin):
    def __init__(
        self,
        *,
        input_dataset: str = None,
        dataset_context: MonitorDatasetContext = None,
        target_column_name: str = None,
        pre_processing_component: str = None,
    ):
        self.input_dataset = input_dataset
        self.dataset_context = dataset_context
        self.target_column_name = target_column_name
        self.pre_processing_component = pre_processing_component

    def _to_rest_object(self) -> MonitoringInputData:
        return super()._to_rest_object()
