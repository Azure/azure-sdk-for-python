# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class ManagedIdentityConfigurationSchema(metaclass=PatchedSchemaMeta):
    client_id = fields.Str()
    resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._credentials import ManagedIdentityConfiguration

        return ManagedIdentityConfiguration(
            client_id=data.pop("client_id"),
            resource_id=data.pop("resource_id"),
        )
