# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import importlib.util
import inspect
import json
import os
import re
import time
import traceback
from pathlib import Path
from typing import Iterator, List

import pandas as pd
from azure.ai.generative.index._documents import (
    SUPPORTED_EXTENSIONS,
    ChunkedDocument,
    Document,
    DocumentChunksIterator,
    DocumentSource,
)
from azure.ai.generative.index._documents.chunking import file_extension_splitters, split_documents
from azure.ai.generative.index._documents.cracking import BaseDocumentLoader, crack_documents, file_extension_loaders
from azure.ai.generative.index._utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)

logger = get_logger("crack_and_chunk")


def chunks_to_dataframe(chunks) -> pd.DataFrame:
    metadata = []
    data = []
    for chunk in chunks:
        metadata.append(json.dumps(chunk.get_metadata()))
        data.append(chunk.load_data())
    chunks_dict = {
        "Metadata": metadata,
        "Chunk": data
    }

    return pd.DataFrame(chunks_dict)


def write_chunks_to_csv(chunks_df, output_path):
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    chunks_df.to_csv(output_path, index=False)


def write_chunks_to_jsonl(chunks: List[Document], output_path):
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for chunk in chunks:
            f.write(chunk.dumps())
            f.write("\n")


def generate_file_name(output_chunks: str, chunked_document: ChunkedDocument, file_extension: str) -> str:
    file_name = chunked_document.source.filename.replace("\\", "_").replace("/", "_")
    return Path(output_chunks) / f"Chunks_{file_name}.{file_extension}"


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False


