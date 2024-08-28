# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DataIndex entities."""

# pylint: disable=no-member

from typing import Dict, Optional

from azure.ai.ml.constants._common import DataIndexTypes
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._inputs_outputs.utils import _remove_empty_values
from azure.ai.ml.entities._mixins import DictMixin


@experimental
class CitationRegex(DictMixin):
    """
    :keyword match_pattern: Regex to match citation in the citation_url + input file path.
        e.g. '(.*)/articles/(.*)(\\.[^.]+)$'.
    :type match_pattern: str
    :keyword replacement_pattern: Replacement string for citation. e.g. '\\1/\\2'.
    :type replacement_pattern: str
    """

    def __init__(
        self,
        *,
        match_pattern: str,
        replacement_pattern: str,
    ):
        """Initialize a CitationRegex object."""
        self.match_pattern = match_pattern
        self.replacement_pattern = replacement_pattern

    def _to_dict(self) -> Dict:
        """Convert the Source object to a dict.
        :return: The dictionary representation of the class
        :rtype: Dict
        """
        keys = [
            "match_pattern",
            "replacement_pattern",
        ]
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)


@experimental
class IndexSource(DictMixin):
    """Congifuration for the destination index to write processed data to.
    :keyword input_data: Input Data to index files from. MLTable type inputs will use `mode: eval_mount`.
    :type input_data: Data
    :keyword input_glob: Connection reference to use for embedding model information,
        only needed for hosted embeddings models (such as Azure OpenAI).
    :type input_glob: str, optional
    :keyword chunk_size: Maximum number of tokens to put in each chunk.
    :type chunk_size: int, optional
    :keyword chunk_overlap: Number of tokens to overlap between chunks.
    :type chunk_overlap: int, optional
    :keyword citation_url: Base URL to join with file paths to create full source file URL for chunk metadata.
    :type citation_url: str, optional
    :keyword citation_url_replacement_regex: Regex match and replacement patterns for citation url. Useful if the paths
        in `input_data` don't match the desired citation format.
    :type citation_url_replacement_regex: CitationRegex, optional
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the IndexSource object cannot be validated.
        Details will be provided in the error message.
    """

    def __init__(
        self,
        *,
        input_data: Data,
        input_glob: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        citation_url: Optional[str] = None,
        citation_url_replacement_regex: Optional[CitationRegex] = None,
    ):
        """Initialize a IndexSource object."""
        self.input_data = input_data
        self.input_glob = input_glob
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.citation_url = citation_url
        self.citation_url_replacement_regex = citation_url_replacement_regex

    def _to_dict(self) -> Dict:
        """Convert the Source object to a dict.
        :return: The dictionary representation of the class
        :rtype: Dict
        """
        keys = [
            "input_data",
            "input_glob",
            "chunk_size",
            "chunk_overlap",
            "citation_url",
            "citation_url_replacement_regex",
        ]
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)


@experimental
class Embedding(DictMixin):
    """Congifuration for the destination index to write processed data to.
    :keyword model: The model to use to embed data. E.g. 'hugging_face://model/sentence-transformers/all-mpnet-base-v2'
        or 'azure_open_ai://deployment/{deployment_name}/model/{model_name}'
    :type model: str
    :keyword connection: Connection reference to use for embedding model information,
        only needed for hosted embeddings models (such as Azure OpenAI).
    :type connection: str, optional
    :keyword cache_path: Folder containing previously generated embeddings.
        Should be parent folder of the 'embeddings' output path used for for this component.
        Will compare input data to existing embeddings and only embed changed/new data, reusing existing chunks.
    :type cache_path: str, optional
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the Embedding object cannot be validated.
        Details will be provided in the error message.
    """

    def __init__(
        self,
        *,
        model: str,
        connection: Optional[str] = None,
        cache_path: Optional[str] = None,
    ):
        """Initialize a Embedding object."""
        self.model = model
        self.connection = connection
        self.cache_path = cache_path

    def _to_dict(self) -> Dict:
        """Convert the Source object to a dict.
        :return: The dictionary representation of the class
        :rtype: Dict
        """
        keys = [
            "model",
            "connection",
            "cache_path",
        ]
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)


@experimental
class IndexStore(DictMixin):
    """Congifuration for the destination index to write processed data to.
    :keyword type: The type of index to write to. Currently supported types are 'acs', 'pinecone', and 'faiss'.
    :type type: str
    :keyword name: Name of index to update/create, only needed for hosted indexes
        (such as Azure Cognitive Search and Pinecone).
    :type name: str, optional
    :keyword connection: Connection reference to use for index information,
        only needed for hosted indexes (such as Azure Cognitive Search and Pinecone).
    :type connection: str, optional
    :keyword config: Configuration for the index. Configuration for the index.
        Primary use is to configure AI Search and Pinecone specific settings.
        Such as custom `field_mapping` for known field types.
    :type config: dict, optional
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the IndexStore object cannot be validated.
        Details will be provided in the error message.
    """

    def __init__(
        self,
        *,
        type: str = DataIndexTypes.FAISS,
        name: Optional[str] = None,
        connection: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        """Initialize a IndexStore object."""
        self.type = type
        self.name = name
        self.connection = connection
        self.config = config

    def _to_dict(self) -> Dict:
        """Convert the Source object to a dict.
        :return: The dictionary representation of the class
        :rtype: Dict
        """
        keys = ["type", "name", "connection", "config"]
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)


@experimental
class DataIndex(Data):
    """Data asset with a creating data index job.
    :param name: Name of the asset.
    :type name: str
    :param path: The path to the asset being created by data index job.
    :type path: str
    :param source: The source data to be indexed.
    :type source: IndexSource
    :param embedding: The embedding model to use when processing source data chunks.
    :type embedding: Embedding
    :param index: The destination index to write processed data to.
    :type index: IndexStore
    :param version: Version of the asset created by running this DataIndex Job.
    :type version: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        source: IndexSource,
        embedding: Embedding,
        index: IndexStore,
        incremental_update: bool = False,
        path: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ):
        """Initialize a DataIndex object."""
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            path=path,
            **kwargs,
        )
        self.source = source
        self.embedding = embedding
        self.index = index
        self.incremental_update = incremental_update
