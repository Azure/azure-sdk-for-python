# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import base64
import os
import time
import traceback
import json
from pathlib import Path
from typing import Optional
import pinecone  # pylint: disable=import-error
import yaml  # type: ignore[import]

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.ai.generative.index._embeddings import EmbeddingsContainer, ReferenceEmbeddedDocument
from azure.ai.generative.index._mlindex import MLIndex
from azure.ai.resources._index._utils.connections import get_connection_credential
from azure.ai.generative.index._utils.logging import (
    _logger_factory,
    get_logger,
    track_activity,
    safe_mlflow_start_run,
    enable_appinsights_logging,
    enable_stdout_logging,
)

logger = get_logger("update_pinecone")


def pinecone_index_client_from_config(pinecone_config: dict, api_key: str):
    """
    Create and return a Pinecone index client.

    :param pinecone_config: Pinecone configuration dictionary. Expected to contain:
            - environment: Pinecone index environment
            - index_name: Pinecone index name
            - field_mapping: Mappings from a set of fields
                understood by MLIndex (refer to MLIndex.INDEX_FIELD_MAPPING_TYPES) to Pinecone field names.
    :type pinecone_config: dict
    :param api_key: API key to use for authentication to the Pinecone index.
    :type api_key: str
    :return: Pinecone index client.
    :rtype: pinecone.Index
    """
    pinecone.init(api_key=api_key, environment=pinecone_config["environment"])
    return pinecone.Index(pinecone_config["index_name"])


