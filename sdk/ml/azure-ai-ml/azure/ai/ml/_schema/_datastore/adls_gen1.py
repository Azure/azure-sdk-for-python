# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict

from azure.ai.ml.constants import AzureMLResourceType
from azure.ai.ml._schema import NestedField, PathAwareSchema
from azure.ai.ml._restclient.v2022_05_01.models import DatastoreType
from azure.ai.ml._schema.core.fields import StringTransformedEnum, UnionField, ArmStr
from azure.ai.ml._utils.utils import camel_to_snake
from marshmallow import fields, post_load

from .credentials import CertificateSchema, NoneCredentialsSchema, ServicePrincipalSchema


class AzureDataLakeGen1Schema(PathAwareSchema):
    name = fields.Str(required=True)
    id = ArmStr(azureml_type=AzureMLResourceType.DATASTORE, dump_only=True)
    type = StringTransformedEnum(
        allowed_values=DatastoreType.AZURE_DATA_LAKE_GEN1,
        casing_transform=camel_to_snake,
        required=True,
    )
    store_name = fields.Str(required=True)
    credentials = UnionField(
        [NestedField(ServicePrincipalSchema), NestedField(CertificateSchema), NestedField(NoneCredentialsSchema)]
    )
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Dict())

    @post_load
    def make(self, data: Dict[str, Any], **kwargs) -> "AzureDataLakeGen1Datastore":
        from azure.ai.ml.entities import AzureDataLakeGen1Datastore

        return AzureDataLakeGen1Datastore(**data)
