# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, IO, Union

from azure.core.polling import LROPoller
from azure.core.polling.base_polling import (
    BadResponse,
    LROBasePolling,
    OperationResourcePolling,
    _as_json,
    _is_empty,
)

from .. import models as _models
from ._operations import KnowledgeBasesOperations as _GeneratedKnowledgeBasesOperations


class _ProvisioningStatePolling(OperationResourcePolling):
    """LRO polling that terminates on ``provisioningState`` instead of ``status``.

    The Bookshelf create/update LRO returns the ``KnowledgeBase`` resource as the
    ``Operation-Location`` body. That body carries two status-like fields:

    * ``status`` -> the *indexing* lifecycle (``IndexingStatus``); for a freshly
      created KB this stays ``NotStarted`` until indexing is separately started.
    * ``provisioningState`` -> the create/update lifecycle (``Accepted`` ->
      ``Succeeded``).

    Azure Core's default poller keys off ``status``, which never reaches a
    create-terminal value during provisioning, so ``begin_create_or_update(...)``
    would poll forever even though the resource provisions successfully. This
    override reads ``provisioningState`` (falling back to ``status`` only when
    ``provisioningState`` is absent).
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


class _CreateOrUpdatePolling(LROBasePolling):
    """Create/update poller that tolerates a synchronous completion.

    ``begin_create_or_update`` is an upsert. Creating a new KnowledgeBase returns
    ``201`` + ``Operation-Location`` -- a genuine LRO polled on
    ``provisioningState`` via :class:`_ProvisioningStatePolling`. Updating an
    *existing* KnowledgeBase can instead complete synchronously with ``200`` and
    *no* ``Operation-Location`` header, and the default poller raises
    ``BadResponse: Unable to find status link for polling`` in that case. This
    poller treats a missing status link as an immediate success and returns the
    resource from the initial response.
    """

    _synchronous: bool = False

    def initialize(self, client: Any, initial_response: Any, deserialization_callback: Any) -> None:
        headers = initial_response.http_response.headers
        if not (headers.get("Operation-Location") or headers.get("operation-location")):
            # Synchronous completion: there is no long-running operation to poll.
            self._client = client
            self._pipeline_response = initial_response
            self._initial_response = initial_response
            self._deserialization_callback = deserialization_callback
            # A (non-polling) operation instance keeps status()/resource() happy.
            self._operation = _ProvisioningStatePolling()
            self._status = "Succeeded"
            self._synchronous = True
            return
        self._synchronous = False
        super().initialize(client, initial_response, deserialization_callback)

    def run(self) -> None:
        if getattr(self, "_synchronous", False):
            return
        super().run()


class KnowledgeBasesOperations(_GeneratedKnowledgeBasesOperations):
    """KnowledgeBases operations with a corrected create/update LRO poller.

    See :class:`_ProvisioningStatePolling` and :class:`_CreateOrUpdatePolling`
    for why the default poller is replaced.
    """

    def begin_create_or_update(  # type: ignore[override]
        self,
        knowledge_base_name: str,
        resource: Union[_models.KnowledgeBase, "dict[str, Any]", IO[bytes]],
        **kwargs: Any,
    ) -> LROPoller[_models.KnowledgeBase]:
        # Only override the default poller; honor an explicitly supplied
        # ``polling`` value (``False`` or a custom ``PollingMethod``).
        if kwargs.get("polling", True) is True:
            lro_delay = kwargs.get("polling_interval", self._config.polling_interval)
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            kwargs["polling"] = _CreateOrUpdatePolling(
                lro_delay,
                lro_algorithms=[_ProvisioningStatePolling()],
                path_format_arguments=path_format_arguments,
            )
        return super().begin_create_or_update(knowledge_base_name, resource, **kwargs)  # type: ignore[arg-type]


__all__: list[str] = [
    "KnowledgeBasesOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
