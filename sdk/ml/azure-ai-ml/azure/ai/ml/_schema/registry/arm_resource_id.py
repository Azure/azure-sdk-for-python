# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class ArmResourceIdSchema(metaclass=PatchedSchemaMeta):
    resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml._restclient.v2022_10_01_preview.models import ArmResourceId

        data.pop("type", None)
        return ArmResourceId(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml._restclient.v2022_10_01_preview.models import ArmResourceId

        if not isinstance(data, ArmResourceId):
            raise ValidationError("Cannot dump non-ArmResourceId object into ArmResourceId")
        return data
