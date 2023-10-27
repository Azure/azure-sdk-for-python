# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import logging.handlers
import multiprocessing as mp
import os
import pathlib
import queue
import time
import traceback
from typing import Iterator, Optional

import pandas as pd
from azure.ai.generative.index._documents import (
    Document,
    StaticDocument,
)
from azure.ai.generative.index._embeddings import EmbeddingsContainer
from azure.ai.generative.index._utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_log_metric,
    safe_mlflow_start_run,
    track_activity,
)

logger = get_logger("embed")


def read_chunks_into_documents(files: Iterator[pathlib.Path], chunk_format: str = "csv") -> Iterator[Document]:
    """Reads chunks from files and yields documents."""
    # Append to list of texts and corresponding metadata
    file_max_chunk_len = 0
    files = list(files)
    num_files = len(files)
    for i, chunk_file in enumerate(files):
        file_name = chunk_file.name
        logger.info(f"==== Reading chunks from file {i+1}/{num_files}: {file_name}")
        max_chunk_len = 0
        num_chunks = 0
        if file_name.lower().endswith(".jsonl") or chunk_format == "jsonl":
            with open(chunk_file) as f:
                for line in f:
                    doc = StaticDocument.loads(line.strip())
                    max_chunk_len = max(max_chunk_len, len(doc.data))
                    num_chunks += 1
                    yield doc
        elif file_name.lower().endswith(".csv") or chunk_format == "csv":
            # Ensure Chunk data is read as string even if it looks like another datatype.
            dtype = {"Chunk": str, "Metadata": str}
            try:
                chunks_df = pd.read_csv(chunk_file, dtype=dtype, keep_default_na=False)
            except Exception as e:
                if "Try engine='python'" in str(e):
                    logger.warning("Failed to read csv with default engine, trying engine='python'")
                    chunks_df = pd.read_csv(chunk_file, dtype=dtype, keep_default_na=False, engine="python")
                else:
                    raise

            chunks_dict = chunks_df.to_dict()
            for chunk_idx, chunk in chunks_dict["Chunk"].items():
                metadata = chunks_dict["Metadata"][chunk_idx]
                metadata_dict = json.loads(metadata)
                max_chunk_len = max(max_chunk_len, len(chunk))
                num_chunks += 1
                yield StaticDocument(data=chunk, metadata=metadata_dict, document_id=metadata_dict["source"]["filename"] + str(chunk_idx), mtime=metadata_dict["source"].get("mtime"))

        logger.info(f"==== Read {num_chunks} chunks file {i+1}/{num_files}: {file_name}, max_chunk_len = {max_chunk_len}")
        file_max_chunk_len = max(file_max_chunk_len, max_chunk_len)
    logger.info(f"longest chunk seen was {file_max_chunk_len}", extra={"print": True})


def load_embeddings_container(embeddings_model_uri: str, connection_args: dict, logger, embeddings_container_path: Optional[str] = None, worker_id=0):
    """Loads embeddings container from uri or from previous run."""
    embeddings_container = None
    if embeddings_container_path is not None:
        with track_activity(logger, "init.load_embeddings_container") as activity_logger:
            if hasattr(activity_logger, "activity_info"):
                activity_logger.activity_info["completionStatus"] = "Failure"
            embeddings_container = EmbeddingsContainer.load_latest_snapshot(embeddings_container_path, activity_logger=activity_logger)

    return embeddings_container if embeddings_container is not None else EmbeddingsContainer.from_uri(embeddings_model_uri, **connection_args)


