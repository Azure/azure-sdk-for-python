# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""File for registering ML Indexes."""

import argparse
import re
import time
import traceback

import fsspec
import yaml
from azureml.core import Run
from azure.ai.ml.entities._indexes._asset_client.client import get_rest_client, register_new_data_asset_version
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)

logger = get_logger("register_mlindex")


def main(args, run, logger, activity_logger):
    ws = run.experiment.workspace

    logger.info(f'Checking for MLIndex at: {args.storage_uri.strip("/")}/MLIndex')
    embeddings_kind = None
    index_kind = None
    index_connection_type = None
    mlindex_yaml = None
    playground_types = []
    try:
        mlindex_file = fsspec.open(f"{args.storage_uri}/MLIndex", "r")
        # parse yaml to dict
        with mlindex_file as f:
            mlindex_yaml = yaml.safe_load(f)
            embeddings_kind = mlindex_yaml.get("embeddings", {}).get("kind", None)
            embeddings_api_type = mlindex_yaml.get("embeddings", {}).get("api_type", None)
            index_kind = mlindex_yaml.get("index", {}).get("kind", None)
            index_connection_type = mlindex_yaml.get("index", {}).get("connection_type", None)
    except Exception as e:
        logger.error(f"Could not find MLIndex: {e}")
        activity_logger.activity_info["error"] = "Could not find MLIndex yaml"
        raise e

    if index_kind is None:
        logger.error(f"Could not find index.kind in MLIndex: {mlindex_yaml}")
        activity_logger.activity_info["error"] = "Could not find index.kind in MLIndex yaml"
        raise ValueError(f"Could not find index.kind in MLIndex: {mlindex_yaml}")
    activity_logger.activity_info["kind"] = index_kind

    if index_connection_type is None:
        logger.error(f"Could not find index.connection_type in MLIndex: {mlindex_yaml}")
        activity_logger.activity_info["error"] = "Could not find index.connection_type in MLIndex yaml"
    if embeddings_kind is None:
        logger.error(f"Could not find embeddings.kind in MLIndex: {mlindex_yaml}")
        activity_logger.activity_info["error"] = "Could not find embeddings.kind in MLIndex yaml"

    if index_kind == "acs" and index_connection_type == "workspace_connection":
        if embeddings_kind == "open_ai":
            playground_types.append("Text")
        elif embeddings_kind == "florence":
            playground_types.append("Image")
        elif embeddings_kind == "serverless_endpoint" and embeddings_api_type == "cohere":
            playground_types.append("Text")

    client = get_rest_client(ws)
    data_version = register_new_data_asset_version(
        client,
        run,
        args.asset_name,
        args.storage_uri,
        properties={
            "azureml.mlIndexAssetKind": index_kind,
            "azureml.mlIndexAsset": "true",
            "azureml.mlIndexAssetSource": run.properties.get("azureml.mlIndexAssetSource", "Unknown"),
            "azureml.mlIndexAssetPipelineRunId": run.properties.get("azureml.pipelinerunid", "Unknown"),
        },
        tags={"PlaygroundType": playground_types},
    )

    asset_id = re.sub(
        "azureml://locations/(.*)/workspaces/(.*)/data",
        f"azureml://subscriptions/{ws._subscription_id}/resourcegroups/{ws._resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{ws._workspace_name}/data",
        data_version.asset_id,
    )
    with open(args.output_asset_id, "w") as f:
        f.write(asset_id)

    logger.info(f"Finished Registering MLIndex Asset '{args.asset_name}', version = {data_version.version_id}")


def main_wrapper(args, run, logger):
    with track_activity(
        logger,
        "register_mlindex",
        custom_dimensions={"source": run.properties.get("azureml.mlIndexAssetSource", "Unknown")},
    ) as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            main(args, run, logger, activity_logger)
        except Exception:
            activity_logger.error(
                f"register_mlindex failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--storage-uri", type=str, required=True, dest="storage_uri")
    parser.add_argument("--asset-name", type=str, required=False, dest="asset_name", default="MLIndexAsset")
    parser.add_argument("--output-asset-id", type=str, dest="output_asset_id")
    args = parser.parse_args()

    print("\n".join(f"{k}={v}" for k, v in vars(args).items()))

    enable_stdout_logging()
    enable_appinsights_logging()

    run: Run = Run.get_context()

    try:
        main_wrapper(args, run, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)  # wait for appinsights to send telemetry
    run.complete()
