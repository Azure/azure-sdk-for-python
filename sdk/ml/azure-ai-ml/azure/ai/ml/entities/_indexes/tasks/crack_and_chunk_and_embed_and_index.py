# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import datetime
import os
import time
import traceback
from logging import Logger
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml.entities._indexes.embeddings import EmbeddingsContainer
from azure.ai.ml.entities._indexes.mlindex import MLIndex
from azure.ai.ml.entities._indexes.tasks.crack_and_chunk_and_embed import crack_and_chunk_and_embed, str2bool
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)

logger = get_logger("crack_and_chunk_and_embed_and_index")


def crack_and_chunk_and_embed_and_index(
    logger,
    source_uri: str,
    source_glob: str = "**/*",
    chunk_size: int = 1000,
    chunk_overlap: int = 0,
    use_rcts: bool = True,
    custom_loader: Optional[str] = None,
    citation_url: Optional[str] = None,
    citation_replacement_regex: Optional[Dict[str, str]] = None,
    doc_intel_connection_id: Optional[str] = None,
    embeddings_model: str = "hugging_face://model/sentence-transformers/all-mpnet-base-v2",
    embeddings_connection: Optional[str] = None,
    embeddings_cache: Optional[Union[str, Path]] = None,
    batch_size: int = 100,
    num_workers: int = -1,
    index_type: str = "acs",
    index_connection: Optional[str] = None,
    index_config: Optional[Dict[str, str]] = None,
    output_path: Optional[Union[str, Path]] = None,
    activity_logger: Optional[Logger] = None,
) -> MLIndex:
    """Crack and chunk and embed and index documents."""
    with EmbeddingsContainer.mount_and_load(
        embeddings_cache, embeddings_model, embeddings_connection, activity_logger
    ) as embeddings_container:
        new_snapshot_dir = None
        if embeddings_cache is not None:
            import uuid

            # TODO: Handle embeddings_container being a remote path using fsspec
            now = datetime.datetime.now()
            snapshot_name = f"{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}_{str(uuid.uuid4()).split('-')[0]}/"
            if embeddings_container.local_path is not None:
                new_snapshot_dir = str(Path(embeddings_container.local_path) / snapshot_name)

            embeddings_container.save(new_snapshot_dir, only_metadata=True)

        embeddings_container = crack_and_chunk_and_embed(
            logger,
            source_uri=source_uri,
            source_glob=source_glob,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            use_rcts=use_rcts,
            custom_loader=custom_loader,
            citation_url=citation_url,
            citation_replacement_regex=citation_replacement_regex,
            doc_intel_connection_id=doc_intel_connection_id,
            embeddings_model=embeddings_model,
            embeddings_connection=embeddings_connection,
            embeddings_container=embeddings_container,
            batch_size=batch_size,
            num_workers=num_workers,
            output_path=new_snapshot_dir,
            activity_logger=activity_logger,
        )

        # EmbeddingsContainer now has current state of sources, and embedded documents, and deleted documents
        # TODO: Need to handle embeddings_cache path as being remote or local, being mounted or not, then that final path being used for the EmbeddingsContainer persistance.
        # New embeddings_container code ideally would handle this?
        if embeddings_cache is not None and new_snapshot_dir is not None:
            embeddings_container.save(new_snapshot_dir, with_metadata=True)

        if index_type == "acs":
            logger.info(f"Creating ACS index from embeddings_container with config {index_config}")
            from azure.ai.ml.entities._indexes.tasks.update_acs import create_index_from_raw_embeddings

            connection_args = {}
            if index_connection is not None:
                connection_args["connection_type"] = "workspace_connection"
                if isinstance(index_connection, str):
                    from azure.ai.ml.entities._indexes.utils.connections import get_connection_by_id_v2

                    connection_args["connection"] = {"id": index_connection}
                    connection = get_connection_by_id_v2(index_connection)
                else:
                    from azure.ai.ml.entities._indexes.utils.connections import get_id_from_connection

                    connection_args["connection"] = {"id": get_id_from_connection(index_connection)}
                    connection = index_connection

                from azure.ai.ml.entities._indexes.utils.connections import (
                    get_metadata_from_connection,
                    get_target_from_connection,
                )

                index_config["endpoint"] = get_target_from_connection(connection)
                index_config["api_version"] = get_metadata_from_connection(connection).get(
                    "apiVersion", "2023-07-01-preview"
                )

            mlindex = create_index_from_raw_embeddings(
                embeddings_container,
                acs_config=index_config,
                connection=connection_args,
                output_path=output_path,
            )
        elif index_type == "faiss":
            logger.info(f"Creating Faiss index from embeddings_container with config {index_config}")
            mlindex = embeddings_container.write_as_faiss_mlindex(
                output_path, engine="azure.ai.ml.entities._indexes.indexes.faiss.FaissAndDocStore"
            )
        elif index_type == "pinecone":
            logger.info(f"Creating Pinecone index from embeddings_container with config {index_config}")
            from azure.ai.ml.entities._indexes.tasks.update_pinecone import create_index_from_raw_embeddings

            connection_args = {}
            if index_connection is not None:
                connection_args["connection_type"] = "workspace_connection"
                if isinstance(index_connection, str):
                    from azure.ai.ml.entities._indexes.utils.connections import get_connection_by_id_v2

                    connection_args["connection"] = {"id": index_connection}
                    connection = get_connection_by_id_v2(index_connection)
                else:
                    from azure.ai.ml.entities._indexes.utils.connections import get_id_from_connection

                    connection_args["connection"] = {"id": get_id_from_connection(index_connection)}
                    connection = index_connection

                from azure.ai.ml.entities._indexes.utils.connections import get_metadata_from_connection

                index_config["environment"] = get_metadata_from_connection(connection)["environment"]

            mlindex = create_index_from_raw_embeddings(
                embeddings_container,
                pinecone_config=index_config,
                connection=connection_args,
                output_path=output_path,
            )
        elif index_type == "milvus":
            logger.info(f"Creating Milvus index from embeddings_container with config {index_config}")
            from azure.ai.ml.entities._indexes.tasks.update_milvus import (
                MILVUS_COLLECTION_NAME_KEY,
                MILVUS_URI_KEY,
                create_index_from_raw_embeddings,
                try_override_milvus_config_with_connection_metadata,
            )

            connection_args = {}
            if index_connection is None:
                raise ValueError("Cannot create index due to missing index connection")

            connection_args["connection_type"] = "workspace_connection"
            if isinstance(index_connection, str):
                from azure.ai.ml.entities._indexes.utils.connections import get_connection_by_id_v2

                connection_args["connection"] = {"id": index_connection}
                connection = get_connection_by_id_v2(index_connection)
            else:
                from azure.ai.ml.entities._indexes.utils.connections import get_id_from_connection

                connection_args["connection"] = {"id": get_id_from_connection(index_connection)}
                connection = index_connection

            from azure.ai.ml.entities._indexes.utils.connections import get_metadata_from_connection

            connection_metadata = get_metadata_from_connection(connection)
            try_override_milvus_config_with_connection_metadata(index_config, MILVUS_URI_KEY, connection_metadata)
            try_override_milvus_config_with_connection_metadata(
                index_config, MILVUS_COLLECTION_NAME_KEY, connection_metadata
            )

            mlindex = create_index_from_raw_embeddings(
                embeddings_container,
                milvus_config=index_config,
                connection=connection_args,
                output_path=output_path,
            )
        elif index_type == "azure_cosmos_mongo_vcore":
            logger.info(f"Creating Azure Cosmos Mongo vCore index from embeddings_container with config {index_config}")
            from azure.ai.ml.entities._indexes.tasks.update_azure_cosmos_mongo_vcore import create_index_from_raw_embeddings

            connection_args = {}
            if index_connection is not None:
                connection_args["connection_type"] = "workspace_connection"
                if isinstance(index_connection, str):
                    from azure.ai.ml.entities._indexes.utils.connections import get_connection_by_id_v2

                    connection_args["connection"] = {"id": index_connection}
                else:
                    from azure.ai.ml.entities._indexes.utils.connections import get_id_from_connection

                    connection_args["connection"] = {"id": get_id_from_connection(index_connection)}

            mlindex = create_index_from_raw_embeddings(
                embeddings_container,
                azure_cosmos_mongo_vcore_config=index_config,
                connection=connection_args,
                output_path=output_path,
            )
        else:
            raise ValueError(f"Unsupported index_type {index_type}")

        return mlindex