def chunk_embedder(worker_id, chunk_queue, results_queue, embeddings_model_uri, connection_args, embeddings_container, output, logger_queue):
    """Embeds chunks from queue and writes to output path."""
    try:
        enable_appinsights_logging()
        logger = get_logger(f"chunk_embedder_{worker_id}")
        # handler = logging.handlers.QueueHandler(logger_queue)
        # logger.addHandler(handler)
        logger.info(f"chunk_embedder_{worker_id} started")

        embedder = load_embeddings_container(embeddings_model_uri, connection_args, logger, embeddings_container, worker_id)

        with track_activity(logger, f"embed.chunk_embedder_{worker_id}") as activity_logger:
            activity_logger.activity_info["chunk_batches"] = 0
            activity_logger.activity_info["chunks"] = 0
            activity_logger.activity_info["embed_time"] = 0.0
            while True:
                logger.info(f"waiting for chunk_batch: {worker_id}")
                entry = chunk_queue.get()
                if entry is None:
                    logger.info(f"got None batch from queue, exiting: {worker_id}")
                    break

                (batch_id, chunks) = entry
                logger.info(f"==== embedding batch_id={batch_id} with {len(chunks)} chunks")
                activity_logger.activity_info["chunk_batches"] += 1
                activity_logger.activity_info["chunks"] += len(chunks)

                pre_embed = time.time()
                embeddings = embedder.embed_and_create_new_instance(chunks)
                post_embed = time.time()
                logger.info(f"Embedding took {post_embed - pre_embed} seconds")
                activity_logger.activity_info["embed_time"] += post_embed - pre_embed
                try:
                    results_queue.put({"documents_embedded": embeddings.statistics["documents_embedded"], "documents_reused": embeddings.statistics["documents_reused"]})
                except Exception as e:
                    logger.warning(f"Failed to put results in results_queue: {e}")

                save_metadata = str(batch_id) == "0"
                if save_metadata:
                    logger.info("Metadata will be saved")
                else:
                    logger.info("Only data will be saved")
                embeddings.save(output, with_metadata=save_metadata, suffix=str(batch_id))

                if _logger_factory.appinsights:
                    _logger_factory.appinsights.flush()
    except Exception as e:
        logger.error(f"Exception in chunk_embedder_{worker_id}: {e}")
        raise


def _check_workers(embedder_futures, activity_logger):
    for i, future in enumerate(embedder_futures):
        try:
            future.get(timeout=1)
        except mp.TimeoutError:
            continue  # Worker hasn't thrown exception
        except Exception as e:
            logger.error(f"Exception in chunk_embedder worker: {e}")
            if activity_logger:
                activity_logger.activity_info["failed_worker_id"] = i
                activity_logger.activity_info["exception_name"] = type(e).__name__
                activity_logger.activity_info["exception_trace"] = traceback.format_exc()
            raise

    return None


def _merge_and_log_worker_results(results_queue, merged_results: dict, activity_logger):
    got_results = False
    while True:
        try:
            results = results_queue.get(timeout=1)
            got_results = True
            merged_results["documents_embedded"] += results["documents_embedded"]
            merged_results["documents_reused"] += results["documents_reused"]
        except Exception:
            break

    if got_results:
        safe_mlflow_log_metric("Documents Embedded", merged_results["documents_embedded"], logger=activity_logger, step=int(time.time() * 1000))
        safe_mlflow_log_metric("Documents Reused", merged_results["documents_reused"], logger=activity_logger, step=int(time.time() * 1000))
    return merged_results


