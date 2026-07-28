# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import base64
import json
import time
from collections.abc import MutableMapping
from io import IOBase
from typing import IO, Any, Iterator, Optional, Union, cast, overload

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    StreamClosedError,
    StreamConsumedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.mgmt.core.exceptions import ARMErrorFormat

from .. import models as _models
from .._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from .._validation import api_version_validation
from ._operations import ComputesOperations as _ComputesOperationsGenerated
from ._operations import build_computes_create_or_update_request

JSON = MutableMapping[str, Any]

_TERMINAL_FAILED_STATES = frozenset({"failed", "canceled", "cancelled"})
_TERMINAL_SUCCESS_STATES = frozenset({"succeeded"})
_CANCELED_STATES = frozenset({"canceled", "cancelled"})


def _encode_continuation_token(resource_group_name: str, account_name: str, compute_name: str) -> str:
    """Encode the polling scope (resource group, account, compute) into an opaque continuation token.

    :param resource_group_name: The resource group name of the compute being polled.
    :type resource_group_name: str
    :param account_name: The Cognitive Services account name of the compute being polled.
    :type account_name: str
    :param compute_name: The name of the compute being polled.
    :type compute_name: str
    :return: A url-safe, opaque continuation token encoding the polling scope.
    :rtype: str
    """
    payload = json.dumps(
        {
            "resource_group_name": resource_group_name,
            "account_name": account_name,
            "compute_name": compute_name,
        }
    )
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii")


def _decode_continuation_token(continuation_token: str):
    """Decode a token produced by :func:`_encode_continuation_token` into its polling scope.

    :param continuation_token: A token previously produced by :func:`_encode_continuation_token`.
    :type continuation_token: str
    :return: The decoded scope as ``(resource_group_name, account_name, compute_name)``.
    :rtype: tuple[str, str, str]
    :raises ValueError: if the token is malformed, so a bad or unrelated token fails loudly instead of
        silently resuming the wrong operation.
    """
    try:
        payload = json.loads(base64.urlsafe_b64decode(continuation_token.encode("ascii")).decode("utf-8"))
        return payload["resource_group_name"], payload["account_name"], payload["compute_name"]
    except Exception as exc:  # pylint: disable=broad-except
        raise ValueError("Invalid continuation_token for compute begin_create_or_update.") from exc


def _state_of(compute: Any) -> str:
    """Return a compute's ``provisioningState`` as a lowercase string (handles enum or str).

    :param compute: A compute object (model or mapping) as returned by ``ComputesOperations.list``.
    :type compute: any
    :return: The compute's ``provisioningState`` lowercased, or an empty string if it is unavailable.
    :rtype: str
    """
    props = getattr(compute, "properties", None)
    state = getattr(props, "provisioning_state", None) if props is not None else None
    if state is None and isinstance(compute, MutableMapping):
        state = (compute.get("properties") or {}).get("provisioningState")
    if state is None:
        return ""
    return str(getattr(state, "value", state)).lower()


def _provisioning_error(compute: Any) -> HttpResponseError:
    """Build a descriptive error from a compute whose provisioning reached a failed state.

    Because the poller reads status from ``list`` (not the operation-status endpoint), the failure
    detail lives in the compute's ``properties.errors``. Surface that instead of azure-core's generic
    ``Operation failed or canceled`` / ``invalid status`` messages.

    :param compute: A compute whose provisioning reached a failed/canceled terminal state.
    :type compute: any
    :return: An error describing the failure using the compute's own ``properties.errors`` detail.
    :rtype: ~azure.core.exceptions.HttpResponseError
    """
    props = getattr(compute, "properties", None)
    errors = getattr(props, "errors", None) if props is not None else None
    if errors is None and isinstance(compute, MutableMapping):
        errors = (compute.get("properties") or {}).get("errors")
    parts = []
    for err in errors or []:
        if isinstance(err, MutableMapping):
            code, message = err.get("code"), err.get("message")
        else:
            code, message = getattr(err, "code", None), getattr(err, "message", None)
        if code and message:
            parts.append(f"{code}: {message}")
        elif message or code:
            parts.append(str(message or code))
    detail = "; ".join(p for p in parts if p)
    state = _state_of(compute) or "failed"
    text = f"Compute provisioning {state}."
    if detail:
        text = f"{text} {detail}"
    return HttpResponseError(message=text)


