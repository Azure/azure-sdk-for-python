# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import DumpableStringField, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.intellectual_property import PublisherSchema
from azure.ai.ml._schema.core.resource import ResourceSchema
from azure.ai.ml._schema.workspace.identity import IdentitySchema
from azure.ai.ml._utils.utils import snake_to_pascal
from azure.ai.ml.constants._common import PublicNetworkAccess
from azure.ai.ml.constants._registry import AcrAccountSku
from azure.ai.ml.entities._registry.registry_support_classes import SystemCreatedAcrAccount

from .registry_region_arm_details import RegistryRegionDetailsSchema
from .system_created_acr_account import SystemCreatedAcrAccountSchema
from .util import acr_format_validator


# Based on 10-01-preview api
class RegistrySchema(ResourceSchema):
    # Inherits name, id, tags, and description fields from ResourceSchema

    # Values from RegistryTrackedResource (Client name: Registry)
    location = fields.Str(required=True)

    # Values from Registry (Client name: RegistryProperties)
    public_network_access = StringTransformedEnum(
        allowed_values=[PublicNetworkAccess.DISABLED, PublicNetworkAccess.ENABLED],
        casing_transform=snake_to_pascal,
    )
    replication_locations = fields.List(NestedField(RegistryRegionDetailsSchema))
    intellectual_property = NestedField(PublisherSchema)
    # This is an acr account which will be applied to every registryRegionArmDetail defined
    # in replication_locations. This is different from the internal swagger
    # definition, which has a per-region list of acr accounts.
    # Per-region acr account configuration is NOT possible through yaml configs for now.
    container_registry = UnionField(
        [DumpableStringField(validate=acr_format_validator), NestedField(SystemCreatedAcrAccountSchema)],
        required=False,
        is_strict=True,
        load_default=SystemCreatedAcrAccount(acr_account_sku=AcrAccountSku.PREMIUM),
    )

    # Values that can only be set by return values from the system, never
    # set by the user.
    identity = NestedField(IdentitySchema, dump_only=True)
    kind = fields.Str(dump_only=True)
    sku = fields.Str(dump_only=True)
    managed_resource_group = fields.Str(dump_only=True)
    mlflow_registry_uri = fields.Str(dump_only=True)
    discovery_url = fields.Str(dump_only=True)
