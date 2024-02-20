# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

from .endpoint_connection import EndpointConnectionSchema


class PrivateEndpointSchema(metaclass=PatchedSchemaMeta):
    approval_type = fields.Str()
    connections = fields.Dict(keys=fields.Str(), values=NestedField(EndpointConnectionSchema))

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import PrivateEndpoint

        return PrivateEndpoint(**data)
