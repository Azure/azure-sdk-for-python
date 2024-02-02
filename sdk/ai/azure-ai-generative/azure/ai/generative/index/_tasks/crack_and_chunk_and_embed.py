# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import datetime
import json
import os
import re
import time
import traceback
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, List, Union, Iterator

from azure.ai.generative.index._documents import (
    DocumentChunksIterator,
    DocumentSource,
)
from azure.ai.generative.index._documents.chunking import file_extension_splitters, split_documents
from azure.ai.generative.index._documents.cracking import crack_documents, file_extension_loaders, files_to_document_source
from azure.ai.generative.index._embeddings import DataEmbeddedDocument, EmbeddedDocumentSource, EmbeddingsContainer
from azure.ai.generative.index._mlindex import MLIndex
from azure.ai.generative.index._tasks.crack_and_chunk import custom_loading, get_activity_logging_filter, str2bool
from azure.ai.generative.index._documents.document import DocumentSource
from azure.ai.generative.index._utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)
from azure.ai.resources._index._documents import Document

logger = get_logger("crack_and_chunk_and_embed")

SOURCE_LOGGING_VERBOSITY = 1
DOCUMENT_LOGGING_VERBOSITY = 2


# TODO: Make `activity_logger` optional, maybe simple interface that User could implement?
def crack_and_chunk_and_embed(
    logger,
    activity_logger,
    source_uri: str,
    source_glob: str = "**/*",
    chunk_size: int = 1000,
    chunk_overlap: int = 0,
    use_rcts: bool = True,
    custom_loader: Optional[Union[str, Path]] = None,
    citation_url: Optional[str] = None,
    citation_replacement_regex: Optional[Union[str, bytes, bytearray]] = None,
    embeddings_model: str = "hugging_face://model/sentence-transformers/all-mpnet-base-v2",
    embeddings_connection: Optional[str] = None,
    embeddings_container: Optional[EmbeddingsContainer] = None,
    verbosity: int = 0,
) -> EmbeddingsContainer:
    """Crack and chunk and embed and index documents."""
    if embeddings_container is None:
        connection_args: Dict[str, Any] = {}
        if embeddings_connection is not None:
            connection_args["connection_type"] = "workspace_connection"
            if isinstance(embeddings_connection, str):
                connection_args["connection"] = {"id": embeddings_connection}
            else:
                from azure.ai.resources._index._utils.connections import get_id_from_connection

                connection_args["connection"] = {"id": get_id_from_connection(embeddings_connection)}

        embeddings_container = EmbeddingsContainer.from_uri(embeddings_model, **connection_args)  # type: ignore[used-before-def,arg-type]

    if citation_replacement_regex:
        document_path_replacement = json.loads(citation_replacement_regex)
        url_replacement_match = re.compile(document_path_replacement["match_pattern"])

        def process_url(url):
            return url_replacement_match.sub(document_path_replacement["replacement_pattern"], url)
    else:
        def process_url(url):
            return url

    source_documents = files_to_document_source(
        source_uri,
        source_glob,
        citation_url if citation_url is not None else DocumentChunksIterator._infer_base_url_from_git(source_uri),
        process_url
    )
    filter_and_log_extensions = get_activity_logging_filter(activity_logger, source_glob)

    # Below is destructive to EmbeddingsContainer in-memory tables
    # TODO: log metrics for reused_sources, deleted_sources, and sources_to_embed
    sources_to_embed: Dict[str, DocumentSource] = OrderedDict() 
    reused_sources = OrderedDict()
    for source_doc in filter_and_log_extensions(source_documents):  # type: ignore
        # TODO: Bug 2879646
        mtime = source_doc.mtime
        # Currently there's no lookup at filename level, only document_ids (post chunking)
        # TODO: Save document_source table along side embedded documents table
        existing_embedded_source = embeddings_container._document_sources.get(source_doc.filename)
        if existing_embedded_source:
            if existing_embedded_source.source.mtime is not None and existing_embedded_source.source.mtime >= mtime:
                if verbosity >= SOURCE_LOGGING_VERBOSITY:
                    logger.info(f"REUSING: source '{source_doc.filename}' embedding as mtime {mtime} is older than existing mtime {existing_embedded_source.source.mtime}")
                reused_sources[source_doc.filename] = existing_embedded_source
            else:
                if verbosity >= SOURCE_LOGGING_VERBOSITY:
                    logger.info(f"EMBEDDING: source '{source_doc.filename}' as mtime {mtime} is newer than existing mtime {existing_embedded_source.source.mtime}")
                sources_to_embed[source_doc.filename] = source_doc
            del embeddings_container._document_sources[source_doc.filename]
        else:
            if verbosity >= SOURCE_LOGGING_VERBOSITY:
                logger.info(f"EMBEDDING: source '{source_doc.filename}' as no existing embedding found")
            sources_to_embed[source_doc.filename] = source_doc

    deleted_sources = embeddings_container._document_sources
    for deleted_source in deleted_sources.values():
        if verbosity >= SOURCE_LOGGING_VERBOSITY:
            logger.info(f"REMOVING: source '{deleted_source.source.filename}' from EmbeddingsContainer as it no longer exists in source")

    # Reset EmbeddingsContainer._document_sources, ready to add reused sources
    embeddings_container._document_sources = OrderedDict()
    embeddings_container._deleted_sources = deleted_sources

    logger.info("Finished processing sources:\n"
                f"Sources to embed: {len(sources_to_embed)}\n"
                f"Sources reused: {len(reused_sources)}\n"
                f"Sources deleted: {len(deleted_sources)}")

    documents_embedded = OrderedDict()
    for reused_source in reused_sources.values():
        embeddings_container._document_sources[reused_source.source.filename] = reused_source
        for doc_id in reused_source.document_ids:
            if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
                logger.info(f"REUSING: chunk '{doc_id}' from source '{reused_source.source.filename}'")
            # Track reused EmbeddedDocuments and remove from EmbeddingsContainer to track documents deleted from source
            documents_embedded[doc_id] = embeddings_container._document_embeddings[doc_id]
            del embeddings_container._document_embeddings[doc_id]

    # Now we have sources_to_embed that we need to chunk, compare with existing embedded documents, and embed, then merge with reused_sources
    # Configure document cracking and chunking
    extension_loaders = copy.deepcopy(file_extension_loaders)
    extension_splitters = copy.deepcopy(file_extension_splitters)

    if custom_loader:
        logger.info(f"Loading custom loader(s) from {custom_loader}", extra={"print": True})
        for python_file_path in Path(custom_loader).glob("**/*.py"):
            custom_loading(str(python_file_path), extension_loaders, extension_splitters)

    splitter_args = {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap, "use_rcts": use_rcts}
    sources_to_embed_values: Iterator[DocumentSource] = iter(sources_to_embed.values())
    cracked_sources = crack_documents(sources_to_embed_values, file_extension_loaders=extension_loaders)
    chunked_docs = split_documents(cracked_sources, splitter_args=splitter_args, file_extension_splitters=extension_splitters)

    documents_to_embed: List[Document] = []
    for chunked_doc in chunked_docs:
        logger.info(f"Processing chunks for source: {chunked_doc.source.filename}")
        source_doc_ids = []
        for document in chunked_doc.chunks:
            import hashlib
            document_data = document.load_data()
            document_hash = hashlib.sha256(document_data.encode("utf-8")).hexdigest()
            document.metadata["content_hash"] = document_hash

            existing_embedded_document = embeddings_container._document_embeddings.get(document.document_id)
            if existing_embedded_document:
                if existing_embedded_document.document_hash == document_hash:
                    if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
                        logger.info(f"SKIPPING: chunk '{document.document_id}' embedding as hash {document_hash} is the same as existing hash {existing_embedded_document.document_hash}")
                    documents_embedded[document.document_id] = existing_embedded_document
                else:
                    if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
                        logger.info(f"EMBEDDING: chunk '{document.document_id}' as hash {document_hash} is different than existing hash {existing_embedded_document.document_hash}")
                    documents_to_embed.append(document)
                del embeddings_container._document_embeddings[document.document_id]
            else:
                if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
                    logger.info(f"EMBEDDING: chunk '{document.document_id}' as no existing embedding found")
                documents_to_embed.append(document)
            source_doc_ids.append(document.document_id)

        embeddings_container._document_sources[chunked_doc.source.filename] = EmbeddedDocumentSource(chunked_doc.source, source_doc_ids)

    deleted_documents = embeddings_container._document_embeddings
    for document in deleted_documents.values():
        if verbosity >= DOCUMENT_LOGGING_VERBOSITY:
            logger.debug(f"REMOVING: chunk '{document.document_id}' from EmbeddingsContainer as it no longer exists in source")

    logger.info("Finished determining Documents to embed:\n"
                f"Documents to embed: {len(documents_to_embed)}\n"
                f"Documents reused: {len(documents_embedded.keys())}\n"
                f"Documents deleted: {len(deleted_documents.keys())}")

    # TODO: Making this a generator breaks `_embed` on OpenAIEmbedder because it calls `len()`.
    # Likely need to batch here if can't use generator as could be way too much data and embeddings to hold in memory.
    # TODO: Consider having Futures pool of workers making embedding requests and pushing results like `embed` task does, but internal to EmbeddingsContainer.
    data_to_embed = [document.load_data() for document in documents_to_embed]

    with track_activity(
        logger,
        "Embeddings.embed",
        custom_dimensions={
            "documents_to_embed": len(documents_to_embed),
            "reused_documents": len(documents_embedded.keys()),
            "deleted_documents": len(deleted_documents.keys()),
            "kind": embeddings_container.kind,
            "model": embeddings_container.arguments.get("model", ""),
        }
    ) as activity_logger:
        embeddings = embeddings_container._embed_fn(data_to_embed, activity_logger=activity_logger)  # type: ignore[call-arg]

    for (document, embedding) in zip(documents_to_embed, embeddings):
        documents_embedded[document.document_id] = DataEmbeddedDocument(
            document.document_id, document.mtime, document.metadata["content_hash"], document.load_data(), embedding, document.metadata  # type: ignore[attr-defined]
        )

    # Set and save with EmbeddingsContainer (snapshot of state for this Run)
    embeddings_container._document_embeddings = documents_embedded
    embeddings_container._deleted_documents = deleted_documents

    file_count = len(sources_to_embed) + len(reused_sources)
    logger.info(f"Processed {file_count} files",)
    activity_logger.activity_info["file_count"] = str(file_count)

    if file_count == 0:
        logger.info(f"No chunked documents found in {source_uri} with glob {source_glob}")
        activity_logger.activity_info["error"] = "No chunks found"
        activity_logger.activity_info["glob"] = source_glob if re.match("^[*/\\\"']+$", source_glob) is not None else "[REDACTED]"
        raise ValueError(f"No chunked documents found in {source_uri} with glob {source_glob}.")

    return embeddings_container


def main(args, logger, activity_logger):
    """Main function for crack_and_chunk_and_embed."""
    with EmbeddingsContainer.mount_and_load(args.embeddings_container, activity_logger) as embeddings_container:
        embeddings_container = crack_and_chunk_and_embed(
            logger,
            activity_logger,
            source_uri=args.input_data,
            source_glob=args.input_glob,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            use_rcts=args.use_rcts,
            custom_loader=args.custom_loader,
            citation_url=args.citation_url,
            citation_replacement_regex=args.citation_replacement_regex,
            embeddings_model=args.embeddings_model,
            embeddings_connection=args.embeddings_connection_id,
            embeddings_container=embeddings_container,
            verbosity=args.verbosity,
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
            activity_logger.error(f"crack_and_chunk failed with exception: {traceback.format_exc()}")  # activity_logger doesn't log traceback
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
    parser.add_argument("--output_path", type=str, required=False)

    parser.add_argument("--verbosity", type=int, default=2, choices=[0, 1, 2],
                        help="0: Aggregate Source/Document Info, 1: Source Ids logged as processed, 2: Document Ids logged as processed.")

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
