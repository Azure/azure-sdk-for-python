# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema._utils.utils import validate_arm_str
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.workspace.customer_managed_key import CustomerManagedKeySchema
from azure.ai.ml._schema.workspace.identity import IdentitySchema
from azure.ai.ml._utils.utils import snake_to_pascal
from azure.ai.ml.constants._common import PublicNetworkAccess
from azure.ai.ml._schema.workspace.networking import ManagedNetworkSchema
from azure.ai.ml._schema._workspace_hub.workspace_hub_config import WorkspaceHubConfigSchema

from azure.ai.ml._schema import ExperimentalField
from azure.ai.ml._utils._experimental import experimental


@experimental
class WorkspaceHubSchema(PathAwareSchema):
    name = fields.Str(required=True)
    location = fields.Str()
    id = fields.Str(dump_only=True)
    resource_group = fields.Str()
    description = fields.Str()
    display_name = fields.Str()
    customer_managed_key = NestedField(CustomerManagedKeySchema)
    storage_account = fields.Str(validate=validate_arm_str)
    container_registry = fields.Str(validate=validate_arm_str)
    key_vault = fields.Str(validate=validate_arm_str)
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    public_network_access = StringTransformedEnum(
        allowed_values=[PublicNetworkAccess.DISABLED, PublicNetworkAccess.ENABLED],
        casing_transform=snake_to_pascal,
    )
    identity = NestedField(IdentitySchema)
    primary_user_assigned_identity = fields.Str()
    managed_network = ExperimentalField(NestedField(ManagedNetworkSchema))
    existing_workspaces = fields.List(fields.Str())
    workspace_hub_config = ExperimentalField(NestedField(WorkspaceHubConfigSchema))
    enable_data_isolation = fields.Bool()
