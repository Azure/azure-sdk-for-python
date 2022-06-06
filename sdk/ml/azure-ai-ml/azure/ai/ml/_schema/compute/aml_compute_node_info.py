# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class AmlComputeNodeInfoSchema(metaclass=PatchedSchemaMeta):
    node_id = fields.Str()
    private_ip_address = fields.Str()
    public_ip_address = fields.Str()
    port = fields.Str()
    node_state = fields.Str()
    current_job_name = fields.Str()
