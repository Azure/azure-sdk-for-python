# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


@experimental
class WorkspaceHubConfigSchema(metaclass=PatchedSchemaMeta):
    additional_workspace_storage_accounts = fields.List(fields.Str())
    default_workspace_resource_group = fields.Str()
