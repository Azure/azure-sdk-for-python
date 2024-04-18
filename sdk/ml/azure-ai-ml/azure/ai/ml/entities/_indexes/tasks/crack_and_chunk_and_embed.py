# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import json
import os
import re
import time
import traceback
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterator, Optional, Union

from azure.ai.ml.entities._indexes.documents import (
    Document,
    DocumentChunksIterator,
    DocumentSource,
)
from azure.ai.ml.entities._indexes.documents.chunking import file_extension_splitters, split_documents
from azure.ai.ml.entities._indexes.documents.cracking import crack_documents, files_to_document_source
from azure.ai.ml.entities._indexes.embeddings import DataEmbeddedDocument, EmbeddedDocumentSource, EmbeddingsContainer
from azure.ai.ml.entities._indexes.tasks.crack_and_chunk import custom_loading, get_activity_logging_filter, str2bool
from azure.ai.ml.entities._indexes.utils.cracking import get_extension_loaders_with_document_intelligence
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
    write_status_log,
)

logger = get_logger("crack_and_chunk_and_embed")

SOURCE_LOGGING_VERBOSITY = 1
METRICS_LOG_INTERVAL_SOURCES_COUNT = 10
DOCUMENT_LOGGING_VERBOSITY = 2
METRICS_LOG_INTERVAL_DOCUMENT_COUNT = 1000


