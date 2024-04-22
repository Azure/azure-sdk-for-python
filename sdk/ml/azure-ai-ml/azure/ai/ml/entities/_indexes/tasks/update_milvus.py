# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import time
import traceback
from pathlib import Path
from typing import Optional

import yaml
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.ai.ml.entities._indexes.embeddings import EmbeddingsContainer
from azure.ai.ml.entities._indexes.indexes.index_stores import MilvusStore
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
from pymilvus import CollectionSchema, DataType, FieldSchema, MilvusClient

MILVUS_URI_KEY = "uri"
MILVUS_TOKEN_KEY = "token"
MILVUS_COLLECTION_NAME_KEY = "collection_name"


logger = get_logger("update_milvus")


def create_index_from_raw_embeddings(
    emb: EmbeddingsContainer,
    milvus_config={},
    connection={},
    output_path: Optional[str] = None,
    credential: Optional[TokenCredential] = None,
    verbosity: int = 1,
) -> MLIndex:
    """Update Milvus with given EmbeddingsContainer and return an MLIndex."""
    with track_activity(
        logger, "update_milvus", custom_dimensions={"num_documents": len(emb._document_embeddings)}
    ) as activity_logger:
        logger.info("Updating Milvus collection with EmbeddingsContainer")

        if MLIndex.INDEX_FIELD_MAPPING_KEY not in milvus_config:
            milvus_config[MLIndex.INDEX_FIELD_MAPPING_KEY] = {
                "content": "content",
                "url": "url",
                "filename": "filepath",
                "title": "title",
                "metadata": "metadata_json_string",
            }
        if emb and emb.kind != "none":
            milvus_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["embedding"] = "contentVector"
        else:
            raise ValueError("EmbeddingsContainer is required to update Milvus index but none was provided")

        connection_credential = get_connection_credential(connection, credential=credential)
        if not isinstance(connection_credential, AzureKeyCredential):
            # We currently only support custom-typed workspace connection whose credential can only be of AzureKeyCredential type
            raise ValueError(
                f"Expected credential to Milvus index to be an AzureKeyCredential instead got: {type(connection_credential)}"
            )

        client = MilvusClient(uri=milvus_config.get(MILVUS_URI_KEY), token=connection_credential.key)
        collection_name = create_collection_with_index_if_not_exists(milvus_config, client, embeddings=emb)

        batch_size = milvus_config.get("batch_size", 100)

        milvus_index_store = MilvusStore(client, collection_name)

        # Delete removed documents
        emb.delete_from_index(milvus_index_store, batch_size=None, activity_logger=activity_logger, verbosity=verbosity)

        # Upload documents
        emb.upload_to_index(
            milvus_index_store,
            milvus_config,
            batch_size=batch_size,
            activity_logger=activity_logger,
            verbosity=verbosity,
        )

        logger.info("Writing MLIndex yaml")
        mlindex_config = {"embeddings": emb.get_metadata()}
        mlindex_config["index"] = {
            "kind": "milvus",
            "engine": "milvus-sdk",
            "index": milvus_config[MILVUS_COLLECTION_NAME_KEY],
            "uri": milvus_config[MILVUS_URI_KEY],
            "field_mapping": milvus_config[MLIndex.INDEX_FIELD_MAPPING_KEY],
        }

        mlindex_config["index"] = {**mlindex_config["index"], **connection}

        if output_path is not None:
            output = Path(output_path)
            output.mkdir(parents=True, exist_ok=True)
            with open(output / "MLIndex", "w") as f:
                yaml.dump(mlindex_config, f)

    mlindex = MLIndex(uri=output_path, mlindex_config=mlindex_config)
    return mlindex


