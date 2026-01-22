# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from collections.abc import MutableMapping, Awaitable  # pylint:disable=import-error
from typing import Any, Callable, Tuple, TypeVar, cast, Mapping, Optional, List

import base64
import functools
import time

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncPollingMethod, PollingMethod
from azure.core.polling.base_polling import (
    BadResponse,
    LongRunningOperation,
    OperationFailed,
)
from azure.core.polling._utils import _decode_continuation_token, _encode_continuation_token
from azure.core.rest import HttpRequest

from ._enums import ExportedProjectFormat
from ._models import (
    AssignedProjectResource,
    CopyProjectDetails,
    CopyProjectState,
    ConversationExportedEntity,
    ConversationExportedIntent,
    ConversationExportedProjectAsset,
    ConversationExportedUtterance,
    CreateDeploymentDetails as _GeneratedCreateDeploymentDetails,
    DeploymentDeleteFromResourcesState,
    DeploymentState,
    EvaluationJobResult,
    EvaluationState,
    ExportProjectState,
    ExportedModelDetails,
    ExportedModelState,
    ExportedProject,
    ExportedUtteranceEntityLabel,
    ImportProjectState,
    LoadSnapshotState,
    ProjectDeletionState,
    ResourceMetadata,
    SwapDeploymentsDetails,
    SwapDeploymentsState,
    TrainingJobDetails,
)

JSON = MutableMapping[str, Any]
T = TypeVar("T")
PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

class _JobsStrategy(LongRunningOperation):
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
    def get_status(self, pipeline_response: JSON) -> str:  # type: ignore
        raw = str(pipeline_response.get("status", "")).lower()
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


class _JobsPollingMethod(PollingMethod):
    def __init__(self, polling_interval: float = 30.0, *, path_format_arguments: Optional[dict] = None, **kwargs: Any):
        self._polling_interval = polling_interval
        self._kwargs = kwargs
        self._path_format_arguments = path_format_arguments or {}

        # predeclare attributes to satisfy pylint W0201
        self._client: Any = None
        self._initial_response: Optional[PipelineResponse] = None
        self._deserialization_callback: Optional[Callable] = None
        self._resource: Optional[PipelineResponse] = None
        self._status: str = "NotStarted"
        self._operation: Any = None  # or a concrete type if available
        self._command: Optional[Callable[[], PipelineResponse]] = None

    # ---- LRO lifecycle ----
    def initialize(self, client: Any, initial_response: PipelineResponse, deserialization_callback: Callable) -> None:
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._resource = None
        self._status = "InProgress"

        # Extract operation-location (case-insensitive)
        headers = initial_response.http_response.headers
        op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        if not op_loc:
            raise BadResponse("Missing Operation-Location header for job polling")

        # Resolve {Endpoint} etc.
        if self._path_format_arguments:
            op_loc = self._client.format_url(op_loc, **self._path_format_arguments)

        # Strategy: always use jobs URL
        self._operation = _JobsStrategy(op_loc)
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
        if self._deserialization_callback is None or self._initial_response is None:
            raise RuntimeError("Polling method not initialized; call initialize() first.")
        # Return typed object using provided callback (expects PipelineResponse)
        return self._deserialization_callback(self._resource or self._initial_response)

    def update_status(self) -> None:
        if self._command is None:
            raise RuntimeError("Polling method not initialized; call initialize() first.")

        try:
            self._resource = self._command()
        except ResourceNotFoundError:
            # Treat as transient if your service uses 404-before-ready semantics
            self._resource = None

        body: JSON = {}
        if self._resource is not None:
            try:
                body = cast(JSON, self._resource.http_response.json())
            except Exception as exc:
                raise BadResponse("Polling response is not JSON") from exc
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
            PipelineResponse,
            self._client._pipeline.run(request, stream=False, **self._kwargs),  # pylint: disable=protected-access
        )

    # ---- Continuation token support (doc pattern) ----
    def get_continuation_token(self) -> str:
        
        return _encode_continuation_token(self._initial_response)

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any) -> Tuple[Any, Any, Callable[[Any], PollingReturnType_co]]:
        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from None

        initial_response = _decode_continuation_token(continuation_token)
        return None, initial_response, deserialization_callback

