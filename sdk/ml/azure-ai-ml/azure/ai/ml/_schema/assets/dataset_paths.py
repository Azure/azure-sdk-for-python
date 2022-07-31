# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, pre_load, post_load, ValidationError
from azure.ai.ml._schema import PatchedSchemaMeta
from azure.ai.ml._restclient.v2021_10_01.models import UriReference


class PathSchema(metaclass=PatchedSchemaMeta):
    folder = fields.Str(
        metadata={"description": "URI pointing to folder."},
    )
    file = fields.Str(
        metadata={"description": "URI pointing to file."},
    )

    @post_load
    def make(self, data, **kwargs):
        return UriReference(**data)

    @pre_load
    def validate(self, data, **kwargs):
        # AnonymousCodeAssetSchema does not support None or arm string(fall back to ArmVersionedStr)
        folder = data.get("folder", None)
        file = data.get("file", None)
        if not folder and not file:
            raise ValidationError("Please provide one folder path or one file path")
        if folder and file:
            raise ValidationError("Please provide only one folder or one file")
        if folder and not folder.strip():
            raise ValidationError("Please provide valid path for one folder, whitespace is not allowed")
        if file and not file.strip():
            raise ValidationError("Please provide valid path for one file, whitespace is not allowed")
        return data
