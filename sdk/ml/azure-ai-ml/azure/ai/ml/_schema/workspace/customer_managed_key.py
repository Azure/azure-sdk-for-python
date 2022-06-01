# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema import PatchedSchemaMeta
from marshmallow import fields, post_load


class CustomerManagedKeySchema(metaclass=PatchedSchemaMeta):
    key_vault = fields.Str()
    key_uri = fields.Url()
    cosmosdb_id = fields.Str()
    storage_id = fields.Str()
    search_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import CustomerManagedKey

        return CustomerManagedKey(**data)
