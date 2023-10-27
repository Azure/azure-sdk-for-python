# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os.path
import json
import re
from pathlib import Path
import pandas as pd

_SUB_ID = "sub-id"
_RES_GRP = "res-grp"
_WS_NAME = "ws-name"
_EXP_NAME = "experiment"
_RUN_ID = "runid"

def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f.readlines()]

def load_jsonl_to_df(path):
    if os.path.exists(path) and os.path.isfile(path):
        return pd.read_json(path, lines=True)
    else:
        raise Exception("File not found: {}".format(path))

def _has_column(data, column_name):
    if data is None:
        return False
    for d in data:
        return False if d.get(column_name) is None else True


def _is_flow(asset):
    if _is_flow_local(asset):
        return True
    else:
        return False


def _is_flow_local(path):
    try:
        if os.path.isdir(path):
            return os.path.isfile(os.path.join(path, "flow.dag.yaml"))
    except Exception as ex:
        return False


def _get_artifact_dir_path(path):
    import mlflow
    from mlflow.tracking.artifact_utils import get_artifact_repository

    _WORKSPACE_INFO_REGEX = r".*/subscriptions/(.+)/resourceGroups/(.+)" \
                            r"/providers/Microsoft.MachineLearningServices/workspaces/([^/]+)"

    _ARTIFACT_URI_REGEX = _WORKSPACE_INFO_REGEX + r"/experiments/([^/]+)/runs/([^/]+)(/artifacts.*)?"

    artifact_uri = mlflow.get_artifact_uri()

    run_info_dict = {}

    mo = re.compile(_ARTIFACT_URI_REGEX).match(artifact_uri)
    run_info_dict[_SUB_ID] = mo.group(1)
    run_info_dict[_RES_GRP] = mo.group(2)
    run_info_dict[_WS_NAME] = mo.group(3)
    run_info_dict[_EXP_NAME] = mo.group(4)
    run_info_dict[_RUN_ID] = mo.group(5)

    artifact_repo = get_artifact_repository(artifact_uri=artifact_uri)

    content_info = artifact_repo.artifacts._client.run_artifacts.get_by_id(
        subscription_id=run_info_dict[_SUB_ID], resource_group_name=run_info_dict[_RES_GRP],
        workspace_name=run_info_dict[_WS_NAME], run_id=run_info_dict[_RUN_ID], experiment_name=run_info_dict[_EXP_NAME],
        path=path)

    datastore = "workspaceartifactstore"
    file_path = Path(content_info.artifact_id).parent.as_posix()

    return f"azureml://datastores/{datastore}/paths/{file_path}"


def _write_properties_to_run_history(properties: dict, logger) -> None:
    import mlflow
    from mlflow.tracking import MlflowClient
    from mlflow.utils.rest_utils import http_request

    # get mlflow run
    run = mlflow.active_run()
    if run is None:
        run = mlflow.start_run()
    # get auth from client
    client = MlflowClient()
    try:
        cred = client._tracking_client.store.get_host_creds()  # pylint: disable=protected-access
        # update host to run history and request PATCH API
        cred.host = cred.host.replace("mlflow/v2.0", "mlflow/v1.0").replace("mlflow/v1.0", "history/v1.0")
        response = http_request(
            host_creds=cred,
            endpoint=f"/experimentids/{run.info.experiment_id}/runs/{run.info.run_id}",
            method="PATCH",
            json={"runId": run.info.run_id, "properties": properties},
        )
        if response.status_code != 200:
            logger.error("Fail writing properties '%s' to run history: %s", properties, response.text)
            response.raise_for_status()
    except AttributeError as e:
        logger.error("Fail writing properties '%s' to run history: %s", properties, e)