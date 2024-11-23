# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.schema import PathAwareSchema

class CapabilityHostSchema(PathAwareSchema):
    name = fields.Str()
    description = fields.Str()
    capability_host_kind = fields.Str()
    vector_store_connections = fields.List(fields.Str())
    ai_services_connections =fields.List(fields.Str())
    storage_connections = fields.List(fields.Str())




