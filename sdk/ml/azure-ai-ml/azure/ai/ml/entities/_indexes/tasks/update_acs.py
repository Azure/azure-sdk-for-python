# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import os
import time
import traceback
from pathlib import Path
from typing import Optional

import yaml
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SimpleField,
)
from azure.ai.ml.entities._indexes.embeddings import EmbeddingsContainer
from azure.ai.ml.entities._indexes.indexes.index_stores import (
    INDEX_DELETE_FAILURE_MESSAGE_PREFIX,
    INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX,
    AzureCognitiveSearchStore,
)
from azure.ai.ml.entities._indexes.mlindex import MLIndex
from azure.ai.ml.entities._indexes.utils.connections import get_connection_credential
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    packages_versions_for_compatibility,
    safe_mlflow_start_run,
    track_activity,
    version,
)
from packaging import version as pkg_version

logger = get_logger("update_acs")

_azure_logger = logging.getLogger("azure.core.pipeline")
_azure_logger.setLevel(logging.WARNING)

acs_user_agent = f"azureml-rag=={version}/pipeline"
azure_documents_search_version = packages_versions_for_compatibility["azure-search-documents"]
# Limit observed from Azure Search error response as being 32000 (as of 2023-10-23)
AZURE_SEARCH_DOCUMENT_ACTION_BATCH_LIMIT = 30000


def search_client_from_config(acs_config: dict, credential):
    """_Create a SearchClient from an acs_config."""
    return SearchClient(
        endpoint=acs_config["endpoint"],
        index_name=acs_config["index_name"],
        credential=credential,
        api_version=acs_config.get("api_version", "2023-07-01-preview"),
        user_agent=acs_user_agent,
    )


def _vector_search_profile_name(vector_search_field_name: str) -> str:
    """Create the vector search profile name based on acs_config."""
    return f"{vector_search_field_name}_profile"


def _get_field(
    field_type: str,
    field_name: str,
    current_version: pkg_version.Version = None,
    embeddings: Optional[EmbeddingsContainer] = None,
) -> Optional[SearchField]:
    if field_type == "content":
        return SearchableField(name=field_name, type=SearchFieldDataType.String, analyzer_name="standard")
    elif field_type in ["url", "filename", "metadata"]:
        return SimpleField(name=field_name, type=SearchFieldDataType.String)
    elif field_type == "title":
        return SearchableField(name=field_name, type=SearchFieldDataType.String)
    elif field_type == "embedding":
        if current_version >= pkg_version.parse("11.4.0"):
            return SearchField(
                name=field_name,
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=embeddings.get_embedding_dimensions(),
                vector_search_profile_name=_vector_search_profile_name(field_name),
            )
        elif current_version >= pkg_version.parse("11.4.0b11"):
            return SearchField(
                name=field_name,
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=embeddings.get_embedding_dimensions(),
                vector_search_profile=f"{field_name}_config",
            )
        else:
            return SearchField(
                name=field_name,
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=embeddings.get_embedding_dimensions(),
                vector_search_configuration=f"{field_name}_config",
            )
    else:
        logger.warning(f"Unknown field type will be ignored and not included in index: {field_type}")
        return None


