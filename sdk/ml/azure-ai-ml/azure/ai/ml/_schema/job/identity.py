# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    AmlToken,
    ManagedIdentity,
    UserIdentity,
    IdentityConfigurationType,
)
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from marshmallow import fields, post_load

from ..core.schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class ManagedIdentitySchema(metaclass=PatchedSchemaMeta):
    identity_type = StringTransformedEnum(
        data_key="type",
        name="type",
        required=True,
        allowed_values=IdentityConfigurationType.MANAGED,
        casing_transform=camel_to_snake,
    )
    client_id = fields.Str()
    object_id = fields.Str()
    msi_resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return ManagedIdentity(**data)


class AMLTokenIdentitySchema(metaclass=PatchedSchemaMeta):
    identity_type = StringTransformedEnum(
        data_key="type",
        name="type",
        required=True,
        allowed_values=IdentityConfigurationType.AML_TOKEN,
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs):
        return AmlToken(**data)


class UserIdentitySchema(metaclass=PatchedSchemaMeta):
    identity_type = StringTransformedEnum(
        data_key="type",
        name="type",
        required=True,
        allowed_values=IdentityConfigurationType.USER_IDENTITY,
        casing_transform=camel_to_snake,
    )

    @post_load
    def make(self, data, **kwargs):
        return UserIdentity(**data)
