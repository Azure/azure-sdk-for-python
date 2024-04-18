# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import time
import traceback
from enum import Enum
from pathlib import Path
from typing import List, Optional

import yaml
from azure.core import CaseInsensitiveEnumMeta
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.ai.ml.entities._indexes.embeddings import EmbeddingsContainer
from azure.ai.ml.entities._indexes.indexes.index_stores import (
    INDEX_DELETE_FAILURE_MESSAGE_PREFIX,
    INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX,
    AzureCosmosMongoVcoreStore,
)
from azure.ai.ml.entities._indexes.mlindex import MLIndex
from azure.ai.ml.entities._indexes.utils.connections import get_connection_credential
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)
from pymongo.mongo_client import MongoClient

INDEX_KIND = "vector-ivf"
INDEX_SIMILARITY_METRIC = "COS"


class IndexUpdateAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """DataflowType."""

    DELETE = "Delete"
    UPLOAD = "Upload"


logger = get_logger("update_azure_cosmos_mongo_vcore")


def get_mongo_client(connection_string: str) -> MongoClient:
    """
    Initialize and return a Mongo client.

    Args:
    ----
        connection_string (str): Connection string to use for authentication to the Mongo client.

    """
    return MongoClient(connection_string)


def create_azure_cosmos_mongo_vcore_index_sdk(
    azure_cosmos_mongo_vcore_config: dict, connection_string: str, embeddings: Optional[EmbeddingsContainer] = None
):
    """
    Create a Azure Cosmos Mongo vCore index using the PyMongo SDK.

    Args:
    ----
        azure_cosmos_mongo_vcore_config (dict): Azure Cosmos Mongo vCore configuration dictionary. Expected to contain:
            - database_name: Azure Cosmos Mongo vCore database name
            - collection_name: Azure Cosmos Mongo vCore collection name
            - index_name: Azure Cosmos Mongo vCore index name
            - field_mapping: Mappings from a set of fields understood by MLIndex (refer to MLIndex.INDEX_FIELD_MAPPING_TYPES) to Azure Cosmos Mongo vCore field names.

        connection_string (str): Connection string to use for authentication to the Mongo client.
        embeddings (EmbeddingsContainer): EmbeddingsContainer to use for creating the index. If provided, the index will be configured to support vector search.

    """
    try:
        database_name = azure_cosmos_mongo_vcore_config["database_name"]
        collection_name = azure_cosmos_mongo_vcore_config["collection_name"]
        index_name = azure_cosmos_mongo_vcore_config["index_name"]
        logger.info(
            f"Ensuring index {index_name} for collection {collection_name} under database {database_name} exists"
        )

        mongo_client = get_mongo_client(connection_string)

        dbs = mongo_client.list_database_names()
        if database_name in dbs:
            logger.info(f"Database {database_name} exists")
            collections = mongo_client[database_name].list_collection_names()
            if collection_name in collections:
                print(f"Collection {collection_name} exists")

        mongo_collection = mongo_client[database_name][collection_name]

        indexes = mongo_collection.index_information()
        if indexes.get(index_name) == None:
            index_dimensions = embeddings.get_embedding_dimensions()
            logger.info(
                f"Creating {index_name} index of kind {INDEX_KIND} with similarity metric {INDEX_SIMILARITY_METRIC} and dimensions {index_dimensions}"
            )
            indexDefs: List[any] = [
                {
                    "name": index_name,
                    "key": {
                        azure_cosmos_mongo_vcore_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["embedding"]: "cosmosSearch"
                    },
                    "cosmosSearchOptions": {
                        "kind": INDEX_KIND,
                        "similarity": INDEX_SIMILARITY_METRIC,
                        "dimensions": index_dimensions,
                    },
                }
            ]
            mongo_client[database_name].command("createIndexes", collection_name, indexes=indexDefs)
            logger.info(f"Created {index_name} index")
        else:
            logger.info(f"Index {index_name} already exists")
    except Exception as e:
        logger.error(f"Failed to create index. Error: {e!s}", exc_info=True, extra={"exception": str(e)})
        raise


