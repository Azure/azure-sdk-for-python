# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class VmSizeSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str()
    family = fields.Str()
    v_cp_us = fields.Int()
    gpus = fields.Int()
    os_vhd_size_mb = fields.Int()
    max_resource_volume_mb = fields.Int()
    memory_gb = fields.Float()
    low_priority_capable = fields.Bool()
    premium_io = fields.Bool()
    supported_compute_types = fields.Str()
