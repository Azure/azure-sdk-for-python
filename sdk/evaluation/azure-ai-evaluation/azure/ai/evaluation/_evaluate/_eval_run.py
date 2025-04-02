# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import contextlib
import dataclasses
import enum
import logging
import os
import posixpath
import time
import types
import uuid
from typing import Any, Dict, List, Optional, Set, Type
from urllib.parse import urlparse

from promptflow._sdk.entities import Run
from typing_extensions import Self

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._http_utils import get_http_client
from azure.ai.evaluation._version import VERSION
from azure.core.pipeline.policies import RetryPolicy
from azure.core.rest import HttpResponse
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobServiceClient
from azure.ai.evaluation._azure._clients import LiteMLClient

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class RunInfo:
    """
    A holder for run info, needed for logging.
    """

    run_id: str
    experiment_id: str
    run_name: str

    @staticmethod
    def generate(run_name: Optional[str]) -> "RunInfo":
        """
        Generate the new RunInfo instance with the RunID and Experiment ID.

        **Note:** This code is used when we are in failed state and cannot get a run.

        :param run_name: The name of a run.
        :type run_name: Optional[str]
        :return: The RunInfo instance.
        :rtype: azure.ai.evaluation._evaluate._eval_run.RunInfo
        """
        return RunInfo(str(uuid.uuid4()), str(uuid.uuid4()), run_name or "")


class RunStatus(enum.Enum):
    """Run states."""

    NOT_STARTED = 0
    STARTED = 1
    BROKEN = 2
    TERMINATED = 3


