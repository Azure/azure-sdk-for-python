# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

import json
import datetime
from typing import TypeVar, Any, Mapping
from typing_extensions import Protocol, runtime_checkable
from azure.core.polling import AsyncLROPoller, AsyncPollingMethod
from .._polling import parse_operation_id

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)


@runtime_checkable
class AsyncDocumentModelAdministrationLROPoller(Protocol[PollingReturnType_co]):  # pylint: disable=name-too-long
    """Implements a protocol followed by returned poller objects."""

    @property
    def details(  # pylint: disable=unused-argument
        self,
    ) -> Mapping[str, Any]:
        ...

    def polling_method(
        self,
    ) -> AsyncPollingMethod[PollingReturnType_co]:
        ...

    def continuation_token(self) -> str:
        ...

    def status(self) -> str:
        ...

    async def result(  # pylint: disable=unused-argument
        self,
    ) -> PollingReturnType_co:
        ...

    async def wait(self) -> None:  # pylint: disable=unused-argument
        ...

    def done(self) -> bool:
        ...


class AsyncDocumentModelAdministrationClientLROPoller(AsyncLROPoller[PollingReturnType_co]):  # pylint: disable=name-too-long
    """Custom poller for model build operations. Call `result()` on the poller to return
    a :class:`~azure.ai.formrecognizer.DocumentModelInfo`.

    .. versionadded:: 2022-08-31
        The *AsyncDocumentModelAdministrationClientLROPoller* poller object
    """

    @property
    def _current_body(self):
        body = self.polling_method()._pipeline_response.http_response.text()
        if body:
            return json.loads(body)
        return {}

    @property
    def details(self) -> Mapping[str, Any]:
        """Returns metadata associated with the long-running operation.

        :return: Returns metadata associated with the long-running operation.
        :rtype: Mapping[str, Any]
        """
        created_on = self._current_body.get("createdDateTime", None)
        if created_on:
            created_on = datetime.datetime.strptime(created_on, "%Y-%m-%dT%H:%M:%SZ")
        last_updated_on = self._current_body.get("lastUpdatedDateTime", None)
        if last_updated_on:
            last_updated_on = datetime.datetime.strptime(last_updated_on, "%Y-%m-%dT%H:%M:%SZ")
        return {
            "operation_id": parse_operation_id(
                self.polling_method()._initial_response.http_response.headers["Operation-Location"]  # type: ignore
            ),
            "operation_kind": self._current_body.get("kind", None),
            "percent_completed": self._current_body.get("percentCompleted", 0),
            "resource_location_url": self._current_body.get("resourceLocation", None),
            "created_on": created_on,
            "last_updated_on": last_updated_on,
        }

    @classmethod
    def from_continuation_token(
        cls, polling_method: AsyncPollingMethod[PollingReturnType_co], continuation_token: str, **kwargs: Any
    ) -> "AsyncDocumentModelAdministrationClientLROPoller":
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)  # type: ignore
