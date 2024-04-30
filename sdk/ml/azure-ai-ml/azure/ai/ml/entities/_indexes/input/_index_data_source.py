# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import json
from typing import Optional, Union

from azure.ai.ml import Input
from azure.ai.ml.constants._common import IndexInputType, DataIndexTypes

from azure.ai.ml.entities import PipelineComponent
from azure.ai.ml.entities._load_functions import load_component
from azure.ai.ml.entities._builders.pipeline import Pipeline

from ._index_config import IndexConfig
from ._ai_search_config import AzureAISearchConfig


# General todo: need to determine which args are required or optional when parsed out into groups like this.
# General todo: move these to more permanent locations?

# Defines stuff related to supplying inputs for an index AKA the base data.
class IndexDataSource:
    """Base class for configs that define data that will be processed into an ML index.
    This class should not be instantiated directly. Use one of its child classes instead.

    :param input_type: A type enum describing the source of the index. Used to avoid
        direct type checking.
    :type input_type: Union[str, ~azure.ai.ml.constants._common.IndexInputType]
    """

    def __init__(self, *, input_type: Union[str, IndexInputType]):
        self.input_type = input_type

    def _createComponent(self, index_config: IndexConfig, ai_search_index_config: Optional[AzureAISearchConfig] = None) -> Pipeline:
        """Given the general config values, as well as the config values related to the output index, produce
        and populate a component that creates an index of the specified type from this input config's data source.

        :param index_config: An internal helper object containing all I/O-agnostic variables involved in
            index creation.
        :type index_config: ~azure.ai.resources.operations.IndexConfig
        :param ai_search_index_config: A config object containing all output-related variable for index creation.
        :type ai_search_index_config:~azure.ai.resources.operations.AzureAISearchConfig
        """
        raise NotImplementedError()  # Intended. This base method should never be called.


# Field bundle for creating an index from files located in a Git repo.
# TODO Does git_url need to specifically be an SSH or HTTPS style link?
# TODO What is git connection id?
class GitSource(IndexDataSource):
    """Config class for creating an ML index from files located in a git repository.

    :param git_url: A link to the repository to use.
    :type git_url: str
    :param git_branch_name: The name of the branch to use from the target repository.
    :type git_branch_name: str
    :param git_connection_id: The connection ID for GitHub
    :type git_connection_id: str
    """

    def __init__(self, *, git_url: str, git_branch_name: str, git_connection_id: str):
        self.git_url = git_url
        self.git_branch_name = git_branch_name
        self.git_connection_id = git_connection_id
        super().__init__(input_type=IndexInputType.GIT)


class AISearchSource(IndexDataSource):
    """Config class for creating an ML index from an OpenAI <thing>.

    :param ai_search_index_name: The name of the Azure AI Search index to use as the source.
    :type ai_search_index_name: str
    :param ai_search_index_content_key: The key for the content field in the Azure AI Search index.
    :type ai_search_index_content_key: str
    :param ai_search_index_embedding_key: The key for the embedding field in the Azure AI Search index.
    :type ai_search_index_embedding_key: str
    :param ai_search_index_title_key: The key for the title field in the Azure AI Search index.
    :type ai_search_index_title_key: str
    :param ai_search_index_metadata_key: The key for the metadata field in the Azure AI Search index.
    :type ai_search_index_metadata_key: str
    :param ai_search_index_connection_id: The connection ID for the Azure AI Search index.
    :type ai_search_index_connection_id: str
    :param num_docs_to_import: Number of documents to import from the existing Azure AI Search index. Defaults to 50.
    :type num_docs_to_import: int
    """

    def __init__(self, *,
        ai_search_index_name: str,
        ai_search_index_content_key: str,
        ai_search_index_embedding_key: str,
        ai_search_index_title_key: str,
        ai_search_index_metadata_key: str,
        ai_search_index_connection_id: str,
        num_docs_to_import: int = 50,
    ):
        self.ai_search_index_name = ai_search_index_name
        self.ai_search_index_connection_id = ai_search_index_connection_id
        self.ai_search_index_content_key = ai_search_index_content_key
        self.ai_search_index_embedding_key = ai_search_index_embedding_key
        self.ai_search_index_title_key = ai_search_index_title_key
        self.ai_search_index_metadata_key= ai_search_index_metadata_key
        self.num_docs_to_import = num_docs_to_import
        super().__init__(input_type=IndexInputType.AOAI)


class LocalSource(IndexDataSource):
    """Config class for creating an ML index from a collection of local files.

    :param input_data: An input object describing the local location of index source files.
    :type input_data: ~azure.ai.ml.Input
    """

    def __init__(self, *, input_data: str):  # todo Make sure type of input_data is correct
        self.input_data = Input(type="uri_folder", path=input_data)
        super().__init__(input_type=IndexInputType.LOCAL)