class _ComputeListPolling(PollingMethod):
    """Blocking LRO poller that reads compute status from the ``list`` API instead of ``get``.

    The compute create is asynchronous (the service returns HTTP 202) and the new compute is **not**
    reliably queryable via ``get`` during creation: a ``GET`` on the resource returns
    ``404 "Cluster not found"`` for an extended, variable period while the cluster backend
    materializes. The compute does, however, appear in the ``list`` response with its
    ``provisioningState`` from the moment the create is accepted. This poller therefore polls ``list``
    (matching the resource by name) until the compute reaches a terminal ``provisioningState``.

    It blocks like a normal long-running-operation poller, never calls the permission-gated
    ``.../computeOperations/{id}`` endpoint (so it does not need ``computeOperations/read``), and
    surfaces the compute's own error detail on failure. A bounded grace period bounds how long the
    compute may be absent from ``list`` before the poller gives up, so a create that never materializes
    does not hang forever.
    """

    _NOT_FOUND_GRACE_SECONDS = 300

    def __init__(
        self,
        operations: "ComputesOperations",
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        interval: float,
        cls: Any = None,
    ) -> None:
        self._operations = operations
        self._resource_group_name = resource_group_name
        self._account_name = account_name
        self._compute_name = compute_name
        self._interval = interval
        self._cls = cls
        self._status = "InProgress"
        self._resource: Optional[_models.Compute] = None
        self._first_missing_at: Optional[float] = None
        self._initial_response: Any = None

    def initialize(self, client: Any, initial_response: Any, deserialization_callback: Any) -> None:
        self._initial_response = initial_response

    def _current_compute(self) -> Optional[_models.Compute]:
        for compute in self._operations.list(self._resource_group_name, self._account_name):
            if getattr(compute, "name", None) == self._compute_name:
                return compute
        return None

    def run(self) -> None:
        while not self.finished():
            compute = self._current_compute()
            if compute is None:
                # The create was accepted, so the compute should appear in ``list`` shortly. Tolerate a
                # brief absence, but give up after a bounded grace so a create that never materializes
                # does not hang forever.
                if self._first_missing_at is None:
                    self._first_missing_at = time.monotonic()
                elif time.monotonic() - self._first_missing_at > self._NOT_FOUND_GRACE_SECONDS:
                    raise HttpResponseError(
                        message=f"Compute '{self._compute_name}' did not appear in the account's compute "
                        "list after it was created."
                    )
            else:
                self._first_missing_at = None
                self._resource = compute
                state = _state_of(compute)
                if state in _TERMINAL_SUCCESS_STATES:
                    self._status = "Succeeded"
                elif state in _TERMINAL_FAILED_STATES:
                    # Preserve the service's terminal status (``Canceled`` vs ``Failed``) so callers can
                    # inspect ``poller.status()`` correctly, while still raising the provisioning error.
                    self._status = "Canceled" if state in _CANCELED_STATES else "Failed"
                    raise _provisioning_error(compute)
            if not self.finished():
                time.sleep(self._interval)

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._status in ("Succeeded", "Failed", "Canceled")

    def resource(self) -> Optional[_models.Compute]:
        # Apply the caller's ``cls`` hook (if any) to the final resource, preserving the generated
        # method's ``cls=`` contract. There is no final pipeline response for the list-based read-back,
        # so ``None`` is passed for that positional argument.
        if self._resource is not None and self._cls is not None:
            return self._cls(None, self._resource, {})
        return self._resource

    def get_continuation_token(self) -> str:
        return _encode_continuation_token(self._resource_group_name, self._account_name, self._compute_name)

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any):
        # Validate the token is well-formed; the polling scope it encodes is applied when the poller is
        # (re)constructed in ``begin_create_or_update``.
        _decode_continuation_token(continuation_token)
        client = kwargs["client"]
        deserialization_callback = kwargs["deserialization_callback"]
        return client, None, deserialization_callback