def create_pinecone_index_sdk(pinecone_config: dict, api_key: str, embeddings: EmbeddingsContainer):
    """
    Create a Pinecone index using the Pinecone SDK.

    :param pinecone_config: Pinecone configuration dictionary. Expected to contain:
        - environment: Pinecone index environment
        - index_name: Pinecone index name
        - field_mapping: Mappings from a set of fields
          understood by MLIndex (refer to MLIndex.INDEX_FIELD_MAPPING_TYPES) to Pinecone field names.
    :type pinecone_config: dict
    :param api_key: API key to use for authentication to the Pinecone index.
    :type api_key: str
    :param embeddings: EmbeddingsContainer to use for creating the index.
        If provided, the index will be configured to support vector search.
    :type embeddings: EmbeddingsContainer
    """
    logger.info(f"Ensuring Pinecone index {pinecone_config['index_name']} exists")

    pinecone.init(api_key=api_key, environment=pinecone_config["environment"])

    if pinecone_config["index_name"] not in pinecone.list_indexes():
        msg = f"with dimensions {embeddings.get_embedding_dimensions()}"
        logger.info(f"Creating {pinecone_config['index_name']} Pinecone index " + msg)
        pinecone.create_index(pinecone_config["index_name"], embeddings.get_embedding_dimensions())
        logger.info(f"Created {pinecone_config['index_name']} Pinecone index")
    else:
        logger.info(f"Pinecone index {pinecone_config['index_name']} already exists")


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def create_index_from_raw_embeddings(
    emb: EmbeddingsContainer,
    pinecone_config: Optional[dict] = None,
    connection: Optional[dict] = None,
    output_path: Optional[str] = None,
    credential: Optional[TokenCredential] = None,
    verbosity: int = 1,
) -> MLIndex:
    """
    Upload an EmbeddingsContainer to Pinecone and return an MLIndex.

    :param emb: EmbeddingsContainer to use for creating the index.
        If provided, the index will be configured to support vector search.
    :type emb: EmbeddingsContainer
    :param pinecone_config: Pinecone configuration dictionary. Expected to contain:
        - environment: Pinecone project/index environment
        - index_name: Pinecone index name
        - field_mapping: Mappings from a set of fields
          understood by MLIndex (refer to MLIndex.INDEX_FIELD_MAPPING_TYPES) to Pinecone field names.
    :type pinecone_config: Optional[dict]
    :param connection: Connection configuration dictionary describing
        the type of the connection to the Pinecone index.
    :type connection: Optional[dict]
    :param output_path: The output path to store the MLIndex.
    :type output_path: Optional[str]
    :param credential: Azure credential to use for authentication.
    :type credential: Optional[TokenCredential]
    :param verbosity: Defaults to 1, which will log aggregate information about
        documents and IDs of deleted documents. 2 will log all document_ids as they are processed.
    :type verbosity: int
    :return: MLIndex object representing the created index.
    :rtype: MLIndex
    """
    if pinecone_config is None:
        pinecone_config = {}

    if connection is None:
        connection = {}

    with track_activity(
        # pylint: disable=protected-access
        logger,
        "create_index_from_raw_embeddings",
        custom_dimensions={"num_documents": len(emb._document_embeddings)},
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
                "Expected credential to Pinecone index to be an AzureKeyCredential, "
                f"instead got: {type(connection_credential)}"
            )

        create_pinecone_index_sdk(pinecone_config, connection_credential.key, embeddings=emb)

        pinecone_index_client = pinecone_index_client_from_config(pinecone_config, connection_credential.key)

        batch_size = pinecone_config["batch_size"] if "batch_size" in pinecone_config else 100

        def process_delete_results(results, start_time):
            if results == {}:
                duration = time.time() - start_time
                activity_logger.info("Deleting documents succeeded", extra={"properties": {"duration": duration}})
                return True
            response_code = results["code"] if "code" in results else ""
            response_msg = results["message"] if "message" in results else ""
            logger.error(
                f"Deleting documents failed with code {response_code} and message '{response_msg}'",
                extra={"properties": {"code": response_code, "message": response_msg}},
            )
            return False

        def process_upsert_results(results, batch_size, start_time):
            if results["upserted_count"] == batch_size:
                duration = time.time() - start_time
                activity_logger.info(
                    "Upserting documents succeeded",
                    extra={"properties": {"num_docs_upserted": batch_size, "duration": duration}},
                )
                return True
            logger.error(
                "Failed to upsert all documents",
                extra={"properties": {"num_docs_upserted": results["upserted_count"], "duration": duration}},
            )
            return False

        # Delete removed documents
        deleted_ids = []
        for (source_id, source) in emb._deleted_sources.items():  # pylint: disable=protected-access
            logger.info(f"Deleting all documents from source: {source_id}")
            for doc_id in source.document_ids:
                deleted_ids.append(base64.urlsafe_b64encode(doc_id.encode("utf-8")).decode("utf-8"))
                if verbosity > 1:
                    logger.info(f"Marked document for deletion: {doc_id}")

        msg = "adding individual documents marked for deletion"
        logger.info(f"Total {len(deleted_ids)} documents from sources marked for deletion, " + msg)
        for doc_id in emb._deleted_documents:  # pylint: disable=protected-access
            deleted_ids.append(base64.urlsafe_b64encode(doc_id.encode("utf-8")).decode("utf-8"))
            if verbosity > 1:
                logger.info(f"Marked document for deletion: {doc_id}")
        logger.info(f"Total {len(deleted_ids)} documents marked for deletion")

        if len(deleted_ids) > 0:
            logger.info(f"Deleting {len(deleted_ids)} documents (ie, records) from Pinecone")
            start_time = time.time()
            results = pinecone_index_client.delete(deleted_ids)
            if not process_delete_results(results, start_time):
                logger.info("Retrying delete documents")
                results = pinecone_index_client.delete(deleted_ids)
                if not process_delete_results(results, start_time):
                    raise RuntimeError("Failed to delete documents")

        # Upload documents
        has_embeddings = emb and emb.kind != "none"
        logger.info(f"Has embeddings: {has_embeddings}")

        if has_embeddings:
            t1 = time.time()
            num_source_docs = 0
            batch = []
            syncing_index = pinecone_config.get("sync_index", pinecone_config.get("full_sync", False))

            last_doc_prefix = None
            doc_prefix_count = 0
            skipped_doc_prefix_count = 0

            for doc_id, emb_doc in emb._document_embeddings.items():  # pylint: disable=protected-access
                doc_prefix = doc_id.split(".")[0]
                if doc_prefix != last_doc_prefix:
                    if doc_prefix_count > 0:
                        logger.info(
                            f"Processed source: {last_doc_prefix}\n"
                            f"Total Documents: {doc_prefix_count}\n"
                            f"Skipped: {skipped_doc_prefix_count}\n"
                            f"Added: {doc_prefix_count - skipped_doc_prefix_count}"
                        )

                    doc_prefix_count = 1
                    skipped_doc_prefix_count = 0
                    logger.info(f"Processing documents from: {doc_prefix}")
                    last_doc_prefix = doc_prefix
                else:
                    doc_prefix_count += 1

                # is_local=False when the EmbeddedDocuments data/embeddings are referenced from a remote source,
                # which is the case when the data was reused from a previous snapshot. is_local=True means the data
                # was generated for this snapshot and needs to pushed to the index.
                if (
                    syncing_index
                    and isinstance(emb_doc, ReferenceEmbeddedDocument)
                    and not emb_doc.is_local  # type: ignore[attr-defined]
                ):
                    # TODO: Bug 2879174
                    skipped_doc_prefix_count += 1
                    if verbosity > 2:
                        logger.info(f"Skipping document as it should already be in index: {doc_id}")
                    continue
                if verbosity > 2:
                    logger.info(f"Pushing document to index: {doc_id}")

                doc_source = emb_doc.metadata.get("source", {})
                if isinstance(doc_source, str):
                    doc_source = {
                        "url": doc_source,
                        "filename": emb_doc.metadata.get("filename", doc_source),
                        "title": emb_doc.metadata.get("title", doc_source),
                    }
                pinecone_doc = {
                    "id": base64.urlsafe_b64encode(doc_id.encode("utf-8")).decode("utf-8"),
                    "values": emb_doc.get_embeddings(),
                }
                pinecone_doc_metadata = {
                    pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["content"]: emb_doc.get_data()
                }
                if "url" in pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
                    pinecone_doc_metadata[pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["url"]] = (
                        doc_source["url"]
                        if "url" in doc_source
                        else f"No {pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]['url']}"
                    )
                if "filename" in pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
                    pinecone_doc_metadata[pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["filename"]] = (
                        doc_source["filename"]
                        if "filename" in doc_source
                        else f"No {pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]['filename']}"
                    )
                if "title" in pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
                    pinecone_doc_metadata[pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["title"]] = doc_source.get(
                        "title",
                        emb_doc.metadata.get(
                            "title", f"No {pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]['title']}"
                        ),
                    )
                if "metadata" in pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
                    pinecone_doc_metadata[pinecone_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["metadata"]] = json.dumps(
                        emb_doc.metadata
                    )
                # Metadata value must be a string, number, boolean or list of strings
                pinecone_doc["metadata"] = pinecone_doc_metadata

                batch.append(pinecone_doc)
                if len(batch) % batch_size == 0:
                    logger.info(f"Sending {len(batch)} documents (ie, records) to Pinecone")
                    start_time = time.time()
                    results = pinecone_index_client.upsert(batch)
                    if not process_upsert_results(results, len(batch), start_time):
                        logger.info(
                            "Retrying upsert documents since not all documents were upserted. "
                            "Documents that were upserted will simply be overwritten with the same values. "
                            "This retry will be idempotent."
                        )
                        results = pinecone_index_client.upsert(batch)
                        if not process_upsert_results(results, len(batch), start_time):
                            raise RuntimeError("Failed to upsert documents")
                    batch = []
                    num_source_docs += batch_size

            if len(batch) > 0:
                logger.info(f"Sending {len(batch)} documents (ie, records) to Pinecone")
                start_time = time.time()
                results = pinecone_index_client.upsert(batch)
                if not process_upsert_results(results, len(batch), start_time):
                    logger.info(
                        "Retrying upsert documents since not all documents were upserted. "
                        "Documents that were upserted will simply be overwritten with the same values. "
                        "This retry will be idempotent."
                    )
                    results = pinecone_index_client.upsert(batch)
                    if not process_upsert_results(results, len(batch), start_time):
                        raise RuntimeError("Failed to upsert documents")
                num_source_docs += len(batch)

            duration = time.time() - t1
            logger.info(
                # pylint: disable=protected-access
                f"Built index from {num_source_docs} documents and {len(emb._document_embeddings)} chunks, "
                + f"took {duration:.4f} seconds"
            )
            activity_logger.info(
                "Built index", extra={"properties": {"num_source_docs": num_source_docs, "duration": duration}}
            )
            activity_logger.activity_info["num_source_docs"] = num_source_docs
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
            with open(output / "MLIndex", "w", encoding="utf-8") as f:
                yaml.dump(mlindex_config, f)

    mlindex = MLIndex(uri=output_path, mlindex_config=mlindex_config)
    return mlindex


