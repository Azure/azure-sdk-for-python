# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema._utils.utils import validate_arm_str
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.workspace.customer_managed_key import CustomerManagedKeySchema
from azure.ai.ml._utils.utils import snake_to_pascal
from azure.ai.ml.constants import PublicNetworkAccess


class WorkspaceSchema(PathAwareSchema):
    name = fields.Str(required=True)
    location = fields.Str()
    id = fields.Str(dump_only=True)
    resource_group = fields.Str()
    description = fields.Str()
    discovery_url = fields.Str()
    display_name = fields.Str()
    hbi_workspace = fields.Bool()
    storage_account = fields.Str(validate=validate_arm_str)
    container_registry = fields.Str(validate=validate_arm_str)
    key_vault = fields.Str(validate=validate_arm_str)
    application_insights = fields.Str(validate=validate_arm_str)
    customer_managed_key = NestedField(CustomerManagedKeySchema)
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    mlflow_tracking_uri = fields.Str(dump_only=True)
    image_build_compute = fields.Str()
    public_network_access = StringTransformedEnum(
        allowed_values=[PublicNetworkAccess.DISABLED, PublicNetworkAccess.ENABLED],
        casing_transform=snake_to_pascal,
    )
    softdelete_enable = fields.Bool()
    allow_recover_softdeleted_workspace = fields.Bool()
