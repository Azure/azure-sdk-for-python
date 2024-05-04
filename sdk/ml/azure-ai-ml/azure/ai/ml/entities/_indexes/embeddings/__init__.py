# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Embeddings generation and management tools."""

import contextlib
import copy
import datetime
import gzip
import json
import os
import time
import uuid
import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, List, Optional, Tuple, Union

import pyarrow as pa
import pyarrow.parquet as pq
import yaml
from azure.core.credentials import TokenCredential
from .florence import FlorenceEmbedder
from .openai import OpenAIEmbedder
from azure.ai.ml.entities._indexes.entities.document import Document
from azure.ai.ml.entities._indexes.langchain.base_embedder import Embeddings as Embedder
from azure.ai.ml.entities._indexes.models import init_open_ai_from_config, init_serverless_from_config

logger = logging.getLogger(__name__)

MB = 1024 * 1024  # Define a constant for Megabyte
USAGE_THRESHOLD = 0.8  # Up to 80% of the payload
ACS_DOCUMENT_SIZE_LIMIT = (
    16 * MB
)  # ACS recommends batching size up to 16 Mb: https://learn.microsoft.com/en-us/rest/api/searchservice/addupdate-or-delete-documents
MAX_ACS_REQUEST_SIZE = ACS_DOCUMENT_SIZE_LIMIT * USAGE_THRESHOLD


class _ActivitySafeEmbedder(Embedder):
    """Embedder with kwargs argument in embed_documents to support loggers being passed in."""

    def __init__(self, embeddings: Embedder):
        self.embeddings = embeddings

    def embed_documents(self, documents: List[str], **kwargs) -> List[List[float]]:
        """Embed the given documents."""
        return self.embeddings.embed_documents(documents)

    def embed_query(self, query: str) -> List[float]:
        """Embed the given query."""
        return self.embeddings.embed_query(query)


def get_langchain_embeddings(
    embedding_kind: str, arguments: dict, credential: Optional[TokenCredential] = None
) -> Embedder:
    """Get an instance of Embedder from the given arguments."""
    if "open_ai" in embedding_kind:
        # return _args_to_openai_embedder(arguments)

        import openai

        arguments = init_open_ai_from_config(arguments, credential=credential)

        # In openai v1.0.0 and above, openai.api_base is replaced by openai.base_url
        embedder = OpenAIEmbedder(
            model=arguments.get("model"),
            api_base=arguments.get("api_base", openai.api_base if hasattr(openai, "api_base") else openai.base_url),
            api_type=arguments.get("api_type", openai.api_type),
            api_version=arguments.get("api_version", openai.api_version),
            api_key=arguments.get("api_key", openai.api_key),
            azure_ad_token_provider=arguments.get("azure_ad_token_provider", None),
            deployment=arguments.get("deployment", None),
            batch_size=arguments.get("batch_size", None),
            max_retries=arguments.get("embedding_ctx_length", None),
        )
        return embedder
    elif embedding_kind == "serverless_endpoint":
        # Using openai type of api
        import openai

        arguments = init_serverless_from_config(arguments)

        embedder = OpenAIEmbedder(
            api_base=arguments.get("api_base"),
            api_type=arguments.get("api_type"),
            api_key=arguments.get("api_key"),
            model=arguments.get("model"),
            batch_size=arguments.get("batch_size", None),
        )

        return _ActivitySafeEmbedder(embedder)
    elif embedding_kind == "hugging_face":
        from azure.ai.ml.entities._indexes.langchain.huggingface import HuggingFaceEmbeddings

        args = copy.deepcopy(arguments)

        if "model_name" in arguments:
            model_name = arguments["model_name"]
            del args["model_name"]
        elif "model" in arguments:
            model_name = arguments["model"]
            del args["model"]
        else:
            raise ValueError("HuggingFace embeddings require a model name.")

        return _ActivitySafeEmbedder(HuggingFaceEmbeddings(model_name=model_name))
    elif embedding_kind == "none":

        class NoneEmbeddings(Embedder):
            def embed_documents(self, documents: List[str], **kwargs) -> List[List[float]]:
                return [[]] * len(documents)

            def embed_query(self, query: str) -> List[float]:
                return []

        return NoneEmbeddings()
    elif embedding_kind == "custom":
        raise NotImplementedError("Custom embeddings are not supported yet.")
    else:
        raise ValueError(f"Unknown embedding kind: {embedding_kind}")


