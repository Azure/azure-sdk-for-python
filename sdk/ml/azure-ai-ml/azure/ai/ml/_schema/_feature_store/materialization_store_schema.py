# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load

from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from .compute_runtime_schema import ComputeRuntimeSchema


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
