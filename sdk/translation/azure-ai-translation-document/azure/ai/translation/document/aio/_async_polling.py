# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Tuple, TypeVar
from azure.core.polling import AsyncLROPoller
from azure.core.polling.base_polling import (
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from .._generated.models import TranslationStatus as _TranslationStatus
from .._models import TranslationStatus

PollingReturnType = TypeVar("PollingReturnType")
_FINISHED = frozenset(["succeeded", "cancelled", "cancelling", "failed"])
_FAILED = frozenset(["validationfailed"])


class AsyncDocumentTranslationLROPoller(AsyncLROPoller[PollingReturnType]):
    """An async custom poller implementation for Document Translation. Call `result()` on the poller to return
    a pageable of :class:`~azure.ai.translation.document.DocumentStatus`."""

    @property
    def id(self) -> str:
        """The ID for the translation operation

        :rtype: str
        """
        if self._polling_method._current_body:  # type: ignore # pylint: disable=protected-access
            return (
                self._polling_method._current_body.id  # type: ignore # pylint: disable=protected-access
            )
        return (
            self._polling_method._get_id_from_headers()  # type: ignore # pylint: disable=protected-access
        )

    @property
    def details(self) -> TranslationStatus:
        """The details for the translation operation

        :rtype: ~azure.ai.translation.document.TranslationStatus
        """
        if self._polling_method._current_body:  # type: ignore # pylint: disable=protected-access
            return TranslationStatus._from_generated(  # pylint: disable=protected-access
                self._polling_method._current_body  # type: ignore # pylint: disable=protected-access
            )
        return TranslationStatus(id=self._polling_method._get_id_from_headers())  # type: ignore # pylint: disable=protected-access

    @classmethod
    def from_continuation_token(  # type: ignore
        cls,
        polling_method: "AsyncDocumentTranslationLROPollingMethod",
        continuation_token: str,
        **kwargs: Any
    ) -> "AsyncDocumentTranslationLROPoller":
        """
        :meta private:
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)  # type: ignore


class AsyncDocumentTranslationLROPollingMethod(AsyncLROBasePolling):
    """A custom polling method implementation for Document Translation."""

    def __init__(self, *args, **kwargs):
        self._cont_token_response = kwargs.pop("cont_token_response")
        super().__init__(*args, **kwargs)

    @property
    def _current_body(self) -> _TranslationStatus:
        return _TranslationStatus.deserialize(self._pipeline_response)

    def _get_id_from_headers(self) -> str:
        return self._initial_response.http_response.headers[
            "Operation-Location"
        ].split("/batches/")[1]

    def finished(self) -> bool:
        """Is this polling finished?
        :rtype: bool
        """
        return self._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    def get_continuation_token(self) -> str:
        if self._current_body:
            return self._current_body.id
        return self._get_id_from_headers()

    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:  # type: ignore
        try:
            client = kwargs["client"]
        except KeyError:
            raise ValueError(
                "Need kwarg 'client' to be recreated from continuation_token"
            )

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError(
                "Need kwarg 'deserialization_callback' to be recreated from continuation_token"
            )

        return client, self._cont_token_response, deserialization_callback

    async def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            await self._delay()
            await self.update_status()

        if self._failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = await self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)