class _AsyncJobsPollingMethod(AsyncPollingMethod):
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

        # Predeclare all attributes to satisfy pylint W0201
        self._client: Any = None
        self._initial_response: Optional[PipelineResponse] = None
        self._deserialization_callback: Optional[Callable] = None
        self._resource: Optional[PipelineResponse] = None
        self._status: str = "NotStarted"
        self._operation: Any = None
        self._command: Optional[Callable[[], Awaitable[PipelineResponse]]] = None

    # ---- LRO lifecycle ----
    def initialize(self, client: Any, initial_response: PipelineResponse, deserialization_callback: Callable) -> None:
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._resource = None  # no type annotation here
        self._status = "InProgress"  # no type annotation here

        # Operation-Location (case-insensitive)
        headers = initial_response.http_response.headers
        op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        if not op_loc:
            raise BadResponse("Missing Operation-Location header for job polling")

        if self._path_format_arguments:
            op_loc = self._client.format_url(op_loc, **self._path_format_arguments)

        self._operation = _JobsStrategy(op_loc)
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
                await self._sleep(self._polling_interval)

        final_url = self._operation.get_final_get_url(self._initial_response)
        if final_url:
            self._resource = await self._do_get_async(final_url)

    async def _sleep(self, seconds: float) -> None:
        # Prefer the Azure Core transport's sleep (fast/no-op in playback)
        transport = getattr(self._client, "_transport", None) or getattr(
            getattr(self._client, "_pipeline", None), "_transport", None
        )
        if transport and hasattr(transport, "sleep"):
            await transport.sleep(seconds)
            return
        # Fallback for non-Azure transports (allowed per rule text)
        import asyncio  # pylint: disable=import-outside-toplevel, do-not-import-asyncio

        await asyncio.sleep(seconds)

    def finished(self) -> bool:
        return self._status in ("Succeeded", "Failed", "Canceled")

    def status(self) -> str:
        return self._status

    def resource(self) -> Any:
        if self._deserialization_callback is None or self._initial_response is None:
            raise RuntimeError("Polling method not initialized; call initialize() first.")
        return self._deserialization_callback(self._resource or self._initial_response)

    async def update_status(self) -> None:
        if self._command is None:
            raise RuntimeError("Polling method not initialized; call initialize() first.")

        try:
            self._resource = await self._command()
        except ResourceNotFoundError:
            self._resource = None

        body: dict = {}
        if self._resource is not None:
            try:
                body = cast(dict, self._resource.http_response.json())
            except Exception as exc:  # be explicit so pylint sees the chain
                raise BadResponse("Polling response is not JSON") from exc
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

        return _encode_continuation_token(self._initial_response)

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any) -> Tuple[Any, Any, Callable[[Any], PollingReturnType_co]]:
        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from None

        initial_response = _decode_continuation_token(continuation_token)
        return None, initial_response, deserialization_callback

class CreateDeploymentDetails(_GeneratedCreateDeploymentDetails):
    """Represents the options for creating or updating a project deployment.

    :ivar trained_model_label: Represents the trained model label.
    :vartype trained_model_label: str
    :ivar azure_resource_ids: Language or AIService resource IDs associated with this deployment.
     For service version 2025-11-15-preview, this is represented as a list of
     class:`AssignedProjectResource`. For service version 2025-11-01, it may be
     constructed from a list of resource ID strings.
    :vartype azure_resource_ids:
     list[~azure.ai.language.conversations.authoring.models.AssignedProjectResource] or list[str]
    """

    _azure_resource_ids_strings: Optional[List[str]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Case 1: mapping initializer → let generated code handle it
        if args and isinstance(args[0], Mapping):
            super().__init__(*args, **kwargs)
            self._azure_resource_ids_strings = None
            return

        azure_ids = kwargs.pop("azure_resource_ids", None)
        self._azure_resource_ids_strings = None

        if azure_ids is None:
            # nothing special, just call base
            super().__init__(*args, azure_resource_ids=None, **kwargs)
            return

        # If user passed AssignedProjectResource list → original behavior
        if all(isinstance(x, AssignedProjectResource) for x in azure_ids):
            super().__init__(*args, azure_resource_ids=azure_ids, **kwargs)
            return

        # If user passed plain strings → GA style, remember them and *don't*
        # try to turn them into AssignedProjectResource here.
        if all(isinstance(x, str) for x in azure_ids):
            self._azure_resource_ids_strings = list(azure_ids)
            super().__init__(*args, azure_resource_ids=None, **kwargs)
            return

        raise TypeError(
            "azure_resource_ids must be a list of str or a list of AssignedProjectResource."
        )

def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = [
    "SwapDeploymentsDetails",
    "CopyProjectState",
    "ExportProjectState",
    "SwapDeploymentsState",
    "CreateDeploymentDetails",
    "DeploymentDeleteFromResourcesState",
    "DeploymentState",
    "ExportedModelDetails",
    "ExportedModelState",
    "LoadSnapshotState",
    "ProjectDeletionState",
    "ExportedProjectFormat",
    "ExportedProject",
    "ImportProjectState",
    "CopyProjectDetails",
    "TrainingJobDetails",
    "CopyProjectDetails",
    "EvaluationJobResult",
    "EvaluationState",
    "ConversationExportedProjectAsset",
    "ConversationExportedIntent",
    "ConversationExportedEntity",
    "ConversationExportedUtterance",
    "ExportedUtteranceEntityLabel",
    "ResourceMetadata",
]
