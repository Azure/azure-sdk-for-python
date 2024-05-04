# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex class for interacting with MLIndex assets."""

import os
import tempfile
import logging
from importlib.util import find_spec
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional, Union

import yaml
from azure.core.credentials import TokenCredential
from azure.ai.ml.entities._indexes.embeddings import EmbeddingsContainer
from azure.ai.ml.entities._indexes.utils.connections import (
    get_connection_by_id_v2,
    get_connection_credential,
    get_target_from_connection,
)
from azure.ai.ml.entities._indexes.utils.versions import (
    langchain_version,
    packages_versions_for_compatibility,
)
from packaging import version as pkg_version

logger = logging.getLogger(__name__)


class MLIndex:
    """MLIndex class for interacting with MLIndex assets."""

    INDEX_FIELD_MAPPING_KEY: ClassVar[str] = "field_mapping"
    INDEX_FIELD_MAPPING_TYPES: ClassVar[Dict[str, str]] = {
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

    def __init__(self, uri: Optional[Union[str, Path, object]] = None, mlindex_config: Optional[dict] = None):
        """
        Initialize MLIndex from a URI or AzureML Data Asset.

        Args:
        ----
            uri: URI to MLIndex asset folder (remote or local)
            mlindex_config: MLIndex config dictionary
            credential: Credential to use for talking to Azure resources

        """
        if uri is not None:
            # if uri is not str or Path, then assume given AzureML Data Asset
            uri = str(uri) if isinstance(uri, (str, Path)) else uri.path

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
                    # so need to get underlying fs path
                    self.base_uri = mlindex_file.fs._path.split("/MLIndex")[0]
                else:
                    self.base_uri = mlindex_file.path.split("/MLIndex")[0]

                with mlindex_file as f:
                    mlindex_config = yaml.safe_load(f)
            except Exception as e:
                raise ValueError(f"Could not find MLIndex: {e}") from e
        elif mlindex_config is None:
            raise ValueError("Must provide either uri or mlindex_config")
        else:
            self.base_uri = None

        self.index_config = mlindex_config.get("index", {})
        if self.index_config is None:
            raise ValueError("Could not find index config in MLIndex yaml")
        self.embeddings_config = mlindex_config.get("embeddings", {})
        if self.embeddings_config is None:
            raise ValueError("Could not find embeddings config in MLIndex yaml")

    @property
    def name(self) -> str:
        """Returns the name of the MLIndex."""
        return self.index_config.get("name", self.index_config.get("index", ""))

    @name.setter
    def name(self, value: str):
        """Sets the name of the MLIndex."""
        self.index_config["name"] = value

    @property
    def description(self) -> str:
        """Returns the description of the MLIndex."""
        return self.index_config.get("description", "")

    @description.setter
    def description(self, value: str):
        """Sets the description of the MLIndex."""
        self.index_config["description"] = value

    def get_langchain_embeddings(self, credential: Optional[TokenCredential] = None):
        """Get the LangChainEmbeddings from the MLIndex."""
        embeddings = EmbeddingsContainer.from_metadata(self.embeddings_config.copy())

        return embeddings.as_langchain_embeddings(credential=credential)

    def as_langchain_vectorstore(self, credential: Optional[TokenCredential] = None):
        """Converts MLIndex to a retriever object that can be used with langchain, may download files."""

        langchain_pkg_version = pkg_version.parse(langchain_version)

        index_kind = self.index_config.get("kind", "none")
        if index_kind == "acs":
            if self.index_config.get("field_mapping", {}).get("embedding", None) is None:
                raise ValueError(
                    "field_mapping.embedding must be set in MLIndex config for acs index, try `.as_langchain_retriever()` instead."
                )

            try:
                connection_credential = get_connection_credential(self.index_config, credential=credential)
            except Exception as e:
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

            azure_search_documents_version = packages_versions_for_compatibility["azure-search-documents"]
            search_client_version = pkg_version.parse(azure_search_documents_version)
            if langchain_pkg_version >= pkg_version.parse("0.1.00"):
                from azure.ai.ml.entities._indexes.utils import _get_azuresearch_module_instance

                azuresearch = _get_azuresearch_module_instance(langchain_pkg_version)

                azuresearch.FIELDS_ID = self.index_config.get("field_mapping", {}).get("id", "id")
                azuresearch.FIELDS_CONTENT = self.index_config.get("field_mapping", {}).get("content", "content")
                azuresearch.FIELDS_CONTENT_VECTOR = self.index_config.get("field_mapping", {}).get(
                    "embedding", "content_vector_open_ai"
                )
                azuresearch.FIELDS_METADATA = self.index_config.get("field_mapping", {}).get(
                    "metadata", "meta_json_string"
                )
                from azure.core.credentials import AzureKeyCredential

                endpoint = self.index_config.get("endpoint", None)
                if not endpoint:
                    endpoint = get_target_from_connection(
                        get_connection_by_id_v2(self.index_config["connection"]["id"], credential=credential)
                    )

                return azuresearch.AzureSearch(
                    azure_search_endpoint=endpoint,
                    azure_search_key=connection_credential.key
                    if isinstance(connection_credential, AzureKeyCredential)
                    else None,
                    index_name=self.index_config.get("index"),
                    embedding_function=self.get_langchain_embeddings(credential=credential).embed_query,
                    search_type="hybrid",
                    semantic_configuration_name=self.index_config.get(
                        "semantic_configuration_name", "azureml-default"
                    ),
                    user_agent=f"langchain=={langchain_version}",
                )
            elif (
                search_client_version > pkg_version.parse("11.4.0b6")
                and search_client_version <= pkg_version.parse("11.4.0b8")
                and langchain_pkg_version > pkg_version.parse("0.0.273")
            ) or (
                search_client_version == pkg_version.parse("11.4.0b6")
                and langchain_pkg_version < pkg_version.parse("0.0.273")
                and langchain_pkg_version >= pkg_version.parse("0.0.198")
            ):
                from azure.ai.ml.entities._indexes.entities.utils import _get_azuresearch_module_instance

                azuresearch = _get_azuresearch_module_instance(langchain_pkg_version)

                azuresearch.FIELDS_ID = self.index_config.get("field_mapping", {}).get("id", "id")
                azuresearch.FIELDS_CONTENT = self.index_config.get("field_mapping", {}).get("content", "content")
                azuresearch.FIELDS_CONTENT_VECTOR = self.index_config.get("field_mapping", {}).get(
                    "embedding", "content_vector_open_ai"
                )
                azuresearch.FIELDS_METADATA = self.index_config.get("field_mapping", {}).get(
                    "metadata", "meta_json_string"
                )

                from azure.core.credentials import AzureKeyCredential
                from langchain.vectorstores import AzureSearch

                endpoint = self.index_config.get("endpoint", None)
                if not endpoint:
                    endpoint = get_target_from_connection(
                        get_connection_by_id_v2(self.index_config["connection"]["id"], credential=credential)
                    )

                return azuresearch.AzureSearch(
                    azure_search_endpoint=endpoint,
                    azure_search_key=connection_credential.key
                    if isinstance(connection_credential, AzureKeyCredential)
                    else None,
                    index_name=self.index_config.get("index"),
                    embedding_function=self.get_langchain_embeddings(credential=credential).embed_query,
                    search_type="hybrid",
                    semantic_configuration_name=self.index_config.get(
                        "semantic_configuration_name", "azureml-default"
                    ),
                    user_agent=f"langchain=={langchain_version}",
                )
            else:
                from azure.ai.ml.entities._indexes.entities.acs import AzureCognitiveSearchVectorStore

                logger.warning(
                    f"azure-search-documents=={azure_search_documents_version} not compatible langchain.vectorstores.azuresearch yet, using REST client based VectorStore."
                )

                return AzureCognitiveSearchVectorStore(
                    index_name=self.index_config.get("index"),
                    endpoint=self.index_config.get(
                        "endpoint",
                        get_target_from_connection(
                            get_connection_by_id_v2(self.index_config["connection"]["id"], credential=credential)
                        ),
                    ),
                    embeddings=self.get_langchain_embeddings(credential=credential),
                    field_mapping=self.index_config.get("field_mapping", {}),
                    credential=connection_credential,
                )
        elif index_kind == "faiss":
            from fsspec.core import url_to_fs

            store = None
            engine = self.index_config.get("engine")
            if engine == "langchain.vectorstores.FAISS":
                embeddings = EmbeddingsContainer.from_metadata(
                    self.embeddings_config.copy()
                ).as_langchain_embeddings(credential=credential)

                # langchain fix https://github.com/langchain-ai/langchain/pull/10823 released in 0.0.318
                if langchain_pkg_version >= pkg_version.parse("0.0.318"):
                    embeddings = embeddings.embed_query

                fs, uri = url_to_fs(self.index_config.get("path", self.base_uri))

                with tempfile.TemporaryDirectory() as tmpdir:
                    fs.download(f"{uri.rstrip('/')}/index.pkl", f"{tmpdir!s}")
                    fs.download(f"{uri.rstrip('/')}/index.faiss", f"{tmpdir!s}")

                    if langchain_pkg_version >= pkg_version.parse("0.1.0"):
                        from langchain_community.vectorstores import FAISS

                        store = FAISS.load_local(str(tmpdir), embeddings, allow_dangerous_deserialization=True)
                    else:
                        from langchain.vectorstores import FAISS

                        store = FAISS.load_local(str(tmpdir), embeddings)
                # except Exception as e:
                    #     logger.warning(
                    #         f"Failed to load FAISS Index using installed version of langchain, retrying with vendored FAISS VectorStore.\n{e}"
                    #     )
                    #     from azureml.rag.langchain.vendor.vectorstores.faiss import FAISS

                    #     store = FAISS.load_local(str(tmpdir), embeddings)
            # This is not supported for avoiding binging too many dup files from azureml.rag
            # elif engine.endswith("indexes.faiss.FaissAndDocStore"):
            #     from azureml.rag.indexes.faiss import FaissAndDocStore

            #     error_fmt_str = """Failed to import langchain faiss bridge module with: {e}\n"
            #         This could be due to an incompatible change in langchain since this bridge was implemented.
            #         If you understand what has changed you could implement your own wrapper of azure.ai.tools.mlindex.indexes.faiss.FaissAndDocStore.
            #         """
            #     try:
            #         from azureml.rag.langchain.faiss import azureml_faiss_as_langchain_faiss
            #     except Exception as e:
            #         logger.warning(error_fmt_str.format(e=e))
            #         azureml_faiss_as_langchain_faiss = None

            #     embeddings = EmbeddingsContainer.from_metadata(
            #         self.embeddings_config.copy()
            #     ).as_langchain_embeddings(credential=credential)

            #     store = FaissAndDocStore.load(self.index_config.get("path", self.base_uri), embeddings.embed_query)
            #     if azureml_faiss_as_langchain_faiss is not None:
            #         try:
            #             store = azureml_faiss_as_langchain_faiss(
            #                 FaissAndDocStore.load(
            #                     self.index_config.get("path", self.base_uri), embeddings.embed_query
            #                 )
            #             )
            #         except Exception as e:
            #             logger.error(error_fmt_str.format(e=e))
            #             raise
            else:
                raise ValueError(f"Unknown engine: {engine}")
            return store
        elif index_kind == "elasticsearch":
            try:
                from langchain_community.vectorstores import ElasticsearchStore
                from azure.core.credentials import AzureKeyCredential

                connection_credential = get_connection_credential(self.index_config, credential=credential)
                if not isinstance(connection_credential, AzureKeyCredential):
                    raise ValueError(
                        f"Expected credential to Elasticsearch index to be an AzureKeyCredential, instead got: {type(connection_credential)}"
                    )
                # Get the connection credential to connect to elasticSearch es cloud ID
                es_connection_url = self.index_config.get("endpoint")
                logger.info(f"Parsed elasticsearch endpoint: {es_connection_url}")

                return ElasticsearchStore(
                    index_name=self.index_config.get("index"),
                    es_url=es_connection_url,
                    es_api_key=connection_credential.key,
                    embedding=self.get_langchain_embeddings(credential=credential),
                    vector_query_field=self.index_config.get("field_mapping", {}).get("embedding", "contentVector"),
                    query_field=self.index_config.get("field_mapping", {}).get("content", "text")
                )
            except Exception as e:
                logger.warn(
                    f"Failed to get elasticsearch vectorstore due to {e}, try again by passing in `embedding` as an Embeddings object."
                )
                raise
        elif index_kind == "pinecone":
            try:
                from azure.core.credentials import AzureKeyCredential
                from langchain_pinecone import PineconeVectorStore
                from pinecone import Pinecone

                connection_credential = get_connection_credential(self.index_config, credential=credential)
                if not isinstance(connection_credential, AzureKeyCredential):
                    raise ValueError(
                        f"Expected credential to Pinecone index to be an AzureKeyCredential, instead got: {type(connection_credential)}"
                    )

                pc = Pinecone(api_key=connection_credential.key)
                index_stats = pc.describe_index(self.index_config.get("index"))
                logger.info(f"Pinecone index {self.index_config.get('index')} with stats {str(index_stats)}")
                activity_logger.info("Pinecone index", extra={"properties": {"stats": str(index_stats)}})

                return PineconeVectorStore(
                    embedding=self.get_langchain_embeddings(credential=credential),
                    text_key=self.index_config.get("field_mapping", {})["content"],
                    pinecone_api_key=connection_credential.key,
                    index_name=self.index_config.get("index"),
                )
            except Exception as e:
                logger.error(f"Failed to create Pinecone vectorstore due to: {e}")
                raise
        elif index_kind == "milvus":
            try:
                from azure.core.credentials import AzureKeyCredential
                try:
                    from langchain.vectorstores.milvus import Milvus
                except ImportError:
                    from langchain_community.vectorstores.milvus import Milvus

                connection_credential = get_connection_credential(self.index_config, credential=credential)
                if not isinstance(connection_credential, AzureKeyCredential):
                    raise ValueError(
                        f"Invalid workspace connection credential type: {type(connection_credential)}. Expected: AzureKeyCredential"
                    )
                return Milvus(
                    embedding_function=self.get_langchain_embeddings(credential=credential),
                    collection_name=self.index_config.get("index"),
                    connection_args={"uri": self.index_config.get("uri"), "token": connection_credential.key},
                    primary_field="id",
                    text_field=self.index_config.get("field_mapping", {}).get("content", "content"),
                    vector_field=self.index_config.get("field_mapping", {}).get("embedding", "contentVector"),
                )
            except Exception as e:
                logger.error(f"Failed to create Milvus vectorstore due to: {e}")
                raise
        elif index_kind == "azure_cosmos_mongo_vcore":
            try:
                from azure.core.credentials import AzureKeyCredential
                from pymongo.mongo_client import MongoClient
                try:
                    from langchain.vectorstores.azure_cosmos_db import AzureCosmosDBVectorSearch
                except ImportError:
                    from langchain_community.vectorstores.azure_cosmos_db import AzureCosmosDBVectorSearch

                connection_credential = get_connection_credential(self.index_config, credential=credential)
                if not isinstance(connection_credential, AzureKeyCredential):
                    raise ValueError(
                        f"Expected credential to Azure Cosmos Mongo vCore index to be an AzureKeyCredential, instead got: {type(connection_credential)}"
                    )

                mongo_client = MongoClient(connection_credential.key)
                mongo_collection = mongo_client[self.index_config.get("database")][
                    self.index_config.get("collection")
                ]
                return AzureCosmosDBVectorSearch(
                    mongo_collection,
                    self.get_langchain_embeddings(credential=credential),
                    index_name=self.index_config.get("index"),
                    text_key=self.index_config.get("field_mapping", {}).get("content", "content"),
                    embedding_key=self.index_config.get("field_mapping", {}).get("embedding", "contentVector"),
                )
            except Exception as e:
                logger.error(f"Failed to create Azure Cosmos Mongo vCore vectorstore due to: {e}")
                raise
        else:
            raise ValueError(f"Unknown index kind: {index_kind}")

    def as_langchain_retriever(self, credential: Optional[TokenCredential] = None, **kwargs):
        """Converts MLIndex to a retriever object that can be used with langchain, may download files."""
        index_kind = self.index_config.get("kind", None)
        if index_kind == "acs":
            if self.index_config.get("field_mapping", {}).get("embedding", None) is None:
                from azure.ai.ml.entities._indexes.entities.acs import AzureCognitiveSearchVectorStore

                connection_credential = get_connection_credential(self.index_config, credential=credential)

                endpoint = self.index_config.get("endpoint", None)
                if not endpoint:
                    endpoint = get_target_from_connection(
                        get_connection_by_id_v2(self.index_config["connection"]["id"], credential=credential)
                    )
                return AzureCognitiveSearchVectorStore(
                    index_name=self.index_config.get("index"),
                    endpoint=endpoint,
                    embeddings=self.get_langchain_embeddings(),
                    field_mapping=self.index_config.get("field_mapping", {}),
                    credential=connection_credential,
                ).as_retriever(**kwargs)

            return self.as_langchain_vectorstore(credential=credential).as_retriever(**kwargs)
        elif index_kind in ["faiss", "pinecone", "milvus", "azure_cosmos_mongo_vcore"]:
            return self.as_langchain_vectorstore(credential=credential).as_retriever(**kwargs)
        else:
            raise ValueError(f"Unknown index kind: {index_kind}")

    def __repr__(self):
        """Returns a string representation of the MLIndex object."""
        return yaml.dump(
            {
                "index": self.index_config,
                "embeddings": self.embeddings_config,
            }
        )
