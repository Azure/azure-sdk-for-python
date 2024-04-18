# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import re
import time
import traceback
import uuid
from logging import Logger
from pathlib import Path
from typing import Dict, Optional, Union

from azureml.core import Run
from azureml.core.authentication import TokenAuthentication
from azureml.core.workspace import Workspace
from azure.ai.ml.entities._indexes._asset_client.client import get_rest_client, register_new_data_asset_version_workspace
from azure.ai.ml.entities._indexes.tasks.crack_and_chunk_and_embed import str2bool
from azure.ai.ml.entities._indexes.tasks.crack_and_chunk_and_embed_and_index import crack_and_chunk_and_embed_and_index
from azure.ai.ml.entities._indexes.tasks.validate_deployments import validate_deployments
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)

try:
    from azure.core.credentials import TokenCredential
except Exception:
    TokenCredential = object

logger = get_logger("crack_chunk_embed_index_and_register")


def crack_chunk_embed_index_and_register(
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
    embeddings_cache: Optional[Union[str, Path]] = None,
    batch_size: int = 100,
    num_workers: int = -1,
    index_type: str = "acs",
    index_connection: Optional[str] = None,
    index_config: Optional[Dict[str, str]] = None,
    output_index_path: Optional[Union[str, Path]] = None,
    output_index_asset_uri: Optional[str] = None,
    credential: Optional[TokenCredential] = None,
    activity_logger: Optional[Logger] = None,
):
    """Main function for crack_chunk_embed_index_and_register."""
    if output_index_path is None:
        output_index_path = f"{Path.cwd()}/embeddings"

    mlindex = crack_and_chunk_and_embed_and_index(
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
        embeddings_cache=embeddings_cache,
        batch_size=batch_size,
        num_workers=num_workers,
        index_type=index_type,
        index_connection=index_connection,
        index_config=index_config,
        output_path=output_index_path,
        activity_logger=activity_logger,
    )

    # If the output_index_asset_uri is None, compose the path ourselves and write a dummy file to create the folder.
    if not output_index_asset_uri:
        run = Run.get_context()
        workspace = run.experiment.workspace
        output_index_asset_uri = f"azureml://subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/workspaces/{workspace.name}/datastores/{workspace.get_default_datastore().name}/paths/OnYourDataMlIndexes/{uuid.uuid4()!s}/"
        from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount

        mnt_options = MountOptions(
            default_permission=0o555, read_only=False, allow_other=False, create_destination=True
        )

        mount_context = rslex_uri_volume_mount(output_index_asset_uri, f"{Path.cwd()}/dummy", options=mnt_options)

        try:
            mount_context.start()
            dummy_file_path = Path(mount_context.mount_point) / "dummy"
            dummy_file_path.touch()
        finally:
            mount_context.stop()

        logger.info(f"Successfully created index asset uri: {output_index_asset_uri}")

    if output_index_asset_uri and "://" in output_index_asset_uri:
        from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount

        mnt_options = MountOptions(default_permission=0o555, read_only=False, allow_other=False)
        mount_context = rslex_uri_volume_mount(
            output_index_asset_uri, f"{Path.cwd()}/mlindex_asset", options=mnt_options
        )
        try:
            mount_context.start()
            mlindex.save(mount_context.mount_point)
        finally:
            mount_context.stop()

        # Register the MLIndex data asset
        register_workspace = None
        # Try parse target workspace from asset_uri
        uri_match = re.match(
            r"/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.MachineLearningServices/workspaces/(.*)/.*",
            output_index_asset_uri,
            flags=re.IGNORECASE,
        )
        if uri_match:
            from azure.ai.ml.identity import AzureMLOnBehalfOfCredential
            from azure.identity import DefaultAzureCredential

            if credential is None:
                client_id = os.environ.get("DEFAULT_IDENTITY_CLIENT_ID", None)
                if os.environ.get("OBO_ENDPOINT"):
                    print("Using User Identity for authentication")
                    credential = AzureMLOnBehalfOfCredential()
                    os.environ["MSI_ENDPOINT"] = os.environ.get("OBO_ENDPOINT", "")
                else:
                    print("Using DefaultAzureCredential for authentication")
                    credential = DefaultAzureCredential(managed_identity_client_id=client_id, process_timeout=60)

            register_workspace = Workspace(
                subscription_id=uri_match.group(1),
                resource_group=uri_match.group(2),
                workspace_name=uri_match.group(3),
                auth=TokenAuthentication(
                    get_token_for_audience=credential.get_token,
                ),
            )
        # Use OBO / MSI / RunToken to auth (credential passed by upstream?)
        if not register_workspace:
            run = Run.get_context()
            register_workspace = run.experiment.workspace
        else:
            try:
                run = Run.get_context()
            except Exception:
                run = None

        mlindex_asset_properties = {
            "azureml.mlIndexAssetKind": index_type,
            "azureml.mlIndexAsset": "true",
        }
        if run:
            mlindex_asset_properties["azureml.mlIndexAssetSource"] = run.properties.get(
                "azureml.mlIndexAssetSource", "Unknown"
            )
            mlindex_asset_properties["azureml.mlIndexAssetPipelineRunId"] = run.properties.get(
                "azureml.pipelinerunid", "Unknown"
            )

        client = get_rest_client(register_workspace)
        data_version = register_new_data_asset_version_workspace(
            client,
            register_workspace,
            args.asset_name,
            args.asset_uri,
            properties=mlindex_asset_properties,
            run_id=run.id if run else None,
            experiment_id=run.experiment.id if run else None,
        )

        logger.info(f"Finished Registering MLIndex Asset '{args.asset_name}', version = {data_version.version_id}")
    else:
        logger.info("Skipping MLIndex Asset registration because no run context was provided")

    return mlindex


