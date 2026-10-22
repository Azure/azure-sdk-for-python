# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import OneLakeArtifactTypes

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class OneLakeArtifactSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=OneLakeArtifactTypes.ONE_LAKE, casing_transform=camel_to_snake, required=True
    )
    name = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import OneLakeConnectionArtifact

        return OneLakeConnectionArtifact(**data)
