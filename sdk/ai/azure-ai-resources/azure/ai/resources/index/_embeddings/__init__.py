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
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, List, Optional, Tuple, Union

import cloudpickle
import pyarrow as pa
import pyarrow.parquet as pq
import yaml
from azure.core.credentials import TokenCredential
from azure.ai.resources.index._documents import Document, DocumentChunksIterator, DocumentSource, StaticDocument
from azure.ai.resources.index._embeddings.openai import OpenAIEmbedder
from azure.ai.resources.index._langchain.vendor.document_loaders.base import BaseLoader
from azure.ai.resources.index._langchain.vendor.embeddings.base import Embeddings as Embedder
from azure.ai.resources.index._langchain.vendor.schema.document import Document as LangChainDocument
from azure.ai.resources.index._models import init_open_ai_from_config, parse_model_uri
from azure.ai.resources.index._utils.logging import get_logger, track_activity
from azure.ai.resources.index._utils.tokens import tiktoken_cache_dir

logger = get_logger(__name__)


def _args_to_openai_embedder(arguments: dict):
    import openai
    from azure.ai.resources.index._langchain.vendor.embeddings.openai import OpenAIEmbeddings
    from azure.ai.resources.index._utils.logging import langchain_version

    arguments = init_open_ai_from_config(arguments)

    if langchain_version > "0.0.154":
        embedder = OpenAIEmbeddings(
            openai_api_base=arguments.get("api_base", openai.api_base),
            openai_api_type=arguments.get("api_type", openai.api_type),
            openai_api_version=arguments.get("api_version", openai.api_version),
            openai_api_key=arguments.get("api_key", openai.api_key),
            max_retries=100,  # TODO: Make this configurable
        )
    else:
        openai.api_base = arguments.get("api_base", openai.api_base)
        openai.api_type = arguments.get("api_type", openai.api_type)
        openai.api_version = arguments.get("api_version", openai.api_version)
        embedder = OpenAIEmbeddings(
            openai_api_key=arguments.get("api_key", openai.api_key),
            max_retries=100,  # TODO: Make this configurable
        )

    if "model_name" in arguments:
        embedder.model = arguments["model_name"]

    if "model" in arguments:
        embedder.model = arguments["model"]

    # Embeddings endpoint for AOAI uses deployment name and no model name.
    if "deployment" in arguments and hasattr(embedder, "deployment"):
        embedder.deployment = arguments["deployment"]

    if "batch_size" in arguments:
        embedder.chunk_size = int(arguments["batch_size"])

    if "embedding_ctx_length" in arguments:
        embedder.embedding_ctx_length = arguments["embedding_ctx_length"]

    return embedder


def get_langchain_embeddings(embedding_kind: str, arguments: dict, credential: Optional[TokenCredential] = None) -> Embedder:
    """Get an instance of Embedder from the given arguments."""
    if "open_ai" in embedding_kind:
        # return _args_to_openai_embedder(arguments)

        import openai

        arguments = init_open_ai_from_config(arguments, credential=credential)

        embedder = OpenAIEmbedder(
            model=arguments.get("model"),
            api_base=arguments.get("api_base", openai.api_base),
            api_type=arguments.get("api_type", openai.api_type),
            api_version=arguments.get("api_version", openai.api_version),
            api_key=arguments.get("api_key", openai.api_key),
            deployment=arguments.get("deployment", None),
            batch_size=arguments.get("batch_size", None),
            max_retries=arguments.get("embedding_ctx_length", None),
        )
        return embedder
    elif embedding_kind == "hugging_face":
        from azure.ai.resources.index._langchain.vendor.embeddings.huggingface import HuggingFaceEmbeddings

        args = copy.deepcopy(arguments)

        if "model_name" in arguments:
            model_name = arguments["model_name"]
            del args["model_name"]
        elif "model" in arguments:
            model_name = arguments["model"]
            del args["model"]
        else:
            raise ValueError("HuggingFace embeddings require a model name.")

        class ActivitySafeHuggingFaceEmbeddings(Embedder):
            """HuggingFaceEmbeddings with kwargs argument to embed_doceuments to support loggers being passed in."""

            def __init__(self, embeddings):
                """Initialize the ActivitySafeHuggingFaceEmbeddings."""
                self.embeddings = embeddings

            def embed_documents(self, documents: List[str], **kwargs) -> List[List[float]]:
                """Embed the given documents."""
                return self.embeddings.embed_documents(documents)

            def embed_query(self, query: str) -> List[float]:
                """Embed the given query."""
                return self.embeddings.embed_query(query)

        return ActivitySafeHuggingFaceEmbeddings(HuggingFaceEmbeddings(model_name=model_name))
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


