# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Dict

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.core.schema import YamlFileSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

from .mltable_metadata_path_schemas import (
    MLTableMetadataPathFileSchema,
    MLTableMetadataPathFolderSchema,
    MLTableMetadataPathPatternSchema,
)


class MLTableMetadataSchema(YamlFileSchema):
    paths = fields.List(
        UnionField(
            [
                NestedField(MLTableMetadataPathFileSchema()),
                NestedField(MLTableMetadataPathFolderSchema()),
                NestedField(MLTableMetadataPathPatternSchema()),
            ]
        ),
        required=True,
    )
    transformations = fields.List(fields.Raw(), required=False)

    @post_load
    def make(self, data: Dict, **kwargs):
        from azure.ai.ml.entities._data.mltable_metadata import MLTableMetadata, MLTableMetadataPath

        paths = [MLTableMetadataPath(pathDict=pathDict) for pathDict in data.pop("paths")]
        return MLTableMetadata(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data, paths=paths)
