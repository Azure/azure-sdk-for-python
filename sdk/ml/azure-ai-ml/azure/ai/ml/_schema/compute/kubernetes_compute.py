# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from .compute import ComputeSchema, IdentitySchema
from ..core.fields import NestedField, StringTransformedEnum
from azure.ai.ml.constants import ComputeType


class KubernetesComputeSchema(ComputeSchema):
    type = StringTransformedEnum(allowed_values=[ComputeType.KUBERNETES], required=True)
    namespace = fields.Str(required=True, default="default")
    properties = fields.Dict()
    identity = NestedField(IdentitySchema)
