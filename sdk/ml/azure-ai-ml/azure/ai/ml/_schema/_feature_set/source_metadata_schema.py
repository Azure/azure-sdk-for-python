# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

from .delay_metadata_schema import DelayMetadataSchema
from .timestamp_column_metadata_schema import TimestampColumnMetadataSchema


class SourceMetadataSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(required=True)
    path = fields.Str(required=True)
    timestamp_column = NestedField(TimestampColumnMetadataSchema)
    source_delay = NestedField(DelayMetadataSchema)

    @post_load
    def make(self, data: Dict, **kwargs):
        from azure.ai.ml.entities._feature_set.source_metadata import SourceMetadata

        return SourceMetadata(**data)