def create_search_index_sdk(acs_config: dict, credential, embeddings: Optional[EmbeddingsContainer] = None):
    """
    Create a search index using the Azure Search SDK.

    Args:
    ----
        acs_config (dict): ACS configuration dictionary. Expected to contain:
            - endpoint: ACS endpoint
            - index_name: ACS index name
            - field_mapping: Mappings from a set of fields understood by MLIndex \
                (refer to MLIndex.INDEX_FIELD_MAPPING_TYPES) to ACS field names.
        credential (TokenCredential): Azure credential to use for authentication.
        embeddings (EmbeddingsContainer): EmbeddingsContainer to use for creating the index. \
            If provided, the index will be configured to support vector search.

    """
    logger.info(f"Ensuring search index {acs_config['index_name']} exists")

    index_client = SearchIndexClient(endpoint=acs_config["endpoint"], credential=credential, user_agent=acs_user_agent)
    current_version = pkg_version.parse(azure_documents_search_version)
    if acs_config["index_name"] not in index_client.list_index_names():
        fields = []
        for field_type, field_name in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY].items():
            new_field = _get_field(
                field_type=field_type, field_name=field_name, current_version=current_version, embeddings=embeddings
            )
            if new_field:
                fields.append(new_field)

        fields.append(SimpleField(name="id", type=SearchFieldDataType.String, key=True))

        if "content" not in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
            raise RuntimeError(
                f"ACS index must have a 'content' field. Please specify a 'content' field in the {MLIndex.INDEX_FIELD_MAPPING_KEY} config."
            )

        # Add vector search configuration if embeddings are provided
        vector_search_args = {}
        if (
            str(acs_config.get("push_embeddings", "true")).lower() == "true"
            and embeddings
            and embeddings.kind != "none"
            and "embedding" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]
        ):
            if current_version >= pkg_version.parse("11.4.0"):
                from azure.search.documents.indexes.models import (
                    HnswAlgorithmConfiguration,
                    VectorSearch,
                    VectorSearchProfile,
                )

                algorithm_configuration_name = f"{acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]['embedding']}_config"
                vector_search_args["vector_search"] = VectorSearch(
                    algorithms=[
                        HnswAlgorithmConfiguration(
                            name=algorithm_configuration_name,
                            parameters={"m": 4, "efConstruction": 400, "efSearch": 500, "metric": "cosine"},
                        )
                    ],
                    profiles=[
                        VectorSearchProfile(
                            name=_vector_search_profile_name(acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["embedding"]),
                            algorithm_configuration_name=algorithm_configuration_name,
                        )
                    ],
                )
            elif current_version >= pkg_version.parse("11.4.0b8"):
                from azure.search.documents.indexes.models import HnswVectorSearchAlgorithmConfiguration, VectorSearch

                vector_search_args["vector_search"] = VectorSearch(
                    algorithm_configurations=[
                        HnswVectorSearchAlgorithmConfiguration(
                            name=f"{acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]['embedding']}_config",
                            parameters={"m": 4, "efConstruction": 400, "efSearch": 500, "metric": "cosine"},
                        )
                    ]
                )
            elif current_version >= pkg_version.parse("11.4.0b4"):
                from azure.search.documents.indexes.models import VectorSearch, VectorSearchAlgorithmConfiguration

                vector_search_args["vector_search"] = VectorSearch(
                    algorithm_configurations=[
                        VectorSearchAlgorithmConfiguration(
                            name=f"{acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]['embedding']}_config",
                            kind="hnsw",
                            hnsw_parameters={"m": 4, "efConstruction": 400, "efSearch": 500, "metric": "cosine"},
                        )
                    ]
                )
            else:
                raise RuntimeError(
                    f"azure-search-documents version {azure_documents_search_version} is not supported when using embeddings. Please upgrade to 11.4.0b4 or later."
                )

        # Add semantic search configuration
        if current_version >= pkg_version.parse("11.4.0"):
            from azure.search.documents.indexes.models import SemanticPrioritizedFields

            semantic_config = SemanticConfiguration(
                name="azureml-default",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name=acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["title"])
                    if "title" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]
                    else None,
                    content_fields=[
                        SemanticField(field_name=acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["content"])
                        if "content" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]
                        else None
                    ],
                ),
            )
        else:
            from azure.search.documents.indexes.models import PrioritizedFields

            semantic_config = SemanticConfiguration(
                name="azureml-default",
                prioritized_fields=PrioritizedFields(
                    title_field=SemanticField(field_name=acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["title"])
                    if "title" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]
                    else None,
                    prioritized_content_fields=[
                        SemanticField(field_name=acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["content"])
                    ],
                ),
            )

        # Create index with semantic search configuration
        if current_version >= pkg_version.parse("11.4.0"):
            from azure.search.documents.indexes.models import SemanticSearch

            index = SearchIndex(
                name=acs_config["index_name"],
                fields=fields,
                semantic_search=SemanticSearch(configurations=[semantic_config]),
                **vector_search_args,
            )
        else:
            from azure.search.documents.indexes.models import SemanticSettings

            index = SearchIndex(
                name=acs_config["index_name"],
                fields=fields,
                semantic_settings=SemanticSettings(configurations=[semantic_config]),
                **vector_search_args,
            )

        logger.info(f"Creating {acs_config['index_name']} search index")
        try:
            result = index_client.create_or_update_index(index)
        except Exception as e:
            logger.error(f"Failed to create search index: {e}")
            raise
        logger.info(f"Created {result.name} search index")
    else:
        logger.info(
            f"Search index {acs_config['index_name']} already exists, checking if this index contains all the required fields"
        )
        index = index_client.get_index(acs_config["index_name"])
        existing_fields = index.fields
        existing_fields_length = len(existing_fields)
        existing_fields_names = [field.name for field in existing_fields]
        new_fields = existing_fields
        for field_type, field_name in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY].items():
            if field_name not in existing_fields_names:
                new_field = _get_field(
                    field_type=field_type, field_name=field_name, current_version=current_version, embeddings=embeddings
                )
                if new_field:
                    new_fields.append(new_field)

        if len(new_fields) > existing_fields_length:
            new_index = SearchIndex(
                name=index.name,
                fields=new_fields,
                semantic_settings=index.semantic_settings,
                vector_search=index.vector_search,
            )
            logger.info(f"Updating {acs_config['index_name']} search index")
            result = index_client.create_or_update_index(new_index)
            logger.info(f"Updated {result.name} search index")


