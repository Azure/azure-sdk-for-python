# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""File for building FAISS Indexes."""
import os
import time
import traceback
from pathlib import Path

from azure.ai.resources.index._embeddings import EmbeddingsContainer
from azure.ai.resources.index._utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)

logger = get_logger("build_faiss")


def main(args, logger, activity_logger):
    raw_embeddings_uri = args.embeddings
    logger.info(f"got embeddings uri as input: {raw_embeddings_uri}")
    splits = raw_embeddings_uri.split("/")
    embeddings_dir_name = splits.pop(len(splits)-2)
    logger.info(f"extracted embeddings directory name: {embeddings_dir_name}")
    parent = "/".join(splits)
    logger.info(f"extracted embeddings container path: {parent}")

    # Mock OPENAI_API_KEY being set so that loading Embeddings doesn't fail, we don't need to do any embedding so should be fine
    os.environ["OPENAI_API_KEY"] = "nope"

    from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount

    mnt_options = MountOptions(
        default_permission=0o555, allow_other=False, read_only=True)
    logger.info(f"mounting embeddings container from: \n{parent} \n   to: \n{os.getcwd()}/raw_embeddings", extra={"print": True})
    activity_logger.info("Mounting embeddings container")
    try:
        with rslex_uri_volume_mount(parent, f"{os.getcwd()}/raw_embeddings", options=mnt_options) as mount_context:
            logger.info("Loading Embeddings")
            emb = EmbeddingsContainer.load(embeddings_dir_name, mount_context.mount_point)
            activity_logger.activity_info["num_documents"] = len(emb._document_embeddings)
            emb.write_as_faiss_mlindex(Path(args.output))
    except Exception as e:
        activity_logger.activity_info["error"] = str(e)
        logger.error(f"Failed to load embeddings: {e}")
        raise e
    logger.info("Generated FAISS index")


def main_wrapper(args, logger):
    with track_activity(logger, "build_faiss") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            main(args, logger, activity_logger)
        except Exception:
            activity_logger.error(f"build_faiss failed with exception: {traceback.format_exc()}")  # activity_logger doesn't log traceback
            raise

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--embeddings", type=str)
    parser.add_argument("--output", type=str)
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
