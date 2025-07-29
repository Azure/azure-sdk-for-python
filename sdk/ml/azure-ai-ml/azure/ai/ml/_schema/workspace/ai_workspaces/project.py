# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema import StringTransformedEnum
from azure.ai.ml._schema.workspace import WorkspaceSchema
from azure.ai.ml.constants import WorkspaceKind


class ProjectSchema(WorkspaceSchema):
    kind = StringTransformedEnum(required=True, allowed_values=WorkspaceKind.PROJECT)
    hub_id = fields.Str(required=True)