def create_index_from_raw_embeddings(
    emb: EmbeddingsContainer,
    acs_config=None,
    connection=None,
    output_path: Optional[str] = None,
    credential: Optional[TokenCredential] = None,
    verbosity: int = 1,
) -> MLIndex:
    """Upload an EmbeddingsContainer to Azure Cognitive Search and return an MLIndex."""
    with track_activity(
        logger, "update_acs", custom_dimensions={"num_documents": len(emb._document_embeddings)}
    ) as activity_logger:
        logger.info("Updating ACS index")

        # Copy acs_config to avoid modifying the input
        acs_config = None if acs_config is None else acs_config.copy()
        # Copy connection to avoid modifying the input
        connection = None if connection is None else connection.copy()

        connection_credential = get_connection_credential(connection, credential=credential)

        if MLIndex.INDEX_FIELD_MAPPING_KEY not in acs_config:
            acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY] = {
                "content": "content",
                "url": "url",
                "filename": "filepath",
                "title": "title",
                "metadata": "meta_json_string",
            }
            if str(acs_config.get("push_embeddings", "true")).lower() == "true" and emb and emb.kind != "none":
                acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["embedding"] = "contentVector"

        logger.info(f"Using Index fields: {json.dumps(acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY], indent=2)}")

        create_search_index_sdk(acs_config, connection_credential, emb)

        search_client = search_client_from_config(acs_config, connection_credential)

        batch_size = acs_config.get("batch_size", 100)

        include_embeddings = (
            str(acs_config.get("push_embeddings", "true")).lower() == "true"
            and emb
            and emb.kind != "none"
            and "embedding" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]
        )
        logger.info(f"Documents include embeddings: {include_embeddings}")

        acs_index_store = AzureCognitiveSearchStore(search_client, include_embeddings=include_embeddings)

        # Delete removed documents
        emb.delete_from_index(
            acs_index_store,
            batch_size=AZURE_SEARCH_DOCUMENT_ACTION_BATCH_LIMIT,
            activity_logger=activity_logger,
            verbosity=verbosity,
        )

        # Upload documents
        emb.upload_to_index(
            acs_index_store, acs_config, batch_size=batch_size, activity_logger=activity_logger, verbosity=verbosity
        )

        logger.info("Writing MLIndex yaml")
        mlindex_config = {"embeddings": emb.get_metadata()}

        mlindex_config["index"] = {
            "kind": "acs",
            "engine": "azure-sdk",
            "index": acs_config["index_name"],
            "api_version": acs_config.get("api_version", "2023-07-01-preview"),
            "field_mapping": acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY],
            "semantic_configuration_name": "azureml-default",
        }

        if not isinstance(connection, DefaultAzureCredential):
            mlindex_config["index"] = {**mlindex_config["index"], **connection}

        # Keyvault auth and Default ambient auth need the endpoint, Workspace Connection auth could get endpoint.
        mlindex_config["index"]["endpoint"] = acs_config["endpoint"]

        if output_path is not None:
            output = Path(output_path)
            output.mkdir(parents=True, exist_ok=True)
            with (output / "MLIndex").open("w") as f:
                yaml.dump(mlindex_config, f)

    mlindex = MLIndex(uri=output_path, mlindex_config=mlindex_config)
    return mlindex


