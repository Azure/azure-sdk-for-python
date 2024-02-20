# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import ValidationError, fields, post_load, validates

from azure.ai.ml._schema import NestedField, PatchedSchemaMeta
from azure.ai.ml._schema._deployment.online.oversize_data_config_schema import OversizeDataConfigSchema

module_logger = logging.getLogger(__name__)


class EventHubSchema(metaclass=PatchedSchemaMeta):
    namespace = fields.Str()
    oversize_data_config = NestedField(OversizeDataConfigSchema)

    @validates("namespace")
    def validate_namespace(self, value, **kwargs):
        if len(value.split(".")) != 2:
            raise ValidationError("Namespace must follow format of {namespace}.{name}")

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.event_hub import EventHub

        return EventHub(**data)
