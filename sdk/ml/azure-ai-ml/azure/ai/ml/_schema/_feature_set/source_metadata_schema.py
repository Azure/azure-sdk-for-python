# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

from .delay_metadata_schema import DelayMetadataSchema
from .source_process_code_metadata_schema import SourceProcessCodeSchema
from .timestamp_column_metadata_schema import TimestampColumnMetadataSchema


class SourceMetadataSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(required=True)
    path = fields.Str(required=False)
    timestamp_column = fields.Nested(TimestampColumnMetadataSchema, required=False)
    source_delay = fields.Nested(DelayMetadataSchema, required=False)
    source_process_code = fields.Nested(SourceProcessCodeSchema, load_only=True, required=False)
    dict = fields.Dict(keys=fields.Str(), values=fields.Str(), data_key="kwargs", load_only=True, required=False)

    @post_load
    def make(self, data: Dict, **kwargs):
        from azure.ai.ml.entities._feature_set.source_metadata import SourceMetadata

        return SourceMetadata(**data)
