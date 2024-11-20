# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.schema import PathAwareSchema

class CapabilityHostSchema(PathAwareSchema):
    name = fields.Str(required = True)
    description = fields.Str(required = False)
    capability_host_kind = fields.Str()
    vector_store_connections = fields.List(fields.Str(), required = True)
    ai_services_connections =fields.List(fields.Str(), required = True)
    storage_connections = fields.List(fields.Str(), required = False)