def get_embed_fn(
    embedding_kind: str, arguments: dict, credential: Optional[TokenCredential] = None
) -> Callable[[List[str]], List[List[float]]]:
    """Get an embedding function from the given arguments."""
    if "open_ai" in embedding_kind:
        import openai

        arguments = init_open_ai_from_config(arguments, credential=credential)

        # In openai v1.0.0 and above, openai.api_base is replaced by openai.base_url
        embedder = OpenAIEmbedder(
            model=arguments.get("model"),
            api_base=arguments.get("api_base", openai.api_base if hasattr(openai, "api_base") else openai.base_url),
            api_type=arguments.get("api_type", openai.api_type),
            api_version=arguments.get("api_version", openai.api_version),
            api_key=arguments.get("api_key", openai.api_key),
            azure_ad_token_provider=arguments.get("azure_ad_token_provider", None),
            deployment=arguments.get("deployment", None),
            batch_size=arguments.get("batch_size", None),
            max_retries=arguments.get("embedding_ctx_length", None),
        )

        def embed(texts: List[str], activity_logger=None) -> List[List[float]]:
            try:
                pre_batch = time.time()
                embedded_documents = embedder.embed_documents(texts)
                return embedded_documents
            except Exception as e:
                duration = time.time() - pre_batch if pre_batch else 0
                logger.error(f"Failed to embed after {duration}s:\n{e}.", exc_info=e, extra={"print": True})
                if activity_logger:
                    activity_logger.error(
                        "Failed to embed",
                        extra={
                            "properties": {
                                "batch_size": embedder.batch_size,
                                "duration": duration,
                                "embedding_kind": embedding_kind,
                            }
                        },
                    )
                raise e
            finally:
                if activity_logger:
                    activity_logger.activity_info["num_retries"] = embedder.statistics.get("num_retries", 0)
                    activity_logger.activity_info["time_spent_sleeping"] = embedder.statistics.get(
                        "time_spent_sleeping", 0
                    )
                    activity_logger.activity_info["num_tokens"] = embedder.statistics.get("num_tokens", 0)

        return embed
    elif embedding_kind == "serverless_endpoint" or embedding_kind == "hugging_face":
        embedder = get_langchain_embeddings(embedding_kind, arguments, credential=credential)
        return embedder.embed_documents
    elif "florence" in embedding_kind:
        embedder = FlorenceEmbedder(arguments.get("api_base"), arguments.get("api_key"))
        return embedder.embed_images
    elif embedding_kind == "custom":

        def load_pickled_function(pickled_embedding_fn):
            import cloudpickle

            return cloudpickle.loads(gzip.decompress(pickled_embedding_fn))

        return arguments.get("embedding_fn", None) or load_pickled_function(arguments.get("pickled_embedding_fn"))
    elif embedding_kind == "none":
        return get_langchain_embeddings(embedding_kind, arguments, credential=credential).embed_documents
    else:
        raise ValueError(f"Invalid embeddings kind: {embedding_kind}")


class WrappedLangChainDocument(Document):
    """A document with an embedding and a reference to the data."""

    from azure.ai.ml.entities._indexes.langchain.schema import Document as LangChainDocument
    document: LangChainDocument

    def __init__(self, document: LangChainDocument):
        """Initialize the document."""
        super().__init__(str(uuid.uuid4()))
        self.document = document

    def modified_time(self) -> Any:
        """Get the modified time of the document."""
        self.document.metadata.get("mtime", None)

    def load_data(self) -> str:
        """Load the data of the document."""
        return self.document.page_content

    def get_metadata(self) -> dict:
        """Get the metadata of the document."""
        return self.document.metadata

    def set_metadata(self, metadata: dict):
        """Set the metadata of the document."""
        self.document.metadata = metadata

    def dumps(self) -> str:
        """Dump the document to a json string."""
        return json.dumps(
            {"page_content": self.load_data(), "metadata": self.get_metadata(), "document_id": self.document_id}
        )

    @classmethod
    def loads(cls, data: str) -> "WrappedLangChainDocument":
        """Load the document from a json string."""
        data_dict = json.loads(data)
        lc_doc = LangChainDocument(data_dict["page_content"], data_dict["metadata"])
        wrapped_doc = cls(lc_doc)
        wrapped_doc.document_id = data_dict["document_id"]
        return wrapped_doc