def main(args, logger, activity_logger):
    """Main function for crack_chunk_embed_index_and_register."""
    if args.embeddings_connection_id is None:
        logger.info("Reading connection id from environment variable")
        args.embeddings_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_AOAI")
    if args.llm_connection_id is None:
        args.llm_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_AOAI")

    llm_config = None
    if args.llm_config:
        llm_config = json.loads(args.llm_config)

    if args.index_connection_id is None:
        logger.info("Reading connection id from environment variable")
        args.index_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_ACS")

    index_config = None
    if args.index_config:
        index_config = json.loads(args.index_config)

    if args.validate_deployments:
        validate_deployments(
            embeddings_model=args.embeddings_model,
            activity_logger=activity_logger,
            embeddings_connection_id=args.embeddings_connection_id,
            llm_config=llm_config,
            llm_connection_id=args.llm_connection_id,
            output=None,
        )

    crack_chunk_embed_index_and_register(
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
        index_config=index_config,
        output_index_path=args.output_path,
        output_index_asset_uri=args.asset_uri,
        activity_logger=activity_logger,
    )


def main_wrapper(args, logger):
    with track_activity(logger, "crack_chunk_embed_index_and_register") as activity_logger, safe_mlflow_start_run(
        logger=logger
    ):
        try:
            main(args, logger, activity_logger)
        except Exception as e:
            activity_logger.error(
                f"crack_chunk_embed_index_and_register failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise e


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    # Connection validation
    parser.add_argument("--validate_deployments", type=str2bool, default=False)
    parser.add_argument("--llm_config", type=str, default=None)
    parser.add_argument("--llm_connection_id", type=str, required=False)
    # Data loading and chunking
    parser.add_argument("--input_data", type=str)
    parser.add_argument("--input_glob", type=str, default="**/*")
    parser.add_argument("--chunk_size", type=int)
    parser.add_argument("--chunk_overlap", type=int)
    parser.add_argument("--citation_url", type=str, required=False)
    parser.add_argument("--citation_replacement_regex", type=str, required=False)
    parser.add_argument("--custom_loader", type=str2bool, default=None)
    parser.add_argument(
        "--doc_intel_connection_id", type=str, default=None, help="The connection id for Document Intelligence service"
    )
    # Chunk embedding
    parser.add_argument("--embeddings_model", type=str, required=False)
    parser.add_argument("--embeddings_connection_id", type=str, required=False)
    parser.add_argument("--embeddings_container", type=str, required=False)
    parser.add_argument("--batch_size", type=int, default=-1)
    parser.add_argument("--num_workers", type=int, default=-1)
    # Chunk indexing
    parser.add_argument("--index_type", type=str, required=False, default="acs")
    parser.add_argument("--index_connection_id", type=str, required=False)
    parser.add_argument("--index_config", type=str, required=True)
    # Asset registration
    parser.add_argument("--asset_name", type=str, required=False)
    parser.add_argument("--asset_description", type=str, required=False)
    # Remote URI to write MLIndex Asset to
    parser.add_argument("--asset_uri", type=str, required=False)
    # Local path to write MLIndex Asset to
    parser.add_argument("--output_path", type=str, required=False)

    # Legacy
    parser.add_argument("--max_sample_files", type=int, default=-1)
    parser.add_argument("--use_rcts", type=str2bool, default=True)

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
