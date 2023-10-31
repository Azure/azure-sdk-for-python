# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml
from typing import Dict, Optional
from dataclasses import dataclass

from azure.ai.ml.entities import Data
from azure.ai.resources.entities import AzureOpenAIConnection, AzureAISearchConnection


@dataclass
class Index:
    name: str
    path: str
    version: str = None
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    properties: Optional[Dict[str, str]] = None


    def query(self, text: str):
        try:
            from azure.ai.resources.index._mlindex import MLIndex as InternalMLIndex
        except ImportError as e:
            print("In order to query an Index, you must have azure-ai-generative[index] installed")
            raise e

        retriever = InternalMLIndex(str(self.path)).as_langchain_retriever()
        return retriever.get_relevant_documents(text)

    def override_connections(self, aoai_connection: AzureOpenAIConnection = None, acs_connection: AzureAISearchConnection = None) -> None:
        with open(self.path/"MLIndex", "r") as f:
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
        with open(self.path/"MLIndex", "w") as f:
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
