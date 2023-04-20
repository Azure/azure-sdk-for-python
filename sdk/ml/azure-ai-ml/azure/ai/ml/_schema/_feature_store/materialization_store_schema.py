# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class MaterializationStoreSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str()
    target = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_store.materialization_store import MaterializationStore

        return MaterializationStore(
            type=data.pop("type"),
            target=data.pop("target"),
        )