def create_index_from_raw_embeddings(
    emb: EmbeddingsContainer,
    azure_cosmos_mongo_vcore_config: dict = {},
    connection: dict = {},
    output_path: Optional[str] = None,
    credential: Optional[TokenCredential] = None,
    verbosity: int = 1,
) -> MLIndex:
    """
    Upload an EmbeddingsContainer to Azure Cosmos Mongo vCore and return an MLIndex.

    Args:
    ----
        emb (EmbeddingsContainer): EmbeddingsContainer to use for creating the index. If provided, the index will be configured to support vector search.
        azure_cosmos_mongo_vcore_config (dict): Azure Cosmos Mongo vCore configuration dictionary. Expected to contain:
            - database_name: Azure Cosmos Mongo vCore database name
            - collection_name: Azure Cosmos Mongo vCore collection name
            - index_name: Azure Cosmos Mongo vCore index name
            - field_mapping: Mappings from a set of fields understood by MLIndex (refer to MLIndex.INDEX_FIELD_MAPPING_TYPES) to Azure Cosmos Mongo vCore field names.

        connection (dict): Connection configuration dictionary describing the type of the connection to the Azure Cosmos Mongo vCore index.
        output_path (str): The output path to store the MLIndex.
        credential (TokenCredential): Azure credential to use for authentication.
        verbosity (int): Defaults to 1, which will log aggregate information about documents and IDs of deleted documents. 2 will log all document_ids as they are processed.

    """
    with track_activity(
        logger, "update_azure_cosmos_mongo_vcore", custom_dimensions={"num_documents": len(emb._document_embeddings)}
    ) as activity_logger:
        logger.info("Updating Azure Cosmos Mongo vCore index")

        if MLIndex.INDEX_FIELD_MAPPING_KEY not in azure_cosmos_mongo_vcore_config:
            azure_cosmos_mongo_vcore_config[MLIndex.INDEX_FIELD_MAPPING_KEY] = {
                "content": "content",
                "url": "url",
                "filename": "filepath",
                "title": "title",
                "metadata": "metadata_json_string",
            }
            if emb and emb.kind != "none":
                azure_cosmos_mongo_vcore_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["embedding"] = "contentVector"

        logger.info(
            f"Using Index fields: {json.dumps(azure_cosmos_mongo_vcore_config[MLIndex.INDEX_FIELD_MAPPING_KEY], indent=2)}"
        )

        connection_credential = get_connection_credential(connection, credential=credential)
        if not isinstance(connection_credential, AzureKeyCredential):
            raise ValueError(
                f"Expected credential to Azure Cosmos Mongo vCore index to be an AzureKeyCredential, instead got: {type(connection_credential)}"
            )

        create_azure_cosmos_mongo_vcore_index_sdk(
            azure_cosmos_mongo_vcore_config, connection_credential.key, embeddings=emb
        )

        mongo_client = get_mongo_client(connection_credential.key)
        mongo_collection = mongo_client[azure_cosmos_mongo_vcore_config["database_name"]][
            azure_cosmos_mongo_vcore_config["collection_name"]
        ]

        batch_size = azure_cosmos_mongo_vcore_config.get("batch_size", 100)

        cosmos_mongo_vcore_index_store = AzureCosmosMongoVcoreStore(mongo_collection)

        # Delete documents
        emb.delete_from_index(
            cosmos_mongo_vcore_index_store, batch_size=None, activity_logger=activity_logger, verbosity=verbosity
        )

        # Upload documents
        has_embeddings = (
            emb
            and emb.kind != "none"
            and "embedding" in azure_cosmos_mongo_vcore_config[MLIndex.INDEX_FIELD_MAPPING_KEY]
        )
        logger.info(f"Has embeddings: {has_embeddings}")

        if has_embeddings:
            emb.upload_to_index(
                cosmos_mongo_vcore_index_store,
                azure_cosmos_mongo_vcore_config,
                batch_size=batch_size,
                activity_logger=activity_logger,
                verbosity=verbosity,
            )
        else:
            logger.error(
                "Documents do not have embeddings and therefore cannot upload to Azure Cosmos Mongo vCore index"
            )
            raise RuntimeError(
                "Failed to upload to Azure Cosmos Mongo vCore index since documents do not have embeddings"
            )

        logger.info("Writing MLIndex yaml")
        mlindex_config = {"embeddings": emb.get_metadata()}
        mlindex_config["index"] = {
            "kind": "azure_cosmos_mongo_vcore",
            "engine": "pymongo-sdk",
            "database": azure_cosmos_mongo_vcore_config["database_name"],
            "collection": azure_cosmos_mongo_vcore_config["collection_name"],
            "index": azure_cosmos_mongo_vcore_config["index_name"],
            "field_mapping": azure_cosmos_mongo_vcore_config[MLIndex.INDEX_FIELD_MAPPING_KEY],
        }

        mlindex_config["index"] = {**mlindex_config["index"], **connection}

        if output_path is not None:
            output = Path(output_path)
            output.mkdir(parents=True, exist_ok=True)
            with open(output / "MLIndex", "w") as f:
                yaml.dump(mlindex_config, f)

    mlindex = MLIndex(uri=output_path, mlindex_config=mlindex_config)
    return mlindex


def main(args, logger, activity_logger):
    try:
        try:
            azure_cosmos_mongo_vcore_config = json.loads(args.azure_cosmos_mongo_vcore_config)
        except Exception as e:
            logger.error(f"Failed to parse azure_cosmos_mongo_vcore_config as json: {e}")
            activity_logger.error("Failed to parse azure_cosmos_mongo_vcore_config as json")
            raise

        connection_args = {}

        if args.connection_id is not None:
            connection_args["connection_type"] = "workspace_connection"
            connection_args["connection"] = {"id": args.connection_id}

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
                azure_cosmos_mongo_vcore_config=azure_cosmos_mongo_vcore_config,
                connection=connection_args,
                output_path=args.output,
                verbosity=args.verbosity,
            )
    except Exception as e:
        logger.error("Failed to update Azure Cosmos Mongo vCore index")
        exception_str = str(e)
        if "Cannot find nested property" in exception_str:
            logger.error(
                f'The vector index provided "{azure_cosmos_mongo_vcore_config["index_name"]}" has a different schema than outlined in this components description. This can happen if a different embedding model was used previously when updating this index.'
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

    logger.info("Updated Azure Cosmos Mongo vCore index")


def main_wrapper(args, logger):
    with track_activity(logger, "update_azure_cosmos_mongo_vcore") as activity_logger, safe_mlflow_start_run(
        logger=logger
    ):
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(
                f"update_azure_cosmos_mongo_vcore failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--embeddings", type=str)
    parser.add_argument("--azure_cosmos_mongo_vcore_config", type=str)
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
        args.connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_COSMOS")

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
