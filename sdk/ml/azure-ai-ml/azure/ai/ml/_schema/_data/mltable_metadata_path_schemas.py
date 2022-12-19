# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class MLTableMetadataPathFileSchema(metaclass=PatchedSchemaMeta):
    file = fields.Str(
        metadata={"description": "This specifies path of file containing data."},
        required=True,
    )


class MLTableMetadataPathFolderSchema(metaclass=PatchedSchemaMeta):
    folder = fields.Str(
        metadata={"description": "This specifies path of folder containing data."},
        required=True,
    )


class MLTableMetadataPathPatternSchema(metaclass=PatchedSchemaMeta):
    pattern = fields.Str(
        metadata={
            "description": "This specifies a search pattern to allow globbing of files and folders containing data."
        },
        required=True,
    )