def main(args, logger, activity_logger):
    """Main function for crack_and_chunk_and_embed."""
    mlindex = crack_and_chunk_and_embed_and_index(
        logger,
        source_uri=args.input_data,
        source_glob=args.input_glob,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        use_rcts=args.use_rcts,
        custom_loader=args.custom_loader,
        citation_url=args.citation_url,
        citation_replacement_regex=args.citation_replacement_regex,
        doc_intel_connection_id=args.doc_intel_connection_id,
        embeddings_model=args.embeddings_model,
        embeddings_connection=args.embeddings_connection_id,
        embeddings_cache=args.embeddings_container,
        index_type=args.index_type,
        index_connection=args.index_connection_id,
        index_config=args.index_config,
        output_path=args.output_path,
        activity_logger=activity_logger,
    )

    if args.mlindex_output_path:
        mlindex.save(args.mlindex_output_path)


def main_wrapper(args, logger):
    with track_activity(logger, "crack_and_chunk_and_embed_and_index") as activity_logger, safe_mlflow_start_run(
        logger=logger
    ):
        try:
            main(args, logger, activity_logger)
        except Exception as e:
            activity_logger.error(
                f"crack_and_chunk failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise e


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data", type=str)
    parser.add_argument("--input_glob", type=str, default="**/*")
    parser.add_argument("--chunk_size", type=int)
    parser.add_argument("--chunk_overlap", type=int)
    parser.add_argument("--citation_url", type=str, required=False)
    parser.add_argument("--citation_replacement_regex", type=str, required=False)
    parser.add_argument("--custom_loader", type=str2bool, default=None)

    parser.add_argument("--embeddings_model", type=str, required=True)
    parser.add_argument("--embeddings_connection_id", type=str, required=False)
    parser.add_argument("--embeddings_container", type=str, required=False)
    parser.add_argument("--batch_size", type=int, default=-1)
    parser.add_argument("--num_workers", type=int, default=-1)

    parser.add_argument("--index_type", type=str, required=True)
    parser.add_argument("--index_connection_id", type=str, required=False)
    parser.add_argument("--index_config", type=str, required=False)

    parser.add_argument("--asset_name", type=str, required=False)
    parser.add_argument("--asset_description", type=str, required=False)
    parser.add_argument("--output_path", type=str)
    parser.add_argument(
        "--doc_intel_connection_id", type=str, default=None, help="The connection id for Document Intelligence service"
    )

    # Legacy
    parser.add_argument("--max_sample_files", type=int, default=-1)
    parser.add_argument("--use_rcts", type=str2bool, default=True)

    args = parser.parse_args()
    print("\n".join(f"{k}={v}" for k, v in vars(args).items()))

    enable_stdout_logging()
    enable_appinsights_logging()

    if args.embeddings_connection_id is None:
        logger.info("Reading connection id from environment variable")
        args.embeddings_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_AOAI")
    if args.index_connection_id is None:
        logger.info("Reading connection id from environment variable")
        args.index_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_ACS")

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
