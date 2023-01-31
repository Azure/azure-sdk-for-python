# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional

from azure.ai.ml._schema._deployment.online.data_collector_schema import DataCollectorSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._deployment.destination import Destination
from azure.ai.ml.entities._deployment.request_logging import RequestLogging
from azure.ai.ml.entities._deployment.deployment_collection import PayloadRequest
from azure.ai.ml.entities._deployment.payload_response import PayloadResponse


class DataCollector:
    """Data Capture deployment entity

    :param request: Entity responsible for enabling payload logging requests.
    :type request: Request
    :param response: Entity responsible for enabling payload logging response.
    :type response: Response
    :param rolling_rate: The rolling rate of mdc files, possible values: ["minute", "hour", "day"].
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
        collections: Optional[list] = None,
        rolling_rate: Optional[str] = None,
        destination: Optional[Destination] = None,
        sampling_rate: Optional[float] = None,
        request_logging: Optional[RequestLogging] = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.collections = collections
        self.rolling_rate = rolling_rate
        self.destination = destination
        self.sampling_rate = sampling_rate
        self.request_logging = request_logging

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DataCollectorSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
