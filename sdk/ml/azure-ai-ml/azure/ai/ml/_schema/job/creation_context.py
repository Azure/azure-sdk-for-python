# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields
from azure.ai.ml._schema import PatchedSchemaMeta


class CreationContextSchema(metaclass=PatchedSchemaMeta):
    created_at = fields.DateTime()
    created_by = fields.Str()
    created_by_type = fields.Str()
    last_modified_at = fields.DateTime()
    last_modified_by = fields.Str()
    last_modified_by_type = fields.Str()
