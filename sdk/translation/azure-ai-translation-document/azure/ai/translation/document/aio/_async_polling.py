# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Tuple, TypeVar
from azure.core.polling import AsyncLROPoller
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from .._generated.models import TranslationStatus
from .._models import JobStatusResult

PollingReturnType = TypeVar("PollingReturnType")


class AsyncDocumentTranslationPoller(AsyncLROPoller[PollingReturnType]):
    """An async custom poller implementation for Document Translation.
    """

    @property
    def id(self) -> str:
        """The ID for the translation job

        :return: str
        """
        if self._polling_method._current_body:
            return self._polling_method._current_body.id
        return self._polling_method._get_id_from_headers()

    @property
    def details(self) -> JobStatusResult:
        """The details for the translation job

        :return: JobStatusResult
        """
        if not self._polling_method._current_body:
            return None
        return JobStatusResult._from_generated(self._polling_method._current_body)

    @classmethod
    def from_continuation_token(
            cls,
            polling_method: "AsyncDocumentTranslationLROPollingMethod",
            continuation_token: str,
            **kwargs: Any
    ) -> "AsyncDocumentTranslationPoller":

        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )

        return cls(client, initial_response, deserialization_callback, polling_method)


class AsyncDocumentTranslationLROPollingMethod(AsyncLROBasePolling):
    """A custom polling method implementation for Document Translation.
    """

    def __init__(self, *args, **kwargs):
        self._cont_token_response = kwargs.pop("cont_token_response")
        super(AsyncDocumentTranslationLROPollingMethod, self).__init__(*args, **kwargs)

    @property
    def _current_body(self) -> TranslationStatus:
        from .._generated.models import TranslationStatus
        return TranslationStatus.deserialize(self._pipeline_response)

    def _get_id_from_headers(self) -> str:
        return self._pipeline_response.http_response.headers["Operation-Location"].split("/batches/")[1]

    def get_continuation_token(self) -> str:
        if self._current_body:
            return self._current_body.id
        return self._get_id_from_headers()

    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:
        try:
            client = kwargs["client"]
        except KeyError:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token")

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token")

        return client, self._cont_token_response, deserialization_callback
