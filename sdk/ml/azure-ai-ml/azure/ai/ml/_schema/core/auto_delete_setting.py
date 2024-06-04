# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import AutoDeleteCondition
from azure.ai.ml.entities._assets.auto_delete_setting import AutoDeleteSetting


@experimental
class BaseAutoDeleteSettingSchema(metaclass=PatchedSchemaMeta):
    @post_load
    def make(self, data, **kwargs) -> "AutoDeleteSetting":
        return AutoDeleteSetting(**data)


@experimental
class AutoDeleteConditionSchema(BaseAutoDeleteSettingSchema):
    condition = StringTransformedEnum(
        allowed_values=[condition.name for condition in AutoDeleteCondition],
        casing_transform=camel_to_snake,
    )


@experimental
class ValueSchema(BaseAutoDeleteSettingSchema):
    value = fields.Str()


@experimental
class AutoDeleteSettingSchema(AutoDeleteConditionSchema, ValueSchema):
    pass
