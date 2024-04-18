# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
from typing import Optional

from azureml._base_sdk_common.service_discovery import get_service_url
from azureml.core import Run, Workspace
from azureml.exceptions import UserErrorException
from azure.ai.ml.entities._indexes.utils.logging import get_logger

from ._restclient._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces as rest_client
from ._restclient.models import CreateRun, DataVersion, DataVersionMutable

logger = get_logger("asset_client")


def _get_workspace_uri_path(subscription_id, resource_group, workspace_name):
    return (
        "/subscriptions/{}/resourceGroups/{}/providers" "/Microsoft.MachineLearningServices" "/workspaces/{}"
    ).format(subscription_id, resource_group, workspace_name)


def get_rest_client(ws: Workspace):
    host = get_service_url(
        ws._auth,
        _get_workspace_uri_path(ws._subscription_id, ws._resource_group, ws._workspace_name),
        ws._workspace_id,
        ws.discovery_url,
    )

    return rest_client(credential=ws._auth, subscription_id=ws.subscription_id, base_url=host)


def list_mlindex_assets(client, workspace: Workspace):
    data_assets = client.mlindex.list(workspace._subscription_id, workspace._resource_group, workspace._workspace_name)
    return data_assets


def get_data_asset_version(client, run: Run, asset_id: str):
    workspace = run.experiment.workspace
    matches = re.match(r".*/data/(?P<asset_name>.*)/versions/(?P<asset_version>.*)$", asset_id)
    data_version = client.data_version.get(
        workspace._subscription_id,
        workspace._resource_group,
        workspace._workspace_name,
        matches.group("asset_name"),
        matches.group("asset_version"),
    )
    return data_version.data_version


def get_uri_for_data_version(data_version) -> str:
    return data_version.data_uri


def register_new_data_asset_version_workspace(
    client,
    workspace: Workspace,
    asset_name: str,
    uri: str,
    properties: dict,
    output_type: str = "UriFolder",
    run_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    tags: Optional[dict] = None,
):
    try:
        create_dto = DataVersion(
            data_type=output_type,
            data_uri=uri,
            run_id=run_id,
            properties=properties,
            mutable_props=DataVersionMutable(tags=tags),
        )
        data_asset_response = client.data_version.create(
            workspace._subscription_id, workspace._resource_group, workspace._workspace_name, asset_name, create_dto
        )
        data_version = data_asset_response.data_version
    except Exception as ex:
        if (
            hasattr(ex, "model")
            and hasattr(ex.model, "error")
            and hasattr(ex.model.error, "message")
            and (
                "OutputName is invalid" in ex.model.error.message
                or "does not have permissions for Microsoft.MachineLearningServices/workspaces/datasets/registered/write actions"
                in ex.model.error.message
            )
        ):
            raise UserErrorException(f"Data asset creation API failed with user error:{ex.model.error.message}")
        raise RuntimeError(f"Data asset creation API failed with system error:{ex}")

    asset_id = data_version.asset_id

    _save_asset_output_lineage_workspace(workspace, client, asset_id, output_type, asset_name, run_id, experiment_id)

    return data_version


def register_new_data_asset_version(
    client,
    run: Run,
    asset_name: str,
    uri: str,
    properties: dict,
    output_type: str = "UriFolder",
    tags: Optional[dict] = None,
):
    workspace = run.experiment.workspace
    output_type = output_type
    try:
        create_dto = DataVersion(
            data_type=output_type,
            data_uri=uri,
            run_id=run.id,
            properties=properties,
            mutable_props=DataVersionMutable(tags=tags),
        )
        data_asset_response = client.data_version.create(
            workspace._subscription_id, workspace._resource_group, workspace._workspace_name, asset_name, create_dto
        )
        data_version = data_asset_response.data_version
    except Exception as ex:
        if (
            hasattr(ex, "model")
            and hasattr(ex.model, "error")
            and hasattr(ex.model.error, "message")
            and (
                "OutputName is invalid" in ex.model.error.message
                or "does not have permissions for Microsoft.MachineLearningServices/workspaces/datasets/registered/write actions"
                in ex.model.error.message
            )
        ):
            raise UserErrorException(f"Data asset creation API failed with user error:{ex.model.error.message}")
        raise RuntimeError(f"Data asset creation API failed with system error:{ex}")

    asset_id = data_version.asset_id

    _save_asset_output_lineage(run, asset_id, output_type, asset_name, client)

    return data_version


def _save_asset_output_lineage_workspace(
    workspace: Workspace, rest_client, asset_id: str, asset_type: str, output_name: str, run_id: str, experiment_id: str
):
    logger.info(
        "saving asset output lineage for output",
        extra={"output_name": output_name, "asset.id": asset_id, "asset.type": asset_type},
    )

    workspace = workspace
    try:
        outputs = {output_name: {"asset_id": asset_id, "type": asset_type}}

        update_dto = CreateRun(run_id=run_id, outputs=outputs, experiment_id=experiment_id)
        run = rest_client.runs.add_or_modify_experiment(
            workspace._subscription_id, workspace._resource_group, workspace._workspace_name, run_id, update_dto
        )
    except Exception as e:
        logger.error("Cannot update output asset lineage", extra={"exception": str(e)})
        raise


def _save_asset_output_lineage(run: Run, asset_id: str, asset_type: str, output_name: str, rest_client):
    # with _tracer.start_as_current_span('data-capability._save_asset_output_lineage'):
    logger.info(
        "saving asset output lineage for output",
        extra={"output_name": output_name, "asset.id": asset_id, "asset.type": asset_type},
    )

    workspace = run.experiment.workspace
    try:
        outputs = {output_name: {"asset_id": asset_id, "type": asset_type}}

        update_dto = CreateRun(run_id=run.id, outputs=outputs, experiment_id=run.experiment.id)
        run = rest_client.runs.add_or_modify_experiment(
            workspace._subscription_id, workspace._resource_group, workspace._workspace_name, run.id, update_dto
        )
    except Exception as e:
        logger.error("Cannot update output asset lineage", extra={"exception": str(e)})
        raise
