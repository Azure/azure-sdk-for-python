# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import time
import traceback
from pathlib import Path
from typing import Optional

import pinecone
import yaml
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.ai.ml.entities._indexes.embeddings import EmbeddingsContainer
from azure.ai.ml.entities._indexes.indexes.index_stores import (
    INDEX_DELETE_FAILURE_MESSAGE_PREFIX,
    INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX,
    PineconeStore,
)
from azure.ai.ml.entities._indexes.mlindex import MLIndex
from azure.ai.ml.entities._indexes.utils.connections import (
    get_connection_by_id_v2,
    get_connection_credential,
    get_metadata_from_connection,
)
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)

logger = get_logger("update_pinecone")


def get_pinecone_environment(config, credential: Optional[TokenCredential] = None):
    """Get the Pinecone project environment from a connection."""
    connection_type = config.get("connection_type", None)
    if connection_type != "workspace_connection":
        raise ValueError(f"Unsupported connection type for Pinecone index: {connection_type}")

    connection_id = config.get("connection", {}).get("id")
    connection = get_connection_by_id_v2(connection_id, credential=credential)
    return get_metadata_from_connection(connection)["environment"]


def pinecone_index_client_from_config(pinecone_config: dict, api_key: str):
    """
    Create and return a Pinecone index client.

    Args:
    ----
        pinecone_config (dict): Pinecone configuration dictionary. Expected to contain:
            - environment: Pinecone index environment
            - index_name: Pinecone index name
            - field_mapping: Mappings from MLIndex fields (MLIndex.INDEX_FIELD_MAPPING_TYPES) to Pinecone fields.

        api_key (str): API key to use for authentication to the Pinecone index.

    """
    pinecone.init(api_key=api_key, environment=pinecone_config["environment"])
    return pinecone.Index(pinecone_config["index_name"])


def create_pinecone_index_sdk(pinecone_config: dict, api_key: str, embeddings: Optional[EmbeddingsContainer] = None):
    """
    Create a Pinecone index using the Pinecone SDK.

    Args:
    ----
        pinecone_config (dict): Pinecone configuration dictionary. Expected to contain:
            - environment: Pinecone index environment
            - index_name: Pinecone index name
            - field_mapping: Mappings from MLIndex fields (MLIndex.INDEX_FIELD_MAPPING_TYPES) to Pinecone fields.

        api_key (str): API key to use for authentication to the Pinecone index.
        embeddings (EmbeddingsContainer): EmbeddingsContainer to use for creating the index. If provided, the index
                                          will be configured to support vector search.

    """
    logger.info(f"Ensuring Pinecone index {pinecone_config['index_name']} exists")

    pinecone.init(api_key=api_key, environment=pinecone_config["environment"])

    if pinecone_config["index_name"] not in pinecone.list_indexes():
        logger.info(
            f"Creating {pinecone_config['index_name']} Pinecone index with dimensions {embeddings.get_embedding_dimensions()}"
        )
        pinecone.create_index(pinecone_config["index_name"], embeddings.get_embedding_dimensions())
        logger.info(f"Created {pinecone_config['index_name']} Pinecone index")
    else:
        logger.info(f"Pinecone index {pinecone_config['index_name']} already exists")


