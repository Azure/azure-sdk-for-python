# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class ComputeRuntimeSchema(metaclass=PatchedSchemaMeta):
    spark_runtime_version = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._workspace.compute_runtime import ComputeRuntime

        return ComputeRuntime(spark_runtime_version=data.pop("spark_runtime_version"))
