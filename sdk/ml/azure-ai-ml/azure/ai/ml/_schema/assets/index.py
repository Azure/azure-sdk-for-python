# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import ArmStr
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AzureMLResourceType

from .artifact import ArtifactSchema


class IndexAssetSchema(ArtifactSchema):
    name = fields.Str(required=True, allow_none=False)
    id = ArmStr(azureml_type=AzureMLResourceType.INDEX, dump_only=True)
    stage = fields.Str(default="Development")
    path = fields.Str(
        required=True,
        metadata={
            "description": "A local path or a Blob URI pointing to a file or directory where index files are located."
        },
    )
    properties = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets import Index

        return Index(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
