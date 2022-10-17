# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.data_collector_schema import DataCollectorSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._deployment.destination import Destination
from azure.ai.ml.entities._deployment.request_logging import RequestLogging
from azure.ai.ml.entities._deployment.sampling_strategy import SamplingStrategy


class DataCollector:
    """Data Capture deployment entity

    :param enabled: Is data capture enabled.
    :type enabled: bool
    :param rolling_rate: The rolling rate of mdc files, possible values: ["year", "month", "day", "hour", "minute"].
    :type rolling_rate: str
    :param destination: Must be blob store.
    :type destination: Destination
    :param sampling_strategy: Sample percent of traffic.
    :type sampling_strategy: SamplingStrategy, optional
    :param request_logging: Logging of request payload parameters.
    :type request_logging: RequestLogging
    """

    def __init__(
        self,
        enabled: bool = None,
        rolling_rate: str = None,
        destination: Destination = None,
        sampling_strategy: SamplingStrategy = None,
        request_logging: RequestLogging = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.enabled = enabled
        self.rolling_rate = rolling_rate
        self.destination = destination
        self.sampling_strategy = sampling_strategy
        self.request_logging = request_logging

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DataCollectorSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