def main(_args, _logger, activity_logger):
    try:
        try:
            pinecone_config = json.loads(_args.pinecone_config)
        except Exception as e:
            _logger.error(f"Failed to parse pinecone_config as json: {e}")
            activity_logger.error("Failed to parse pinecone_config as json")
            raise

        connection_args = {}

        if _args.connection_id is not None:
            connection_args["connection_type"] = "workspace_connection"
            connection_args["connection"] = {"id": _args.connection_id}
            from azure.ai.resources._index._utils.connections import (
                get_connection_by_id_v2,
                get_metadata_from_connection,
            )

            connection = get_connection_by_id_v2(_args.connection_id)
            pinecone_config["environment"] = get_metadata_from_connection(connection)["environment"]

        # Mount embeddings container and create index from it
        raw_embeddings_uri = _args.embeddings
        _logger.info(f"got embeddings uri as input: {raw_embeddings_uri}")
        splits = raw_embeddings_uri.split("/")
        embeddings_dir_name = splits.pop(len(splits) - 2)
        _logger.info(f"extracted embeddings directory name: {embeddings_dir_name}")
        parent = "/".join(splits)
        _logger.info(f"extracted embeddings container path: {parent}")

        from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount

        mnt_options = MountOptions(default_permission=0o555, allow_other=False, read_only=True)
        _logger.info(f"mounting embeddings container from: \n{parent} \n   to: \n{os.getcwd()}/embeddings_mount")
        with rslex_uri_volume_mount(parent, f"{os.getcwd()}/embeddings_mount", options=mnt_options) as mount_context:
            emb = EmbeddingsContainer.load(embeddings_dir_name, mount_context.mount_point)
            create_index_from_raw_embeddings(
                emb,
                pinecone_config=pinecone_config,
                connection=connection_args,
                output_path=_args.output,
                verbosity=_args.verbosity,
            )

    except Exception as e:
        _logger.error("Failed to update Pinecone index")
        exception_str = str(e)
        if "Cannot find nested property" in exception_str:
            error_msg_1 = f'The vector index provided "{pinecone_config["index_name"]}" has a different schema '
            error_msg_2 = "than outlined in this components description. "
            error_msg_3 = "This can happen if a different embedding model was used previously when updating this index."
            _logger.error(error_msg_1 + error_msg_2 + error_msg_3)
            activity_logger.activity_info["error_classification"] = "UserError"
            activity_logger.activity_info["error"] = f"{e.__class__.__name__}: Cannot find nested property"
        elif "Failed to upsert" in exception_str:
            activity_logger.activity_info["error"] = exception_str
            activity_logger.activity_info["error_classification"] = "SystemError"
        else:
            activity_logger.activity_info["error"] = str(e.__class__.__name__)
            activity_logger.activity_info["error_classification"] = "SystemError"
        raise e

    _logger.info("Updated Pinecone index")


def main_wrapper(_args, _logger):
    with track_activity(_logger, "update_pinecone") as activity_logger, safe_mlflow_start_run(logger=_logger):
        try:
            main(_args, _logger, activity_logger)
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
    msg_1 = "Defaults to 1, which will log aggregate information about documents and IDs of deleted documents. "
    msg_2 = "2 will log all document_ids as they are processed."
    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        help=msg_1 + msg_2,
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
