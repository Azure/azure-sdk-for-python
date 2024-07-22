# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Any, Dict

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_10_01.models import DatastoreType
from azure.ai.ml._schema.core.fields import NestedField, PathAwareSchema, StringTransformedEnum, UnionField
from azure.ai.ml._utils.utils import camel_to_snake

from .credentials import (
    AccountKeySchema,
    CertificateSchema,
    NoneCredentialsSchema,
    SasTokenSchema,
    ServicePrincipalSchema,
)


class AzureStorageSchema(PathAwareSchema):
    name = fields.Str(required=True)
    id = fields.Str(dump_only=True)
    account_name = fields.Str(required=True)
    endpoint = fields.Str()
    protocol = fields.Str()
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())


class AzureFileSchema(AzureStorageSchema):
    type = StringTransformedEnum(
        allowed_values=DatastoreType.AZURE_FILE,
        casing_transform=camel_to_snake,
        required=True,
    )
    file_share_name = fields.Str(required=True)
    credentials = UnionField(
        [
            NestedField(AccountKeySchema),
            NestedField(SasTokenSchema),
            NestedField(NoneCredentialsSchema),
        ]
    )

    @post_load
    def make(self, data: Dict[str, Any], **kwargs) -> "AzureFileDatastore":  # type: ignore[name-defined]
        from azure.ai.ml.entities import AzureFileDatastore

        return AzureFileDatastore(**data)


class AzureBlobSchema(AzureStorageSchema):
    type = StringTransformedEnum(
        allowed_values=DatastoreType.AZURE_BLOB,
        casing_transform=camel_to_snake,
        required=True,
    )
    container_name = fields.Str(required=True)
    credentials = UnionField(
        [
            NestedField(AccountKeySchema),
            NestedField(SasTokenSchema),
            NestedField(NoneCredentialsSchema),
        ],
    )

    @post_load
    def make(self, data: Dict[str, Any], **kwargs) -> "AzureBlobDatastore":  # type: ignore[name-defined]
        from azure.ai.ml.entities import AzureBlobDatastore

        return AzureBlobDatastore(**data)


class AzureDataLakeGen2Schema(AzureStorageSchema):
    type = StringTransformedEnum(
        allowed_values=DatastoreType.AZURE_DATA_LAKE_GEN2,
        casing_transform=camel_to_snake,
        required=True,
    )
    filesystem = fields.Str(required=True)
    credentials = UnionField(
        [
            NestedField(ServicePrincipalSchema),
            NestedField(CertificateSchema),
            NestedField(NoneCredentialsSchema),
        ]
    )

    @post_load
    def make(self, data: Dict[str, Any], **kwargs) -> "AzureDataLakeGen2Datastore":
        from azure.ai.ml.entities import AzureDataLakeGen2Datastore

        return AzureDataLakeGen2Datastore(**data)
