# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from .dataset_paths import PathSchema
from marshmallow import fields, post_load, validates, ValidationError

from azure.ai.ml._schema.core.fields import ArmStr
from .artifact import ArtifactSchema
from .asset import AnonymousAssetSchema
from azure.ai.ml._schema import NestedField, UnionField
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AzureMLResourceType


class DatasetSchema(ArtifactSchema):
    id = ArmStr(azureml_type=AzureMLResourceType.DATASET, dump_only=True)
    local_path = fields.Str(metadata={"description": "the path from which the artifact gets uploaded to the cloud"})
    paths = UnionField(
        [
            fields.List(NestedField(PathSchema())),
        ],
        metadata={"description": "URI pointing to file or folder."},
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets import Dataset

        data[BASE_PATH_CONTEXT_KEY] = self.context[BASE_PATH_CONTEXT_KEY]
        return Dataset(**data)

    @validates("paths")
    def validate_paths(self, paths):
        if len(paths) <= 0:
            raise ValidationError("paths size must be greater than 0.")


class AnonymousDatasetSchema(DatasetSchema, AnonymousAssetSchema):
    # This is just a subclass of the two parents; it has no additional implementation
    # Necessary methods are provided by parents.
    pass
