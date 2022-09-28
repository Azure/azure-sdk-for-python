# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.resource import ResourceSchema
from azure.ai.ml._utils.utils import snake_to_pascal
from azure.ai.ml.constants._common import PublicNetworkAccess
from azure.ai.ml.constants._registry import AcrAccountSku
from azure.ai.ml.entities._registry.registry_support_classes import SystemCreatedAcrAccount

from .registry_region_arm_details import RegistryRegionArmDetailsSchema
from .system_created_acr_account import SystemCreatedAcrAccountSchema
from .util import acr_format_validator


# Based on 10-01-preview api
class RegistrySchema(ResourceSchema):
    # Inherits name, id, tag and description fields from ResourceSchema

    # Values from RegistryTrackedResource (Client name: Registry)
    location = fields.Str(required=True)
    # identity = ignored - output only
    # kind = ignored - output only
    # sku = ignored - output only

    # Values from Registry (Client name: RegistryProperties)
    public_network_access = StringTransformedEnum(
        allowed_values=[PublicNetworkAccess.DISABLED, PublicNetworkAccess.ENABLED],
        casing_transform=snake_to_pascal,
    )
    replication_locations = fields.List(NestedField(RegistryRegionArmDetailsSchema))
    intellectual_property_publisher = fields.Str()
    # This is an acr account which will be applied to every registryRegionArmDetail defined
    # in replication_locations. This is different from the internal swagger
    # definition, which has a per-region list of acr accounts.
    # Per-region acr account configuration is NOT possible through yaml configs for now.
    container_registry = UnionField(
        [fields.Str(validate=acr_format_validator), NestedField(SystemCreatedAcrAccountSchema)],
        required=False,
        is_strict=True,
        load_default=SystemCreatedAcrAccount(acr_account_sku=AcrAccountSku.PREMIUM),
    )
    # managed_resource_group = ignored - output only
    # mlflow_registry_uri = ignored - output only
    # discovery_url = ignored - output only
