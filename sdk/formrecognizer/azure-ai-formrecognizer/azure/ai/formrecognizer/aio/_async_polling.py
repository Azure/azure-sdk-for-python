# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

import json
import datetime
from typing import TypeVar, Any
from azure.core.polling import AsyncLROPoller, AsyncPollingMethod
from .._polling import parse_operation_id

PollingReturnType = TypeVar("PollingReturnType")


class AsyncDocumentModelAdministrationLROPoller(AsyncLROPoller[PollingReturnType]):
    """Custom poller for model build operations. Call `result()` on the poller to return
    a :class:`~azure.ai.formrecognizer.DocumentModelInfo`.

    .. versionadded:: 2021-09-30-preview
        The *AsyncDocumentModelAdministrationLROPoller* poller object
    """

    @property
    def _current_body(self):
        body = self.polling_method()._pipeline_response.http_response.text()
        if body:
            return json.loads(body)
        return {}

    @property
    def operation_id(self):
        # type: () -> str
        """The operation ID of the model operation.

        :rtype: str
        """
        return parse_operation_id(
            self.polling_method()._initial_response.http_response.headers["Operation-Location"]  # type: ignore
        )

    @property
    def operation_kind(self):
        # type: () -> str
        """The model operation kind. For example, 'documentModelBuild', 'documentModelCompose',
        'documentModelCopyTo'.

        :rtype: str
        """
        return self._current_body.get("kind", None)

    @property
    def percent_completed(self):
        # type: () -> int
        """Operation progress (0-100).

        :rtype: int
        """
        percent_completed = self._current_body.get("percentCompleted", None)
        return 0 if percent_completed is None else percent_completed

    @property
    def resource_location_url(self):
        # type: () -> str
        """URL of the resource targeted by this operation.

        :rtype: str
        """
        return self._current_body.get("resourceLocation", None)

    @property
    def created_on(self):
        # type: () -> datetime.datetime
        """Date and time (UTC) when the operation was created.

        :rtype: ~datetime.datetime
        """
        created_on = self._current_body.get("createdDateTime", None)
        if created_on:
            return datetime.datetime.strptime(created_on, "%Y-%m-%dT%H:%M:%SZ")
        return created_on

    @property
    def last_updated_on(self):
        # type: () -> datetime.datetime
        """Date and time (UTC) when the operation was last updated.

        :rtype: ~datetime.datetime
        """
        last_updated_on = self._current_body.get("lastUpdatedDateTime", None)
        if last_updated_on:
            return datetime.datetime.strptime(last_updated_on, "%Y-%m-%dT%H:%M:%SZ")
        return last_updated_on

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: AsyncPollingMethod[PollingReturnType],
        continuation_token: str,
        **kwargs: Any
    ) -> "AsyncDocumentModelAdministrationLROPoller":
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)  # type: ignore
