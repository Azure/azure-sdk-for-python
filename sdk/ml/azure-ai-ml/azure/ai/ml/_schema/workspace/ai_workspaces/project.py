# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import EXCLUDE, fields

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._schema.workspace import WorkspaceSchema

@experimental
class ProjectSchema(WorkspaceSchema):
    hub = fields.Str(required=True)
