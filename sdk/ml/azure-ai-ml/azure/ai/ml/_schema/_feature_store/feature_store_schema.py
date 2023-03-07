# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema._utils.utils import validate_arm_str
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.workspace.customer_managed_key import CustomerManagedKeySchema
from azure.ai.ml._schema.workspace.identity import IdentitySchema
from azure.ai.ml._utils.utils import snake_to_pascal
from azure.ai.ml.constants._common import PublicNetworkAccess
from .compute_runtime_schema import ComputeRuntimeSchema
from .materialization_store_schema import MaterializationStoreSchema
from .managed_identity_schema import ManagedIdentityConfigurationSchema


class FeatureStoreSchema(PathAwareSchema):
    name = fields.Str(required=True)
    compute_runtime = NestedField(ComputeRuntimeSchema)
    offline_store = NestedField(MaterializationStoreSchema)
    materialization_identity = NestedField(ManagedIdentityConfigurationSchema)
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
    mlflow_tracking_uri = fields.Str(dump_only=True)
    image_build_compute = fields.Str()
    public_network_access = StringTransformedEnum(
        allowed_values=[PublicNetworkAccess.DISABLED, PublicNetworkAccess.ENABLED],
        casing_transform=snake_to_pascal,
    )
    identity = NestedField(IdentitySchema)
    primary_user_assigned_identity = fields.Str()
