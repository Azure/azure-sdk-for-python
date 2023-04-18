# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._experimental import experimental

from azure.ai.ml.constants._monitoring import MonitorDatasetContext
from azure.ai.ml.entities._inputs_outputs import Input


@experimental
class MonitorInputData:
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