def custom_loading(python_file_path: str, ext_loaders, ext_splitters):
    """Load custom loader from python file."""
    module_name = os.path.basename(python_file_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, python_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for _, obj in inspect.getmembers(module):
        logger.debug(f"Found {obj} in {module_name}")
        if inspect.isclass(obj) and obj != BaseDocumentLoader and (issubclass(obj, BaseDocumentLoader) or (hasattr(obj, "file_extensions") and hasattr(obj, "load"))):
            loader = obj(None, None, None)
            file_extensions = loader.file_extensions()
            logger.info(f"Registering custom loader for {file_extensions}")
            for file_extension in file_extensions:
                ext_loaders[file_extension] = obj
                # for now, use the text splitter for everything
                ext_splitters[file_extension] = file_extension_splitters[".txt"]


def get_activity_logging_filter(activity_logger, source_glob):
    """Get a filter function with activity logging."""
    def filter_and_log_extensions(sources: Iterator[DocumentSource], allowed_extensions=SUPPORTED_EXTENSIONS) -> Iterator[DocumentSource]:
        """Filter out sources with extensions not in allowed_extensions."""
        total_files = 0
        skipped_files = 0
        skipped_extensions = {}
        kept_extension = {}
        for source in sources:
            total_files += 1
            if allowed_extensions is not None:
                if source.path.suffix not in allowed_extensions:
                    skipped_files += 1
                    ext_skipped = skipped_extensions.get(source.path.suffix, 0)
                    skipped_extensions[source.path.suffix] = ext_skipped + 1
                    logger.debug(f'Filtering out extension "{source.path.suffix}" source: {source.filename}')
                    continue
            ext_kept = kept_extension.get(source.path.suffix, 0)
            kept_extension[source.path.suffix] = ext_kept + 1
            logger.info(f"Processing file: {source.filename}")
            yield source
        logger.info(f"[DocumentChunksIterator::filter_extensions] Filtered {skipped_files} files out of {total_files}")
        logger.info(f"[DocumentChunksIterator::filter_extensions] Skipped extensions: {json.dumps(skipped_extensions, indent=2)}")
        logger.info(f"[DocumentChunksIterator::filter_extensions] Kept extensions: {json.dumps(kept_extension, indent=2)}")
        activity_logger.activity_info["total_files"] = total_files
        activity_logger.activity_info["skipped_files"] = skipped_files
        activity_logger.activity_info["skipped_extensions"] = json.dumps(skipped_extensions)
        activity_logger.activity_info["kept_extensions"] = json.dumps(kept_extension)
        if total_files == 0:
            raise Exception(f"No files found in input path using glob {source_glob}")
        if skipped_files == total_files:
            raise Exception(f"None of the provided file extensions are supported. List of supported file extensions is {allowed_extensions}")

    return filter_and_log_extensions


def main(args, logger, activity_logger):
    extension_loaders = copy.deepcopy(file_extension_loaders)
    extension_splitters = copy.deepcopy(file_extension_splitters)

    if args.custom_loader:
        logger.info(f"Loading custom loader(s) from {args.custom_loader}")
        for python_file_path in Path(args.custom_loader).glob("**/*.py"):
            custom_loading(python_file_path, extension_loaders, extension_splitters)

    splitter_args = {"chunk_size": args.chunk_size, "chunk_overlap": args.chunk_overlap, "use_rcts": args.use_rcts}

    filter_and_log_extensions = get_activity_logging_filter(activity_logger, args.input_glob)

    chunked_documents = DocumentChunksIterator(
        files_source=args.input_data,
        glob=args.input_glob,
        base_url=args.data_source_url,
        document_path_replacement_regex=args.document_path_replacement_regex,
        file_filter=lambda sources: filter_and_log_extensions(sources=sources, allowed_extensions=list(extension_loaders.keys())),
        source_loader=lambda sources: crack_documents(sources, file_extension_loaders=extension_loaders),
        chunked_document_processors=[lambda docs: split_documents(docs, splitter_args=splitter_args, file_extension_splitters=extension_splitters)],
    )
    file_count = 0
    total_time = 0
    for chunked_document in chunked_documents:
        file_start_time = time.time()
        file_count += 1
        # TODO: Ideally make it easy to limit number of files with a `- take: n` operation on input URI in MLTable
        if (args.max_sample_files != -1 and file_count >= args.max_sample_files):
            logger.info(f"file count: {file_count} - reached max sample file count: {args.max_sample_files}", extra={"print": True})
            break

        if args.output_format == "csv":
            write_chunks_to_csv(
                chunks_to_dataframe(chunked_document.chunks),
                generate_file_name(args.output_chunks, chunked_document, "csv"))
        elif args.output_format == "jsonl":
            write_chunks_to_csv(
                chunks_to_dataframe(chunked_document.chunks),
                generate_file_name(args.output_chunks, chunked_document, "jsonl"))
        file_end_time = time.time()
        total_time += file_end_time - file_start_time

    logger.info(f"Processed {file_count} files",)
    activity_logger.activity_info["file_count"] = str(file_count)

    if file_count == 0:
        logger.info(f"No chunked documents found in {args.input_data} with glob {args.input_glob}")
        activity_logger.activity_info["error"] = "No chunks found"
        activity_logger.activity_info["glob"] = args.input_glob if re.match("^[*/\\\"']+$", args.input_glob) is not None else "[REDACTED]"
        raise ValueError(f"No chunked documents found in {args.input_data} with glob {args.input_glob}.")

    logger.info(f"Wrote chunks to {file_count} files in {total_time} seconds (chunk generation time excluded)")
    activity_logger.activity_info["file_count"] = file_count


def main_wrapper(args, logger):
    with track_activity(logger, "crack_and_chunk") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(f"crack_and_chunk failed with exception: {traceback.format_exc()}")  # activity_logger doesn't log traceback
            raise


def crack_and_chunk_arg_parser():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data", type=str)
    parser.add_argument("--input_glob", type=str, default="**/*")
    parser.add_argument("--allowed_extensions", required=False, type=str, default=",".join(SUPPORTED_EXTENSIONS))
    parser.add_argument("--chunk_size", type=int)
    parser.add_argument("--chunk_overlap", type=int)
    parser.add_argument("--output_chunks", type=str, required=False)
    parser.add_argument("--data_source_url", type=str, required=False)
    parser.add_argument("--document_path_replacement_regex", type=str, required=False)
    parser.add_argument("--max_sample_files", type=int, default=-1)
    parser.add_argument("--use_rcts", type=str2bool, default=True)
    parser.add_argument("--output_format", type=str, default="csv")
    parser.add_argument("--custom_loader", type=str, default=None)
    # Deprecated
    parser.add_argument("--output_title_chunk", type=str, required=False)
    parser.add_argument("--openai_api_version", type=str, default="2023-03-15-preview")
    parser.add_argument("--openai_api_type", type=str, default=None)

    return parser


def __main__(arg_parser, main_func):
    args = arg_parser.parse_args()
    print("\n".join(f"{k}={v}" for k, v in vars(args).items()))

    enable_stdout_logging()
    enable_appinsights_logging()

    if args.output_title_chunk is not None:
        logger.warning("output_title_chunk is deprecated, use output_chunks instead.")
        args.output_chunks = args.output_title_chunk if args.output_chunks is None else args.output_chunks
    if args.output_chunks is None:
        raise ValueError("output_chunks or output_title_chunk is required")

    if args.openai_api_version is not None:
        logger.warning("openai_api_version is deprecated, this argument is not used and will be removed in a future release.")
    if args.openai_api_type is not None:
        logger.warning("openai_api_type is deprecated, this argument is not used and will be removed in a future release.")

    try:
        main_func(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)


if __name__ == "__main__":
    parser = crack_and_chunk_arg_parser()

    __main__(parser, main_wrapper)
