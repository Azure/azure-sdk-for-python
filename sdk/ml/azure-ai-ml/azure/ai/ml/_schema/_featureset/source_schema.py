# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

from .delay_schema import DelaySchema
from .timestamp_column_schema import TimestampColumnSchema


class SourceSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(required=True)
    path = fields.Str(required=True)
    timestamp_column = NestedField(TimestampColumnSchema)
    source_delay = NestedField(DelaySchema)

    @post_load
    def make(self, data: Dict, **kwargs):
        from azure.ai.ml.entities._featureset.source import Source

        return Source(**data)