class ComputesOperations(_ComputesOperationsGenerated):
    """Customized ``ComputesOperations`` that tracks compute creation via the ``list`` API.

    The generated :meth:`begin_create_or_update` has two problems against the current service:

    * :meth:`_create_or_update_initial` rejects the ``202 Accepted`` the service returns for the async
      create with "Operation returned an invalid status 'Accepted'"; and
    * its poller follows the ``Azure-AsyncOperation`` header to
      ``.../locations/{location}/computeOperations/{operationId}``, which requires the
      ``Microsoft.CognitiveServices/locations/computeOperations/read`` permission. Many callers who
      are allowed to create a compute lack that permission, so the poll fails with
      ``AuthorizationFailed`` even though the create itself succeeded.

    This override keeps the generated method's public shape (overloads, api-version validation and
    ``continuation_token`` resume path) unchanged. It (1) accepts the ``202`` in
    :meth:`_create_or_update_initial` and (2) blocks on a :class:`_ComputeListPolling` poller that
    reads ``provisioningState`` from the ``list`` API. ``list`` is used rather than ``get`` because a
    ``GET`` on a just-created compute returns ``404 "Cluster not found"`` for an extended period while
    it provisions, whereas ``list`` reflects the compute's state from the moment the create is
    accepted. The poller only needs ``computes/read``, still blocks until a terminal state, and
    surfaces a genuine provisioning failure instead of masking it.
    """

    @api_version_validation(
        method_added_on="2026-03-15-preview",
        params_added_on={
            "2026-03-15-preview": [
                "api_version",
                "subscription_id",
                "resource_group_name",
                "account_name",
                "compute_name",
                "content_type",
                "accept",
            ]
        },
        api_versions_list=["2026-03-15-preview", "2026-05-15-preview"],
    )
    def _create_or_update_initial(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: Union[_models.Compute, JSON, IO[bytes]],
        **kwargs: Any,
    ) -> Iterator[bytes]:
        # Mirrors the generated ``_create_or_update_initial`` exactly, except it accepts ``202``. The
        # generated code only allows 200/201 and rejects the service's async 202 with
        # "Operation returned an invalid status 'Accepted'", failing a create the service accepted.
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: Any = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _content = None
        if isinstance(resource, (IOBase, bytes)):
            _content = resource
        else:
            _content = json.dumps(resource, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_computes_create_or_update_request(
            resource_group_name=resource_group_name,
            account_name=account_name,
            compute_name=compute_name,
            subscription_id=self._config.subscription_id,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.base_url", self._config.base_url, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _decompress = kwargs.pop("decompress", True)
        _stream = True
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 201, 202]:
            try:
                response.read()  # Load the body in memory and close the socket
            except (StreamConsumedError, StreamClosedError):
                pass
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = _failsafe_deserialize(_models.ErrorResponse, response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        response_headers = {}
        if response.status_code in [201, 202]:
            response_headers["Azure-AsyncOperation"] = self._deserialize(
                "str", response.headers.get("Azure-AsyncOperation")
            )
            response_headers["Retry-After"] = self._deserialize("int", response.headers.get("Retry-After"))

        deserialized = response.iter_bytes() if _decompress else response.iter_raw()

        if cls:
            return cls(pipeline_response, deserialized, response_headers)  # type: ignore

        return deserialized  # type: ignore

    @overload
    def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: _models.Compute,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.Compute]: ...
    @overload
    def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.Compute]: ...
    @overload
    def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.Compute]: ...

    @distributed_trace
    @api_version_validation(
        method_added_on="2026-03-15-preview",
        params_added_on={
            "2026-03-15-preview": [
                "api_version",
                "subscription_id",
                "resource_group_name",
                "account_name",
                "compute_name",
                "content_type",
                "accept",
            ]
        },
        api_versions_list=["2026-03-15-preview", "2026-05-15-preview"],
    )
    def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: Union[_models.Compute, JSON, IO[bytes]],
        **kwargs: Any,
    ) -> LROPoller[_models.Compute]:
        """Creates or updates a compute associated with the Cognitive Services account.

        This override accepts the service's ``202 Accepted`` and blocks until the compute reaches a
        terminal state, reading ``provisioningState`` from the ``list`` API rather than polling the
        operation-status endpoint (which requires ``computeOperations/read``). ``list`` is used because
        a ``GET`` on a just-created compute returns ``404 "Cluster not found"`` while it provisions. It
        raises on a genuine provisioning failure, so callers get correct results without needing the
        operation-status read permission.

        :param resource_group_name: The name of the resource group. The name is case insensitive.
         Required.
        :type resource_group_name: str
        :param account_name: The name of Cognitive Services account. Required.
        :type account_name: str
        :param compute_name: The name of the compute associated with the Cognitive Services Account.
         Required.
        :type compute_name: str
        :param resource: The compute properties. Is one of the following types: Compute, JSON,
         IO[bytes] Required.
        :type resource: ~azure.mgmt.cognitiveservices.models.Compute or JSON or IO[bytes]
        :return: An instance of LROPoller that returns Compute. The Compute is compatible with
         MutableMapping
        :rtype: ~azure.core.polling.LROPoller[~azure.mgmt.cognitiveservices.models.Compute]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: Any = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = self._create_or_update_initial(
                resource_group_name=resource_group_name,
                account_name=account_name,
                compute_name=compute_name,
                resource=resource,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs,
            )
            raw_result.http_response.read()  # type: ignore
            # A synchronous terminal failure (rare: the accepted body itself is already Failed/Canceled)
            # would otherwise slip through to a poller that would just keep listing; surface the
            # resource's own error detail immediately instead.
            try:
                initial_body = raw_result.http_response.json()
            except Exception:  # pylint: disable=broad-except
                initial_body = None
            if isinstance(initial_body, MutableMapping) and _state_of(initial_body) in _TERMINAL_FAILED_STATES:
                raise _provisioning_error(initial_body)
        else:
            # Opaque-token contract: the token is the source of truth for which operation to resume, so
            # decode the polling scope from it (raising on a malformed token) rather than trusting the
            # method arguments, and do not re-issue the create.
            resource_group_name, account_name, compute_name = _decode_continuation_token(cont_token)
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response = pipeline_response.http_response
            deserialized = _deserialize(_models.Compute, response.json())
            if cls:
                return cls(pipeline_response, deserialized, {})  # type: ignore
            return deserialized

        if polling is True:
            polling_method: PollingMethod = cast(
                PollingMethod,
                _ComputeListPolling(self, resource_group_name, account_name, compute_name, lro_delay, cls),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller[_models.Compute].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller[_models.Compute](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )


__all__: list[str] = [
    "ComputesOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
