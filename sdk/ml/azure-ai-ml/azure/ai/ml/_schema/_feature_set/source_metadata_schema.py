# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

from .delay_metadata_schema import DelayMetadataSchema
from .source_process_code_metadata_schema import SourceProcessCodeSchema
from .timestamp_column_metadata_schema import TimestampColumnMetadataSchema


class SourceMetadataSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(required=True)
    path = UnionField([fields.Str(), fields.Dict()], required=True)
    timestamp_column = fields.Nested(TimestampColumnMetadataSchema, required=True)
    source_delay = fields.Nested(DelayMetadataSchema, required=False)
    source_process_code = fields.Nested(SourceProcessCodeSchema, required=False)

    @post_load
    def make(self, data: Dict, **kwargs):
        from azure.ai.ml.entities._feature_set.source_metadata import SourceMetadata

        return SourceMetadata(**data)
