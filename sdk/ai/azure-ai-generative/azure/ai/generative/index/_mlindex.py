# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex class for interacting with MLIndex assets."""
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union

from importlib.util import find_spec
import yaml  # type: ignore[import]
from packaging import version as pkg_version
from azure.core.credentials import TokenCredential
from azure.ai.generative.index._documents import Document, DocumentChunksIterator
from azure.ai.generative.index._embeddings import EmbeddingsContainer
from azure.ai.resources._index._utils.connections import (
    BaseConnection,
    WorkspaceConnection,
    get_connection_by_id_v2,
    get_connection_credential,
    get_id_from_connection,
    get_pinecone_environment,
    get_target_from_connection,
)
from azure.ai.generative.index._utils.logging import (
    get_logger,
    langchain_version,
    packages_versions_for_compatibility,
    track_activity,
    version,
)

try:
    from langchain.document_loaders.base import BaseLoader
except ImportError:
    BaseLoader = Iterator[Document]

logger = get_logger("mlindex")


class MLIndex:
    """MLIndex class for interacting with MLIndex assets."""

    INDEX_FIELD_MAPPING_KEY = "field_mapping"
    INDEX_FIELD_MAPPING_TYPES = {
        "content": "Raw data content of indexed document",
        "embedding": "Embedding of indexed document content",
        "metadata": "Metadata of indexed document, must be a JSON string",
        "filename": "Filename of indexed document, relative to data source root",
        "title": "Title of indexed document",
        "url": "User facing citation URL for indexed document",
    }

    base_uri: str
    index_config: dict
    embeddings_config: dict

    def __init__(self, uri: Optional[Union[str, Path]] = None, mlindex_config: Optional[dict] = None):
        """
        Initialize MLIndex from a URI or AzureML Data Asset.

        Args:
        ----
            uri: URI to MLIndex asset folder (remote or local)
            mlindex_config: MLIndex config dictionary
            credential: Credential to use for talking to Azure resources
        """
        with track_activity(logger, "MLIndex.__init__") as activity_logger:
            if uri is not None:
                if isinstance(uri, str):
                    uri = str(uri)
                elif isinstance(uri, Path):
                    uri = str(uri)
                else:
                    # Assume given AzureML Data Asset
                    uri = uri.path

                if find_spec("fsspec") is None:
                    raise ValueError(
                        "fsspec python package not installed. Please install it with `pip install fsspec`."
                    )

                if find_spec("azureml.fsspec") is None:
                    logger.warning(
                        "azureml-fsspec python package not installed. "
                        "Loading from remote filesystems supported by AzureML will not work. "
                        "Please install it with `pip install azureml-fsspec`."
                    )

                self.base_uri = uri

                mlindex_config = None
                uri = uri.rstrip("/")
                mlindex_uri = f"{uri}/MLIndex" if not uri.endswith("MLIndex") else uri
                try:
                    import fsspec

                    mlindex_file = fsspec.open(mlindex_uri, "r")
                    if hasattr(mlindex_file.fs, "_path"):
                        # File on azureml filesystem has path relative to container root
                        # Need to get underlying fs path
                        self.base_uri = mlindex_file.fs._path.split("/MLIndex")[0]
                    else:
                        self.base_uri = mlindex_file.path.split("/MLIndex")[0]  # pylint: disable=no-member

                    with mlindex_file as f:
                        mlindex_config = yaml.safe_load(f)
                except Exception as e:
                    raise ValueError(f"Could not find MLIndex: {e}") from e
            elif mlindex_config is None:
                raise ValueError("Must provide either uri or mlindex_config")

            self.index_config = mlindex_config.get("index", {})
            if self.index_config is None:
                raise ValueError("Could not find index config in MLIndex yaml")
            activity_logger.activity_info["index_kind"] = self.index_config.get("kind", "none")
            self.embeddings_config = mlindex_config.get("embeddings", {})
            if self.embeddings_config is None:
                raise ValueError("Could not find embeddings config in MLIndex yaml")
            activity_logger.activity_info["embeddings_kind"] = self.embeddings_config.get("kind", "none")
            activity_logger.activity_info["embeddings_api_type"] = self.embeddings_config.get("api_type", "none")

    @property
    def name(self) -> str:
        """
        Returns the name of the MLIndex.

        :return: The name of the MLIndex.
        :rtype: str
        """
        return self.index_config.get("name", "")

    @name.setter
    def name(self, value: str):
        """
        Sets the name of the MLIndex.

        :keyword value: The name of the MLIndex.
        :paramtype value: str
        """
        self.index_config["name"] = value

    @property
    def description(self) -> str:
        """
        Returns the description of the MLIndex.

        :return: The description of the MLIndex.
        :rtype: str
        """
        return self.index_config.get("description", "")

    @description.setter
    def description(self, value: str):
        """
        Sets the description of the MLIndex.

        :keyword value: The name of the MLIndex.
        :paramtype value: str
        """
        self.index_config["description"] = value

    def get_langchain_embeddings(self, credential: Optional[TokenCredential] = None):
        """
        Get the LangChainEmbeddings from the MLIndex.

        :keyword credential: The credential used to get the LangChainEmbeddings from the MLIndex.
        :paramtype credential: Optional[TokenCredential]
        """
        embeddings = EmbeddingsContainer.from_metadata(self.embeddings_config.copy())

        return embeddings.as_langchain_embeddings(credential=credential)

    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    def as_langchain_vectorstore(self, credential: Optional[TokenCredential] = None):
        """
        Converts MLIndex to a retriever object that can be used with langchain, may download files.

        :keyword credential: The credential used to converts MLIndex to a retriever object.
        :paramtype credential: Optional[TokenCredential]
        """
        with track_activity(logger, "MLIndex.as_langchain_vectorstore") as activity_logger:
            index_kind = self.index_config.get("kind", "none")

            activity_logger.activity_info["index_kind"] = index_kind
            activity_logger.activity_info["embeddings_kind"] = self.embeddings_config.get("kind", "none")
            activity_logger.activity_info["embeddings_api_type"] = self.embeddings_config.get("api_type", "none")

            langchain_pkg_version = pkg_version.parse(langchain_version)

            if index_kind == "acs":
                from azure.ai.resources._index._indexes.azure_search import import_azure_search_or_so_help_me

                import_azure_search_or_so_help_me()

                if self.index_config.get("field_mapping", {}).get("embedding", None) is None:
                    msg = "field_mapping.embedding must be set in MLIndex config for acs index, "
                    raise ValueError(msg + "try `.as_langchain_retriever()` instead.")

                try:
                    connection_credential = get_connection_credential(self.index_config, credential=credential)
                except Exception as e:  # pylint: disable=broad-except
                    # azure.ai.generative has workflow where env vars are set before doing stuff.
                    # AZURE_AI_SEARCH_KEY is new key, but fall back to AZURE_COGNITIVE_SEARCH_KEY for backward compat.
                    if "AZURE_AI_SEARCH_KEY" in os.environ or "AZURE_COGNITIVE_SEARCH_KEY" in os.environ:
                        from azure.core.credentials import AzureKeyCredential

                        logger.warning(f"Failed to get credential for ACS with {e}, falling back to env vars.")
                        connection_credential = AzureKeyCredential(
                            os.environ["AZURE_AI_SEARCH_KEY"]
                            if "AZURE_AI_SEARCH_KEY" in os.environ
                            else os.environ["AZURE_COGNITIVE_SEARCH_KEY"]
                        )
                    else:
                        raise e

                index_endpoint = self.index_config.get("endpoint", None)
                if not index_endpoint:
                    index_endpoint = get_target_from_connection(
                        get_connection_by_id_v2(self.index_config["connection"]["id"], credential=credential)
                    )

                azure_search_documents_version = packages_versions_for_compatibility["azure-search-documents"]
                search_client_version = pkg_version.parse(azure_search_documents_version)
                langchain_pkg_version = pkg_version.parse(langchain_version)

                if (
                    pkg_version.parse("11.4.0b8") >= search_client_version > pkg_version.parse("11.4.0b6")
                    and langchain_pkg_version > pkg_version.parse("0.0.273")
                ) or (
                    search_client_version == pkg_version.parse("11.4.0b6")
                    and pkg_version.parse("0.0.273") > langchain_pkg_version >= pkg_version.parse("0.0.198")
                ):
                    from langchain.vectorstores import azuresearch  # pylint: disable=import-error

                    # TODO: These fields effect all ACS retrievers in the same process, should change class so it can
                    # use these as defaults but uses names passed in as args preferentially
                    azuresearch.FIELDS_ID = self.index_config.get("field_mapping", {}).get("id", "id")
                    azuresearch.FIELDS_CONTENT = self.index_config.get("field_mapping", {}).get("content", "content")
                    azuresearch.FIELDS_CONTENT_VECTOR = self.index_config.get("field_mapping", {}).get(
                        "embedding", "content_vector_open_ai"
                    )
                    azuresearch.FIELDS_METADATA = self.index_config.get("field_mapping", {}).get(
                        "metadata", "meta_json_string"
                    )

                    from azure.core.credentials import AzureKeyCredential
                    from langchain.vectorstores.azuresearch import AzureSearch  # pylint: disable=import-error

                    return AzureSearch(
                        azure_search_endpoint=index_endpoint,
                        azure_search_key=connection_credential.key
                        if isinstance(connection_credential, AzureKeyCredential)
                        else None,
                        index_name=self.index_config.get("index"),
                        embedding_function=self.get_langchain_embeddings(credential=credential).embed_query,
                        search_type="hybrid",
                        semantic_configuration_name=self.index_config.get(
                            "semantic_configuration_name", "azureml-default"
                        ),
                        user_agent=f"azureml-rag=={version}/mlindex,langchain=={langchain_version}",
                    )
                from azure.ai.generative.index._langchain.acs import AzureCognitiveSearchVectorStore

                msg = f"azure-search-documents=={azure_search_documents_version} not compatible "
                logger.warning(msg + "langchain.vectorstores.azuresearch yet, using REST client based VectorStore.")

                return AzureCognitiveSearchVectorStore(
                    index_name=self.index_config.get("index", ""),
                    endpoint=index_endpoint,
                    embeddings=self.get_langchain_embeddings(credential=credential),
                    field_mapping=self.index_config.get("field_mapping", {}),
                    credential=connection_credential,
                )
            if index_kind == "faiss":
                from fsspec.core import url_to_fs

                store = None
                engine: str = self.index_config.get("engine", "")
                if engine == "langchain.vectorstores.FAISS":
                    embeddings = EmbeddingsContainer.from_metadata(
                        self.embeddings_config.copy()
                    ).as_langchain_embeddings(credential=credential)

                    # langchain fix https://github.com/langchain-ai/langchain/pull/10823 released in 0.0.318
                    if langchain_pkg_version >= pkg_version.parse("0.0.318"):
                        embeddings = embeddings.embed_query

                    fs, uri = url_to_fs(self.base_uri)

                    with tempfile.TemporaryDirectory() as tmpdir:
                        fs.download(f"{uri.rstrip('/')}/index.pkl", f"{str(tmpdir)}")
                        fs.download(f"{uri.rstrip('/')}/index.faiss", f"{str(tmpdir)}")

                        try:
                            from langchain.vectorstores import FAISS

                            store = FAISS.load_local(str(tmpdir), embeddings)
                        except ImportError as e:
                            msg = f"retrying with vendored FAISS VectorStore.\n{e}"
                            logger.warning("Failed to load FAISS Index using installed version of langchain, " + msg)

                            from azure.ai.resources._index._langchain.vendor.vectorstores.faiss import FAISS

                            store = FAISS.load_local(str(tmpdir), embeddings)

                elif engine.endswith("indexes.faiss.FaissAndDocStore"):
                    from azure.ai.resources._index._indexes.faiss import FaissAndDocStore

                    # pylint: disable=line-too-long
                    error_fmt_str = """Failed to import langchain faiss bridge module with: {e}\n"
                        This could be due to an incompatible change in langchain since this bridge was implemented.
                        If you understand what has changed you could implement your own wrapper of azure.ai.tools.mlindex._indexes.faiss.FaissAndDocStore.
                        """
                    try:
                        from azure.ai.generative.index._langchain.faiss import azureml_faiss_as_langchain_faiss
                    except ImportError as e:
                        logger.warning(error_fmt_str.format(e=e))
                        azureml_faiss_as_langchain_faiss = None  # type: ignore[assignment]

                    embeddings = EmbeddingsContainer.from_metadata(
                        self.embeddings_config.copy()
                    ).as_langchain_embeddings(credential=credential)

                    store = FaissAndDocStore.load(self.base_uri, embeddings.embed_query)
                    if azureml_faiss_as_langchain_faiss is not None:
                        try:
                            store = azureml_faiss_as_langchain_faiss(
                                FaissAndDocStore.load(self.base_uri, embeddings.embed_query)
                            )
                        except Exception as e:
                            logger.error(error_fmt_str.format(e=e))
                            raise
                else:
                    raise ValueError(f"Unknown engine: {engine}")
                return store
            if index_kind == "pinecone":
                try:
                    import pinecone  # pylint: disable=import-error
                    from azure.core.credentials import AzureKeyCredential
                    from langchain.vectorstores import Pinecone  # pylint: disable=import-error

                    connection_credential = get_connection_credential(self.index_config, credential=credential)
                    if not isinstance(connection_credential, AzureKeyCredential):
                        raise ValueError(
                            "Expected credential to Pinecone index to be an AzureKeyCredential, "
                            + f"instead got: {type(connection_credential)}"
                        )

                    environment = get_pinecone_environment(self.index_config, credential=credential)
                    pinecone.init(api_key=connection_credential.key, environment=environment)
                    pinecone_index = pinecone.Index(self.index_config.get("index"))

                    index_stats = pinecone_index.describe_index_stats()
                    logger.info(f"Pinecone index {self.index_config.get('index')} with stats {index_stats}")
                    activity_logger.info("Pinecone index", extra={"properties": {"stats": index_stats}})

                    try:
                        logger.info("Get Pinecone vectorstore by passing in `embedding` as a Callable.")
                        return Pinecone.from_existing_index(
                            self.index_config.get("index"),
                            self.get_langchain_embeddings(credential=credential).embed_query,
                            text_key=self.index_config.get("field_mapping", {})["content"],
                        )
                    except Exception as e:  # pylint: disable=broad-except
                        msg = f"Failed to get Pinecone vectorstore due to {e}, "
                        logger.warn(msg + "try again by passing in `embedding` as an Embeddings object.")
                        return Pinecone.from_existing_index(
                            self.index_config.get("index"),
                            self.get_langchain_embeddings(credential=credential),
                            text_key=self.index_config.get("field_mapping", {})["content"],
                        )
                except Exception as e:
                    logger.error(f"Failed to create Pinecone vectorstore due to: {e}")
                    raise
            raise ValueError(f"Unknown index kind: {index_kind}")

    def as_langchain_retriever(self, credential: Optional[TokenCredential] = None, **kwargs):
        """
        Converts MLIndex to a retriever object that can be used with langchain, may download files.

        :keyword credential: The credential used to converts MLIndex to a retriever object.
        :paramtype credential: Optional[TokenCredential]
        """
        index_kind = self.index_config.get("kind", None)
        if index_kind == "acs":
            if self.index_config.get("field_mapping", {}).get("embedding", None) is None:
                from azure.ai.generative.index._langchain.acs import AzureCognitiveSearchVectorStore

                connection_credential = get_connection_credential(self.index_config, credential=credential)

                endpoint = self.index_config.get("endpoint", None)
                if not endpoint:
                    endpoint = get_target_from_connection(
                        get_connection_by_id_v2(self.index_config["connection"]["id"], credential=credential)
                    )
                return AzureCognitiveSearchVectorStore(
                    index_name=self.index_config.get("index", ""),
                    endpoint=endpoint,
                    embeddings=self.get_langchain_embeddings(),
                    field_mapping=self.index_config.get("field_mapping", {}),
                    credential=connection_credential,
                ).as_retriever(**kwargs)

            return self.as_langchain_vectorstore(credential=credential).as_retriever(**kwargs)
        if index_kind == "faiss":
            return self.as_langchain_vectorstore(credential=credential).as_retriever(**kwargs)
        if index_kind == "pinecone":
            return self.as_langchain_vectorstore(credential=credential).as_retriever(**kwargs)
        raise ValueError(f"Unknown index kind: {index_kind}")

    def as_native_index_client(self, credential: Optional[TokenCredential] = None):
        """
        Converts MLIndex config into a client for the underlying Index, may download files.

        An azure.search.documents.SearchClient for acs indexes or
        an azure.ai.resources._index._indexes.indexFaissAndDocStore for faiss indexes.

        :keyword credential: The credential used to converts MLIndex config into a client for the underlying Index.
        :paramtype credential: Optional[TokenCredential]
        """
        index_kind = self.index_config.get("kind", None)
        if index_kind == "acs":
            connection_credential = get_connection_credential(self.index_config, credential=credential)

            from azure.search.documents import SearchClient

            return SearchClient(
                endpoint=self.index_config.get("endpoint"),
                index_name=self.index_config.get("index"),
                credential=connection_credential,
                user_agent=f"azureml-rag=={version}/mlindex",
                api_version=self.index_config.get("api_version", "2023-07-01-preview"),
            )
        if index_kind == "faiss":
            from azure.ai.resources._index._indexes.faiss import FaissAndDocStore

            embeddings = self.get_langchain_embeddings(credential=credential)

            return FaissAndDocStore.load(self.base_uri, embeddings.embed_query)
        if index_kind == "pinecone":
            import pinecone  # pylint: disable=import-error
            from azure.core.credentials import AzureKeyCredential

            connection_credential = get_connection_credential(self.index_config, credential=credential)
            if not isinstance(connection_credential, AzureKeyCredential):
                raise ValueError(
                    "Expected credential to Pinecone index to be an AzureKeyCredential, "
                    + f"instead got: {type(connection_credential)}"
                )

            environment = get_pinecone_environment(self.index_config, credential=credential)
            pinecone.init(api_key=connection_credential.key, environment=environment)
            return pinecone.Index(self.index_config.get("index"))
        raise ValueError(f"Unknown index kind: {index_kind}")

    def __repr__(self):
        """
        Returns a string representation of the MLIndex object.

        :return: A string representation of the MLIndex object.
        :rtype: str
        """
        return yaml.dump(
            {
                "index": self.index_config,
                "embeddings": self.embeddings_config,
            }
        )

    def override_connections(
        self,
        embedding_connection: Optional[Union[str, BaseConnection, WorkspaceConnection]] = None,
        index_connection: Optional[Union[str, BaseConnection, WorkspaceConnection]] = None,
        credential: Optional[TokenCredential] = None,
    ) -> "MLIndex":
        """
        Override the connections used by the MLIndex.

        :keyword embedding_connection: Optional connection to use for embeddings model.
        :paramtype embedding_connection: Optional[Union[str, BaseConnection, WorkspaceConnection]]
        :keyword index_connection: Optional connection to use for index.
        :paramtype index_connection: Optional[Union[str, BaseConnection, WorkspaceConnection]]
        :keyword credential: Optional credential to use when resolving connection information.
        :paramtype credential: Optional[TokenCredential]
        :return: A MLIndex object.
        :rtype: MLIndex
        """
        if embedding_connection:
            if self.embeddings_config.get("key") is not None:
                self.embeddings_config.pop("key")

            if embedding_connection.__class__.__name__ == "AzureOpenAIConnection":
                embedding_connection: Union[BaseConnection, WorkspaceConnection]  # type: ignore[no-redef]
                # PromptFlow Connection
                self.embeddings_config["connection_type"] = "inline"
                self.embeddings_config["connection"] = {
                    "key": embedding_connection.secrets.get("api_key"),  # type: ignore[union-attr]
                    "api_base": embedding_connection.api_base,  # type: ignore[union-attr]
                    "api_type": embedding_connection.api_type,  # type: ignore[union-attr]
                }
            else:
                self.embeddings_config["connection_type"] = "workspace_connection"
                if isinstance(embedding_connection, str):
                    embedding_connection = get_connection_by_id_v2(embedding_connection, credential=credential)
                self.embeddings_config["connection"] = {"id": get_id_from_connection(embedding_connection)}
        if index_connection:
            if self.index_config["kind"] != "acs":
                print("Index kind is not acs, ignoring override for connection")
            else:
                self.index_config["connection_type"] = "workspace_connection"
                if isinstance(index_connection, str):
                    index_connection = get_connection_by_id_v2(index_connection, credential=credential)
                self.index_config["connection"] = {"id": get_id_from_connection(index_connection)}
        self.save(self.base_uri, just_config=True)
        return self

    def set_embeddings_connection(
        self,
        connection: Optional[Union[str, BaseConnection, WorkspaceConnection]],
    ) -> "MLIndex":
        """
        Set the embeddings connection used by the MLIndex.

        :keyword connection: Optional connection to use for embeddings model.
        :paramtype connection: Optional[Union[str, BaseConnection, WorkspaceConnection]]
        """
        return self.override_connections(embedding_connection=connection)

    @staticmethod
    def from_files(
        source_uri: str,
        source_glob: str = "**/*",
        chunk_size: int = 1000,
        chunk_overlap: int = 0,
        citation_url: Optional[str] = None,
        citation_replacement_regex: Optional[Dict[str, str]] = None,
        embeddings_model: str = "hugging_face://model/sentence-transformers/all-mpnet-base-v2",
        embeddings_connection: Optional[str] = None,
        embeddings_container: Optional[Union[str, Path]] = None,
        index_type: str = "faiss",
        index_connection: Optional[str] = None,
        index_config: Optional[Dict[str, Any]] = None,
        output_path: Optional[Union[str, Path]] = None,
        credential: Optional[TokenCredential] = None,
    ) -> "MLIndex":
        r"""
        Create a new MLIndex from a repo.

        :keyword source_uri: Iterator of documents to index.
        :paramtype source_uri: str
        :keyword source_glob: Glob pattern to match files to index.
        :paramtype source_glob: str
        :keyword chunk_size: Size of chunks to split documents into.
        :paramtype chunk_size: int
        :keyword chunk_overlap: Size of overlap between chunks.
        :paramtype chunk_overlap: int
        :keyword citation_url: Optional url to replace citation urls with.
        :paramtype citation_url: Optional[str]
        :keyword citation_replacement_regex: Optional regex to use to replace citation urls.
        :paramtype citation_replacement_regex: Optional[Dict[str, str]]
        :keyword embeddings_model: Name of embeddings model to use.
        :paramtype embeddings_model: str
        :keyword embeddings_connection: Optional connection to use for embeddings model.
        :paramtype embeddings_connection: Optional[str]
        :keyword embeddings_container: Optional path to location where un-indexed embeddings can be saved/loaded.
        :paramtype embeddings_container: Optional[Union[str, Path]]
        :keyword index_type: Type of index to use.
        :paramtype index_type: str
        :keyword index_connection: Optional connection to use for index.
        :paramtype index_connection: Optional[str]
        :keyword index_config: Config for index.
        :paramtype index_config: Optional[Dict[str, Any]]
        :keyword output_path: Optional path to save index to.
        :paramtype output_path: Optional[Union[str, Path]]
        :keyword credential: Optional credential to use when resolving connection information.
        :paramtype credential: Optional[TokenCredential]
        :return: A new MLIndex.
        :rtype: MLIndex
        """
        if index_config is None:
            index_config = {}

        from azure.ai.generative.index._documents import split_documents

        with track_activity(logger, "MLIndex.from_files"):
            chunked_documents = DocumentChunksIterator(
                files_source=source_uri,
                glob=source_glob,
                base_url=citation_url,
                document_path_replacement_regex=citation_replacement_regex,
                chunked_document_processors=[
                    lambda docs: split_documents(
                        docs,
                        splitter_args={"chunk_size": chunk_size, "chunk_overlap": chunk_overlap, "use_rcts": False},
                    )
                ],
            )

            mlindex = MLIndex.from_documents(
                chunked_documents,
                embeddings_model=embeddings_model,
                embeddings_connection=embeddings_connection,
                embeddings_container=embeddings_container,
                index_type=index_type,
                index_connection=index_connection,
                index_config=index_config,
                output_path=output_path,
                credential=credential,
            )

        return mlindex

    @staticmethod
    def from_documents(
        documents: Union[Iterator[Document], BaseLoader, DocumentChunksIterator],
        embeddings_model: str = "hugging_face://model/sentence-transformers/all-mpnet-base-v2",
        embeddings_connection: Optional[str] = None,
        embeddings_container: Optional[Union[str, Path]] = None,
        index_type: str = "faiss",
        index_connection: Optional[str] = None,
        index_config: Optional[Dict[str, Any]] = None,
        output_path: Optional[Union[str, Path]] = None,
        credential: Optional[TokenCredential] = None,
    ) -> "MLIndex":
        """
        Create a new MLIndex from documents.

        :keyword documents: Iterator of documents to index.
        :paramtype documents: Union[Iterator[Document], BaseLoader, DocumentChunksIterator]
        :keyword embeddings_model: Name of embeddings model to use.
        :paramtype embeddings_model: str
        :keyword embeddings_connection: Optional connection to use for embeddings model.
        :paramtype embeddings_connection: Optional[str]
        :keyword embeddings_container: Optional path to location where un-indexed embeddings can be saved/loaded.
        :paramtype embeddings_container: Optional[Union[str, Path]]
        :keyword index_type: Type of index to use.
        :paramtype index_type: str
        :keyword index_connection: Optional connection to use for index.
        :paramtype index_connection: Optional[str]
        :keyword index_config: Config for index.
        :paramtype index_config: Optional[Dict[str, Any]]
        :keyword output_path: Optional path to save index to.
        :paramtype output_path: Optional[Union[str, Path]]
        :keyword credential: Optional credential to use when resolving connection information.
        :paramtype credential: Optional[TokenCredential]
        :return: A new MLIndex.
        :rtype: MLIndex
        """
        if index_config is None:
            index_config = {}

        import time

        embeddings = None
        # TODO: Move this logic to load from embeddings_container into EmbeddingsContainer
        try:  # pylint: disable=too-many-nested-blocks
            if embeddings_container is not None:
                if isinstance(embeddings_container, str) and "://" in embeddings_container:
                    from fsspec.core import url_to_fs

                    url_to_fs(embeddings_container)
                else:
                    embeddings_container = Path(embeddings_container)
                    previous_embeddings_dir_name = None
                    try:
                        previous_embeddings_dir_name = str(
                            max(
                                (dir for dir in embeddings_container.glob("*") if dir.is_dir()), key=os.path.getmtime
                            ).name
                        )
                    except FileNotFoundError as e:
                        logger.warning(
                            f"failed to get latest folder from {embeddings_container} with {e}.", extra={"print": True}
                        )
                    if previous_embeddings_dir_name is not None:
                        try:
                            embeddings = EmbeddingsContainer.load(
                                previous_embeddings_dir_name, embeddings_container  # type: ignore[arg-type]
                            )
                        except (IOError, ValueError) as e:
                            logger.warning(
                                f"failed to load embeddings from {embeddings_container} with {e}.",
                                extra={"print": True},
                            )
        finally:
            if embeddings is None:
                logger.info("Creating new EmbeddingsContainer")
                if isinstance(embeddings_model, str):
                    connection_args = {}
                    if "open_ai" in embeddings_model:
                        if embeddings_connection:
                            if isinstance(embeddings_connection, str):
                                embeddings_connection: Union[  # type: ignore[no-redef]
                                    Dict[str, Dict[str, Dict[str, Any]]], Any
                                ] = get_connection_by_id_v2(embeddings_connection, credential=credential)
                            connection_args = {
                                "connection_type": "workspace_connection",
                                "connection": {"id": get_id_from_connection(embeddings_connection)},
                                "endpoint": embeddings_connection.target
                                if hasattr(embeddings_connection, "target")
                                else embeddings_connection["properties"]["target"],  # type: ignore[index]
                            }
                        else:
                            import openai

                            api_key = "OPENAI_API_KEY"
                            api_base = "OPENAI_API_BASE"
                            if pkg_version.parse(openai.version.VERSION) >= pkg_version.parse("1.0.0"):
                                api_key = "AZURE_OPENAI_KEY"
                                api_base = "AZURE_OPENAI_ENDPOINT"
                            connection_args = {
                                "connection_type": "environment",
                                "connection": {"key": api_key},
                                "endpoint": os.getenv(api_base),
                            }
                            if os.getenv("OPENAI_API_TYPE"):
                                connection_args["api_type"] = os.getenv("OPENAI_API_TYPE")
                            if os.getenv("OPENAI_API_VERSION"):
                                connection_args["api_version"] = os.getenv("OPENAI_API_VERSION")

                    embeddings = EmbeddingsContainer.from_uri(
                        embeddings_model, credential=credential, **connection_args
                    )
                else:
                    raise ValueError(f"Unknown embeddings model: {embeddings_model}")
                    # try:
                    #     import sentence_transformers
                    #     if isinstance(embeddings_model, sentence_transformers.SentenceTransformer):
                    #         embeddings = EmbeddingsContainer.from_sentence_transformer(embeddings_model)
                    # except Exception as e:
                    #     logger.warning(f"Failed to load sentence_transformers with {e}.")

        pre_embed = time.time()
        embeddings = embeddings.embed(documents)
        post_embed = time.time()
        logger.info(f"Embedding took {post_embed - pre_embed} seconds")

        if embeddings_container is not None:
            now = datetime.now()
            # TODO: This means new snapshots will be created for every run
            # Ideally there'd be a use container as readonly vs persist snapshot option
            embeddings.save(
                str(
                    Path(embeddings_container)
                    / f"{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}_{str(uuid.uuid4()).split('-', 1)[0]}"
                )
            )

        mlindex = MLIndex.from_embeddings_container(
            embeddings,
            index_type=index_type,
            index_connection=index_connection,
            index_config=index_config,
            output_path=output_path,
            credential=credential,
        )

        return mlindex

    @staticmethod
    def from_embeddings_container(
        embeddings: EmbeddingsContainer,
        index_type: str,
        index_connection: Optional[str] = None,
        index_config: Optional[Dict[str, Any]] = None,
        output_path: Optional[Union[str, Path]] = None,
        credential: Optional[TokenCredential] = None,
    ) -> "MLIndex":
        """
        Create a new MLIndex from embeddings.

        :keyword embeddings: EmbeddingsContainer to index.
        :paramtype embeddings: EmbeddingsContainer
        :keyword index_type: Type of index to use.
        :paramtype index_type: str
        :keyword index_connection: Optional connection to use for index.
        :paramtype index_connection: Optional[str]
        :keyword index_config: Config for index.
        :paramtype index_config: Optional[Dict[str, Any]]
        :keyword output_path: Optional path to save index to.
        :paramtype output_path: Optional[Union[str, Path]]
        :keyword credential: Optional credential to use when resolving connection information.
        :paramtype credential: Optional[TokenCredential]
        :return: A new MLIndex.
        :rtype: MLIndex
        """
        if index_config is None:
            index_config = {}
        if output_path is None:
            output_path = Path.cwd() / f"{index_type}_{embeddings.kind}_index"
        if index_type == "faiss":
            embeddings.write_as_faiss_mlindex(
                output_path=output_path, engine=index_config.get("engine", "indexes.faiss.FaissAndDocStore")
            )

            mlindex = MLIndex(
                uri=Path(output_path),
            )
        elif index_type == "acs":
            from azure.ai.generative.index._tasks.update_acs import create_index_from_raw_embeddings

            if not index_connection:
                index_config = {
                    **index_config,
                    **{
                        "endpoint": os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
                        "api_version": "2023-07-01-preview",
                    },
                }
                connection_args = {"connection_type": "environment", "connection": {"key": "AZURE_AI_SEARCH_KEY"}}
            else:
                if isinstance(index_connection, str):
                    index_connection: Union[  # type: ignore[no-redef]
                        Dict[str, Dict[str, Dict[str, Any]]], Any
                    ] = get_connection_by_id_v2(index_connection, credential=credential)
                index_config = {
                    **index_config,
                    **{
                        "endpoint": (
                            index_connection.target
                            if hasattr(index_connection, "target")
                            else index_connection["properties"]["target"]  # type: ignore[index]
                        ),
                        "api_version": (
                            index_connection.metadata.get("apiVersion", "2023-07-01-preview")
                            if hasattr(index_connection, "metadata")
                            else index_connection["properties"]["metadata"].get(  # type: ignore
                                "apiVersion", "2023-07-01-preview"
                            )
                        ),
                    },
                }
                connection_args = {
                    "connection_type": "workspace_connection",
                    "connection": {"id": get_id_from_connection(index_connection)},
                }

            mlindex = create_index_from_raw_embeddings(
                embeddings,
                index_config,
                connection=connection_args,
                output_path=str(output_path),
                credential=credential,
            )
        elif index_type == "pinecone":
            from azure.ai.generative.index._tasks.update_pinecone import (  # type: ignore[assignment]
                create_index_from_raw_embeddings,
            )

            if not index_connection:
                index_config = {**index_config, **{"environment": os.getenv("PINECONE_ENVIRONMENT")}}
                connection_args = {"connection_type": "environment", "connection": {"key": "PINECONE_API_KEY"}}
            else:
                if isinstance(index_connection, str):
                    index_connection = get_connection_by_id_v2(  # type: ignore[assignment,used-before-def]
                        index_connection, credential=credential
                    )
                index_config = {
                    **index_config,
                    **{"environment": index_connection["properties"]["metadata"]["environment"]},  # type: ignore[index]
                }
                connection_args = {
                    "connection_type": "workspace_connection",
                    "connection": {"id": get_id_from_connection(index_connection)},
                }

            mlindex = create_index_from_raw_embeddings(
                embeddings,
                index_config,
                connection=connection_args,
                output_path=str(output_path),
                credential=credential,
            )
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        return mlindex

    def save(self, output_uri: str, just_config: bool = False):
        """
        Save the MLIndex to a uri.

        Will use uri MLIndex was loaded from if `output_uri` not set.

        :keyword output_uri: The output path of saving the MLIndex.
        :paramtype output_uri: str
        :keyword just_config: Config of saving the MLIndex.
        :paramtype just_config: bool
        """
        # Use fsspec to create MLIndex yaml file at output_uri and call save on _underlying_index if present
        try:
            import fsspec

            mlindex_file = fsspec.open(f"{output_uri.rstrip('/')}/MLIndex", "w")
            # parse yaml to dict
            with mlindex_file as f:
                yaml.safe_dump({"embeddings": self.embeddings_config, "index": self.index_config}, f)

            if not just_config:
                files = fsspec.open_files(f"{self.base_uri}/*")
                files += fsspec.open_files(f"{self.base_uri}/**/*")
                for file in files:
                    if file.path.endswith("MLIndex"):
                        continue

                    with file.open() as src:
                        with fsspec.open(
                            f"{output_uri.rstrip('/')}/{file.path.replace(self.base_uri, '').lstrip('/')}", "wb"
                        ) as dest:
                            dest.write(src.read())
        except Exception as e:
            raise ValueError(f"Could not save MLIndex: {e}") from e