# TODO: Make `activity_logger` optional, maybe simple interface that User could implement?
def crack_and_chunk_and_embed(
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
    embeddings_model: Optional[str] = None,
    embeddings_connection: Optional[str] = None,
    embeddings_container: Optional[Union[str, Path]] = None,
    batch_size: int = 100,
    num_workers: int = -1,
    output_path: Optional[Optional[Union[str, Path]]] = None,
    verbosity: int = 0,
    activity_logger=None,
) -> EmbeddingsContainer:
    """Crack and chunk and embed and index documents."""
    connection_args = {}
    if embeddings_container is None:
        if embeddings_connection is not None:
            connection_args["connection_type"] = "workspace_connection"
            if isinstance(embeddings_connection, str):
                connection_args["connection"] = {"id": embeddings_connection}
            else:
                from azure.ai.ml.entities._indexes.utils.connections import get_id_from_connection

                connection_args["connection"] = {"id": get_id_from_connection(embeddings_connection)}

        embeddings_container = EmbeddingsContainer.from_uri(embeddings_model, **connection_args)

    if citation_replacement_regex:
        document_path_replacement = json.loads(citation_replacement_regex)
        url_replacement_match = re.compile(document_path_replacement["match_pattern"])

        def process_url(url):
            return url_replacement_match.sub(document_path_replacement["replacement_pattern"], url)
    else:

        def process_url(url):
            return url

    filter_and_log_extensions = get_activity_logging_filter(source_glob, activity_logger)
    source_documents = files_to_document_source(
        source_uri,
        source_glob,
        citation_url if citation_url is not None else DocumentChunksIterator._infer_base_url_from_git(source_uri),
        process_url,
    )
    source_documents = filter_and_log_extensions(source_documents)

    # Below is destructive to EmbeddingsContainer in-memory tables.
    # `sources_to_embed` and `documents_to_embed` are generators that yield sources and documents to be processed,
    # while removing reused and modified sources and documents from EmbeddingsContainer tables.
    # After the `documents_to_embed` generator is fully consumed the EmbeddingsContainer tables contain deleted documents and sources.
    # These are captured and the EmbeddingsContainer reset with the new state of processed sources and documents.

    num_sources = 0
    # TODO: log metrics for reused_sources, deleted_sources, and sources_to_embed
    sources_reused = OrderedDict()
    sources_embedded = OrderedDict()
    num_documents = 0
    num_documents_reused = 0
    num_documents_to_embed = 0
    documents_reused = OrderedDict()

    def sources_to_embed(source_documents) -> Iterator[DocumentSource]:
        nonlocal num_sources
        nonlocal sources_reused
        nonlocal num_documents
        nonlocal num_documents_reused
        nonlocal embeddings_container
        for source_doc in source_documents:
            num_sources += 1
            mtime = source_doc.mtime
            # Currently there's no lookup at filename level, only document_ids (post chunking)
            # TODO: Save document_source table along side embedded documents table
            existing_embedded_source = embeddings_container._document_sources.get(source_doc.filename)
            if existing_embedded_source:
                # TODO: Consider mtime being != as a signal to reprocess, rather than just newer. (thanks Andrei)
                if existing_embedded_source.source.mtime is not None and existing_embedded_source.source.mtime >= mtime:
                    if verbosity >= SOURCE_LOGGING_VERBOSITY:
                        logger.info(
                            f"REUSING: source '{source_doc.filename}' embedding as mtime {mtime} is older than existing mtime {existing_embedded_source.source.mtime}"
                        )
                    sources_reused[source_doc.filename] = existing_embedded_source
                    reused_documents = len(existing_embedded_source.document_ids)
                    num_documents += reused_documents
                    num_documents_reused += reused_documents
                    for doc_id in existing_embedded_source.document_ids:
                        if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
                            logger.info(
                                f"REUSING: chunk '{doc_id}' from source '{existing_embedded_source.source.filename}'"
                            )
                        # Track reused EmbeddedDocuments and remove from EmbeddingsContainer to track documents deleted from source
                        documents_reused[doc_id] = embeddings_container._document_embeddings[doc_id]
                        del embeddings_container._document_embeddings[doc_id]
                else:
                    if verbosity >= SOURCE_LOGGING_VERBOSITY:
                        logger.info(
                            f"EMBEDDING: source '{source_doc.filename}' as mtime {mtime} is newer than existing mtime {existing_embedded_source.source.mtime}"
                        )
                    yield source_doc
                del embeddings_container._document_sources[source_doc.filename]
            else:
                if verbosity >= SOURCE_LOGGING_VERBOSITY:
                    logger.info(f"EMBEDDING: source '{source_doc.filename}' as no existing embedding found")
                yield source_doc
            if num_sources % METRICS_LOG_INTERVAL_SOURCES_COUNT == 0:
                write_status_log(
                    stage="sourcing",
                    message="Processed Sources",
                    total_units=num_sources,
                    processed_units=len(sources_reused) + len(sources_embedded),
                    unit="processed_sources",
                    logger=activity_logger,
                )
                write_status_log(
                    stage="sourcing",
                    message="Total Documents",
                    total_units=num_documents,
                    processed_units=num_documents_reused + num_documents_to_embed,
                    unit="documents_total",
                    logger=activity_logger,
                )
                write_status_log(
                    stage="sourcing",
                    message="Reused Documents",
                    total_units=num_documents_reused,
                    processed_units=num_documents_reused,
                    unit="documents_reused",
                    logger=activity_logger,
                )

    # Configure document cracking and chunking
    extension_loaders = get_extension_loaders_with_document_intelligence(doc_intel_connection_id)
    extension_splitters = copy.deepcopy(file_extension_splitters)

    if custom_loader:
        logger.info(f"Loading custom loader(s) from {custom_loader}", extra={"print": True})
        for python_file_path in Path(custom_loader).glob("**/*.py"):
            custom_loading(python_file_path, extension_loaders, extension_splitters)

    splitter_args = {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap, "use_rcts": use_rcts}
    cracked_sources = crack_documents(sources_to_embed(source_documents), file_extension_loaders=extension_loaders)
    chunked_docs = split_documents(
        cracked_sources,
        splitter_args=splitter_args,
        file_extension_splitters=extension_splitters,
        activity_logger=activity_logger,
    )

    documents_embedded = OrderedDict()

    def documents_to_embed(chunked_docs) -> Iterator[Document]:
        """
        Process chunked documents, store reused documents, and yield documents to embed.

        All processed documents from source found in EmbeddingsContainer are removed, leaving only documents no longer present in source.
        """
        nonlocal num_sources
        nonlocal sources_reused
        nonlocal sources_embedded
        nonlocal num_documents
        nonlocal num_documents_reused
        nonlocal documents_reused
        nonlocal num_documents_to_embed
        nonlocal embeddings_container
        nonlocal logger
        log_threshold = METRICS_LOG_INTERVAL_DOCUMENT_COUNT
        for chunked_doc in chunked_docs:
            logger.info(f"Processing chunks for source: {chunked_doc.source.filename}")
            source_doc_ids = []
            for document in chunked_doc.chunks:
                num_documents += 1
                import hashlib

                document_data = document.load_data()
                document_hash = hashlib.sha256(document_data.encode("utf-8")).hexdigest()
                document.metadata["content_hash"] = document_hash

                existing_embedded_document = embeddings_container._document_embeddings.get(document.document_id)
                if existing_embedded_document:
                    if existing_embedded_document.document_hash == document_hash:
                        if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
                            logger.info(
                                f"SKIPPING: chunk '{document.document_id}' embedding as hash {document_hash} is the same as existing hash {existing_embedded_document.document_hash}"
                            )
                        num_documents_reused += 1
                        documents_reused[document.document_id] = existing_embedded_document
                    else:
                        if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
                            logger.info(
                                f"EMBEDDING: chunk '{document.document_id}' as hash {document_hash} is different than existing hash {existing_embedded_document.document_hash}"
                            )
                        num_documents_to_embed += 1
                        yield document
                    del embeddings_container._document_embeddings[document.document_id]
                else:
                    if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
                        logger.info(f"EMBEDDING: chunk '{document.document_id}' as no existing embedding found")
                    num_documents_to_embed += 1
                    yield document
                source_doc_ids.append(document.document_id)

                log_threshold -= 1
                if log_threshold == 0:
                    log_threshold = METRICS_LOG_INTERVAL_DOCUMENT_COUNT
                    write_status_log(
                        stage="chunking",
                        message="Processed Sources",
                        total_units=num_sources,
                        processed_units=len(sources_reused) + len(sources_embedded),
                        unit="processed_sources",
                        logger=activity_logger,
                    )
                    write_status_log(
                        stage="chunking",
                        message="Total Documents",
                        total_units=num_documents,
                        processed_units=num_documents_reused + num_documents_to_embed,
                        unit="documents_total",
                        logger=activity_logger,
                    )
                    write_status_log(
                        stage="chunking",
                        message="Documents Reused",
                        total_units=num_documents_reused,
                        processed_units=num_documents_reused,
                        unit="documents_reused",
                        logger=activity_logger,
                    )

            sources_embedded[chunked_doc.source.filename] = EmbeddedDocumentSource(chunked_doc.source, source_doc_ids)

        write_status_log(
            stage="chunking",
            message="Processed Sources",
            total_units=num_sources,
            processed_units=len(sources_reused) + len(sources_embedded),
            unit="processed_sources",
            logger=activity_logger,
        )
        write_status_log(
            stage="chunking",
            message="Total Documents",
            total_units=num_documents,
            processed_units=num_documents_reused + num_documents_to_embed,
            unit="documents_total",
            logger=activity_logger,
        )
        write_status_log(
            stage="chunking",
            message="Documents Reused",
            total_units=num_documents_reused,
            processed_units=num_documents_reused,
            unit="documents_reused",
            logger=activity_logger,
        )

    def log_embeddings_results(results: dict, activity_logger=None):
        nonlocal num_documents
        nonlocal num_documents_reused
        nonlocal num_documents_to_embed

        write_status_log(
            stage="embedding",
            message="Embedded Documents",
            total_units=num_documents_to_embed,
            processed_units=results["documents_embedded"],
            unit="documents_embedded",
            logger=activity_logger,
        )
        write_status_log(
            stage="embedding",
            message="Total Documents",
            total_units=num_documents,
            processed_units=num_documents_reused + results["documents_embedded"],
            unit="documents_total",
            logger=activity_logger,
        )

    # Embed in parallel workers and output incrementally if saving EmbeddingsContainer, otherwise embed on main thread.
    if output_path is not None:
        from azure.ai.ml.entities._indexes.tasks.embed import create_embeddings

        with track_activity(
            logger,
            "create_embeddings",
            custom_dimensions={
                "kind": embeddings_container.kind,
                "model": embeddings_container.arguments.get("model", ""),
            },
        ) as embeddings_activity_logger:
            # workers only load metadata of EmbeddingsContainer to skip reuse check during embed
            # workers embed and write out batches to new snapshot of EmbeddingsContainer
            num_embedded = create_embeddings(
                chunks=documents_to_embed(chunked_docs),
                embeddings_model_uri=embeddings_model,
                connection_args=connection_args,
                embeddings_container=embeddings_container.local_path,
                output=output_path,
                snapshot_dir_name=embeddings_container.current_snapshot,
                metadata_only=True,
                activity_logger=embeddings_activity_logger,
                results_callback=log_embeddings_results,
                batch_size=batch_size,
                num_workers=num_workers,
            )

        if num_embedded > 0:
            output_path_path = Path(output_path)
            embeddings = EmbeddingsContainer.load(str(output_path_path.name), str(output_path_path.parent))
            documents_embedded.update(embeddings._document_embeddings)
    else:
        # Embed on main thread, making this a generator breaks `_embed` on OpenAIEmbedder because it calls `len()`.
        # Ideally this would still be batched single thread to avoid OOMs

        data_to_embed = []
        documents = []
        for doc in documents_to_embed(chunked_docs):
            documents.append(doc)
            data_to_embed.append(doc.load_data())

        logger.info(
            "Finished determining Documents to embed:\n"
            f"Documents to embed: {num_documents_to_embed}\n"
            f"Documents reused: {len(documents_reused.keys())}\n"
        )

        with track_activity(
            logger,
            "Embeddings.embed",
            custom_dimensions={
                "documents_to_embed": num_documents_to_embed,
                "reused_documents": num_documents_reused,
                "kind": embeddings_container.kind,
                "model": embeddings_container.arguments.get("model", ""),
            },
        ) as activity_logger:
            embeddings = embeddings_container._embed_fn(data_to_embed, activity_logger=activity_logger)

        for document, embedding in zip(documents, embeddings):
            documents_embedded[document.document_id] = DataEmbeddedDocument(
                document.document_id,
                document.mtime,
                document.metadata["content_hash"],
                document.load_data(),
                embedding,
                document.metadata,
            )

    # All sources and documents have been processed.
    # Capture remaining deleted sources and documents, reset EmbeddingsContainer and add back reused sources and documents.
    deleted_sources = embeddings_container._document_sources
    num_deleted_sources = len(deleted_sources.keys())
    if verbosity >= SOURCE_LOGGING_VERBOSITY:
        for deleted_source in deleted_sources.values():
            logger.info(
                f"REMOVING: source '{deleted_source.source.filename}' from EmbeddingsContainer as it no longer exists in source"
            )

    deleted_documents = embeddings_container._document_embeddings
    num_deleted_documents = len(deleted_documents.keys())
    if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
        for document in deleted_documents.values():
            logger.debug(
                f"REMOVING: chunk '{document.document_id}' from EmbeddingsContainer as it no longer exists in source"
            )

    logger.info(
        "Finished processing sources:\n"
        f"Sources to embed: {len(sources_embedded)}\n"
        f"Sources reused: {len(sources_reused)}\n"
        f"Sources deleted: {num_deleted_sources}"
    )

    # Reset EmbeddingsContainer._document_sources, ready to add reused sources
    embeddings_container._document_sources = sources_reused
    embeddings_container._document_sources.update(sources_embedded)
    embeddings_container._deleted_sources = deleted_sources

    write_status_log(
        stage="embedding",
        message="Deleted Sources",
        total_units=num_deleted_sources,
        processed_units=num_deleted_sources,
        unit="deleted_sources",
        logger=activity_logger,
    )
    write_status_log(
        stage="embedding",
        message="Deleted Documents",
        total_units=num_deleted_documents,
        processed_units=num_deleted_documents,
        unit="deleted_documents",
        logger=activity_logger,
    )

    # Set and save with EmbeddingsContainer (snapshot of state for this Run)
    embeddings_container._document_embeddings = documents_reused
    embeddings_container._document_embeddings.update(documents_embedded)
    embeddings_container._deleted_documents = deleted_documents  # list(deleted_documents.keys())

    logger.info(f"Processed {num_sources} files")
    activity_logger.activity_info["file_count"] = str(num_sources)

    if num_sources == 0:
        logger.info(f"No chunked documents found in {source_uri} with glob {source_glob}")
        activity_logger.activity_info["error"] = "No chunks found"
        activity_logger.activity_info["glob"] = (
            source_glob if re.match("^[*/\\\"']+$", source_glob) is not None else "[REDACTED]"
        )
        raise ValueError(f"No chunked documents found in {source_uri} with glob {source_glob}.")

    return embeddings_container


