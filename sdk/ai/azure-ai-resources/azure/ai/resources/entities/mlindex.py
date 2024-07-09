# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml  # type: ignore[import]
from typing import Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass

from azure.ai.ml.entities import Data
from azure.ai.resources.entities import AzureOpenAIConnection, AzureAISearchConnection
from azure.ai.resources._index._langchain.vendor.schema.document import Document

@dataclass
class Index:
    """A search index for queries
    
    :param name: The name of the index.
    :type name: str
    :param path: The path to the index files.
    :type path: str
    :param version: The version of the index.
    :type version: Optional[str]
    :param description: The description of the index.
    :type description: Optional[str]
    :param tags: Tags associated with the index.
    :type tags: Optional[Dict[str, str]]
    :param properties: The properties of the index.
    :type properties: Optional[Dict[str, str]]
    """
    name: str
    path: Union[str, Path]
    version: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    properties: Optional[Dict[str, str]] = None


    def query(self, text: str) -> List[Document]:
        """Query the index with the provided text
        
        :param text: The text to query the index with.
        :type text: str
        :return: A list of documents relevant to the query.
        :rtype: List[azure.ai.resources._index._langchain.vendor.schema.document.Document]
        :raises ImportError: If the azure-ai-generative[index] package is not installed
        """
        try:
            from azure.ai.resources._index._mlindex import MLIndex as InternalMLIndex
        except ImportError as e:
            print("In order to query an Index, you must have azure-ai-generative[index] installed")
            raise e

        retriever = InternalMLIndex(str(self.path)).as_langchain_retriever()
        return retriever.get_relevant_documents(text)

    def override_connections(self, aoai_connection: Optional[AzureOpenAIConnection] = None, acs_connection: Optional[AzureAISearchConnection] = None) -> None:
        """Override the connections in the index with the provided connections
        
        :param aoai_connection: The AzureOpenAIConnection to override the index's connection with.
        :type aoai_connection: Optional[~azure.ai.resources.entities.AzureOpenAIConnection]
        :param acs_connection: The AzureAISearchConnection to override the index's connection with.
        :type acs_connection: Optional[~azure.ai.resources.entities.AzureAISearchConnection]
        """
        with open(Path(self.path)/"MLIndex", "r") as f:
            mlindex_dict = yaml.safe_load(f)

        embeddings_dict = mlindex_dict["embeddings"]
        if aoai_connection:
            if embeddings_dict.get("key") is not None:
                embeddings_dict.pop("key")
            embeddings_dict["connection_type"] = "workspace_connection"
            embeddings_dict["connection"] = {"id": aoai_connection.id}
        if acs_connection:
            index_dict = mlindex_dict["index"]
            if index_dict["kind"] != "acs":
                print("Index kind is not acs, ignoring override for acs connection")
            else:
                index_dict["connection_type"] = "workspace_connection"
                index_dict["connection"] = {"id": acs_connection.id}
        with open(Path(self.path)/"MLIndex", "w") as f:
            yaml.safe_dump(mlindex_dict, f)

    @classmethod
    def _from_data_asset(cls, data: Data) -> "Index":
        return cls(
            name=data.name,
            version=data.version,
            description=data.description,
            tags=data.tags,
            path=data.path
        )