def create_collection_with_index_if_not_exists(
    milvus_config: dict, client: MilvusClient, embeddings: Optional[EmbeddingsContainer] = None
):
    """
    Create a collection with search index in Milvus if the given collection cannot be found

    Args:
    ----
        milvus_config (dict): Milvus configuration dictionary. Expected to contain:
            - collection_name: Milvus collection name
            - field_mapping: Mappings from a set of fields understood by MLIndex (refer to MLIndex.INDEX_FIELD_MAPPING_TYPES) to Milvus field names.
        client (MilvusClient): Milvus client
        embeddings (EmbeddingsContainer): EmbeddingsContainer to use for creating the index. If provided, the index will be configured to support vector search.

    """
    collection_name = milvus_config.get(MILVUS_COLLECTION_NAME_KEY)
    logger.info(f"Ensuring collection {collection_name} exists")

    if collection_name not in client.list_collections():
        logger.info(f"Creating collection with name {collection_name}")

        fields = []
        vector_field_name = None
        for field_type, field_name in milvus_config[MLIndex.INDEX_FIELD_MAPPING_KEY].items():
            if field_type in ["content", "url", "filename", "title", "metadata"]:
                fields.append(FieldSchema(name=field_name, dtype=DataType.VARCHAR, max_length=65535))
            elif field_type == "embedding":
                vector_field = FieldSchema(
                    name=field_name, dtype=DataType.FLOAT_VECTOR, dim=embeddings.get_embedding_dimensions()
                )
                vector_field_name = vector_field.name
                fields.append(vector_field)
            else:
                logger.warning(f"Unknown field type will be ignored and not included in index: {field_type}")

        if not vector_field_name:
            raise ValueError(f'Failed to create collection "{collection_name}" due to missing vector field')

        fields.append(
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                max_length=65535,
                is_primary=True,
                auto_id=False,
            )
        )

        schema = CollectionSchema(fields=fields, auto_id=False)

        index_params = {"index_type": "HNSW", "metric_type": "L2", "field_name": vector_field_name}

        try:
            client.create_collection_with_schema(
                collection_name=collection_name,
                schema=schema,
                index_param=index_params,
                auto_id=False,
            )
        except Exception as e:
            logger.error(f'Failed to create collection with name "{collection_name}" due to error: {e!s}')
            raise

        logger.info(f"Created collection: {collection_name}")
    else:
        logger.info(f'Collection with name "{collection_name}" already exists. Skip creating it.')

    return collection_name


def main(args, logger, activity_logger):
    try:
        try:
            milvus_config = json.loads(args.milvus_config)
        except Exception as e:
            logger.error(f"Failed to parse milvus_config as json: {e}")
            activity_logger.error("Failed to parse milvus_config as json")
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
            connection_metadata = get_metadata_from_connection(connection)
            try_override_milvus_config_with_connection_metadata(milvus_config, MILVUS_URI_KEY, connection_metadata)
            try_override_milvus_config_with_connection_metadata(
                milvus_config, MILVUS_COLLECTION_NAME_KEY, connection_metadata
            )

        validate_milvus_config(milvus_config)

        # Mount embeddings container and create or update index from it
        raw_embeddings_uri = args.embeddings
        logger.info(f"got embeddings uri as input: {raw_embeddings_uri}")
        splits = raw_embeddings_uri.split("/")
        embeddings_dir_name = splits.pop(len(splits) - 2)
        logger.info(f"extracted embeddings directory name: {embeddings_dir_name}")
        parent = "/".join(splits)
        logger.info(f"extracted embeddings container path: {parent}")

        from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount

        mnt_options = MountOptions(default_permission=0o555, allow_other=False, read_only=True)
        logger.info(f"mounting embeddings container from: \n{parent} \n   to: \n{os.getcwd()}/embeddings_mount")
        with rslex_uri_volume_mount(parent, f"{os.getcwd()}/embeddings_mount", options=mnt_options) as mount_context:
            emb = EmbeddingsContainer.load(embeddings_dir_name, mount_context.mount_point)
            if not emb or emb.kind == "none":
                raise RuntimeError("Unable to load embeddings from embedding directory")
            create_index_from_raw_embeddings(
                emb,
                milvus_config=milvus_config,
                connection=connection_args,
                output_path=args.output,
                verbosity=args.verbosity,
            )

    except Exception as e:
        logger.error("Failed to update milvus index")
        message = str(e)
        # TODO: handle user error
        activity_logger.activity_info["error"] = str(e.__class__.__name__)
        activity_logger.activity_info["error_classification"] = "SystemError"
        raise

    logger.info("Updated Milvus index")


def try_override_milvus_config_with_connection_metadata(config, key, connection_metadata):
    if connection_metadata.get(key) is not None:
        config[key] = connection_metadata.get(key)


def validate_milvus_config(milvus_config_to_validate: dict):
    for required_key in [MILVUS_URI_KEY, MILVUS_COLLECTION_NAME_KEY]:
        if required_key not in milvus_config_to_validate:
            raise ValueError(f"Required key {required_key} is missing in Milvus config")


def main_wrapper(args, logger):
    with track_activity(logger, "update_milvus") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(
                f"update_milvus failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--embeddings", type=str)
    parser.add_argument("--milvus_config", type=str)
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
        args.connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_MILVUS")

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
