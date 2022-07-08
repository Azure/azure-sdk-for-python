# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, validate

from .artifact import ArtifactSchema
from .asset import AnonymousAssetSchema
from azure.ai.ml.constants import AssetTypes


class DataSchema(ArtifactSchema):
    path = fields.Str(metadata={"description": "URI pointing to a file or folder."}, required=True)
    type = fields.Str(
        metadata={"description": "the type of data. Valid values are uri_file, uri_folder, or mltable."},
        validate=validate.OneOf([AssetTypes.URI_FILE, AssetTypes.URI_FOLDER, AssetTypes.MLTABLE]),
        default=AssetTypes.URI_FOLDER,
        error_messages={"validator_failed": "value must be uri_file, uri_folder, or mltable."},
    )


class AnonymousDataSchema(DataSchema, AnonymousAssetSchema):
    pass