class EvalRun(contextlib.AbstractContextManager):  # pylint: disable=too-many-instance-attributes
    """
    The simple singleton run class, used for accessing artifact store.

    :param run_name: The name of the run.
    :type run_name: Optional[str]
    :param tracking_uri: Tracking URI for this run; required to make calls.
    :type tracking_uri: str
    :param subscription_id: The subscription ID used to track run.
    :type subscription_id: str
    :param group_name: The resource group used to track run.
    :type group_name: str
    :param workspace_name: The name of workspace/project used to track run.
    :type workspace_name: str
    :param management_client: The trace destination string to parse the AI ML workspace blob store from.
    :type management_client:
        ~azure.ai.evaluation._promptflow.azure._lite_azure_management_client.LiteMLClient
    :param promptflow_run: The promptflow run used by the
    :type promptflow_run: Optional[promptflow._sdk.entities.Run]
    """

    _MAX_RETRIES = 5
    _BACKOFF_FACTOR = 2
    _TIMEOUT = 5

    EVALUATION_ARTIFACT = "instance_results.jsonl"

    def __init__(
        self,
        run_name: Optional[str],
        tracking_uri: str,
        subscription_id: str,
        group_name: str,
        workspace_name: str,
        management_client: LiteMLClient,
        promptflow_run: Optional[Run] = None,
    ) -> None:
        self._tracking_uri: str = tracking_uri
        self._subscription_id: str = subscription_id
        self._resource_group_name: str = group_name
        self._workspace_name: str = workspace_name
        self._management_client: LiteMLClient = management_client
        self._is_promptflow_run: bool = promptflow_run is not None
        self._run_name = run_name
        self._promptflow_run = promptflow_run
        self._status = RunStatus.NOT_STARTED
        self._url_base: Optional[str] = None
        self._info: Optional[RunInfo] = None

    @property
    def status(self) -> RunStatus:
        """
        Return the run status.

        :return: The status of the run.
        :rtype: promptflow._sdk._constants.RunStatus
        """
        return self._status

    @property
    def info(self) -> RunInfo:
        if self._info is None:
            msg = "Run info is missing"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.EVAL_RUN,
                category=ErrorCategory.UNKNOWN,
                blame=ErrorBlame.UNKNOWN,
            )

        return self._info

    def _get_scope(self) -> str:
        """
        Return the scope information for the workspace.

        :return: The scope information for the workspace.
        :rtype: str
        """
        return (
            "/subscriptions/{}/resourceGroups/{}/providers" "/Microsoft.MachineLearningServices" "/workspaces/{}"
        ).format(
            self._subscription_id,
            self._resource_group_name,
            self._workspace_name,
        )

    def _start_run(self) -> None:
        """
        Start the run, or, if it is not applicable (for example, if tracking is not enabled), mark it as started.
        """
        self._check_state_and_log("start run", {v for v in RunStatus if v != RunStatus.NOT_STARTED}, True)
        self._status = RunStatus.STARTED
        if self._tracking_uri is None:
            LOGGER.warning(
                "A tracking_uri was not provided, The results will be saved locally, but will not be logged to Azure."
            )
            self._url_base = None
            self._status = RunStatus.BROKEN
            self._info = RunInfo.generate(self._run_name)
        else:
            self._url_base = urlparse(self._tracking_uri).netloc
            if self._promptflow_run is not None:
                self._info = RunInfo(
                    self._promptflow_run.name,
                    self._promptflow_run._experiment_name or "",  # pylint: disable=protected-access
                    self._promptflow_run.name,
                )
            else:
                url = f"https://{self._url_base}/mlflow/v2.0" f"{self._get_scope()}/api/2.0/mlflow/runs/create"
                body = {
                    "experiment_id": "0",
                    "user_id": "azure-ai-evaluation",
                    "start_time": int(time.time() * 1000),
                    "tags": [{"key": "mlflow.user", "value": "azure-ai-evaluation"}],
                }
                if self._run_name:
                    body["run_name"] = self._run_name
                response = self.request_with_retry(url=url, method="POST", json_dict=body)
                if response.status_code != 200:
                    self._info = RunInfo.generate(self._run_name)
                    LOGGER.warning(
                        "The run failed to start: %s: %s."
                        "The results will be saved locally, but will not be logged to Azure.",
                        response.status_code,
                        response.text(),
                    )
                    self._status = RunStatus.BROKEN
                else:
                    parsed_response = response.json()
                    self._info = RunInfo(
                        run_id=parsed_response["run"]["info"]["run_id"],
                        experiment_id=parsed_response["run"]["info"]["experiment_id"],
                        run_name=parsed_response["run"]["info"]["run_name"],
                    )
                    self._status = RunStatus.STARTED

    def _end_run(self, reason: str) -> None:
        """
        Terminate the run.

        :param reason: Reason for run termination. Possible values are "FINISHED" "FAILED", and "KILLED"
        :type reason: str
        :raises EvaluationException: Raised if the run is not in ("FINISHED", "FAILED", "KILLED")
        """
        if not self._check_state_and_log(
            "stop run", {RunStatus.BROKEN, RunStatus.NOT_STARTED, RunStatus.TERMINATED}, False
        ):
            return
        if self._is_promptflow_run:
            # This run is already finished, we just add artifacts/metrics to it.
            self._status = RunStatus.TERMINATED
            return
        if reason not in ("FINISHED", "FAILED", "KILLED"):
            raise EvaluationException(
                message=f"Incorrect terminal status {reason}. Valid statuses are 'FINISHED', 'FAILED' and 'KILLED'.",
                internal_message="Incorrect terminal status. Valid statuses are 'FINISHED', 'FAILED' and 'KILLED'",
                target=ErrorTarget.EVAL_RUN,
                category=ErrorCategory.FAILED_EXECUTION,
                blame=ErrorBlame.UNKNOWN,
            )
        url = f"https://{self._url_base}/mlflow/v2.0" f"{self._get_scope()}/api/2.0/mlflow/runs/update"
        body = {
            "run_uuid": self.info.run_id,
            "status": reason,
            "end_time": int(time.time() * 1000),
            "run_id": self.info.run_id,
        }
        response = self.request_with_retry(url=url, method="POST", json_dict=body)
        if response.status_code != 200:
            LOGGER.warning("Unable to terminate the run.")
        self._status = RunStatus.TERMINATED

    def __enter__(self) -> Self:
        """The Context Manager enter call.

        :return: The instance of the class.
        :rtype: azure.ai.evaluation._evaluate._eval_run.EvalRun
        """
        self._start_run()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        """The context manager exit call.

        :param exc_type: The exception type
        :type exc_type: Optional[Type[BaseException]]
        :param exc_value: The exception value
        :type exc_value: Optional[BaseException]
        :param exc_tb: The exception traceback
        :type exc_tb: Optional[types.TracebackType]
        """
        self._end_run("FINISHED")

    def get_run_history_uri(self) -> str:
        """
        Get the run history service URI.

        :return: The run history service URI.
        :rtype: str
        """
        return (
            f"https://{self._url_base}"
            "/history/v1.0"
            f"{self._get_scope()}"
            f"/experimentids/{self.info.experiment_id}/runs/{self.info.run_id}"
        )

    def get_artifacts_uri(self) -> str:
        """
        Gets the URI to upload the artifacts to.

        :return: The URI to upload the artifacts to.
        :rtype: str
        """
        return self.get_run_history_uri() + "/artifacts/batch/metadata"

    def get_metrics_url(self):
        """
        Return the url needed to track the mlflow metrics.

        :return: The url needed to track the mlflow metrics.
        :rtype: str
        """
        return f"https://{self._url_base}" "/mlflow/v2.0" f"{self._get_scope()}" f"/api/2.0/mlflow/runs/log-metric"

    def _get_token(self) -> str:
        return self._management_client.get_token()

    def request_with_retry(
        self, url: str, method: str, json_dict: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> HttpResponse:
        """
        Send the request with retries.

        :param url: The url to send the request to.
        :type url: str
        :param method: The request method to be used.
        :type method: str
        :param json_dict: The json dictionary (not serialized) to be sent.
        :type json_dict: Dict[str, Any]
        :param headers: The headers to be sent with the request.
        :type headers: Optional[Dict[str, str]]
        :return: The response
        :rtype: HttpResponse
        """
        if headers is None:
            headers = {}
        headers["User-Agent"] = f"promptflow/{VERSION}"
        headers["Authorization"] = f"Bearer {self._get_token()}"

        session = get_http_client().with_policies(
            retry_policy=RetryPolicy(
                retry_total=EvalRun._MAX_RETRIES,
                retry_connect=EvalRun._MAX_RETRIES,
                retry_read=EvalRun._MAX_RETRIES,
                retry_status=EvalRun._MAX_RETRIES,
                retry_on_status_codes=(408, 429, 500, 502, 503, 504),
                retry_backoff_factor=EvalRun._BACKOFF_FACTOR,
            )
        )
        return session.request(method, url, headers=headers, json=json_dict, timeout=EvalRun._TIMEOUT)

    def _log_warning(self, failed_op: str, response: HttpResponse) -> None:
        """
        Log the error if request was not successful.

        :param failed_op: The user-friendly message for the failed operation.
        :type failed_op: str
        :param response: The request.
        :type response: HttpResponse
        """
        LOGGER.warning(
            "Unable to %s, the request failed with status code %s, response.text()=%s.",
            failed_op,
            response.status_code,
            response.text(),
        )

    def _check_state_and_log(self, action: str, bad_states: Set[RunStatus], should_raise: bool) -> bool:
        """
        Check that the run is in the correct state and log worning if it is not.

        :param action: Action, which caused this check. For example if it is "log artifact",
            the log message will start "Unable to log artifact."
        :type action: str
        :param bad_states: The states, considered invalid for given action.
        :type bad_states: Set[RunStatus]
        :param should_raise: Should we raise an error if the bad state has been encountered
        :type should_raise: bool
        :raises: ~azure.ai.evaluations._exceptions.EvaluationException if should_raise is True
             and invalid state was encountered.
        :return: Whether or not run is in the correct state.
        :rtype: bool
        """
        if self._status in bad_states:
            msg = f"Unable to {action} due to Run status={self._status}."
            if should_raise:
                raise EvaluationException(
                    message=msg,
                    internal_message=msg,
                    target=ErrorTarget.EVAL_RUN,
                    category=ErrorCategory.FAILED_EXECUTION,
                    blame=ErrorBlame.UNKNOWN,
                )
            LOGGER.warning(msg)
            return False
        return True

    def log_artifact(self, artifact_folder: str, artifact_name: str = EVALUATION_ARTIFACT) -> None:
        """
        The local implementation of mlflow-like artifact logging.

        **Note:** In the current implementation we are not using the thread pool executor
        as it is done in azureml-mlflow, instead we are just running upload in cycle as we are not
        expecting uploading a lot of artifacts.

        :param artifact_folder: The folder with artifacts to be uploaded.
        :type artifact_folder: str
        :param artifact_name: The name of the artifact to be uploaded. Defaults to
            azure.ai.evaluation._evaluate._eval_run.EvalRun.EVALUATION_ARTIFACT.
        :type artifact_name: str
        """
        if not self._check_state_and_log("log artifact", {RunStatus.BROKEN, RunStatus.NOT_STARTED}, False):
            return
        # Check if artifact directory is empty or does not exist.
        if not os.path.isdir(artifact_folder):
            LOGGER.warning("The path to the artifact is either not a directory or does not exist.")
            return
        if not os.listdir(artifact_folder):
            LOGGER.warning("The path to the artifact is empty.")
            return
        if not os.path.isfile(os.path.join(artifact_folder, artifact_name)):
            LOGGER.warning("The run results file was not found, skipping artifacts upload.")
            return
        # First we will list the files and the appropriate remote paths for them.
        root_upload_path = posixpath.join("promptflow", "PromptFlowArtifacts", self.info.run_id)
        remote_paths: Dict[str, List[Dict[str, str]]] = {"paths": []}
        local_paths = []
        # Go over the artifact folder and upload all artifacts.
        for root, _, filenames in os.walk(artifact_folder):
            upload_path = root_upload_path
            if root != artifact_folder:
                rel_path = os.path.relpath(root, artifact_folder)
                if rel_path != ".":
                    upload_path = posixpath.join(root_upload_path, rel_path)
            for f in filenames:
                remote_file_path = posixpath.join(upload_path, f)
                remote_paths["paths"].append({"path": remote_file_path})
                local_file_path = os.path.join(root, f)
                local_paths.append(local_file_path)

        # We will write the artifacts to the workspaceblobstore
        datastore = self._management_client.workspace_get_default_datastore(
            self._workspace_name, include_credentials=True
        )
        account_url = f"{datastore.account_name}.blob.{datastore.endpoint}"

        svc_client = BlobServiceClient(account_url=account_url, credential=datastore.credential)
        try:
            for local, remote in zip(local_paths, remote_paths["paths"]):
                blob_client = svc_client.get_blob_client(container=datastore.container_name, blob=remote["path"])
                with open(local, "rb") as fp:
                    blob_client.upload_blob(fp, overwrite=True)
        except HttpResponseError as ex:
            if ex.status_code == 403:
                msg = (
                    "Failed to upload evaluation run to the cloud due to insufficient permission to access the storage."
                    " Please ensure that the necessary access rights are granted."
                )
                raise EvaluationException(
                    message=msg,
                    target=ErrorTarget.EVAL_RUN,
                    category=ErrorCategory.FAILED_REMOTE_TRACKING,
                    blame=ErrorBlame.USER_ERROR,
                    tsg_link="https://aka.ms/azsdk/python/evaluation/remotetracking/troubleshoot",
                ) from ex

            raise ex

        # To show artifact in UI we will need to register it. If it is a promptflow run,
        # we are rewriting already registered artifact and need to skip this step.
        if self._is_promptflow_run:
            return

        url = (
            f"https://{self._url_base}/artifact/v2.0/subscriptions/{self._subscription_id}"
            f"/resourceGroups/{self._resource_group_name}/providers/"
            f"Microsoft.MachineLearningServices/workspaces/{self._workspace_name}/artifacts/register"
        )

        response = self.request_with_retry(
            url=url,
            method="POST",
            json_dict={
                "origin": "ExperimentRun",
                "container": f"dcid.{self.info.run_id}",
                "path": artifact_name,
                "dataPath": {
                    "dataStoreName": datastore.name,
                    "relativePath": posixpath.join(root_upload_path, artifact_name),
                },
            },
        )
        if response.status_code != 200:
            self._log_warning("register artifact", response)

        # register artifacts for images if exists in image folder
        try:
            for remote_path in remote_paths["paths"]:
                remote_file_path = remote_path["path"]
                if "images" in os.path.normpath(remote_file_path).split(os.sep):
                    response = self.request_with_retry(
                        url=url,
                        method="POST",
                        json_dict={
                            "origin": "ExperimentRun",
                            "container": f"dcid.{self.info.run_id}",
                            "path": posixpath.join("images", os.path.basename(remote_file_path)),
                            "dataPath": {
                                "dataStoreName": datastore.name,
                                "relativePath": remote_file_path,
                            },
                        },
                    )
                    if response.status_code != 200:
                        self._log_warning("register image artifact", response)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            LOGGER.debug("Exception occurred while registering image artifact. ex: %s", ex)

    def log_metric(self, key: str, value: float) -> None:
        """
        Log the metric to azure similar to how it is done by mlflow.

        :param key: The metric name to be logged.
        :type key: str
        :param value: The valure to be logged.
        :type value: float
        """
        if not self._check_state_and_log("log metric", {RunStatus.BROKEN, RunStatus.NOT_STARTED}, False):
            return
        body = {
            "run_uuid": self.info.run_id,
            "key": key,
            "value": value,
            "timestamp": int(time.time() * 1000),
            "step": 0,
            "run_id": self.info.run_id,
        }
        response = self.request_with_retry(
            url=self.get_metrics_url(),
            method="POST",
            json_dict=body,
        )
        if response.status_code != 200:
            self._log_warning("save metrics", response)

    def write_properties_to_run_history(self, properties: Dict[str, Any]) -> None:
        """
        Write properties to the RunHistory service.

        :param properties: The properties to be written to run history.
        :type properties: dict
        """
        if not self._check_state_and_log("write properties", {RunStatus.BROKEN, RunStatus.NOT_STARTED}, False):
            return
        # update host to run history and request PATCH API
        response = self.request_with_retry(
            url=self.get_run_history_uri(),
            method="PATCH",
            json_dict={"runId": self.info.run_id, "properties": properties},
        )
        if response.status_code != 200:
            LOGGER.error("Fail writing properties '%s' to run history: %s", properties, response.text())
