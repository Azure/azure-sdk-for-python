# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class DataCollectorSchema(metaclass=PatchedSchemaMeta):
    enabled = fields.Bool()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._deployment.data_collector import DataCollector

        return DataCollector(**data)
