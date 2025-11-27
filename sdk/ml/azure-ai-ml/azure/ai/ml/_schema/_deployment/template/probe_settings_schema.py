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
class ProbeSettingsSchema(metaclass=PatchedSchemaMeta):
    period = fields.Int()
    initial_delay = fields.Int()
    timeout = fields.Int()
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
