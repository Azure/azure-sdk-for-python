# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema import StringTransformedEnum
from azure.ai.ml._schema.workspace import WorkspaceSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants import WorkspaceKind


@experimental
class HubSchema(WorkspaceSchema):
    # additional_workspace_storage_accounts This field exists in the API, but is unused, and thus not surfaced yet.
    kind = StringTransformedEnum(required=True, allowed_values=WorkspaceKind.HUB)
    default_resource_group = fields.Str(required=False)
    associated_workspaces = fields.List(fields.Str(), required=False, dump_only=True)