def main(args, logger, activity_logger):
    """Main function for crack_and_chunk_and_embed."""
    with EmbeddingsContainer.mount_and_load(args.embeddings_container, activity_logger) as embeddings_container:
        embeddings_container = crack_and_chunk_and_embed(
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
            embeddings_container=embeddings_container,
            batch_size=args.batch_size,
            num_workers=args.num_workers,
            output_path=args.output_path,
            verbosity=args.verbosity,
            activity_logger=activity_logger,
        )

        # EmbeddingsContainer now has current state of sources, and embedded documents, and deleted documents
        # TODO: Need to handle embeddings_cache path as being remote or local, being mounted or not, then that final path being used for the EmbeddingsContainer persistance.
        # New embeddings_container code ideally would handle this?
        if args.output_path is not None:
            embeddings_container.save(args.output_path, with_metadata=True)


def main_wrapper(args, logger):
    with track_activity(logger, "crack_and_chunk_and_embed") as activity_logger, safe_mlflow_start_run(logger=logger):
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

    parser.add_argument("--embeddings_model", type=str, required=False)
    parser.add_argument("--embeddings_connection_id", type=str, required=False)
    parser.add_argument("--embeddings_container", type=str, required=False)
    parser.add_argument("--batch_size", type=int, default=-1)
    parser.add_argument("--num_workers", type=int, default=-1)
    parser.add_argument("--output_path", type=str, required=False)

    parser.add_argument(
        "--verbosity",
        type=int,
        default=2,
        choices=[0, 1, 2],
        help="0: Aggregate Source/Document Info, 1: Source Ids logged as processed, 2: Document Ids logged as processed.",
    )
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

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
