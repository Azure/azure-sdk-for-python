# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Optional, Union, cast

from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from ._operations import _AnalyzeDocumentsClientOperationsMixin as GeneratedAnalyzeDocumentsClientOperationsMixin
from .._lro import AnalyzeDocumentsLROPollingMethod


class _AnalyzeDocumentsClientOperationsMixin(GeneratedAnalyzeDocumentsClientOperationsMixin):
    @distributed_trace
    def begin_submit_job(
        self,
        body: Any,
        **kwargs: Any
    ) -> LROPoller[None]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token = kwargs.pop("continuation_token", None)

        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            if cls:
                return cls(pipeline_response, None, {})
            return None

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method = cast(
                PollingMethod,
                AnalyzeDocumentsLROPollingMethod(
                    lro_delay,
                    path_format_arguments=path_format_arguments,
                    **kwargs
                ),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling

        if cont_token is not None:
            return LROPoller[None].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        raw_result = self._submit_job_initial(
            body=body,
            content_type=content_type,
            cls=lambda x, y, z: x,
            headers=_headers,
            params=_params,
            **kwargs
        )
        raw_result.http_response.read()  # type: ignore[attr-defined]

        return LROPoller[None](self._client, raw_result, get_long_running_output, polling_method)

    @distributed_trace
    def begin_cancel_job(self, job_id: str, **kwargs: Any) -> LROPoller[None]:
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token = kwargs.pop("continuation_token", None)

        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            if cls:
                return cls(pipeline_response, None, {})
            return None

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method = cast(
                PollingMethod,
                AnalyzeDocumentsLROPollingMethod(
                    lro_delay,
                    path_format_arguments=path_format_arguments,
                    **kwargs
                ),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling

        if cont_token is not None:
            return LROPoller[None].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )

        raw_result = self._cancel_job_initial(
            job_id=job_id,
            cls=lambda x, y, z: x,
            headers=_headers,
            params=_params,
            **kwargs
        )
        raw_result.http_response.read()  # type: ignore[attr-defined]

        return LROPoller[None](self._client, raw_result, get_long_running_output, polling_method)


__all__: list[str] = [
    "_AnalyzeDocumentsClientOperationsMixin",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