class EmbeddingsContainer:
    """
    A class for generating embeddings.

    Once some chunks have been embedded using `EmbeddingsContainer.embed`,
    they can be loaded into a FAISS Index or persisted to be loaded later via `EmbeddingsContainer.save` and `EmbeddingsContainer.load`.

    When saved to files:
    - The metadata about the EmbeddingsContainer is stored in `embeddings_metadata.yaml`.
    - The metadata each document (doc_id, mtime, hash, metadata, path_to_data) is stored in `embeddings*.parquet`, the start meaning multiple files (partitions) can be written to the same folder containing distinct documents. This enables parallel generation of embeddings, multiple partitions are handled in `EmbeddingsContainer.load` as well.
    - The document chunk content and embedding vectors are stores in `data*.parquet` files. These are loaded from lazily when the data or embeddings for a document is requested, not when `EmbeddingsContainer.load` is called.
    """

    _embeddings_schema = ["doc_id", "mtime", "hash", "metadata", "path_to_data", "index", "is_local"]
    _data_schema = ["data", "embeddings"]
    _sources_schema = ["source_id", "mtime", "filename", "url", "document_ids"]
    _deleted_documents_schema = ["doc_id", "mtime", "hash", "metadata"]
    _model_context_lengths = {"text-embedding-ada-002": 8191}
    kind: str
    arguments: dict
    _embed_fn: Callable[[List[str]], List[List[float]]]

    _document_sources: OrderedDict
    _deleted_sources: OrderedDict
    _document_embeddings: OrderedDict
    _deleted_documents: OrderedDict

    def __getitem__(self, key):
        """Get document by doc_id."""
        return self._document_embeddings[key]

    def __len__(self):
        """Get the number of documents in the embeddings."""
        return len(self._document_embeddings)

    def __init__(self, kind: str, credential: Optional[TokenCredential] = None, **kwargs):
        """Initialize the embeddings."""
        self.kind = kind
        self.arguments = kwargs
        self._embed_fn = get_embed_fn(kind, kwargs, credential=credential)
        self._document_sources = OrderedDict()
        self._deleted_sources = OrderedDict()
        self._document_embeddings = OrderedDict()
        self._deleted_documents = OrderedDict()
        self._local_path = None
        self._current_snapshot = None
        self.dimension = kwargs.get("dimension", None)
        self.statistics = {
            "documents_embedded": 0,
            "documents_reused": 0,
        }

    @property
    def local_path(self):
        """Get the path to the embeddings container."""
        return self._local_path

    @local_path.setter
    def local_path(self, value):
        """Set the path to the embeddings container."""
        self._local_path = value

    @property
    def current_snapshot(self):
        """Get the current snapshot of the embeddings container."""
        return self._current_snapshot

    @current_snapshot.setter
    def current_snapshot(self, value):
        """Set the current snapshot of the embeddings container."""
        self._current_snapshot = value

    @staticmethod
    def from_metadata(metadata: dict) -> "EmbeddingsContainer":
        """Create an embeddings object from metadata."""
        schema_version = metadata.get("schema_version", "1")
        if schema_version == "1":
            embeddings = EmbeddingsContainer(metadata["kind"], **metadata["arguments"])
            return embeddings
        elif schema_version == "2":
            kind = metadata["kind"]
            del metadata["kind"]
            if kind == "custom":
                import cloudpickle
                metadata["embedding_fn"] = cloudpickle.loads(gzip.decompress(metadata["pickled_embedding_fn"]))
                del metadata["pickled_embedding_fn"]

            embeddings = EmbeddingsContainer(kind, **metadata)
            return embeddings
        else:
            raise ValueError(f"Schema version {schema_version} is not supported")

    def as_langchain_embeddings(self, credential: Optional[TokenCredential] = None) -> Embedder:
        """Returns a langchain Embedder that can be used to embed text."""
        return get_langchain_embeddings(self.kind, self.arguments, credential=credential)
