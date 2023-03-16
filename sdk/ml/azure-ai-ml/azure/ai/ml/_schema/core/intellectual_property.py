# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-self-use,unused-kwargs

from marshmallow import fields, post_load
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import IPProtectionLevel
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty


@experimental
class IntellectualPropertySchema(metaclass=PatchedSchemaMeta):

    publisher = fields.String()
    protection_level = StringTransformedEnum(
        allowed_values=[level.name for level in IPProtectionLevel],
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs) -> "IntellectualProperty":

        return IntellectualProperty(**data)