def main(args, logger, activity_logger):
    """Main function for updating an ACS index with embeddings."""
    try:
        try:
            acs_config = json.loads(args.acs_config)
        except Exception as e:
            logger.error(f"Failed to parse acs_config as json: {e}")
            activity_logger.error("Failed to parse acs_config as json")
            raise

        connection_args = {}

        if args.connection_id is not None:
            connection_args["connection_type"] = "workspace_connection"
            connection_args["connection"] = {"id": args.connection_id}
            from azure.ai.ml.entities._indexes.utils.connections import (
                get_connection_by_id_v2,
                get_metadata_from_connection,
                get_target_from_connection,
            )

            connection = get_connection_by_id_v2(args.connection_id)
            acs_config["endpoint"] = get_target_from_connection(connection)
            acs_config["api_version"] = get_metadata_from_connection(connection).get("apiVersion", "2023-07-01-preview")
        elif "endpoint_key_name" in acs_config:
            connection_args["connection_type"] = "workspace_keyvault"
            from azureml.core import Run

            run = Run.get_context()
            ws = run.experiment.workspace
            connection_args["connection"] = {
                "key": acs_config["endpoint_key_name"],
                "subscription": ws.subscription_id,
                "resource_group": ws.resource_group,
                "workspace": ws.name,
            }

        # Mount embeddings container and create index from it
        raw_embeddings_uri = args.embeddings
        logger.info(f"got embeddings uri as input: {raw_embeddings_uri}")
        splits = raw_embeddings_uri.split("/")
        embeddings_dir_name = splits.pop(len(splits) - 2)
        logger.info(f"extracted embeddings directory name: {embeddings_dir_name}")
        parent = "/".join(splits)
        logger.info(f"extracted embeddings container path: {parent}")

        from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount

        mnt_options = MountOptions(default_permission=0o555, allow_other=False, read_only=True)
        logger.info(f"mounting embeddings container from: \n{parent} \n   to: \n{Path.cwd()}/embeddings_mount")
        with rslex_uri_volume_mount(parent, f"{Path.cwd()}/embeddings_mount", options=mnt_options) as mount_context:
            emb = EmbeddingsContainer.load(embeddings_dir_name, mount_context.mount_point)
            create_index_from_raw_embeddings(
                emb,
                acs_config=acs_config,
                connection=connection_args,
                output_path=args.output,
                verbosity=args.verbosity,
            )

    except Exception as e:
        logger.error("Failed to update ACS index")
        exception_str = str(e)
        if "Floats quota has been exceeded for this service." in exception_str:
            logger.error(
                "Floats quota exceeded on Azure Cognitive Search Service. For more information check these docs: https://github.com/Azure/cognitive-search-vector-pr#storage-and-vector-index-size-limits"
            )
            logger.error(
                "The usage statistic of an index can be checked using this REST API: https://learn.microsoft.com/en-us/rest/api/searchservice/get-index-statistics "
            )
            activity_logger.activity_info["error_classification"] = "UserError"
            activity_logger.activity_info["error"] = (
                f"{e.__class__.__name__}: Floats quota has been exceeded for this service."
            )
        elif "Cannot find nested property" in exception_str:
            logger.error(
                f'The vector index provided "{acs_config["index_name"]}" has a different schema than outlined in this components description. This can happen if a different embedding model was used previously when updating this index.'
            )
            activity_logger.activity_info["error_classification"] = "UserError"
            activity_logger.activity_info["error"] = f"{e.__class__.__name__}: Cannot find nested property"
        elif (
            INDEX_DELETE_FAILURE_MESSAGE_PREFIX in exception_str or INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX in exception_str
        ):
            activity_logger.activity_info["error"] = exception_str
            activity_logger.activity_info["error_classification"] = "SystemError"
        else:
            activity_logger.activity_info["error"] = str(e.__class__.__name__)
            activity_logger.activity_info["error_classification"] = "SystemError"
        raise e

    logger.info("Updated ACS index")


def main_wrapper(args, logger):
    """Wrapper function for main function to handle exceptions and logging."""
    with track_activity(logger, "update_acs") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(
                f"update_acs failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--embeddings", type=str)
    parser.add_argument("--acs_config", type=str)
    parser.add_argument("--connection_id", type=str, required=False)
    parser.add_argument("--output", type=str)
    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        help="Defaults to 1, which will log aggregate information about documents and IDs of deleted documents. 2 will log all document_ids as they are processed.",
    )
    args = parser.parse_args()

    print("\n".join(f"{k}={v}" for k, v in vars(args).items()))

    enable_stdout_logging()
    enable_appinsights_logging()

    if args.connection_id is None:
        logger.info("Reading connection id from environment variable")
        args.connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_ACS")

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
