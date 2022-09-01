# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.data_collector_schema import DataCollectorSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class DataCollector:
    """Data Capture deployment entity

    :param enabled: Is data capture enabled.
    :type enabled: bool
    """

    def __init__(self, enabled: bool, **kwargs):  # pylint: disable=unused-argument
        self.enabled = enabled

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DataCollectorSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
