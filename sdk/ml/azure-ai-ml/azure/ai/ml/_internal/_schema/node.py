# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import INCLUDE, post_load, pre_dump

from azure.ai.ml._schema import ArmVersionedStr, NestedField, RegistryStr, StringTransformedEnum, UnionField
from azure.ai.ml._schema.pipeline.component_job import BaseNodeSchema, _resolve_inputs_outputs
from azure.ai.ml.constants import AzureMLResourceType
from .component import NodeType
from .component import InternalBaseComponentSchema
from ..._schema.resource_configuration import ResourceConfigurationSchema


class InternalBaseNodeSchema(BaseNodeSchema):
    component = UnionField(
        [
            # for registry type assets
            RegistryStr(),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
            # inline component or component file reference starting with FILE prefix
            NestedField(InternalBaseComponentSchema, unknown=INCLUDE),
        ],
        required=True,
    )
    type = StringTransformedEnum(
        allowed_values=NodeType.all_values(),
        casing_transform=lambda x: x,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._builders import parse_inputs_outputs

        # parse inputs/outputs
        data = parse_inputs_outputs(data)
        return data

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)
