# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio  # pylint: disable=do-not-import-asyncio
import time
from typing import IO, Any, Optional, Union, cast, overload

from azure.core.exceptions import HttpResponseError
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ... import models as _models, types as _types
from ..._utils.model_base import _deserialize
from ..._validation import api_version_validation
from ...operations._patch import (
    _CANCELED_STATES,
    _TERMINAL_FAILED_STATES,
    _TERMINAL_SUCCESS_STATES,
    _decode_continuation_token,
    _encode_continuation_token,
    _provisioning_error,
    _state_of,
)
from ._operations import ComputesOperations as _ComputesOperationsGenerated


class _AsyncComputeListPolling(AsyncPollingMethod):
    """Poll compute provisioning through list(), avoiding the permission-gated status endpoint."""

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

    def initialize(self, client: Any, initial_response: Any, deserialization_callback: Any) -> None:
        pass

    async def _current_compute(self) -> Optional[_models.Compute]:
        async for compute in self._operations.list(self._resource_group_name, self._account_name):
            if getattr(compute, "name", None) == self._compute_name:
                return compute
        return None

    async def run(self) -> None:
        while not self.finished():
            compute = await self._current_compute()
            if compute is None:
                if self._first_missing_at is None:
                    self._first_missing_at = time.monotonic()
                elif time.monotonic() - self._first_missing_at > self._NOT_FOUND_GRACE_SECONDS:
                    raise HttpResponseError(
                        message=f"Compute '{self._compute_name}' did not appear in the account's compute list."
                    )
            else:
                self._first_missing_at = None
                self._resource = compute
                state = _state_of(compute)
                if state in _TERMINAL_SUCCESS_STATES:
                    self._status = "Succeeded"
                elif state in _TERMINAL_FAILED_STATES:
                    self._status = "Canceled" if state in _CANCELED_STATES else "Failed"
                    raise _provisioning_error(compute)
            if not self.finished():
                await asyncio.sleep(self._interval)

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._status in ("Succeeded", "Failed", "Canceled")

    def resource(self) -> Optional[_models.Compute]:
        if self._resource is not None and self._cls is not None:
            return self._cls(None, self._resource, {})
        return self._resource

    def get_continuation_token(self) -> str:
        return _encode_continuation_token(self._resource_group_name, self._account_name, self._compute_name)

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs: Any):
        _decode_continuation_token(continuation_token)
        return kwargs["client"], None, kwargs["deserialization_callback"]


class ComputesOperations(_ComputesOperationsGenerated):
    """Computes operations that poll provisioning through the account's compute list."""

    @overload
    async def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: _models.Compute,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.Compute]: ...

    @overload
    async def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: _types.Compute,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.Compute]: ...

    @overload
    async def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.Compute]: ...

    @distributed_trace_async
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
            ]
        },
        api_versions_list=["2026-03-15-preview", "2026-05-15-preview", "2026-07-15-preview"],
    )
    async def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: Union[_models.Compute, _types.Compute, IO[bytes]],
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.Compute]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}
        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: Any = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        continuation_token: Optional[str] = kwargs.pop("continuation_token", None)
        if continuation_token is None:
            raw_result = await self._create_or_update_initial(
                resource_group_name=resource_group_name,
                account_name=account_name,
                compute_name=compute_name,
                resource=resource,
                content_type=content_type,
                cls=lambda response, value, headers: response,
                headers=_headers,
                params=_params,
                **kwargs,
            )
            await raw_result.http_response.read()  # type: ignore
            try:
                initial_body = raw_result.http_response.json()
            except Exception:  # pylint: disable=broad-except
                initial_body = None
            if isinstance(initial_body, dict) and _state_of(initial_body) in _TERMINAL_FAILED_STATES:
                raise _provisioning_error(initial_body)
        else:
            resource_group_name, account_name, compute_name = _decode_continuation_token(continuation_token)
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            deserialized = _deserialize(_models.Compute, pipeline_response.http_response.json())
            if cls:
                return cls(pipeline_response, deserialized, {})  # type: ignore
            return deserialized

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                _AsyncComputeListPolling(self, resource_group_name, account_name, compute_name, lro_delay, cls),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if continuation_token:
            return AsyncLROPoller[_models.Compute].from_continuation_token(
                polling_method=polling_method,
                continuation_token=continuation_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncLROPoller[_models.Compute](
            self._client, raw_result, get_long_running_output, polling_method  # type: ignore
        )


__all__: list[str] = ["ComputesOperations"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
