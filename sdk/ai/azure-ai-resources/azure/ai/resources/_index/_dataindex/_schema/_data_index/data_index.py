# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.assets.data import DataSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr, LocalPathField, NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.job.input_output_entry import generate_datastore_property
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import AssetTypes, AzureMLResourceType, InputOutputModes


# FROM: azure.ai.ml._schema.job.input_output_entry
def generate_path_property(azureml_type, **kwargs):
    return UnionField(
        [
            ArmVersionedStr(azureml_type=azureml_type),
            fields.Str(metadata={"pattern": r"^(http(s)?):.*"}),
            fields.Str(metadata={"pattern": r"^(wasb(s)?):.*"}),
            LocalPathField(pattern=r"^file:.*"),
            LocalPathField(
                pattern=r"^(?!(azureml|http(s)?|wasb(s)?|file):).*",
            ),
        ],
        is_strict=True,
        **kwargs,
    )


class DataIndexTypes:
    """DataIndexTypes is an enumeration of values for the types out indexes which can be written to by DataIndex."""

    ACS = "acs"
    """Azure Cognitive Search index type."""
    FAISS = "faiss"
    """Faiss index type."""


class CitationRegexSchema(metaclass=PatchedSchemaMeta):
    match_pattern = fields.Str(
        required=True,
        metadata={"description": "Regex to match citation in the citation_url + input file path. e.g. '\\1/\\2'"},
    )
    replacement_pattern = fields.Str(
        required=True,
        metadata={"description": r"Replacement string for citation. e.g. '(.*)/articles/(.*)(\.[^.]+)$'"},
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.resources._index._dataindex.entities.data_index import CitationRegex

        return CitationRegex(**data)


class InputDataSchema(metaclass=PatchedSchemaMeta):
    mode = StringTransformedEnum(
        allowed_values=[
            InputOutputModes.RO_MOUNT,
            InputOutputModes.RW_MOUNT,
            InputOutputModes.DOWNLOAD,
        ],
        required=False,
    )
    type = StringTransformedEnum(
        allowed_values=[
            AssetTypes.URI_FILE,
            AssetTypes.URI_FOLDER,
        ]
    )
    path = generate_path_property(azureml_type=AzureMLResourceType.DATA)
    datastore = generate_datastore_property()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import Data

        return Data(**data)


class InputMLTableSchema(metaclass=PatchedSchemaMeta):
    mode = StringTransformedEnum(
        allowed_values=[
            InputOutputModes.EVAL_MOUNT,
            InputOutputModes.EVAL_DOWNLOAD,
        ],
        required=False,
    )
    type = StringTransformedEnum(allowed_values=[AssetTypes.MLTABLE])
    path = generate_path_property(azureml_type=AzureMLResourceType.DATA)
    datastore = generate_datastore_property()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import Data

        return Data(**data)


class IndexSourceSchema(metaclass=PatchedSchemaMeta):
    input_data = UnionField(
        [NestedField(InputDataSchema), NestedField(InputMLTableSchema)],
        required=True,
        allow_none=False,
        metadata={"description": "Input Data to index files from. MLTable type inputs will use `mode: eval_mount`."},
    )
    input_glob = fields.Str(
        required=False,
        metadata={
            "description": "Glob pattern to filter files from input_data. If not specified, all files will be indexed."
        },
    )
    chunk_size = fields.Int(
        required=False,
        allow_none=False,
        metadata={"description": "Maximum number of tokens to put in each chunk."},
    )
    chunk_overlap = fields.Int(
        required=False,
        allow_none=False,
        metadata={"description": "Number of tokens to overlap between chunks."},
    )
    citation_url = fields.Str(
        required=False,
        metadata={"description": "Base URL to join with file paths to create full source file URL for chunk metadata."},
    )
    citation_url_replacement_regex = NestedField(
        CitationRegexSchema,
        required=False,
        metadata={
            "description": "Regex match and replacement patterns for citation url. Useful if the paths in `input_data` "
            "don't match the desired citation format."
        },
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.resources._index._dataindex.entities.data_index import IndexSource

        return IndexSource(**data)


class EmbeddingSchema(metaclass=PatchedSchemaMeta):
    model = fields.Str(
        required=True,
        allow_none=False,
        metadata={
            "description": "The model to use to embed data. E.g. 'hugging_face://model/sentence-transformers/"
            "all-mpnet-base-v2' or 'azure_open_ai://deployment/{{deployment_name}}/model/{{model_name}}'"
        },
    )
    connection = fields.Str(
        required=False,
        metadata={
            "description": "Connection reference to use for embedding model information, "
            "only needed for hosted embeddings models (such as Azure OpenAI)."
        },
    )
    cache_path = generate_path_property(
        azureml_type=AzureMLResourceType.DATASTORE,
        required=False,
        metadata={
            "description": "Folder containing previously generated embeddings. "
            "Should be parent folder of the 'embeddings' output path used for for this component. "
            "Will compare input data to existing embeddings and only embed changed/new data, "
            "reusing existing chunks."
        },
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.resources._index._dataindex.entities.data_index import Embedding

        return Embedding(**data)


class IndexStoreSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[
            DataIndexTypes.ACS,
            DataIndexTypes.FAISS,
        ],
        metadata={"description": "The type of index to write to. Currently supported types are 'acs' and 'faiss'."},
    )
    name = fields.Str(
        required=False,
        metadata={"description": "Name of the index to write to. If not specified, a name will be generated."},
    )
    connection = fields.Str(
        required=False,
        metadata={
            "description": "Connection reference to use for index information, "
            "only needed for hosted indexes (such as Azure Cognitive Search)."
        },
    )
    config = fields.Dict(
        required=False,
        metadata={
            "description": "Configuration for the index. Primary use is to configure Azure Cognitive Search specific settings."
            "Such as custom `field_mapping` for known field types."
        }
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.resources._index._dataindex.entities.data_index import IndexStore

        return IndexStore(**data)


@experimental
class DataIndexSchema(DataSchema):
    source = NestedField(IndexSourceSchema, required=True, allow_none=False)
    embedding = NestedField(EmbeddingSchema, required=True, allow_none=False)
    index = NestedField(IndexStoreSchema, required=True, allow_none=False)
    incremental_update = fields.Bool()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.resources._index._dataindex.entities.data_index import DataIndex

        return DataIndex(**data)
