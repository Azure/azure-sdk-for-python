# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class EndpointConnectionSchema(metaclass=PatchedSchemaMeta):
    subscription_id = fields.UUID()
    resource_group = fields.Str()
    location = fields.Str()
    vnet_name = fields.Str()
    subnet_name = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import EndpointConnection

        return EndpointConnection(**data)
