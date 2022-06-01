# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.core.schema import YamlFileSchema

from azure.ai.ml._schema.assets.dataset_paths import PathSchema
from marshmallow import fields, post_load

from azure.ai.ml._schema import NestedField
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY


class MLTableMetadataSchema(YamlFileSchema):
    paths = fields.List(NestedField(PathSchema()), required=True)
    transformations = fields.List(fields.Raw(), required=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._data.mltable_metadata import MLTableMetadata

        return MLTableMetadata(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
