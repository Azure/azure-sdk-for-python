# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional, Any, MutableMapping
from azure.core.polling.base_polling import LongRunningOperation, BadResponse, OperationFailed
from azure.core.pipeline import PipelineResponse
import functools
import time
import base64
import asyncio
from typing import Any, Callable, Tuple, MutableMapping, Optional, cast
from azure.core.polling import PollingMethod, AsyncPollingMethod
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest
from azure.core.polling.base_polling import BadResponse
from azure.core.exceptions import ResourceNotFoundError
from ._models import (
    AssignDeploymentResourcesDetails,
    AssignDeploymentResourcesDetails,
    UnassignDeploymentResourcesDetails,
    SwapDeploymentsDetails,
    DeploymentResourcesState,
    CopyProjectState,
    ExportProjectState,
    SwapDeploymentsState,
    DeploymentResourcesState,
    DeleteDeploymentDetails,
    CreateDeploymentDetails,
    DeploymentDeleteFromResourcesState,
    DeploymentState,
    ExportedModelDetails,
    ExportedModelState,
    LoadSnapshotState,
    DeploymentResourcesState,
    ProjectDeletionState,
    ExportedProject,
    ImportProjectState,
    CopyProjectDetails,
    TrainingJobDetails,
    CopyProjectDetails,
    EvaluationJobResult,
    EvaluationState,
)

JSON = MutableMapping[str, Any]


class JobsStrategy(LongRunningOperation):
    """Interprets job-status responses and tells the poller which URL to use."""

    def __init__(self, async_url: str):
        self._async_url = async_url

    # We can poll if we have an operation-location URL
    def can_poll(self, pipeline_response: PipelineResponse) -> bool:  # noqa: D401
        return bool(self._async_url)

    # Always poll the jobs URL from operation-location
    def get_polling_url(self) -> str:  # noqa: D401
        return self._async_url

    # Initial status after the first call (202→InProgress, 200 could be immediate success)
    def set_initial_status(self, pipeline_response: PipelineResponse) -> str:  # noqa: D401
        sc = pipeline_response.http_response.status_code
        if sc in (200, 201):
            return "InProgress"  # job hasn’t finished yet; service will report status on poll
        if sc in (202, 204):
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    # Map service statuses to core strings
    def get_status(self, response: JSON) -> str:  # noqa: D401
        raw = str(response.get("status", "")).lower()
        if raw in ("succeeded",):
            return "Succeeded"
        if raw in ("failed",):
            return "Failed"
        if raw in ("cancelled", "canceled"):
            return "Canceled"
        # notstarted, running, cancelling, partiallycompleted → still in progress
        return "InProgress"

    # Force the final GET to also come from operation-location (or return None to use last body)
    def get_final_get_url(self, pipeline_response: PipelineResponse) -> Optional[str]:  # noqa: D401
        return self._async_url


class JobsPollingMethod(PollingMethod):
    def __init__(self, polling_interval: float = 30.0, *, path_format_arguments: Optional[dict] = None, **kwargs: Any):
        self._polling_interval = polling_interval
        self._kwargs = kwargs
        self._path_format_arguments = path_format_arguments or {}

    # ---- LRO lifecycle ----
    def initialize(self, client: Any, initial_response: PipelineResponse, deserialization_callback: Callable) -> None:
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._resource: Optional[PipelineResponse] = None
        self._status: str = "InProgress"

        # Extract operation-location (case-insensitive)
        headers = initial_response.http_response.headers
        op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        if not op_loc:
            raise BadResponse("Missing Operation-Location header for job polling")

        # Resolve {Endpoint} etc.
        if self._path_format_arguments:
            op_loc = self._client.format_url(op_loc, **self._path_format_arguments)

        # Strategy: always use jobs URL
        self._operation = JobsStrategy(op_loc)
        if not self._operation.can_poll(initial_response):
            raise BadResponse("Cannot poll: no jobs URL")

        # Command to GET status from jobs URL
        self._command = functools.partial(self._do_get, self._operation.get_polling_url())

        # Initial status
        self._status = self._operation.set_initial_status(initial_response)

    def run(self) -> None:
        while not self.finished():
            self.update_status()
            if not self.finished():
                time.sleep(self._polling_interval)

        # Final GET (via jobs URL) if strategy asks for it
        final_url = self._operation.get_final_get_url(self._initial_response)
        if final_url:
            self._resource = self._do_get(final_url)

    def finished(self) -> bool:
        return self._status in ("Succeeded", "Failed", "Canceled")

    def status(self) -> str:
        return self._status

    def resource(self) -> Any:
        # Return typed object using provided callback (expects PipelineResponse)
        return self._deserialization_callback(self._resource or self._initial_response)

    def update_status(self) -> None:
        try:
            self._resource = self._command()
        except ResourceNotFoundError:
            # Treat as transient if your service uses 404-before-ready semantics
            self._resource = None

        body: JSON = {}
        if self._resource is not None:
            try:
                body = cast(JSON, self._resource.http_response.json())
            except Exception:
                raise BadResponse("Polling response is not JSON")
        self._status = self._operation.get_status(body)

    # ---- Helpers ----
    def _do_get(self, url: str) -> PipelineResponse:
        # REST pipeline path (new core)
        if hasattr(self._client, "send_request"):
            req = HttpRequest("GET", url)
            return cast(
                PipelineResponse, self._client.send_request(req, _return_pipeline_response=True, **self._kwargs)
            )
        # Legacy pipeline fallback
        request = self._client.get(url)
        return cast(
            PipelineResponse, self._client._pipeline.run(request, stream=False, **self._kwargs)
        )  # pylint: disable=protected-access

    # ---- Continuation token support (doc pattern) ----
    def get_continuation_token(self) -> str:
        import pickle

        return base64.b64encode(pickle.dumps(self._initial_response)).decode("ascii")

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any) -> Tuple[Any, PipelineResponse, Callable]:
        import pickle

        client = kwargs["client"]
        deserialization_callback = kwargs["deserialization_callback"]
        initial_response = pickle.loads(base64.b64decode(continuation_token))  # nosec
        return client, initial_response, deserialization_callback

