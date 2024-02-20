# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure Cognitive Search vector store."""
import base64
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

from azure.ai.generative.index._utils.logging import get_logger
from azure.ai.resources._index._utils.requests import send_post_request

try:
    from langchain.schema.document import Document
    from langchain.schema.embeddings import Embeddings
    from langchain.schema.vectorstore import VectorStore
except ImportError:
    from azure.ai.resources._index._langchain.vendor.embeddings.base import Embeddings
    from azure.ai.resources._index._langchain.vendor.schema.document import Document
    from azure.ai.resources._index._langchain.vendor.vectorstores.base import VectorStore

logger = get_logger("langchain.acs")


# TODO: FieldMappings dataclass


def get_acs_headers(credential) -> dict:
    """Get the headers for Azure Cognitive Search."""
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential

    headers = {"Content-Type": "application/json"}
    if isinstance(credential, DefaultAzureCredential):
        headers["Authorization"] = f"Bearer {credential.get_token('https://search.azure.com/.default').token}"
    elif isinstance(credential, AzureKeyCredential):
        headers["api-key"] = credential.key
    return headers


class AzureCognitiveSearchVectorStore(VectorStore):
    """Wrapper around Azure Cognitive Search Index which has embeddings vectors."""

    def __init__(
        self,
        endpoint: str,
        index_name: str,
        embeddings: Embeddings,
        field_mapping: dict,
        credential: Optional[object] = None,
    ):
        """Initialize a vector store from an Azure Cognitive Search Index."""
        try:
            from azure.identity import DefaultAzureCredential
        except ImportError:
            raise ValueError(
                "Could not import azure-identity python package. "
                "Please install it with `pip install azure-identity`."
            )
        try:
            from azure.core.credentials import AzureKeyCredential  # noqa:F401
        except ImportError:
            raise ValueError(
                "Could not import azure-core python package. Please install it with `pip install azure-core`."
            )
        self.endpoint = endpoint
        self.index_name = index_name
        self.credential = credential if credential is not None else DefaultAzureCredential(process_timeout=60)
        self.embedding_function = embeddings.embed_query
        self.field_mapping = field_mapping

    @classmethod
    def from_mlindex(cls, uri: str):
        """Create a vector store from a MLIndex uri."""
        from ..mlindex import MLIndex
        mlindex = MLIndex(uri)
        return mlindex.as_langchain_vectorstore()

    def similarity_search(self, query: str, k: int = 8, **kwargs: Any) -> List[Document]:
        """Search for similar documents by query."""
        return [item[0] for item in self._similarity_search_with_relevance_scores(query, k, **kwargs)]

    def _similarity_search_with_relevance_scores(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        """Search for similar documents by query."""
        embedded_query = self.embedding_function(query)
        return self._similarity_search_by_vector_with_relevance_scores(query, embedded_query, k, **kwargs)

    def _similarity_search_by_vector_with_relevance_scores(
        self, query: Optional[str], embedded_query: List[float], k: int = 4, **kwargs
    ) -> List[Tuple[Document, float]]:
        post_url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version=2023-07-01-Preview"
        headers = get_acs_headers(self.credential)
        post_payload: Dict[str, Any] = {}

        if query is not None:
            logger.info(f"Query: {query}")
            post_payload["search"] = query

        post_payload["top"] = str(k)
        post_payload["select"] = ",".join(["id", self.field_mapping["content"], self.field_mapping["metadata"]])

        if self.field_mapping.get("embedding", None) is not None:
            logger.info(f"Using embedding field: {self.field_mapping['embedding']}")
            post_payload["vectors"] = [{"value": embedded_query, "fields": self.field_mapping["embedding"], "k": k}]
            if kwargs.get("include_embedding_vector", False):
                post_payload["select"] += f",{self.field_mapping['embedding']}"

        response = send_post_request(post_url, headers, post_payload)

        if response.content:
            response_json = response.json()
            logger.debug(response_json)
            results = []
            if "value" in response_json:
                for item in response_json["value"]:
                    doc = Document(
                        page_content=item[self.field_mapping["content"]],
                        metadata={
                            "id": item["id"],
                            "doc_id": base64.b64decode(item["id"]).decode("utf8"),
                            **(
                                json.loads(item[self.field_mapping["metadata"]])
                                if self.field_mapping["metadata"].endswith("json_string")
                                else item[self.field_mapping["metadata"]]
                            ),
                        },
                    )
                    if self.field_mapping.get("embedding", None) is not None and kwargs.get(
                        "include_embedding_vector", False
                    ):
                        doc.metadata["content_vector"] = (item.get(self.field_mapping["embedding"], []),)
                    results.append((doc, item["@search.score"]))
                return results
            else:
                logger.info("no value in response from ACS")
        else:
            logger.info("empty response from ACS")

        return []

    def add_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None, **kwargs: Any) -> List[str]:
        """Add texts to the vector store."""
        raise NotImplementedError

    def similarity_search_by_vector_with_relevance_scores(
        self, vector: List[float], k: int = 4, **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        """Search for similar documents by vector with relevance scores."""
        if self.field_mapping.get("embedding", None) is None:
            raise ValueError("No embedding field specified in field_mapping")
        return self._similarity_search_by_vector_with_relevance_scores(None, vector, k, **kwargs)

    def similarity_search_by_vector(self, vector: List[float], k: int = 4, **kwargs: Any) -> List[Document]:
        """Search for similar documents by vector."""
        if self.field_mapping.get("embedding", None) is None:
            raise ValueError("No embedding field specified in field_mapping")
        return [doc for (doc, _) in self._similarity_search_by_vector_with_relevance_scores(None, vector, k, **kwargs)]

    @classmethod
    def from_texts(cls, texts: Iterable[str], metadatas: Optional[List[dict]] = None, **kwargs: Any) -> VectorStore:
        """Create a vector store from a list of texts."""
        raise NotImplementedError
