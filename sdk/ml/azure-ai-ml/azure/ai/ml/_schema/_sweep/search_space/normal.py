# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import ValidationError, fields, post_load
from marshmallow.decorators import pre_dump

from azure.ai.ml._schema.core.fields import DumpableIntegerField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants._common import TYPE
from azure.ai.ml.constants._job.sweep import SearchSpace


class NormalSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=SearchSpace.NORMAL_LOGNORMAL)
    mu = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)
    sigma = UnionField([DumpableIntegerField(strict=True), fields.Float()], required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import LogNormal, Normal

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
        from azure.ai.ml.sweep import QLogNormal, QNormal

        return QNormal(**data) if data[TYPE] == SearchSpace.QNORMAL else QLogNormal(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import QLogNormal, QNormal

        if not isinstance(data, (QNormal, QLogNormal)):
            raise ValidationError("Cannot dump non-QNormal or non-QLogNormal object into QNormalSchema")
        return data


class IntegerQNormalSchema(QNormalSchema):
    mu = DumpableIntegerField(strict=True, required=True)
    sigma = DumpableIntegerField(strict=True, required=True)
    q = DumpableIntegerField(strict=True, required=True)
