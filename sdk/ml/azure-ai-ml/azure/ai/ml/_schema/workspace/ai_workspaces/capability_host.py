# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._utils._experimental import experimental


@experimental
class CapabilityHostSchema(PathAwareSchema):
    name = fields.Str()
    description = fields.Str()
    capability_host_kind = fields.Str()
    vector_store_connections = fields.List(fields.Str(), required=False)
    ai_services_connections = fields.List(fields.Str(), required=False)
    storage_connections = fields.List(fields.Str(), required=False)
    thread_storage_connections = fields.List(fields.Str(), required=False)
