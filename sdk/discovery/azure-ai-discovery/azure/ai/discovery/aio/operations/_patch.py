# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, IO, Union

from azure.core.polling import AsyncLROPoller
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling.base_polling import (
    BadResponse,
    OperationResourcePolling,
    _as_json,
    _is_empty,
)

from ... import models as _models
from ._operations import KnowledgeBasesOperations as _GeneratedKnowledgeBasesOperations


class _ProvisioningStatePolling(OperationResourcePolling):
    """LRO polling that terminates on ``provisioningState`` instead of ``status``.

    See the sync ``operations/_patch.py`` for the full rationale: the Bookshelf
    create/update LRO returns the ``KnowledgeBase`` resource, whose ``status``
    field is the *indexing* lifecycle (``NotStarted`` for a new KB and never
    create-terminal). The correct create/update completion signal is
    ``provisioningState`` (``Accepted`` -> ``Succeeded``). The polling algorithm
    is transport-agnostic, so the same class is reused by the async poller.
    """

    def get_status(self, pipeline_response: Any) -> str:
        response = pipeline_response.http_response
        if _is_empty(response):
            raise BadResponse("The response from long running operation does not contain a body.")
        body = _as_json(response)
        status = body.get("provisioningState") or body.get("status")
        if not status:
            raise BadResponse("No provisioningState or status found in long running operation response.")
        return status


class _AsyncCreateOrUpdatePolling(AsyncLROBasePolling):
    """Async create/update poller that tolerates a synchronous completion.

    See the sync ``operations/_patch.py`` for the rationale: creating a new KB is
    an LRO (``201`` + ``Operation-Location``), but updating an existing KB can
    complete synchronously (``200`` with no ``Operation-Location``), which the
    default poller rejects with ``BadResponse: Unable to find status link for
    polling``. This poller treats a missing status link as immediate success.
    """

    _synchronous: bool = False

    def initialize(self, client: Any, initial_response: Any, deserialization_callback: Any) -> None:
        headers = initial_response.http_response.headers
        if not (headers.get("Operation-Location") or headers.get("operation-location")):
            self._client = client
            self._pipeline_response = initial_response
            self._initial_response = initial_response
            self._deserialization_callback = deserialization_callback
            self._operation = _ProvisioningStatePolling()
            self._status = "Succeeded"
            self._synchronous = True
            return
        self._synchronous = False
        super().initialize(client, initial_response, deserialization_callback)

    async def run(self) -> None:
        if getattr(self, "_synchronous", False):
            return
        await super().run()


class KnowledgeBasesOperations(_GeneratedKnowledgeBasesOperations):
    """Async KnowledgeBases operations with a corrected create/update LRO poller."""

    async def begin_create_or_update(  # type: ignore[override]
        self,
        knowledge_base_name: str,
        resource: Union[_models.KnowledgeBase, "dict[str, Any]", IO[bytes]],
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.KnowledgeBase]:
        # Only override the default poller; honor an explicitly supplied
        # ``polling`` value (``False`` or a custom ``AsyncPollingMethod``).
        if kwargs.get("polling", True) is True:
            lro_delay = kwargs.get("polling_interval", self._config.polling_interval)
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            kwargs["polling"] = _AsyncCreateOrUpdatePolling(
                lro_delay,
                lro_algorithms=[_ProvisioningStatePolling()],
                path_format_arguments=path_format_arguments,
            )
        return await super().begin_create_or_update(knowledge_base_name, resource, **kwargs)  # type: ignore[arg-type]


__all__: list[str] = [
    "KnowledgeBasesOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