def create_index_from_raw_embeddings(
    emb: EmbeddingsContainer,
    pinecone_config: dict = {},
    connection: dict = {},
    output_path: Optional[str] = None,
    credential: Optional[TokenCredential] = None,
    verbosity: int = 1,
) -> MLIndex:
    """
    Upload an EmbeddingsContainer to Pinecone and return an MLIndex.

    Args:
    ----
        emb (EmbeddingsContainer): EmbeddingsContainer to use for creating the index. If provided, the index
                                   will be configured to support vector search.
        pinecone_config (dict): Pinecone configuration dictionary. Expected to contain:
            - environment: Pinecone project/index environment
            - index_name: Pinecone index name
            - field_mapping: Mappings from MLIndex fields (MLIndex.INDEX_FIELD_MAPPING_TYPES) to Pinecone fields.

        connection (dict): Configuration dictionary describing the type of the connection to the Pinecone index.
        output_path (str): The output path to store the MLIndex.
        credential (TokenCredential): Azure credential to use for authentication.
        verbosity (int): Defaults to 1.
            - 1: Log aggregate information about documents and IDs of deleted documents.
            - 2: Log all document_ids as they are processed.

    """
    with track_activity(
        logger, "create_index_from_raw_embeddings", custom_dimensions={"num_documents": len(emb._document_embeddings)}
    ) as activity_logger:
        logger.info("Updating Pinecone index")

        if MLIndex.INDEX_FIELD_MAPPING_KEY not in pinecone_config:
            pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY] = {
                "content": "content",
                "url": "url",
                "filename": "filepath",
                "title": "title",
                "metadata": "metadata_json_string",
            }

        logger.info(f"Using Index fields: {json.dumps(pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY], indent=2)}")

        connection_credential = get_connection_credential(connection, credential=credential)
        if not isinstance(connection_credential, AzureKeyCredential):
            raise ValueError(
                f"Expected credential to Pinecone index to be an AzureKeyCredential, instead got: {type(connection_credential)}"
            )

        create_pinecone_index_sdk(pinecone_config, connection_credential.key, embeddings=emb)

        pinecone_index_client = pinecone_index_client_from_config(pinecone_config, connection_credential.key)

        batch_size = pinecone_config.get("batch_size", 100)

        pinecone_index_store = PineconeStore(pinecone_index_client)

        # Delete removed documents
        emb.delete_from_index(
            pinecone_index_store, batch_size=None, activity_logger=activity_logger, verbosity=verbosity
        )

        # Upload documents
        has_embeddings = emb and emb.kind != "none"
        logger.info(f"Has embeddings: {has_embeddings}")

        if has_embeddings:
            emb.upload_to_index(
                pinecone_index_store,
                pinecone_config,
                batch_size=batch_size,
                activity_logger=activity_logger,
                verbosity=verbosity,
            )
        else:
            logger.error("Documents do not have embeddings and therefore cannot upload to Pinecone index")
            raise RuntimeError("Failed to upload to Pinecone index since documents do not have embeddings")

        logger.info("Writing MLIndex yaml")
        mlindex_config = {"embeddings": emb.get_metadata()}
        mlindex_config["index"] = {
            "kind": "pinecone",
            "engine": "pinecone-sdk",
            "index": pinecone_config["index_name"],
            "field_mapping": pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY],
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
            pinecone_config = json.loads(args.pinecone_config)
        except Exception as e:
            logger.error(f"Failed to parse pinecone_config as json: {e}")
            activity_logger.error("Failed to parse pinecone_config as json")
            raise

        connection_args = {}

        if args.connection_id is not None:
            connection_args["connection_type"] = "workspace_connection"
            connection_args["connection"] = {"id": args.connection_id}
            from azure.ai.ml.entities._indexes.utils.connections import (
                get_connection_by_id_v2,
                get_metadata_from_connection,
            )

            connection = get_connection_by_id_v2(args.connection_id)
            pinecone_config["environment"] = get_metadata_from_connection(connection)["environment"]

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
                pinecone_config=pinecone_config,
                connection=connection_args,
                output_path=args.output,
                verbosity=args.verbosity,
            )

    except Exception as e:
        logger.error("Failed to update Pinecone index")
        exception_str = str(e)
        if "Cannot find nested property" in exception_str:
            logger.error(
                f'The vector index provided "{pinecone_config["index_name"]}" has a different schema than outlined in this components description. This can happen if a different embedding model was used previously when updating this index.'
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

    logger.info("Updated Pinecone index")


def main_wrapper(args, logger):
    with track_activity(logger, "update_pinecone") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(
                f"update_pinecone failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--embeddings", type=str)
    parser.add_argument("--pinecone_config", type=str)
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
        args.connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_PINECONE")

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
