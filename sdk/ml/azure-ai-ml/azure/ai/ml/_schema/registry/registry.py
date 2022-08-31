# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.resource import ResourceSchema
from .registry_region_arm_details import RegistryRegionArmDetailsSchema


# Initally based on registry.yaml from azureml_run_specification master branch in Aug '22.
class RegistrySchema(ResourceSchema):
    # Already has name, id, tag, description from parent
    region_details = fields.List(NestedField(RegistryRegionArmDetailsSchema))