class AsyncJobsPollingMethod(AsyncPollingMethod):
    def __init__(
        self,
        polling_interval: float = 30.0,
        *,
        path_format_arguments: Optional[dict] = None,
        **kwargs: Any,
    ):
        self._polling_interval = polling_interval
        self._kwargs = kwargs
        self._path_format_arguments = path_format_arguments or {}

    # ---- LRO lifecycle ----
    def initialize(self, client: Any, initial_response: PipelineResponse, deserialization_callback: Callable) -> None:
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._resource: Optional[PipelineResponse] = None
        self._status: str = "InProgress"

        # Operation-Location (case-insensitive)
        headers = initial_response.http_response.headers
        op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        if not op_loc:
            raise BadResponse("Missing Operation-Location header for job polling")

        if self._path_format_arguments:
            op_loc = self._client.format_url(op_loc, **self._path_format_arguments)

        self._operation = JobsStrategy(op_loc)
        if not self._operation.can_poll(initial_response):
            raise BadResponse("Cannot poll: no jobs URL")

        # async GET command bound to jobs URL
        self._command = functools.partial(self._do_get_async, self._operation.get_polling_url())

        # Seed initial status from first response
        self._status = self._operation.set_initial_status(initial_response)

    async def run(self) -> None:
        while not self.finished():
            await self.update_status()
            if not self.finished():
                await asyncio.sleep(self._polling_interval)

        # Final GET (using jobs URL) if strategy requires it
        final_url = self._operation.get_final_get_url(self._initial_response)
        if final_url:
            self._resource = await self._do_get_async(final_url)

    def finished(self) -> bool:
        return self._status in ("Succeeded", "Failed", "Canceled")

    def status(self) -> str:
        return self._status

    def resource(self) -> Any:
        # Return typed object via provided callback (expects PipelineResponse)
        return self._deserialization_callback(self._resource or self._initial_response)

    async def update_status(self) -> None:
        try:
            self._resource = await self._command()
        except ResourceNotFoundError:
            # Optional: services that briefly 404 while job is materializing
            self._resource = None

        body: dict = {}
        if self._resource is not None:
            try:
                body = cast(dict, self._resource.http_response.json())
            except Exception:
                raise BadResponse("Polling response is not JSON")
        self._status = self._operation.get_status(body)

    # ---- Helpers ----
    async def _do_get_async(self, url: str) -> PipelineResponse:
        # New core: async pipeline client has async send_request
        if hasattr(self._client, "send_request"):
            req = HttpRequest("GET", url)
            return cast(
                PipelineResponse,
                await self._client.send_request(req, _return_pipeline_response=True, **self._kwargs),
            )
        # Legacy fallback (unlikely in modern azure-core)
        request = self._client.get(url)
        return cast(
            PipelineResponse,
            await self._client._pipeline.run(request, stream=False, **self._kwargs),  # pylint: disable=protected-access
        )

    # ---- Continuation token ----
    def get_continuation_token(self) -> str:
        import pickle
        return base64.b64encode(pickle.dumps(self._initial_response)).decode("ascii")

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any) -> Tuple[Any, PipelineResponse, Callable]:
        import pickle
        client = kwargs["client"]
        deserialization_callback = kwargs["deserialization_callback"]
        initial_response = pickle.loads(base64.b64decode(continuation_token))  # nosec
        return client, initial_response, deserialization_callback

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = [
    "JobsStrategy",
    "JobsPollingMethod",
    "AssignDeploymentResourcesDetails",
    "UnassignDeploymentResourcesDetails",
    "SwapDeploymentsDetails",
    "DeploymentResourcesState",
    "CopyProjectState",
    "ExportProjectState",
    "SwapDeploymentsState",
    "DeploymentResourcesState",
    "DeleteDeploymentDetails",
    "CreateDeploymentDetails",
    "DeploymentDeleteFromResourcesState",
    "DeploymentState",
    "ExportedModelDetails",
    "ExportedModelState",
    "LoadSnapshotState",
    "DeploymentResourcesState",
    "ProjectDeletionState",
    "ExportedProjectFormat",
    "ExportedProject",
    "ImportProjectState",
    "CopyProjectDetails",
    "TrainingJobDetails",
    "CopyProjectDetails",
    "EvaluationJobResult",
    "EvaluationState",
    "AsyncJobsPollingMethod",
]