def get_embed_fn(embedding_kind: str, arguments: dict, credential: Optional[TokenCredential] = None) -> Callable[[List[str]], List[List[float]]]:
    """Get an embedding function from the given arguments."""
    if "open_ai" in embedding_kind:
        # from azure.ai.resources.index._langchain.openai import patch_openai_embedding_retries

        # embedder = _args_to_openai_embedder(arguments)

        # def embed(texts: List[str], activity_logger=None) -> List[List[float]]:
        #     # AOAI doesn't allow batch_size > 1 so we serialize embedding here to improve error handling
        #     patch_openai_embedding_retries(logger, activity_logger)
        #     embeddings = []
        #     pre_batch = None
        #     for i in range(0, len(texts), int(arguments.get("batch_size", embedder.chunk_size))):
        #         texts_chunk = texts[i:i + embedder.chunk_size]
        #         try:
        #             pre_batch = time.time()
        #             embeddings.extend(embedder.embed_documents(texts_chunk))
        #         except Exception as e:
        #             duration = time.time() - pre_batch if pre_batch else 0
        #             logger.error(f"Failed to embed after {duration}s:\n{e}.", exc_info=e, extra={"print": True})
        #             if activity_logger:
        #                 activity_logger.error("Failed to embed", extra={"properties": {"batch_size": embedder.chunk_size, "duration": duration, "embedding_kind": embedding_kind}})
        #             print(f"Failed texts: {texts_chunk}\nlengths: {[len(t) for t in texts_chunk]}\n")
        #             raise e
        #     return embeddings

        import openai

        arguments = init_open_ai_from_config(arguments, credential=credential)

        embedder = OpenAIEmbedder(
            model=arguments.get("model"),
            api_base=arguments.get("api_base", openai.api_base),
            api_type=arguments.get("api_type", openai.api_type),
            api_version=arguments.get("api_version", openai.api_version),
            api_key=arguments.get("api_key", openai.api_key),
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
                    activity_logger.error("Failed to embed", extra={"properties": {"batch_size": embedder.batch_size, "duration": duration, "embedding_kind": embedding_kind}})
                raise e
            finally:
                if activity_logger:
                    activity_logger.activity_info["num_retries"] = embedder.statistics.get("num_retries", 0)
                    activity_logger.activity_info["time_spent_sleeping"] = embedder.statistics.get("time_spent_sleeping", 0)
                    activity_logger.activity_info["num_tokens"] = embedder.statistics.get("num_tokens", 0)

        return embed
    elif embedding_kind == "hugging_face":
        embedder = get_langchain_embeddings(embedding_kind, arguments, credential=credential)

        return embedder.embed_documents
    elif embedding_kind == "custom":
        def load_pickled_function(pickled_embedding_fn):
            import cloudpickle
            return cloudpickle.loads(gzip.decompress(pickled_embedding_fn))

        return arguments.get("embedding_fn", None) or load_pickled_function(arguments.get("pickled_embedding_fn"))
    elif embedding_kind == "none":
        return get_langchain_embeddings(embedding_kind, arguments, credential=credential).embed_documents
    else:
        raise ValueError(f"Invalid embeddings kind: {embedding_kind}")


def get_query_embed_fn(embedding_kind: str, arguments: dict, credential: Optional[TokenCredential] = None) -> Callable[[str], List[float]]:
    """Get an embedding function from the given arguments."""
    if embedding_kind == "open_ai":
        # embedder = _args_to_openai_embedder(arguments)
        # return embedder.embed_query

        import openai

        arguments = init_open_ai_from_config(arguments, credential)

        embedder = OpenAIEmbedder(
            model=arguments.get("model"),
            api_base=arguments.get("api_base", openai.api_base),
            api_type=arguments.get("api_type", openai.api_type),
            api_version=arguments.get("api_version", openai.api_version),
            api_key=arguments.get("api_key", openai.api_key),
            deployment=arguments.get("deployment", None),
            batch_size=arguments.get("batch_size", None),
            max_retries=arguments.get("embedding_ctx_length", None),
        )

        return embedder.embed_query
    elif embedding_kind == "hugging_face":
        embedder = get_langchain_embeddings(embedding_kind, arguments, credential=credential)

        return embedder.embed_query
    elif embedding_kind == "custom":
        def load_pickled_function(pickled_embedding_fn):
            import cloudpickle
            return cloudpickle.loads(gzip.decompress(pickled_embedding_fn))

        return arguments.get("embedding_fn", None) or load_pickled_function(arguments.get("pickled_embedding_fn"))
    elif embedding_kind == "none":
        return get_langchain_embeddings(embedding_kind, arguments, credential=credential).embed_query
    else:
        raise ValueError("Invalid embeddings kind.")


@dataclass
class EmbeddedDocumentSource:
    """A document source with embedded documents."""

    source: DocumentSource
    document_ids: List[str]


class EmbeddedDocument(ABC):
    """A document with an embedding."""

    document_id: str
    mtime: Any
    document_hash: str
    metadata: dict

    def __init__(self, document_id: str, mtime, document_hash: str, metadata: dict):
        """Initialize the document."""
        self.document_id = document_id
        self.mtime = mtime
        self.document_hash = document_hash
        self.metadata = metadata

    @abstractmethod
    def get_data() -> str:
        """Get the data of the document."""
        pass

    @abstractmethod
    def get_embeddings() -> List[float]:
        """Get the embeddings of the document."""
        pass


class DataEmbeddedDocument(EmbeddedDocument):
    """A document with an embedding and data."""

    def __init__(self, document_id: str, mtime, document_hash: str, data: str, embeddings: List[float], metadata: dict):
        """Initialize the document."""
        super().__init__(document_id, mtime, document_hash, metadata)
        self._data = data
        self._embeddings = embeddings

    def get_data(self) -> str:
        """Get the data of the document."""
        return self._data

    def get_embeddings(self) -> List[float]:
        """Get the embeddings of the document."""
        return self._embeddings


class ReferenceEmbeddedDocument(EmbeddedDocument):
    """A document with an embedding and a reference to the data."""

    _last_opened_embeddings: Optional[Tuple[str, object]] = None

    def __init__(self, document_id: str, mtime, document_hash: str, path_to_data: str, index, embeddings_container_path: str, metadata: dict):
        """Initialize the document."""
        super().__init__(document_id, mtime, document_hash, metadata)
        self.path_to_data = path_to_data
        self.embeddings_container_path = embeddings_container_path
        self.index = index

    def get_data(self) -> str:
        """Get the data of the document."""
        table = self.open_embedding_file(os.path.join(self.embeddings_container_path, self.path_to_data))
        return table.column("data")[self.index].as_py()

    def get_embeddings(self) -> str:
        """Get the embeddings of the document."""
        table = self.open_embedding_file(os.path.join(self.embeddings_container_path, self.path_to_data))
        return table.column("embeddings")[self.index].as_py()

    @classmethod
    def open_embedding_file(cls, path) -> pa.Table:
        """Open the embedding file and cache it."""
        if cls._last_opened_embeddings is None or cls._last_opened_embeddings[0] != path:
            logger.debug(f"caching embeddings file: \n{path}\n   previous path cached was: \n{cls._last_opened_embeddings}")
            table = pq.read_table(path)
            cls._last_opened_embeddings = (path, table)

        return cls._last_opened_embeddings[1]


class WrappedLangChainDocument(Document):
    """A document with an embedding and a reference to the data."""

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
        return json.dumps({"page_content": self.load_data(), "metadata": self.get_metadata(), "document_id": self.document_id})

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
    _model_context_lengths = {
        "text-embedding-ada-002": 8191
    }
    kind: str
    arguments: dict
    _embed_fn: Callable[[List[str]], List[List[float]]]

    _document_sources: OrderedDict
    _deleted_sources: OrderedDict
    _document_embeddings: OrderedDict
    _deleted_documents: List[str]

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
        self._embeddings_container_path = None
        self.dimension = kwargs.get("dimension", None)
        self.statistics = {
            "documents_embedded": 0,
            "documents_reused": 0,
        }

    @property
    def embeddings_container_local_path(self):
        """Get the path to the embeddings container."""
        return self._embeddings_container_path

    @embeddings_container_local_path.setter
    def embeddings_container_local_path(self, value):
        """Set the path to the embeddings container."""
        self._embeddings_container_path = value

    @staticmethod
    def from_uri(uri: str, credential: Optional[TokenCredential] = None, **kwargs) -> "EmbeddingsContainer":
        """Create an embeddings object from a URI."""
        config = parse_model_uri(uri, **kwargs)
        kwargs["credential"] = credential
        return EmbeddingsContainer(**{**config, **kwargs})

    def get_metadata(self):
        """Get the metadata of the embeddings."""
        arguments = copy.deepcopy(self.arguments)
        if self.kind == "custom":
            arguments["pickled_embedding_fn"] = gzip.compress(
                cloudpickle.dumps(arguments["embedding_fn"]))
            del arguments["embedding_fn"]

        if "open_ai" in self.kind:
            if "api_base" not in arguments:
                import openai
                arguments["api_base"] = openai.api_base
            if "api_key" in arguments:
                del arguments["api_key"]
            if "key" in arguments:
                del arguments["key"]

        metadata = {
            "schema_version": "2",
            "kind": self.kind,
            "dimension": self.get_embedding_dimensions(),
            **arguments
        }

        return metadata

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
                metadata["embedding_fn"] = cloudpickle.loads(
                    gzip.decompress(metadata["pickled_embedding_fn"]))
                del metadata["pickled_embedding_fn"]

            embeddings = EmbeddingsContainer(kind, **metadata)
            return embeddings
        else:
            raise ValueError(f"Schema version {schema_version} is not supported")

    @staticmethod
    def load(dir_name: str, embeddings_container_path, metadata_only=False):
        """Load embeddings from a directory."""
        path = Path(embeddings_container_path) / dir_name
        logger.info(f"loading embeddings from: {path}")
        with (path / "embeddings_metadata.yaml").open() as f:
            metadata = yaml.safe_load(f)

        if metadata is None:
            raise ValueError("Metadata file is empty.")

        embeddings = EmbeddingsContainer.from_metadata(metadata)
        embeddings.embeddings_container_local_path = embeddings_container_path

        if not metadata_only:
            file_format_version = metadata.get("file_format_version", "1")
            if file_format_version == "1":
                logger.info(f"loading embeddings from file format version: {file_format_version}")
                embeddings = embeddings.load_v1(dir_name, embeddings_container_path)
            elif file_format_version == "2":
                logger.info(f"loading embeddings from file format version: {file_format_version}")
                embeddings = embeddings.load_v2(dir_name, embeddings_container_path)
            else:
                raise ValueError(f"Schema version {file_format_version} is not supported")

        return embeddings

    def load_v1(self, dir_name: str, embeddings_container_path):
        """Load embeddings from a directory assuming file format version 1."""
        path = Path(embeddings_container_path) / dir_name
        embedding_partitions_files = list(Path(path).glob("embeddings*.parquet"))
        logger.info(f"found following embedding partitions: {embedding_partitions_files}")
        for partition in embedding_partitions_files:
            logger.info(f"processing partition: {partition}")
            table = pq.read_table(partition)
            for column in EmbeddingsContainer._embeddings_schema:
                if column not in table.column_names:
                    raise ValueError(f"Format of provided embedding file ({partition}) is not supported.  Missing column {column}")
            # TODO: Keep pyarrow partition in Embeddings instance and give out `ReferenceEmbeddedDocument` when iterated over/indexed into with doc_id.
            # Allows each partition of embeddings to be stored in one array and users to retrieve it as one array with cow properties.
            for i in range(table.num_rows):
                doc_id = table.column("doc_id")[i].as_py()
                mtime = table.column("mtime")[i].as_py()
                document_hash = table.column("hash")[i].as_py()
                metadata = json.loads(table.column("metadata")[i].as_py())
                path_to_data = None
                # when loading from previous location convert all its local data references to remote ones
                if table.column("is_local")[i].as_py():
                    path_to_data = os.path.join(
                        dir_name, table.column("path_to_data")[i].as_py())
                else:
                    path_to_data = table.column("path_to_data")[i].as_py()
                index_of_data = table.column("index")[i].as_py()
                self._document_embeddings[doc_id] = \
                    ReferenceEmbeddedDocument(
                        doc_id, mtime, document_hash, path_to_data, index_of_data, embeddings_container_path, metadata)

            logger.info(f"Loaded {table.num_rows} documents from {partition}")

        logger.info(f"Loaded {len(self._document_embeddings.keys())} documents from {len(embedding_partitions_files)} partitions")

        return self

    def load_v2(self, dir_name: str, embeddings_container_path):
        """Load embeddings from a directory assuming file format version 2."""
        path = Path(embeddings_container_path) / dir_name

        # Load Document Sources
        sources_partitions_files = list(Path(path).glob("sources*.parquet"))
        logger.info(f"found following sources partitions: {sources_partitions_files}")
        for partition in sources_partitions_files:
            logger.info(f"processing partition: {partition}")
            table = pq.read_table(partition)
            for column in EmbeddingsContainer._sources_schema:
                if column not in table.column_names:
                    raise ValueError(f"Format of provided sources file ({partition}) is not supported.  Missing column {column}")
            for i in range(table.num_rows):
                source_id = table.column("source_id")[i].as_py()
                mtime = table.column("mtime")[i].as_py()
                filename = table.column("filename")[i].as_py()
                url = table.column("url")[i].as_py()
                document_ids = table.column("document_ids")[i].as_py()
                self._document_sources[source_id] = EmbeddedDocumentSource(
                    source=DocumentSource(
                        path=None,
                        filename=filename,
                        mtime=mtime,
                        url=url
                    ),
                    document_ids=document_ids,
                )

        # Load Deleted Document Sources
        deleted_sources_partitions_files = list(Path(path).glob("deleted_sources*.parquet"))
        logger.info(f"found following deleted sources partitions: {deleted_sources_partitions_files}")
        for partition in deleted_sources_partitions_files:
            logger.info(f"processing partition: {partition}")
            table = pq.read_table(partition)
            for column in EmbeddingsContainer._sources_schema:
                if column not in table.column_names:
                    raise ValueError(f"Format of provided sources file ({partition}) is not supported.  Missing column {column}")
            for i in range(table.num_rows):
                source_id = table.column("source_id")[i].as_py()
                mtime = table.column("mtime")[i].as_py()
                filename = table.column("filename")[i].as_py()
                url = table.column("url")[i].as_py()
                document_ids = table.column("document_ids")[i].as_py()
                self._deleted_sources[source_id] = EmbeddedDocumentSource(
                    source=DocumentSource(
                        path=None,
                        filename=filename,
                        mtime=mtime,
                        url=url
                    ),
                    document_ids=document_ids,
                )

        # Load Documents
        embedding_partitions_files = list(Path(path).glob("embeddings*.parquet"))
        logger.info(f"found following embedding partitions: {embedding_partitions_files}")
        for partition in embedding_partitions_files:
            logger.info(f"processing partition: {partition}")
            table = pq.read_table(partition)
            for column in EmbeddingsContainer._embeddings_schema:
                if column not in table.column_names:
                    raise ValueError(f"Format of provided embedding file ({partition}) is not supported.  Missing column {column}")
            # TODO: Keep pyarrow partition in Embeddings instance and give out `ReferenceEmbeddedDocument` when iterated over/indexed into with doc_id.
            # Allows each partition of embeddings to be stored in one array and users to retrieve it as one array with cow properties.
            for i in range(table.num_rows):
                doc_id = table.column("doc_id")[i].as_py()
                mtime = table.column("mtime")[i].as_py()
                document_hash = table.column("hash")[i].as_py()
                metadata = json.loads(table.column("metadata")[i].as_py())
                path_to_data = None
                # when loading from previous location convert all its local data references to remote ones
                if table.column("is_local")[i].as_py():
                    path_to_data = str(Path(dir_name) / table.column("path_to_data")[i].as_py())
                else:
                    path_to_data = table.column("path_to_data")[i].as_py()
                index_of_data = table.column("index")[i].as_py()
                self._document_embeddings[doc_id] = \
                    ReferenceEmbeddedDocument(
                        doc_id, mtime, document_hash, path_to_data, index_of_data, embeddings_container_path, metadata)

        # Load Deleted Documents
        deleted_documents_partitions_files = list(Path(path).glob("deleted_documents*.parquet"))
        logger.info(f"found following deleted document partitions: {deleted_documents_partitions_files}")
        for partition in deleted_documents_partitions_files:
            logger.info(f"processing partition: {partition}")
            table = pq.read_table(partition)
            for column in EmbeddingsContainer._deleted_documents_schema:
                if column not in table.column_names:
                    raise ValueError(f"Format of provided documents file ({partition}) is not supported.  Missing column {column}")
            for i in range(table.num_rows):
                doc_id = table.column("doc_id")[i].as_py()
                mtime = table.column("mtime")[i].as_py()
                document_hash = table.column("hash")[i].as_py()
                metadata = json.loads(table.column("metadata")[i].as_py())
                self._deleted_documents[doc_id] = ReferenceEmbeddedDocument(
                    doc_id,
                    mtime,
                    document_hash,
                    path_to_data=None,
                    index=None,
                    embeddings_container_path=embeddings_container_path,
                    metadata=metadata
                )

        return self

    def save(self, path: str, with_metadata=True, suffix: Optional[str] = None, file_format_version: str = "2"):
        """Save the embeddings to a directory."""
        if file_format_version == "1":
            return self.save_v1(path, with_metadata, suffix)
        elif file_format_version == "2":
            return self.save_v2(path, with_metadata, suffix)
        else:
            raise ValueError(f"Schema version {file_format_version} is not supported")

    def save_v2(self, path: str, with_metadata=True, suffix: Optional[str] = None):
        """Save the embeddings to a directory using file format version 2."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Document Sources
        if len(self._document_sources) > 0:
            sources_file_name = f"sources_{suffix}.parquet" if suffix is not None else "sources.parquet"

            source_ids = []
            source_mtimes = []
            source_filename = []
            source_url = []
            source_document_ids = []
            for (source_id, source) in self._document_sources.items():
                source_ids.append(str(source_id))
                source_mtimes.append(source.source.mtime)
                source_filename.append(source.source.filename)
                source_url.append(source.source.url)
                source_document_ids.append(source.document_ids)
            table = pa.Table.from_arrays(
                [
                    pa.array(source_ids),
                    pa.array(source_mtimes),
                    pa.array(source_filename),
                    pa.array(source_url),
                    pa.array(source_document_ids)
                ], names=EmbeddingsContainer._sources_schema)
            pq.write_table(table, path / sources_file_name)

        # Deleted Document Sources
        if len(self._deleted_sources) > 0:
            deleted_sources_file_name = f"deleted_sources_{suffix}.parquet" if suffix is not None else "deleted_sources.parquet"

            deleted_source_ids = []
            deleted_source_mtimes = []
            deleted_source_filename = []
            deleted_source_url = []
            deleted_document_ids = []
            for (source_id, source) in self._deleted_sources.items():
                deleted_source_ids.append(str(source_id))
                deleted_source_mtimes.append(source.source.mtime)
                deleted_source_filename.append(source.source.filename)
                deleted_source_url.append(source.source.url)
                deleted_document_ids.append(source.document_ids)
            table = pa.Table.from_arrays(
                [
                    pa.array(deleted_source_ids),
                    pa.array(deleted_source_mtimes),
                    pa.array(deleted_source_filename),
                    pa.array(deleted_source_url),
                    pa.array(deleted_document_ids)
                ], names=EmbeddingsContainer._sources_schema)
            pq.write_table(table, path / deleted_sources_file_name)

        # Documents
        if len(self._document_embeddings) > 0:
            local_data_file_name = f"data_{suffix}.parquet" if suffix is not None else "data.parquet"
            embeddings_file_name = f"embeddings_{suffix}.parquet" if suffix is not None else "embeddings.parquet"

            doc_ids = []
            mtimes = []
            hashes = []
            paths = []
            indexes = []
            embeddings = []
            local_data = []
            is_local = []
            metadata = []
            for (doc_id, document) in self._document_embeddings.items():
                doc_ids.append(str(doc_id))
                mtimes.append(document.mtime)
                hashes.append(document.document_hash)
                metadata.append(json.dumps(document.metadata))
                if isinstance(document, DataEmbeddedDocument):
                    indexes.append(len(local_data))
                    local_data.append(document.get_data())
                    embeddings.append(document.get_embeddings())
                    paths.append(local_data_file_name)
                    is_local.append(True)
                elif isinstance(document, ReferenceEmbeddedDocument):
                    indexes.append(document.index)
                    paths.append(document.path_to_data)
                    is_local.append(False)

            # write embeddings.parquet
            table = pa.Table.from_arrays(
                [
                    pa.array(doc_ids),
                    pa.array(mtimes),
                    pa.array(hashes),
                    pa.array(metadata),
                    pa.array(paths),
                    pa.array(indexes),
                    pa.array(is_local)
                ], names=EmbeddingsContainer._embeddings_schema)
            pq.write_table(table, path / embeddings_file_name)

            # write data.paruet with data embedded in this run
            data_table = pa.Table.from_arrays(
                [
                    pa.array(local_data),
                    pa.array(embeddings)
                ], names=["data", "embeddings"])
            pq.write_table(data_table, path / local_data_file_name)

        # Deleted EmbeddedDocuments
        if len(self._deleted_documents) > 0:
            deleted_documents_file_name = f"deleted_documents_{suffix}.parquet" if suffix is not None else "deleted_documents.parquet"

            deleted_doc_ids = []
            deleted_mtimes = []
            deleted_hashes = []
            deleted_metdata = []
            for (doc_id, document) in self._deleted_documents.items():
                deleted_doc_ids.append(str(doc_id))
                deleted_mtimes.append(document.mtime)
                deleted_hashes.append(document.document_hash)
                deleted_metdata.append(json.dumps(document.metadata))

            table = pa.Table.from_arrays(
                [
                    pa.array(deleted_doc_ids),
                    pa.array(deleted_mtimes),
                    pa.array(deleted_hashes),
                    pa.array(deleted_metdata),
                ], names=EmbeddingsContainer._deleted_documents_schema)
            pq.write_table(table, path / deleted_documents_file_name)

        # write metadata file
        if with_metadata:
            self.save_metadata(path, file_format_version="2")

    def save_v1(self, path: str, with_metadata=True, suffix: Optional[str] = None):
        """Save the embeddings to a directory using file format version 1."""
        doc_ids = []
        mtimes = []
        hashes = []
        paths = []
        indexes = []
        embeddings = []
        local_data = []
        is_local = []
        metadata = []

        local_data_file_name = f"data_{suffix}.parquet" if suffix is not None else "data.parquet"
        embeddings_file_name = f"embeddings_{suffix}.parquet" if suffix is not None else "embeddings.parquet"

        for (doc_id, document) in self._document_embeddings.items():
            doc_ids.append(str(doc_id))
            mtimes.append(document.mtime)
            hashes.append(document.document_hash)
            metadata.append(json.dumps(document.metadata))
            if isinstance(document, DataEmbeddedDocument):
                indexes.append(len(local_data))
                local_data.append(document.get_data())
                embeddings.append(document.get_embeddings())
                paths.append(local_data_file_name)
                is_local.append(True)
            elif isinstance(document, ReferenceEmbeddedDocument):
                indexes.append(document.index)
                paths.append(document.path_to_data)
                is_local.append(False)

        import os
        os.makedirs(path, exist_ok=True)

        # write embeddings.parquet
        table = pa.Table.from_arrays(
            [
                pa.array(doc_ids),
                pa.array(mtimes),
                pa.array(hashes),
                pa.array(metadata),
                pa.array(paths),
                pa.array(indexes),
                pa.array(is_local)
            ], names=EmbeddingsContainer._embeddings_schema)
        pq.write_table(table, os.path.join(path, embeddings_file_name))

        # write data.paruet with data embedded in this run
        data_table = pa.Table.from_arrays(
            [
                pa.array(local_data),
                pa.array(embeddings)
            ], names=["data", "embeddings"])
        pq.write_table(data_table, os.path.join(path, local_data_file_name))

        # write metadata file
        if with_metadata:
            self.save_metadata(path)

    def save_metadata(self, path, file_format_version="1"):
        """Save the metadata to a directory."""
        with (Path(path) / "embeddings_metadata.yaml").open("w+") as f:
            metadata = self.get_metadata()
            metadata["file_format_version"] = file_format_version
            yaml.dump(metadata, f)

    def get_query_embed_fn(self) -> Callable[[str], List[float]]:
        """Returns a function that embeds a query string."""
        return get_query_embed_fn(self.kind, self.arguments)

    def get_embedding_dimensions(self) -> Optional[int]:
        """Returns the embedding dimensions."""
        if self.dimension is not None:
            return self.dimension
        elif len(self._document_embeddings) > 0:
            return len(next(iter(self._document_embeddings.values())).get_embeddings())
        else:
            return None

    def as_langchain_embeddings(self, credential: Optional[TokenCredential] = None) -> Embedder:
        """Returns a langchain Embedder that can be used to embed text."""
        return get_langchain_embeddings(self.kind, self.arguments, credential=credential)

    # TODO: Either we need to implement the same split/embed/average flow used by `_get_len_safe_embeddings`
    # on OpenAIEmbeddings or make sure that data_chunking_component always respects max chunk_size.
    # Short term fix is to truncate any text longer than the embedding_ctx_limit if it's set.
    def get_embedding_ctx_length_truncate_func(self):
        """Returns a function that truncates text to the embedding context length if it's set."""
        model = ""
        if "model" in self.arguments:
            model = self.arguments["model"]
        elif "model_name" in self.arguments:
            model = self.arguments["model_name"]

        ctx_length = EmbeddingsContainer._model_context_lengths.get(model, None)

        if ctx_length:
            import tiktoken

            with tiktoken_cache_dir():
                enc = tiktoken.encoding_for_model(model)

            def truncate_by_tokens(text):
                # Some chunks still managed to tokenize above the limit so leaving 20 tokens buffer.
                tokens = enc.encode(text=text)[:ctx_length - 20]
                return enc.decode(tokens)
            return truncate_by_tokens
        else:
            return lambda text: text

    def embed(self, input_documents: Union[Iterator[Document], BaseLoader, DocumentChunksIterator]):
        """Embeds inout documents if they are new or changed and mutates current instance to drop embeddings for documents that are no longer present."""
        self._document_embeddings = self._get_embeddings_internal(input_documents)
        return self

    def embed_and_create_new_instance(self, input_documents: Union[Iterator[Document], BaseLoader, DocumentChunksIterator]) -> "EmbeddingsContainer":
        """Embeds input documents if they are new or changed and returns a new instance with the new embeddings. Current instance is not mutated."""
        document_embeddings = self._get_embeddings_internal(input_documents)
        new_embeddings = EmbeddingsContainer(self.kind, **self.arguments)
        new_embeddings._document_embeddings = document_embeddings
        new_embeddings.statistics = self.statistics.copy()
        return new_embeddings

    def _get_embeddings_internal(self, input_documents: Union[Iterator[Document], BaseLoader, DocumentChunksIterator]) -> OrderedDict:
        if self._embed_fn is None:
            raise ValueError("No embed function provided.")

        if hasattr(input_documents, "__module__") and "langchain" in input_documents.__module__ and "document_loaders" in input_documents.__module__:
            input_documents = iter([WrappedLangChainDocument(d)
                                   for d in input_documents.load()])
        elif isinstance(input_documents, DocumentChunksIterator):
            flattened_docs = []
            for chunked_doc in input_documents:
                flattened_docs.extend(chunked_doc.flatten())
            input_documents = iter(flattened_docs)

        documents_to_embed = []
        documents_embedded = OrderedDict()
        for document in input_documents:
            if hasattr(document, "__module__") and "langchain" in document.__module__ and ".Document" in str(document.__class__):
                document = WrappedLangChainDocument(document)

            logger.info(f"Processing document: {document.document_id}")
            mtime = document.modified_time()
            current_embedded_document = self._document_embeddings.get(document.document_id)
            if mtime \
                    and current_embedded_document \
                    and current_embedded_document.mtime \
                    and current_embedded_document.mtime == mtime:
                documents_embedded[document.document_id] = current_embedded_document

                with contextlib.suppress(Exception):
                    mtime = datetime.datetime.fromtimestamp(mtime)

                logger.info(
                    f"Skip embedding document {document.document_id} as it has not been modified since last embedded at {mtime}")
                self.statistics["documents_reused"] = len(documents_embedded.keys())
                continue

            import hashlib
            document_data = document.load_data()
            document_hash = hashlib.sha256(document_data.encode("utf-8")).hexdigest()

            if current_embedded_document and current_embedded_document.document_hash == document_hash:
                documents_embedded[document.document_id] = current_embedded_document
                logger.info(
                    f"Skip embedding document {document.document_id} as it has not been modified since last embedded")
                self.statistics["documents_reused"] = len(documents_embedded.keys())
                continue

            document_metadata = document.get_metadata()
            documents_to_embed.append(
                (document.document_id, mtime, document_data, document_hash, document_metadata))
            self.statistics["documents_embedded"] = len(documents_to_embed)

        logger.info(f"Documents to embed: {len(documents_to_embed)}"
                    f"\nDocuments reused: {len(documents_embedded.keys())}")

        truncate_func = self.get_embedding_ctx_length_truncate_func()

        data_to_embed = [truncate_func(t) for (_, _, t, _, _) in documents_to_embed]

        embeddings = []
        try:
            with track_activity(
                logger,
                "Embeddings.embed",
                custom_dimensions={
                    "documents_to_embed": len(documents_to_embed),
                    "reused_documents": len(documents_embedded.keys()),
                    "kind": self.kind,
                    "model": self.arguments.get("model", ""),
                }
            ) as activity_logger:
                embeddings = self._embed_fn(data_to_embed, activity_logger=activity_logger)
        except Exception as e:
            logger.error(f"Failed to get embeddings with error: {e}")
            raise

        for ((doc_id, mtime, document_data, document_hash, document_metadata), embeddings) in zip(documents_to_embed, embeddings):
            documents_embedded[doc_id] = \
                DataEmbeddedDocument(doc_id, mtime, document_hash,
                                     document_data, embeddings, document_metadata)

        return documents_embedded

    def as_faiss_index(self, engine: str = "langchain.vectorstores.FAISS"):
        """Returns a FAISS index that can be used to query the embeddings."""
        if engine == "langchain.vectorstores.FAISS":
            # Using vendored version here would mean promptflow can't unpickle the vectorstore.
            from langchain.docstore.in_memory import InMemoryDocstore
            from langchain.schema.document import Document as NotVendoredLangchainDocument
            from langchain.vectorstores import FAISS
            from langchain.vectorstores.faiss import dependable_faiss_import

            def add_doc(doc_id, emb_doc, documents):
                documents.append(
                    NotVendoredLangchainDocument(
                        page_content=emb_doc.get_data(),
                        metadata={
                            "source_doc_id": doc_id,
                            "chunk_hash": emb_doc.document_hash,
                            "mtime": emb_doc.mtime,
                            **emb_doc.metadata
                        }
                    )
                )

            DocstoreClass = InMemoryDocstore
            FaissClass = FAISS
            import_faiss_or_so_help_me = dependable_faiss_import
        elif engine.endswith("indexes.faiss.FaissAndDocStore"):
            from azure.ai.resources.index._docstore import FileBasedDocstore
            from azure.ai.resources.index._indexes.faiss import FaissAndDocStore, import_faiss_or_so_help_me

            def add_doc(doc_id, emb_doc, documents):
                documents.append(
                    StaticDocument(
                        data=emb_doc.get_data(),
                        metadata={
                            "doc_id": doc_id,
                            "chunk_hash": emb_doc.document_hash,
                            **emb_doc.metadata
                        },
                        document_id=doc_id,
                        mtime=emb_doc.mtime
                    )
                )

            DocstoreClass = FileBasedDocstore
            FaissClass = FaissAndDocStore
        else:
            raise ValueError(f"Invalid engine: {engine}")

        import numpy as np

        logger.info("Building faiss index")
        t1 = time.time()
        num_source_docs = 0
        documents = []
        embeddings = []
        index_to_id = {}
        for i, (doc_id, emb_doc) in enumerate(self._document_embeddings.items()):
            logger.info(f"Adding document: {doc_id}")
            logger.debug(f"{doc_id},{emb_doc.document_hash},{emb_doc.get_embeddings()[0:20]}")
            embeddings.append(emb_doc.get_embeddings())
            # TODO: Document/RefDocument gets uri to page_content
            add_doc(doc_id, emb_doc, documents)
            index_to_id[i] = doc_id
            num_source_docs += 1

        if len(embeddings) == 0:
            raise ValueError("No embeddings to index")

        docstore = DocstoreClass(
            {index_to_id[i]: doc for i, doc in enumerate(documents)}
        )

        faiss = import_faiss_or_so_help_me()
        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(np.array(embeddings, dtype=np.float32))

        logger.info(f"Built index from {num_source_docs} documents and {len(embeddings)} chunks, took {time.time()-t1:.4f} seconds")

        return FaissClass(self.get_query_embed_fn(), index, docstore, index_to_id)

    def write_as_faiss_mlindex(self, output_path: Path, engine: str = "langchain.vectorstores.FAISS"):
        """Writes the embeddings to a FAISS MLIndex file."""
        from azure.ai.resources.index._mlindex import MLIndex

        faiss_index = self.as_faiss_index(engine)

        logger.info("Saving index")
        output_path = Path(output_path)
        faiss_index.save_local(str(output_path))

        mlindex_config = {
            "embeddings": self.get_metadata()
        }
        mlindex_config["index"] = {
            "kind": "faiss",
            "engine": engine,
            "method": "FlatL2"
        }
        with (output_path / "MLIndex").open("w") as f:
            yaml.dump(mlindex_config, f)

        return MLIndex(output_path)

    @staticmethod
    def load_latest_snapshot(local_embeddings_cache: str, activity_logger=None) -> "EmbeddingsContainer":
        """Loads the latest snapshot from the embeddings container."""
        embeddings_container_dir_name = None
        embeddings_container = None
        # list all folders in embeddings_container and find the latest one
        try:
            snapshot_files = list(local_embeddings_cache.glob("*/*"))
            last_snapshot = None
            for file in snapshot_files:
                curr_snapshot = file.parent.name
                if curr_snapshot != last_snapshot:
                    last_snapshot = curr_snapshot
                    logger.info(f"Found Snapshot: {curr_snapshot = } - mtime: {os.path.getmtime(file)}")

            embeddings_container_dir_name = str(max(
                [file for file in local_embeddings_cache.glob("*/*") if file.is_file() and file.parent.name != os.environ.get("AZUREML_RUN_ID")],
                key=os.path.getmtime
            ).parent.name)
        except Exception as e:
            if activity_logger:
                activity_logger.warn("Failed to get latest folder from embeddings_container.")
            logger.warn(f"failed to get latest folder from {local_embeddings_cache} with {e}.")

        if embeddings_container_dir_name is not None:
            logger.info(
                f"loading embeddings snapshot from {embeddings_container_dir_name} in {local_embeddings_cache}")
            embeddings_container = None
            try:
                embeddings_container = EmbeddingsContainer.load(
                    embeddings_container_dir_name, str(local_embeddings_cache))
                if activity_logger and hasattr(activity_logger, "activity_info"):
                    activity_logger.activity_info["completionStatus"] = "Success"
            except Exception as e:
                if activity_logger:
                    activity_logger.warn("Failed to load from embeddings_container_dir_name.")
                logger.warn(f"Failed to load from previous embeddings with {e}.")

        return embeddings_container

    @staticmethod
    @contextlib.contextmanager
    def mount_and_load(embeddings_cache_path: str, activity_logger=None) -> "EmbeddingsContainer":
        """
        Mounts the embeddings container and loads it.

        Acts as a ContextManager, so it can be used in a `with` statement, keeping the embeddings_cache mounted if it is a remote path.
        This ensures that Referenced Embeddings accessed while interacting with the EmbeddingsContainer remain accessable.
        """
        local_embeddings_cache = None
        if embeddings_cache_path is not None:
            with track_activity(logger, "EmbeddingsContainer.mount_and_load") as embeddings_container_activity_logger:
                if hasattr(embeddings_container_activity_logger, "activity_info"):
                    embeddings_container_activity_logger.activity_info["completionStatus"] = "Failure"
                # TODO: Support using fsspec to access files for embeddings_container, implement on EmbeddingsContainer
                mount_context = None
                embeddings_cache = str(embeddings_cache_path)
                try:
                    if "://" in embeddings_cache and not embeddings_cache.startswith("file://"):
                        from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount
                        mnt_options = MountOptions(
                            default_permission=0o555, read_only=False, allow_other=False, create_destination=True)
                        mount_context = rslex_uri_volume_mount(embeddings_cache, f"{Path.cwd()}/embeddings_container", options=mnt_options)
                        mount_context.start()
                        local_embeddings_cache = Path(mount_context.mount_point)
                    else:
                        local_embeddings_cache = Path(embeddings_cache.replace("file://", ""))
                        logger.info(f"Embeddings cache is a local path: {embeddings_cache}")

                    embeddings_container = EmbeddingsContainer.load_latest_snapshot(local_embeddings_cache, activity_logger=activity_logger)
                    try:
                        yield embeddings_container
                        return None
                    except Exception as e:
                        embeddings_container_activity_logger.warn("Failed to use embeddings_container.")
                        logger.warn(f"Failed to use embeddings_container with {e}.")
                        raise
                except Exception as e:
                    embeddings_container_activity_logger.warn("Failed to mount embeddings_container.")
                    logger.warn(f"Failed to mount embeddings_container with {e}.")
                    raise
                finally:
                    if mount_context:
                        mount_context.stop()
        yield None
