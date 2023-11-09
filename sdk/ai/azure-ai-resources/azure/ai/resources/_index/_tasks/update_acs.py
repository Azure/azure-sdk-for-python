# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import base64
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
    PrioritizedFields,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticSettings,
    SimpleField,
)
from azure.ai.resources.index._embeddings import EmbeddingsContainer, ReferenceEmbeddedDocument
from azure.ai.resources.index._mlindex import MLIndex
from azure.ai.resources.index._utils.connections import get_connection_credential
from azure.ai.resources.index._utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    packages_versions_for_compatibility,
    safe_mlflow_start_run,
    track_activity,
    version,
)

logger = get_logger("update_acs")

_azure_logger = logging.getLogger("azure.core.pipeline")
_azure_logger.setLevel(logging.WARNING)

acs_user_agent = f"azureml-rag=={version}/pipeline"
azure_documents_search_version = packages_versions_for_compatibility["azure-search-documents"]


def search_client_from_config(acs_config: dict, credential):
    return SearchClient(endpoint=acs_config["endpoint"],
                        index_name=acs_config["index_name"],
                        credential=credential,
                        api_version=acs_config.get("api_version", "2023-07-01-preview"),
                        user_agent=acs_user_agent)


def create_search_index_sdk(acs_config: dict, credential, embeddings: Optional[EmbeddingsContainer] = None):
    """
    Create a search index using the Azure Search SDK.

    Args:
    ----
        acs_config (dict): ACS configuration dictionary. Expected to contain:
            - endpoint: ACS endpoint
            - index_name: ACS index name
            - field_mapping: Mappings from a set of fields understoon by MLIndex (refer to MLIndex.INDEX_FIELD_MAPPING_TYPES) to ACS field names.
        credential (TokenCredential): Azure credential to use for authentication.
        embeddings (EmbeddingsContainer): EmbeddingsContainer to use for creating the index. If provided, the index will be configured to support vector search.
    """
    logger.info(f"Ensuring search index {acs_config['index_name']} exists")
    index_client = SearchIndexClient(endpoint=acs_config["endpoint"], credential=credential, user_agent=acs_user_agent)
    if acs_config["index_name"] not in index_client.list_index_names():
        fields = []
        for field_type, field_name in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY].items():
            if field_type == "content":
                fields.append(SearchableField(name=field_name, type=SearchFieldDataType.String, analyzer_name="standard"))
            elif field_type == "url" or field_type == "filename":
                fields.append(SimpleField(name=field_name, type=SearchFieldDataType.String))
            elif field_type == "title":
                fields.append(SearchableField(name=field_name, type=SearchFieldDataType.String))
            elif field_type == "metadata":
                fields.append(SimpleField(name=field_name, type=SearchFieldDataType.String))
            elif field_type == "embedding":
                fields.append(SearchField(
                    name=field_name,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=embeddings.get_embedding_dimensions(),
                    vector_search_configuration=f"{field_name}_config"))
            else:
                logger.warning(f"Unknown field type will be ignored and not included in index: {field_type}")

        fields.append(SimpleField(name="id", type=SearchFieldDataType.String, key=True))
        # fields.append(SimpleField(name="content_hash", type=SearchFieldDataType.String))

        if "content" not in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
            raise RuntimeError(f"ACS index must have a 'content' field. Please specify a 'content' field in the {MLIndex.INDEX_FIELD_MAPPING_KEY} config.")

        vector_search_args = {}
        if str(acs_config.get("push_embeddings", "true")).lower() == "true" and embeddings and embeddings.kind != "none" and "embedding" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
            if azure_documents_search_version >= "11.4.0b8":
                from azure.search.documents.indexes.models import HnswVectorSearchAlgorithmConfiguration, VectorSearch

                vector_search_args["vector_search"] = VectorSearch(
                    algorithm_configurations=[
                        HnswVectorSearchAlgorithmConfiguration(
                            name=f"{acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]['embedding']}_config",
                            parameters={
                                "m": 4,
                                "efConstruction": 400,
                                "efSearch": 500,
                                "metric": "cosine"
                            }
                        )
                    ]
                )
            elif azure_documents_search_version >= "11.4.0b4":
                from azure.search.documents.indexes.models import VectorSearch, VectorSearchAlgorithmConfiguration

                vector_search_args["vector_search"] = VectorSearch(
                    algorithm_configurations=[
                        VectorSearchAlgorithmConfiguration(
                            name=f"{acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]['embedding']}_config",
                            kind="hnsw",
                            hnsw_parameters={
                                "m": 4,
                                "efConstruction": 400,
                                "efSearch": 500,
                                "metric": "cosine"
                            }
                        )
                    ]
                )
            else:
                raise RuntimeError(f"azure-search-documents version {azure_documents_search_version} is not supported when using embeddings. Please upgrade to 11.4.0b4 or later.")

        semantic_config = SemanticConfiguration(
            name="azureml-default",
            prioritized_fields=PrioritizedFields(
                title_field=SemanticField(field_name=acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["title"]) if "title" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY] else None,
                prioritized_content_fields=[SemanticField(field_name=acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["content"])]
            )
        )

        index = SearchIndex(
            name=acs_config["index_name"],
            fields=fields,
            semantic_settings=SemanticSettings(configurations=[semantic_config]),
            **vector_search_args
        )

        logger.info(f"Creating {acs_config['index_name']} search index")
        result = index_client.create_or_update_index(index)
        logger.info(f"Created {result.name} search index")
    else:
        logger.info(f"Search index {acs_config['index_name']} already exists")


