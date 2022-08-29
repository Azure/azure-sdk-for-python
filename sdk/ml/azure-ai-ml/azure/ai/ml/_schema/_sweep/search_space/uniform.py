# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema._sweep._constants import BASE_ERROR_MESSAGE
from azure.ai.ml._schema.core.fields import DumpableIntegerField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants import TYPE, SearchSpace


class UniformSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=SearchSpace.UNIFORM_LOGUNIFORM)
    min_value = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)
    max_value = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import LogUniform, Uniform

        if not (isinstance(data, Uniform) or isinstance(data, LogUniform)):
            raise ValidationError("Cannot dump non-Uniform or non-LogUniform object into UniformSchema")
        if data.type.lower() not in SearchSpace.UNIFORM_LOGUNIFORM:
            raise ValidationError(BASE_ERROR_MESSAGE + str(SearchSpace.UNIFORM_LOGUNIFORM))
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import LogUniform, Uniform

        return Uniform(**data) if data[TYPE] == SearchSpace.UNIFORM else LogUniform(**data)


class QUniformSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=SearchSpace.QUNIFORM_QLOGUNIFORM)
    min_value = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)
    max_value = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)
    q = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import QLogUniform, QUniform

        return QUniform(**data) if data[TYPE] == SearchSpace.QUNIFORM else QLogUniform(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import QLogUniform, QUniform

        if not (isinstance(data, QUniform) or isinstance(data, QLogUniform)):
            raise ValidationError("Cannot dump non-QUniform or non-QLogUniform object into UniformSchema")
        return data
