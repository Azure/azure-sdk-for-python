# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from .compute import ComputeSchema


class AttachedComputeSchema(ComputeSchema):
    resource_id = fields.Str(required=True)
    ssh_port = fields.Int()
    compute_location = fields.Str()
