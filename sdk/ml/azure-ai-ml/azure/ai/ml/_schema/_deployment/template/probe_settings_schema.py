# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class ProbeSettingsSchema(metaclass=PatchedSchemaMeta):
    period = fields.Str()
    initial_delay = fields.Str()
    timeout = fields.Str()
    success_threshold = fields.Int()
    failure_threshold = fields.Int()
    scheme = fields.Str()
    method = fields.Str()
    path = fields.Str()
    port = fields.Int()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings

        return ProbeSettings(**data)
