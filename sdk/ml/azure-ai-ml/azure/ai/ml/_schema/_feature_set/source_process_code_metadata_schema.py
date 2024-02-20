# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class SourceProcessCodeSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str(required=True, allow_none=False)
    process_class = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.source_process_code_metadata import SourceProcessCodeMetadata

        return SourceProcessCodeMetadata(**data)
