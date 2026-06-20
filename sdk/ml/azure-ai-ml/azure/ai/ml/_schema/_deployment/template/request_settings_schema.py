# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental

module_logger = logging.getLogger(__name__)


@experimental
class RequestSettingsSchema(metaclass=PatchedSchemaMeta):
    request_timeout_ms = fields.Int(required=False)
    max_concurrent_requests_per_instance = fields.Int(required=False)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.deployment_template_settings import OnlineRequestSettings

        return OnlineRequestSettings(**data)
