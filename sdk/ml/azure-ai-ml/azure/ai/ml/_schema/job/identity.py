# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_10_01_preview.models import IdentityConfigurationType
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._job.identity import AmlToken, ManagedIdentity, UserIdentity

from ..core.schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class ManagedIdentitySchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        required=True,
        allowed_values=IdentityConfigurationType.MANAGED,
        casing_transform=camel_to_snake,
    )
    client_id = fields.Str()
    object_id = fields.Str()
    msi_resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        data.pop("type")
        return ManagedIdentity(**data)


class AMLTokenIdentitySchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        required=True,
        allowed_values=IdentityConfigurationType.AML_TOKEN,
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs):
        data.pop("type")
        return AmlToken(**data)


class UserIdentitySchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        required=True,
        allowed_values=IdentityConfigurationType.USER_IDENTITY,
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs):
        data.pop("type")
        return UserIdentity(**data)
