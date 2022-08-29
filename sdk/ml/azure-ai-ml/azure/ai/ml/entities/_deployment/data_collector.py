# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
)
from typing import Dict
from azure.ai.ml._schema._deployment.online.data_collector_schema import DataCollectorSchema


class DataCollector:
    """Data Capture deployment entity

    :param enabled: Is data capture enabled.
    :type enabled: bool
    """

    def __init__(self, enabled: bool, **kwargs):
        self.enabled = enabled

    def _to_dict(self) -> Dict:
        return DataCollectorSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
