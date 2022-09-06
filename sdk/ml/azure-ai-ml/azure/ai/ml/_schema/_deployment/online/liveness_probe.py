# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class LivenessProbeSchema(metaclass=PatchedSchemaMeta):
    period = fields.Int()
    initial_delay = fields.Int()
    timeout = fields.Int()
    success_threshold = fields.Int()
    failure_threshold = fields.Int()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import ProbeSettings

        return ProbeSettings(**data)
