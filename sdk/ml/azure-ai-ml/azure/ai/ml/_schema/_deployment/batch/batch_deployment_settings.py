# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from azure.ai.ml._schema import PatchedSchemaMeta
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from marshmallow import fields, post_load

module_logger = logging.getLogger(__name__)


class BatchRetrySettingsSchema(metaclass=PatchedSchemaMeta):
    max_retries = fields.Int(
        metadata={"description": "The number of maximum tries for a failed or timeout mini batch."},
    )
    timeout = fields.Int(metadata={"description": "The timeout for a mini batch."})

    @post_load
    def make(self, data: Any, **kwargs: Any) -> BatchRetrySettings:
        return BatchRetrySettings(**data)
