# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema import NestedField, PatchedSchemaMeta, StringTransformedEnum
from azure.ai.ml._schema._deployment.online.destination_schema import DestinationSchema
from azure.ai.ml._schema._deployment.online.request_logging_schema import RequestLoggingSchema
from azure.ai.ml._schema._deployment.online.sampling_strategy_schema import SamplingStrategySchema
from azure.ai.ml.constants._common import RollingRate

module_logger = logging.getLogger(__name__)


class DataCollectorSchema(metaclass=PatchedSchemaMeta):
    enabled = fields.Bool()
    rolling_rate = StringTransformedEnum(
        required=False,
        allowed_values=[RollingRate.HOUR, RollingRate.YEAR, RollingRate.MONTH, RollingRate.DAY, RollingRate.MINUTE],
    )
    destination = NestedField(DestinationSchema)
    sampling_strategy = NestedField(SamplingStrategySchema)
    request_logging = NestedField(RequestLoggingSchema)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._deployment.data_collector import DataCollector

        return DataCollector(**data)
