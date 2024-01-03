# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Any, Dict

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_10_01_preview.models import DatastoreType
from azure.ai.ml._schema.core.fields import NestedField, PathAwareSchema, StringTransformedEnum, UnionField
from azure.ai.ml._utils.utils import camel_to_snake

from ._on_prem_credentials import KerberosKeytabSchema, KerberosPasswordSchema


class HdfsSchema(PathAwareSchema):
    name = fields.Str(required=True)
    id = fields.Str(dump_only=True)
    type = StringTransformedEnum(
        allowed_values=DatastoreType.HDFS,
        casing_transform=camel_to_snake,
        required=True,
    )
    hdfs_server_certificate = fields.Str()
    name_node_address = fields.Str(required=True)
    protocol = fields.Str()
    credentials = UnionField(
        [NestedField(KerberosPasswordSchema), NestedField(KerberosKeytabSchema)],
        required=True,
    )
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Dict())

    @post_load
    def make(self, data: Dict[str, Any], **kwargs) -> "HdfsDatastore":
        from azure.ai.ml.entities._datastore._on_prem import HdfsDatastore

        return HdfsDatastore(**data)
