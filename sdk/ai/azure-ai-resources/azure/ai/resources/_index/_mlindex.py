# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex class for interacting with MLIndex assets."""
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Union

import yaml  # type: ignore[import]
from azure.ai.ml.entities import Data
from azure.core.credentials import TokenCredential
from azure.ai.resources._index._documents import Document
from azure.ai.resources._index._embeddings import EmbeddingsContainer
from azure.ai.resources._index._utils.connections import (
    get_connection_credential,
    get_connection_by_id_v2,
    get_target_from_connection,
)
from azure.ai.resources._index._utils.logging import (
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

    def __init__(
        self,
        uri: Optional[Union[str, Path, Data]] = None,
        mlindex_config: Optional[dict] = None
    ):
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
                try:
                    import fsspec
                except ImportError:
                    raise ValueError(
                        "Could not import fsspec python package. "
                        "Please install it with `pip install fsspec`."
                    )
                try:
                    import azureml.fsspec
                    # TODO: Patch azureml.dataprep auth logic to use given credential for loading MLIndex
                except ImportError:
                    logger.warning(
                        "Could not import azureml-fsspec python package. "
                        "Loading from remote filesystems supported by AzureML will not work. "
                        "Please install it with `pip install azureml-fsspec`."
                    )

                self.base_uri = uri

                mlindex_config = None
                uri = str(uri).rstrip("/")
                mlindex_uri = f"{uri}/MLIndex" if not str(uri).endswith("MLIndex") else uri
                try:
                    mlindex_file = fsspec.open(mlindex_uri, "r")
                    if hasattr(mlindex_file.fs, "_path"):
                        # File on azureml filesystem has path relative to container root so need to get underlying fs path
                        self.base_uri = mlindex_file.fs._path.split("/MLIndex")[0]
                    else:
                        self.base_uri = mlindex_file.path.split("/MLIndex")[0]

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
        """Returns the name of the MLIndex."""
        return self.index_config.get("name", "")

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
        with track_activity(logger, "MLIndex.as_langchain_vectorstore") as activity_logger:
            index_kind = self.index_config.get("kind", "none")

            activity_logger.activity_info["index_kind"] = index_kind
            activity_logger.activity_info["embeddings_kind"] = self.embeddings_config.get("kind", "none")
            activity_logger.activity_info["embeddings_api_type"] = self.embeddings_config.get("api_type", "none")

            if index_kind == "acs":
                from azure.ai.resources._index._indexes.azure_search import import_azure_search_or_so_help_me

                import_azure_search_or_so_help_me()

                if self.index_config.get("field_mapping", {}).get("embedding", None) is None:
                    raise ValueError("field_mapping.embedding must be set in MLIndex config for acs index, try `.as_langchain_retriever()` instead.")

                try:
                    connection_credential = get_connection_credential(self.index_config, credential=credential)
                except Exception as e:
                    # azure.ai.resources has workflow where env vars are set before doing stuff.
                    if "AZURE_AI_SEARCH_KEY" in os.environ or "AZURE_COGNITIVE_SEARCH_KEY" in os.environ:
                        from azure.core.credentials import AzureKeyCredential

                        logger.warning(f"Failed to get credential for ACS with {e}, falling back to env vars.")
                        connection_credential = AzureKeyCredential(os.environ["AZURE_AI_SEARCH_KEY"] if "AZURE_AI_SEARCH_KEY" in os.environ else os.environ["AZURE_COGNITIVE_SEARCH_KEY"])
                    else:
                        raise e

                azure_search_documents_version = packages_versions_for_compatibility["azure-search-documents"]
                if (azure_search_documents_version > "11.4.0b6" and langchain_version > "0.0.273") or (azure_search_documents_version == "11.4.0b6" and langchain_version < "0.0.273" and langchain_version >= "0.0.198"):
                    from langchain.vectorstores import azuresearch
                    # TODO: These fields effect all ACS retrievers in the same process, should change class so it can
                    # use these as defaults but uses names passed in as args preferentially
                    azuresearch.FIELDS_ID = self.index_config.get("field_mapping", {}).get("id", "id")
                    azuresearch.FIELDS_CONTENT = self.index_config.get("field_mapping", {}).get("content", "content")
                    azuresearch.FIELDS_CONTENT_VECTOR = self.index_config.get("field_mapping", {}).get("embedding", "content_vector_open_ai")
                    azuresearch.FIELDS_METADATA = self.index_config.get("field_mapping", {}).get("metadata", "meta_json_string")

                    from azure.core.credentials import AzureKeyCredential
                    from langchain.vectorstores.azuresearch import AzureSearch

                    return AzureSearch(
                        azure_search_endpoint=self.index_config.get(
                            "endpoint",
                            get_target_from_connection(
                                get_connection_by_id_v2(
                                    self.index_config["connection"]["id"],
                                    credential=credential
                                )
                            )
                        ),
                        azure_search_key=connection_credential.key if isinstance(connection_credential, AzureKeyCredential) else None,
                        index_name=self.index_config.get("index"),
                        embedding_function=self.get_langchain_embeddings(credential=credential).embed_query,
                        search_type="hybrid",
                        semantic_configuration_name=self.index_config.get("semantic_configuration_name", "azureml-default"),
                        user_agent=f"azureml-rag=={version}/mlindex,langchain=={langchain_version}",
                    )
                else:
                    from azure.ai.resources._index._langchain.acs import AzureCognitiveSearchVectorStore

                    logger.warning(f"azure-search-documents=={azure_search_documents_version} not compatible langchain.vectorstores.azuresearch yet, using REST client based VectorStore.")

                    return AzureCognitiveSearchVectorStore(
                        index_name=self.index_config.get("index", ""),
                        endpoint=self.index_config.get(
                            "endpoint",
                            get_target_from_connection(
                                get_connection_by_id_v2(
                                    self.index_config["connection"]["id"],
                                    credential=credential
                                )
                            )
                        ),
                        embeddings=self.get_langchain_embeddings(credential=credential),
                        field_mapping=self.index_config.get("field_mapping", {}),
                        credential=connection_credential,
                    )
            elif index_kind == "faiss":
                from fsspec.core import url_to_fs

                store = None
                engine: str = self.index_config.get("engine", "")
                if engine == "langchain.vectorstores.FAISS":
                    from azure.ai.resources._index._langchain.vendor.vectorstores.faiss import FAISS

                    embeddings = EmbeddingsContainer.from_metadata(self.embeddings_config.copy()).as_langchain_embeddings(credential=credential)

                    fs, uri = url_to_fs(self.base_uri)

                    with tempfile.TemporaryDirectory() as tmpdir:
                        fs.download(f"{uri.rstrip('/')}/index.pkl", f"{str(tmpdir)}")
                        fs.download(f"{uri.rstrip('/')}/index.faiss", f"{str(tmpdir)}")
                        store = FAISS.load_local(str(tmpdir), embeddings)
                elif engine.endswith("indexes.faiss.FaissAndDocStore"):
                    from azure.ai.resources._index._indexes.faiss import FaissAndDocStore
                    error_fmt_str = """Failed to import langchain faiss bridge module with: {e}\n"
                        This could be due to an incompatible change in langchain since this bridge was implemented.
                        If you understand what has changed you could implement your own wrapper of azure.ai.tools.mlindex._indexes.faiss.FaissAndDocStore.
                        """
                    try:
                        from azure.ai.resources._index._langchain.faiss import azureml_faiss_as_langchain_faiss
                    except Exception as e:
                        logger.warning(error_fmt_str.format(e=e))
                        azureml_faiss_as_langchain_faiss = None  # type: ignore[assignment]

                    embeddings = EmbeddingsContainer.from_metadata(self.embeddings_config.copy()).as_langchain_embeddings(credential=credential)

                    store: FaissAndDocStore = FaissAndDocStore.load(self.base_uri, embeddings.embed_query)  # type: ignore[no-redef]
                    if azureml_faiss_as_langchain_faiss is not None:
                        try:
                            store = azureml_faiss_as_langchain_faiss(FaissAndDocStore.load(self.base_uri, embeddings.embed_query))
                        except Exception as e:
                            logger.error(error_fmt_str.format(e=e))
                            raise
                else:
                    raise ValueError(f"Unknown engine: {engine}")
                return store
            else:
                raise ValueError(f"Unknown index kind: {index_kind}")

    def as_langchain_retriever(self, credential: Optional[TokenCredential] = None, **kwargs):
        """Converts MLIndex to a retriever object that can be used with langchain, may download files."""
        index_kind = self.index_config.get("kind", None)
        if index_kind == "acs":
            if self.index_config.get("field_mapping", {}).get("embedding", None) is None:
                from azure.ai.resources._index._langchain.acs import AzureCognitiveSearchVectorStore

                connection_credential = get_connection_credential(self.index_config, credential=credential)

                return AzureCognitiveSearchVectorStore(
                    index_name=self.index_config.get("index", ""),
                    endpoint=self.index_config.get(
                        "endpoint",
                        get_target_from_connection(
                            get_connection_by_id_v2(
                                self.index_config["connection"]["id"],
                                credential=credential
                            )
                        )
                    ),
                    embeddings=self.get_langchain_embeddings(credential=credential),
                    field_mapping=self.index_config.get("field_mapping", {}),
                    credential=connection_credential,
                ).as_retriever(**kwargs)

            return self.as_langchain_vectorstore(credential=credential).as_retriever(**kwargs)
        elif index_kind == "faiss":
            return self.as_langchain_vectorstore(credential=credential).as_retriever(*kwargs)
        else:
            raise ValueError(f"Unknown index kind: {index_kind}")

    def __repr__(self):
        """Returns a string representation of the MLIndex object."""
        return yaml.dump({
            "index": self.index_config,
            "embeddings": self.embeddings_config,
        })

    def save(self, output_uri: str, just_config: bool = False):
        """
        Save the MLIndex to a uri.

        Will use uri MLIndex was loaded from if `output_uri` not set.
        """
        # Use fsspec to create MLIndex yaml file at output_uri and call save on _underlying_index if present
        try:
            import fsspec

            mlindex_file = fsspec.open(f"{output_uri.rstrip('/')}/MLIndex", "w")
            # parse yaml to dict
            with mlindex_file as f:
                yaml.safe_dump({
                    "embeddings": self.embeddings_config,
                    "index": self.index_config
                }, f)

            if not just_config:
                files = fsspec.open_files(f"{self.base_uri}/*")
                files += fsspec.open_files(f"{self.base_uri}/**/*")
                for file in files:
                    if file.path.endswith("MLIndex"):
                        continue

                    with file.open() as src:
                        with fsspec.open(f"{output_uri.rstrip('/')}/{file.path.replace(self.base_uri, '').lstrip('/')}", "wb") as dest:
                            dest.write(src.read())
        except Exception as e:
            raise ValueError(f"Could not save MLIndex: {e}") from e
