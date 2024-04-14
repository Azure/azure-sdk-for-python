# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema import StringTransformedEnum
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._schema.workspace import WorkspaceSchema
from azure.ai.ml.constants import WorkspaceType


@experimental
class ProjectSchema(WorkspaceSchema):
    type = StringTransformedEnum(required=True, allowed_values=WorkspaceType.PROJECT)
    hub_id = fields.Str(required=True)
