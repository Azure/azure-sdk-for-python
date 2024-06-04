# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._assets import IPProtectionLevel
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty


@experimental
class BaseIntellectualPropertySchema(metaclass=PatchedSchemaMeta):
    @post_load
    def make(self, data, **kwargs) -> "IntellectualProperty":
        return IntellectualProperty(**data)


@experimental
class ProtectionLevelSchema(BaseIntellectualPropertySchema):
    protection_level = StringTransformedEnum(
        allowed_values=[level.name for level in IPProtectionLevel],
        casing_transform=camel_to_snake,
    )


@experimental
class PublisherSchema(BaseIntellectualPropertySchema):
    publisher = fields.Str()


@experimental
class IntellectualPropertySchema(ProtectionLevelSchema, PublisherSchema):
    pass
