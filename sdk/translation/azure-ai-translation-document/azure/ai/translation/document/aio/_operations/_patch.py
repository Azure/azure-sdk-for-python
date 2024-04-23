# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from typing import Any, IO, List, Optional, Union, cast
from azure.core.polling import AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from ..._model_base import SdkJSONEncoder, _deserialize
from ._operations import (
    DocumentTranslationClientOperationsMixin as GeneratedDocumentTranslationClientOperationsMixin,
    JSON,
    ClsType,
)
from ...aio._patch import AsyncDocumentTranslationLROPoller
from ... import models as _models

class DocumentTranslationClientOperationsMixin(GeneratedDocumentTranslationClientOperationsMixin):

    @distributed_trace
    async def begin_start_translation(
        self, body: Union[_models.StartTranslationDetails, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[_models.TranslationStatus]:
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.TranslationStatus] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._start_translation_initial(  
                body=body, content_type=content_type, cls=lambda x, y, z: x, headers=_headers, params=_params, **kwargs
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )

            deserialized = _deserialize(_models.TranslationStatus, response.json())
            if cls:
                return cls(pipeline_response, deserialized, response_headers)  
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod, AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncDocumentTranslationLROPoller[_models.TranslationStatus].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncDocumentTranslationLROPoller[_models.TranslationStatus](
            self._client, raw_result, get_long_running_output, polling_method  
        )

__all__: List[str] = ["DocumentTranslationClientOperationsMixin"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
