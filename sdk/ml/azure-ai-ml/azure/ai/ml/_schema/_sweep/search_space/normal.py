# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow.decorators import pre_dump
from azure.ai.ml.constants import TYPE, SearchSpace
from marshmallow import fields, post_load, ValidationError
from azure.ai.ml._schema.core.fields import StringTransformedEnum, UnionField, DumpableIntegerField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class NormalSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=SearchSpace.NORMAL_LOGNORMAL)
    mu = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)
    sigma = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import Normal, LogNormal

        return Normal(**data) if data[TYPE] == SearchSpace.NORMAL else LogNormal(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import Normal

        if not isinstance(data, Normal):
            raise ValidationError("Cannot dump non-Normal object into NormalSchema")
        return data


class QNormalSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=SearchSpace.QNORMAL_QLOGNORMAL)
    mu = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)
    sigma = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)
    q = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import QNormal, QLogNormal

        return QNormal(**data) if data[TYPE] == SearchSpace.QNORMAL else QLogNormal(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import QNormal, QLogNormal

        if not (isinstance(data, QNormal) or isinstance(data, QLogNormal)):
            raise ValidationError("Cannot dump non-QNormal or non-QLogNormal object into QNormalSchema")
        return data
