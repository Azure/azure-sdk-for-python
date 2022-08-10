# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields

from azure.ai.ml.constants import ComputeType

from ..core.fields import NestedField, StringTransformedEnum
from .compute import ComputeSchema, IdentitySchema


class KubernetesComputeSchema(ComputeSchema):
    type = StringTransformedEnum(allowed_values=[ComputeType.KUBERNETES], required=True)
    namespace = fields.Str(required=True, dump_default="default")
    properties = fields.Dict()
    identity = NestedField(IdentitySchema)