def create_embeddings(chunks: Iterator[Document],
                      embeddings_model_uri: str,
                      connection_args: dict,
                      embeddings_container: str,
                      output: str,
                      activity_logger=None,
                      batch_size: int = 100,
                      num_workers: int = -1,
    ):
    """Queues chunks for embedding by process workers."""
    num_workers = num_workers if num_workers > 0 else max(mp.cpu_count() // 2, 2)
    if activity_logger:
        activity_logger.activity_info["num_workers"] = num_workers

    with mp.Manager() as manager:
        try:
            # Create a queue to hold the chunks
            chunk_queue = manager.Queue(maxsize=num_workers)
            results_queue = manager.Queue(maxsize=num_workers * 2)
            merged_results = {"documents_embedded": 0, "documents_reused": 0}

            logger_queue = manager.Queue(maxsize=-1)
            listener = logging.handlers.QueueListener(logger_queue, *logger.handlers)
            listener.start()

            # Create a thread pool for embedding
            # Replace concurrent futures with multiprocessing Pool
            with mp.Pool(processes=num_workers) as pool:
                # Start processes to take chunks from the queue and embed them
                embedder_futures = [pool.apply_async(chunk_embedder, (i, chunk_queue, results_queue, embeddings_model_uri, connection_args, embeddings_container, output, logger_queue)) for i in range(num_workers)]

                # Read chunks and put them in the queue
                chunk_batch = []
                batch_id = 0
                for chunk in chunks:
                    chunk_batch.append(chunk)
                    if len(chunk_batch) == batch_size:
                        logger.info(f"==== Putting batch_id={batch_id} with {len(chunk_batch)} chunks in queue")
                        while True:
                            _check_workers(embedder_futures, activity_logger)
                            merged_results = _merge_and_log_worker_results(results_queue, merged_results, activity_logger)
                            try:
                                chunk_queue.put((batch_id, chunk_batch), timeout=3)
                                break
                            except queue.Full:
                                pass
                        batch_id += 1
                        chunk_batch = []

                if len(chunk_batch) > 0:
                    logger.info(f"==== Putting batch_id={batch_id} with {len(chunk_batch)} chunks in queue")
                    while True:
                        _check_workers(embedder_futures, activity_logger)
                        merged_results = _merge_and_log_worker_results(results_queue, merged_results, activity_logger)
                        try:
                            chunk_queue.put((batch_id, chunk_batch), timeout=3)
                            break
                        except queue.Full:
                            pass

                    batch_id += 1
                    chunk_batch = []

                logger.info(f"==== Waiting for embedders to finish, {num_workers if batch_id > num_workers else batch_id}/{batch_id} batches remaining")

                # Put sentinel values in the queue to stop the embedder processes
                for _ in range(num_workers):
                    while True:
                        _check_workers(embedder_futures, activity_logger)
                        merged_results = _merge_and_log_worker_results(results_queue, merged_results, activity_logger)
                        try:
                            chunk_queue.put(None, timeout=3)
                            break
                        except queue.Full:
                            pass

                # Wait for all embedder processes to finish
                for i, future in enumerate(embedder_futures):
                    try:
                        future.get()
                    except Exception as e:
                        logger.error(f"Exception in chunk_embedder worker: {e}")
                        if activity_logger:
                            activity_logger.activity_info["failed_worker_id"] = i
                            activity_logger.activity_info["exception_name"] = type(e).__name__
                            activity_logger.activity_info["exception_trace"] = traceback.format_exc()
                        raise

                merged_results = _merge_and_log_worker_results(results_queue, merged_results, activity_logger)
        finally:
            listener.enqueue_sentinel()
            listener.stop()


def main(args, logger, activity_logger):
    """Main function for creating embeddings."""
    logger.info("Reading chunks from the chunks_source", extra={"print": True})

    files = pathlib.Path(args.chunks_source).rglob("**/*")
    chunks = read_chunks_into_documents(files)

    connection_args = {}
    connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_AOAI")
    if connection_id is not None:
        connection_args["connection_type"] = "workspace_connection"
        connection_args["connection"] = {"id": connection_id}
    else:
        if "open_ai" in args.embeddings_model:
            from azure.ai.generative.index._utils.azureml import get_workspace_from_environment

            ws = get_workspace_from_environment()
            connection_args["connection_type"] = "workspace_keyvault"
            connection_args["connection"] = {
                "subscription": ws.subscription_id if ws is not None else "",
                "resource_group": ws.resource_group if ws is not None else "",
                "workspace": ws.name if ws is not None else "",
                "key": "OPENAI-API-KEY"
            }

    if args.embeddings_container is not None:
        with track_activity(logger, "init.load_embeddings_container") as embeddings_container_activity_logger:
            if hasattr(embeddings_container_activity_logger, "activity_info"):
                embeddings_container_activity_logger.activity_info["completionStatus"] = "Failure"
            from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount
            mnt_options = MountOptions(
                default_permission=0o555, read_only=False, allow_other=False, create_destination=True) # read_only=True,
            try:
                create_embeddings_failed = False
                with rslex_uri_volume_mount(args.embeddings_container, f"{os.getcwd()}/embeddings_container", options=mnt_options) as mount_context:
                    try:
                        create_embeddings(chunks,
                                        args.embeddings_model,
                                        connection_args,
                                        mount_context.mount_point,
                                        args.output,
                                        activity_logger,
                                        args.batch_size)
                    except Exception:
                        create_embeddings_failed = True
                        raise

            except Exception as e:
                if not create_embeddings_failed:
                    embeddings_container_activity_logger.warn("Failed to mount embeddings_container.")
                    logger.warn(f"Failed to mount embeddings_container with {e}.")
                raise
    else:
        create_embeddings(chunks,
                            args.embeddings_model,
                            connection_args,
                            None,
                            args.output,
                            activity_logger,
                            args.batch_size,
                            args.num_workers)


def main_wrapper(args, logger):
    """Wrapper for main function to track activity."""
    with track_activity(logger, "embed") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(f"embed failed with exception: {traceback.format_exc()}")  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    # If chunking was done separately
    parser.add_argument("--chunks_source", required=True, type=str)
    # If adding to previously generated Embeddings
    parser.add_argument("--embeddings_container", required=False, type=str, default=None)
    parser.add_argument("--output", type=str)
    # Embeddings settings
    parser.add_argument("--embeddings_model", type=str, default="azure_oen_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002")
    parser.add_argument("--batch_size", type=int, default=-1)
    parser.add_argument("--num_workers", type=int, default=-1)
    args = parser.parse_args()

    print("\n".join(f"{k}={v}" for k, v in vars(args).items()))

    enable_stdout_logging()
    enable_appinsights_logging()

    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
