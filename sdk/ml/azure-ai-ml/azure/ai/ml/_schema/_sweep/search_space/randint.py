# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants._job.sweep import SearchSpace


class RandintSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=SearchSpace.RANDINT)
    upper = fields.Integer(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import Randint

        return Randint(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import Randint

        if not isinstance(data, Randint):
            raise ValidationError("Cannot dump non-Randint object into RandintSchema")
        return data
