# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, EXCLUDE

from azure.ai.ml._schema._utils.utils import validate_arm_str
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.workspace.customer_managed_key import CustomerManagedKeySchema
from azure.ai.ml._schema.workspace.identity import IdentitySchema, UserAssignedIdentitySchema
from azure.ai.ml._utils.utils import snake_to_pascal
from azure.ai.ml.constants._common import PublicNetworkAccess
from azure.ai.ml._schema.workspace.networking import ManagedNetworkSchema
from .compute_runtime_schema import ComputeRuntimeSchema
from .materialization_store_schema import MaterializationStoreSchema


class FeatureStoreSchema(PathAwareSchema):
    name = fields.Str(required=True)
    compute_runtime = NestedField(ComputeRuntimeSchema)
    offline_store = NestedField(MaterializationStoreSchema)
    online_store = NestedField(MaterializationStoreSchema)
    materialization_identity = NestedField(UserAssignedIdentitySchema)
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    display_name = fields.Str()
    location = fields.Str()
    resource_group = fields.Str()
    hbi_workspace = fields.Bool()
    storage_account = fields.Str(validate=validate_arm_str)
    container_registry = fields.Str(validate=validate_arm_str)
    key_vault = fields.Str(validate=validate_arm_str)
    application_insights = fields.Str(validate=validate_arm_str)
    customer_managed_key = NestedField(CustomerManagedKeySchema)
    image_build_compute = fields.Str()
    public_network_access = StringTransformedEnum(
        allowed_values=[PublicNetworkAccess.DISABLED, PublicNetworkAccess.ENABLED],
        casing_transform=snake_to_pascal,
    )
    identity = NestedField(IdentitySchema)
    primary_user_assigned_identity = fields.Str()
    managed_network = NestedField(ManagedNetworkSchema, unknown=EXCLUDE)