def create_index_from_raw_embeddings(
    emb: EmbeddingsContainer,
    acs_config={},
    connection={},
    output_path: Optional[str] = None,
    credential: Optional[TokenCredential] = None,
    verbosity: int = 1,
) -> MLIndex:
    """Upload an EmbeddingsContainer to Azure Cognitive Search and return an MLIndex."""
    with track_activity(logger, "update_acs", custom_dimensions={"num_documents": len(emb._document_embeddings)}) as activity_logger:
        logger.info("Updating ACS index")

        connection_credential = get_connection_credential(connection, credential=credential)

        if MLIndex.INDEX_FIELD_MAPPING_KEY not in acs_config:
            acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY] = {
                "content": "content",
                "url": "sourcepage",
                "filename": "sourcefile",
                "title": "title",
                "metadata": "meta_json_string",
            }
            if str(acs_config.get("push_embeddings", "true")).lower() == "true" and emb and emb.kind != "none":
                acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["embedding"] = f"content_vector_{emb.kind}"

        logger.info(f"Using Index fields: {json.dumps(acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY], indent=2)}")

        create_search_index_sdk(acs_config, connection_credential, emb)

        search_client = search_client_from_config(acs_config, connection_credential)

        batch_size = acs_config["batch_size"] if "batch_size" in acs_config else 100

        def process_upload_results(results, start_time):
            succeeded = []
            failed = []
            for r in results:
                if isinstance(r, dict):
                    if r["status"] is False:
                        failed.append(r)
                    else:
                        succeeded.append(r)
                else:
                    if r.succeeded:
                        succeeded.append(r)
                    else:
                        failed.append(r)
            duration = time.time() - start_time
            logger.info(f"Uploaded {len(succeeded)} documents to ACS in {duration:.4f} seconds, {len(failed)} failed")
            activity_logger.info("Uploaded documents", extra={"properties": {"succeeded": len(succeeded), "failed": len(failed), "duration": duration}})
            if len(failed) > 0:
                for r in failed:
                    error = r["errorMessage"] if isinstance(r, dict) else r.error_message
                    logger.error(f"Failed document reason: {error}")
                return failed
            return []

        # Delete removed documents
        deleted_ids = []
        for (source_id, source) in emb._deleted_sources.items():
            logger.info(f"Deleting all documents from source: {source_id}")
            for doc_id in source.document_ids:
                deleted_ids.append({"id": base64.urlsafe_b64encode(doc_id.encode("utf-8")).decode("utf-8")})
                if verbosity > 1:
                    logger.info(f"Marked document for deletion: {doc_id}")

        logger.info(f"{len(deleted_ids)} documents from sources marked for deletion, adding individual documents marked for deletion")
        for doc_id in emb._deleted_documents:
            deleted_ids.append({"id": base64.urlsafe_b64encode(doc_id.encode("utf-8")).decode("utf-8")})
            if verbosity > 1:
                logger.info(f"Marked document for deletion: {doc_id}")
        logger.info(f"Total {len(deleted_ids)} documents marked for deletion")

        if len(deleted_ids) > 0:
            logger.info(f"Deleting {len(deleted_ids)} documents from ACS")
            start_time = time.time()
            results = search_client.delete_documents(deleted_ids)
            logger.info(f"First delete result: {vars(results[0])}")
            failed = process_upload_results(results, start_time)
            if len(failed) > 0:
                logger.info(f"Retrying {len(failed)} documents")
                failed_ids = [fail["key"] for fail in failed]
                results = search_client.delete_documents([doc for doc in deleted_ids if doc["id"] in failed_ids])
                failed = process_upload_results(results, start_time)
                if len(failed) > 0:
                    raise RuntimeError(f"Failed to delete {len(failed)} documents.")

        # Upload documents
        include_embeddings = str(acs_config.get("push_embeddings", "true")).lower() == "true" and emb and emb.kind != "none" and "embedding" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]
        logger.info(f"Documents include embeddings: {include_embeddings}")

        t1 = time.time()
        num_source_docs = 0
        batch = []
        syncing_index = acs_config.get("sync_index", False)

        last_doc_prefix = None
        doc_prefix_count = 0
        skipped_doc_prefix_count = 0
        for doc_id, emb_doc in emb._document_embeddings.items():
            doc_prefix = doc_id.split(".")[0]
            if doc_prefix != last_doc_prefix:
                if doc_prefix_count > 0:
                    logger.info(f"Processed source: {last_doc_prefix}\n"
                        f"Total Documents: {doc_prefix_count}\n"
                        f"Skipped: {skipped_doc_prefix_count}\n"
                        f"Added: {doc_prefix_count - skipped_doc_prefix_count}")

                doc_prefix_count = 1
                skipped_doc_prefix_count = 0
                logger.info(f"Processing documents from: {doc_prefix}")
                last_doc_prefix = doc_prefix
            else:
                doc_prefix_count += 1

            if syncing_index and isinstance(emb_doc, ReferenceEmbeddedDocument):
                skipped_doc_prefix_count += 1
                if verbosity > 2:
                    logger.info(f"Skipping document as it should already be in index: {doc_id}")
                continue
            else:
                if verbosity > 2:
                    logger.info(f"Pushing document to index: {doc_id}")

            doc_source = emb_doc.metadata.get("source", {})
            if isinstance(doc_source, str):
                doc_source = {
                    "url": doc_source,
                    "filename": emb_doc.metadata.get("filename", doc_source),
                    "title": emb_doc.metadata.get("title", doc_source),
                }
            acs_doc = {
                "@search.action": "mergeOrUpload",
                "id": base64.urlsafe_b64encode(doc_id.encode("utf-8")).decode("utf-8"),
                acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["content"]: emb_doc.get_data(),
            }
            if "url" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
                acs_doc[acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["url"]] = doc_source["url"]
            if "filename" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
                acs_doc[acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["filename"]] = doc_source["filename"]
            if "title" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
                acs_doc[acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["title"]] = doc_source.get("title", emb_doc.metadata.get("title"))
            if "metadata" in acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]:
                acs_doc[acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["metadata"]] = json.dumps(emb_doc.metadata)

            if include_embeddings:
                acs_doc[acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY]["embedding"]] = emb_doc.get_embeddings()

            batch.append(acs_doc)
            if len(batch) % batch_size == 0:
                logger.info(f"Sending {len(batch)} documents to ACS")
                start_time = time.time()
                results = search_client.upload_documents(batch)
                failed = process_upload_results(results, start_time)
                if len(failed) > 0:
                    logger.info(f"Retrying {len(failed)} documents")
                    failed_ids = [fail["key"] for fail in failed]
                    results = search_client.upload_documents([doc for doc in batch if doc["id"] in failed_ids])
                    failed = process_upload_results(results, start_time)
                    if len(failed) > 0:
                        raise RuntimeError(f"Failed to upload {len(failed)} documents.")
                batch = []
                num_source_docs += batch_size

        if len(batch) > 0:
            logger.info(f"Sending {len(batch)} documents to ACS")
            start_time = time.time()
            results = search_client.upload_documents(batch)
            failed = process_upload_results(results, start_time)
            if len(failed) > 0:
                logger.info(f"Retrying {len(failed)} documents")
                failed_ids = [fail["key"] for fail in failed]
                results = search_client.upload_documents([doc for doc in batch if doc["id"] in failed_ids])
                failed = process_upload_results(results, start_time)
                if len(failed) > 0:
                    raise RuntimeError(f"Failed to upload {len(failed)} documents.")

            num_source_docs += len(batch)

        duration = time.time()-t1
        logger.info(f"Built index from {num_source_docs} documents and {len(emb._document_embeddings)} chunks, took {duration:.4f} seconds")
        activity_logger.info("Built index", extra={"properties": {"num_source_docs": num_source_docs, "duration": duration}})
        activity_logger.activity_info["num_source_docs"] = num_source_docs

        logger.info("Writing MLIndex yaml")
        mlindex_config = {
            "embeddings": emb.get_metadata()
        }
        mlindex_config["index"] = {
            "kind": "acs",
            "engine": "azure-sdk",
            "index": acs_config["index_name"],
            "api_version": acs_config.get("api_version", "2023-07-01-preview"),
            "field_mapping": acs_config[MLIndex.INDEX_FIELD_MAPPING_KEY],
            "semantic_configuration_name": "azureml-default"
        }

        if not isinstance(connection, DefaultAzureCredential):
            mlindex_config["index"] = {**mlindex_config["index"], **connection}

        # Keyvault auth and Default ambient auth need the endpoint, Workspace Connection auth could get endpoint.
        mlindex_config["index"]["endpoint"] = acs_config["endpoint"]

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
            acs_config = json.loads(args.acs_config)
        except Exception as e:
            logger.error(f"Failed to parse acs_config as json: {e}")
            activity_logger.error("Failed to parse acs_config as json")
            raise

        connection_args = {}

        if args.connection_id is not None:
            connection_args["connection_type"] = "workspace_connection"
            connection_args["connection"] = {"id": args.connection_id}
            from azure.ai.resources.index._utils.connections import (
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
        embeddings_dir_name = splits.pop(len(splits)-2)
        logger.info(f"extracted embeddings directory name: {embeddings_dir_name}")
        parent = "/".join(splits)
        logger.info(f"extracted embeddings container path: {parent}")

        from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount

        mnt_options = MountOptions(
            default_permission=0o555, allow_other=False, read_only=True)
        logger.info(f"mounting embeddings container from: \n{parent} \n   to: \n{os.getcwd()}/embeddings_mount")
        with rslex_uri_volume_mount(parent, f"{os.getcwd()}/embeddings_mount", options=mnt_options) as mount_context:
            emb = EmbeddingsContainer.load(embeddings_dir_name, mount_context.mount_point)
            create_index_from_raw_embeddings(emb, acs_config=acs_config, connection=connection_args, output_path=args.output, verbosity=args.verbosity)

    except Exception as e:
        logger.error("Failed to update ACS index")
        exception_str = str(e)
        if "Floats quota has been exceeded for this service." in exception_str:
            logger.error("Floats quota exceeded on Azure Cognitive Search Service. For more information check these docs: https://github.com/Azure/cognitive-search-vector-pr#storage-and-vector-index-size-limits")
            logger.error("The usage statistic of an index can be checked using this REST API: https://learn.microsoft.com/en-us/rest/api/searchservice/get-index-statistics ")
            activity_logger.activity_info["error_classification"] = "UserError"
            activity_logger.activity_info["error"] = f"{e.__class__.__name__}: Floats quota has been exceeded for this service."
        elif "Cannot find nested property" in exception_str:
            logger.error(f'The vector index provided "{acs_config["index_name"]}" has a different schema than outlined in this components description. This can happen if a different embedding model was used previously when updating this index.')
            activity_logger.activity_info["error_classification"] = "UserError"
            activity_logger.activity_info["error"] = f"{e.__class__.__name__}: Cannot find nested property"
        elif "Failed to upload" in exception_str:
            activity_logger.activity_info["error"] = exception_str
            activity_logger.activity_info["error_classification"] = "SystemError"
        else:
            activity_logger.activity_info["error"] = str(e.__class__.__name__)
            activity_logger.activity_info["error_classification"] = "SystemError"
        raise e

    logger.info("Updated ACS index")


def main_wrapper(args, logger):
    with track_activity(logger, "update_acs") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(f"update_acs failed with exception: {traceback.format_exc()}")  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--embeddings", type=str)
    parser.add_argument("--acs_config", type=str)
    parser.add_argument("--connection_id", type=str, required=False)
    parser.add_argument("--output", type=str)
    parser.add_argument("--verbosity", type=int, default=1, help="Defaults to 1, which will log aggregate information about documents and IDs of deleted documents. 2 will log all document_ids as they are processed.")
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
