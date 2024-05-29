# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import DataCollector as RestDataCollector
from azure.ai.ml._schema._deployment.online.data_collector_schema import DataCollectorSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._deployment.deployment_collection import DeploymentCollection
from azure.ai.ml.entities._deployment.request_logging import RequestLogging


@experimental
class DataCollector:
    """Data Capture deployment entity.

    :param collections: Mapping dictionary of strings mapped to DeploymentCollection entities.
    :type collections: Mapping[str, DeploymentCollection]
    :param rolling_rate: The rolling rate of mdc files, possible values: ["minute", "hour", "day"].
    :type rolling_rate: str
    :param sampling_rate: The sampling rate of mdc files, possible values: [0.0, 1.0].
    :type sampling_rate: float
    :param request_logging: Logging of request payload parameters.
    :type request_logging: RequestLogging
    """

    def __init__(
        self,
        collections: Dict[str, DeploymentCollection],
        *,
        rolling_rate: Optional[str] = None,
        sampling_rate: Optional[float] = None,
        request_logging: Optional[RequestLogging] = None,
        **kwargs: Any,
    ):  # pylint: disable=unused-argument
        self.collections = collections
        self.rolling_rate = rolling_rate
        self.sampling_rate = sampling_rate
        self.request_logging = request_logging

        if self.sampling_rate:
            for collection in self.collections.values():
                collection.sampling_rate = self.sampling_rate

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = DataCollectorSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _from_rest_object(cls, rest_obj: RestDataCollector) -> "DataCollector":
        collections = {}
        sampling_rate = None
        for k, v in rest_obj.collections.items():
            sampling_rate = v.sampling_rate
            collections[k] = DeploymentCollection._from_rest_object(v)
            delattr(collections[k], "sampling_rate")

        return DataCollector(
            collections=collections,
            rolling_rate=rest_obj.rolling_rate,
            request_logging=(
                RequestLogging._from_rest_object(rest_obj.request_logging) if rest_obj.request_logging else None
            ),
            sampling_rate=sampling_rate,
        )

    def _to_rest_object(self) -> RestDataCollector:
        rest_collections: dict = {}
        for collection in self.collections.values():
            collection.sampling_rate = self.sampling_rate
        delattr(self, "sampling_rate")
        if self.request_logging:
            self.request_logging = self.request_logging._to_rest_object()
        if self.collections:
            rest_collections = {}
            for k, v in self.collections.items():
                rest_collections[k] = v._to_rest_object()
        return RestDataCollector(
            collections=rest_collections, rolling_rate=self.rolling_rate, request_logging=self.request_logging
        )
