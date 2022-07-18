# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import base64
import functools
import json
from typing import Mapping, Any, TypeVar, Generator, Awaitable
from typing_extensions import Protocol, runtime_checkable
from azure.core.exceptions import HttpResponseError
from azure.core.polling import AsyncLROPoller, AsyncPollingMethod
from azure.core.polling.base_polling import OperationFailed, BadStatus
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from .._lro import TextAnalyticsOperationResourcePolling
from .._generated.v2022_05_01.models import JobState


_FINISHED = frozenset(["succeeded", "cancelled", "failed", "partiallycompleted", "partiallysucceeded"])
_FAILED = frozenset(["failed"])
_SUCCEEDED = frozenset(["succeeded", "partiallycompleted", "partiallysucceeded"])

PollingReturnType = TypeVar("PollingReturnType")


@runtime_checkable
class AsyncTextAnalysisLROPoller(Protocol[PollingReturnType], Awaitable):
    """Implements a protocol which returned poller objects are consistent with.
    """

    @property
    def details(self) -> Mapping[str, Any]:
        ...

    def polling_method(self) -> AsyncPollingMethod[PollingReturnType]:
        ...

    def continuation_token(self) -> str:
        ...

    def status(self) -> str:
        ...

    async def result(self) -> PollingReturnType:
        ...

    async def wait(self) -> None:
        ...

    def done(self) -> bool:
        ...

    def __await__(self) -> Generator[Any, None, PollingReturnType]:
        ...


class TextAnalyticsAsyncLROPollingMethod(AsyncLROBasePolling):
    def finished(self):
        """Is this polling finished?
        :rtype: bool
        """
        return TextAnalyticsAsyncLROPollingMethod._finished(self.status())

    @staticmethod
    def _finished(status):
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status):
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    @staticmethod
    def _raise_if_bad_http_status_and_method(response):
        """Check response status code is valid.

        Must be 200, 201, 202, or 204.

        :raises: BadStatus if invalid status.
        """
        code = response.status_code
        if code in {200, 201, 202, 204}:
            return
        raise BadStatus(
            "Invalid return status {!r} for {!r} operation".format(
                code, response.request.method
            )
        )

    async def _poll(self):  # pylint:disable=invalid-overridden-method
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """
        while not self.finished():
            await self._delay()
            await self.update_status()

        if TextAnalyticsAsyncLROPollingMethod._failed(self.status()):
            try:
                job = json.loads(self._pipeline_response.http_response.text())
                error_message = ""
                for err in job["errors"]:
                    error_message += "({}) {}".format(err["code"], err["message"])
                raise HttpResponseError(message=error_message, response=self._pipeline_response.http_response)
            except KeyError as e:
                raise OperationFailed("Operation failed or canceled") from e

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = await self.request_status(final_get_url)
            TextAnalyticsAsyncLROPollingMethod._raise_if_bad_http_status_and_method(
                self._pipeline_response.http_response
            )


class AsyncAnalyzeHealthcareEntitiesLROPollingMethod(
    TextAnalyticsAsyncLROPollingMethod
):
    def __init__(self, *args, **kwargs):
        self._text_analytics_client = kwargs.pop("text_analytics_client")
        self._doc_id_order = kwargs.pop("doc_id_order", None)
        self._show_stats = kwargs.pop("show_stats", None)
        super().__init__(
            *args, **kwargs
        )

    @property
    def _current_body(self):
        return JobState.deserialize(self._pipeline_response)

    @property
    def created_on(self):
        if not self._current_body:
            return None
        return self._current_body.created_date_time

    @property
    def expires_on(self):
        if not self._current_body:
            return None
        return self._current_body.expiration_date_time

    @property
    def last_modified_on(self):
        if not self._current_body:
            return None
        return self._current_body.last_update_date_time

    @property
    def id(self):
        if not self._current_body:
            return None
        return self._current_body.job_id

    @property
    def display_name(self):
        if not self._current_body:
            return None
        return self._current_body.display_name

    def get_continuation_token(self):
        # type() -> str
        import pickle
        self._initial_response.context.options["doc_id_order"] = self._doc_id_order
        self._initial_response.context.options["show_stats"] = self._show_stats
        return base64.b64encode(pickle.dumps(self._initial_response)).decode('ascii')


class AsyncAnalyzeHealthcareEntitiesLROPoller(AsyncLROPoller[PollingReturnType]):
    def polling_method(self) -> AsyncAnalyzeHealthcareEntitiesLROPollingMethod:  # type: ignore
        """Return the polling method associated to this poller."""
        return self._polling_method  # type: ignore

    @property
    def details(self) -> Mapping[str, Any]:
        return {
            "id": self.polling_method().id,
            "created_on": self.polling_method().created_on,
            "expires_on": self.polling_method().expires_on,
            "display_name": self.polling_method().display_name,
            "last_modified_on": self.polling_method().last_modified_on,
        }

    def __getattr__(self, item):
        attrs = [
            "created_on",
            "expires_on",
            "display_name",
            "last_modified_on",
            "id"
        ]
        if item in attrs:
            return self.details[item]
        return self.__getattribute__(item)

    @classmethod
    def from_continuation_token(  # type: ignore
        cls,
        polling_method: AsyncAnalyzeHealthcareEntitiesLROPollingMethod,
        continuation_token: str,
        **kwargs: Any
    ) -> "AsyncAnalyzeHealthcareEntitiesLROPoller":
        """
        :meta private:
        """
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        polling_method._lro_algorithms = [  # pylint: disable=protected-access
            TextAnalyticsOperationResourcePolling(
                show_stats=initial_response.context.options["show_stats"]
            )
        ]
        return cls(
            client,
            initial_response,
            functools.partial(deserialization_callback, initial_response),
            polling_method  # type: ignore
        )

    async def cancel(self, **kwargs) -> "AsyncLROPoller[None]":  # type: ignore
        """Cancel the operation currently being polled.

        :keyword int polling_interval: The polling interval to use to poll the cancellation status.
            The default value is 5 seconds.
        :return: Returns an instance of an AsyncLROPoller that returns None.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError: When the operation has already reached a terminal state.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_analyze_healthcare_entities_with_cancellation_async.py
                :start-after: [START analyze_healthcare_entities_with_cancellation_async]
                :end-before: [END analyze_healthcare_entities_with_cancellation_async]
                :language: python
                :dedent: 4
                :caption: Cancel an existing health operation.
        """
        polling_interval = kwargs.pop("polling_interval", 5)
        await self.polling_method().update_status()

        try:
            client = getattr(
                self._polling_method, "_text_analytics_client"
            )
            try:
                return await client.begin_cancel_health_job(
                    self.id, polling=TextAnalyticsAsyncLROPollingMethod(timeout=polling_interval)
                )
            except ValueError:  # language API compat
                return await client.begin_analyze_text_cancel_job(
                    self.id, polling=TextAnalyticsAsyncLROPollingMethod(timeout=polling_interval)
                )
        except HttpResponseError as error:
            from .._response_handlers import process_http_response_error

            process_http_response_error(error)


class AsyncAnalyzeActionsLROPollingMethod(TextAnalyticsAsyncLROPollingMethod):
    def __init__(self, *args, **kwargs):
        self._doc_id_order = kwargs.pop("doc_id_order", None)
        self._task_id_order = kwargs.pop("task_id_order", None)
        self._show_stats = kwargs.pop("show_stats", None)
        super().__init__(*args, **kwargs)

    @property
    def _current_body(self):
        return JobState.deserialize(self._pipeline_response)

    @property
    def created_on(self):
        if not self._current_body:
            return None
        return self._current_body.created_date_time

    @property
    def display_name(self):
        if not self._current_body:
            return None
        return self._current_body.display_name

    @property
    def expires_on(self):
        if not self._current_body:
            return None
        return self._current_body.expiration_date_time

    @property
    def actions_failed_count(self):
        if not self._current_body:
            return None
        return self._current_body.additional_properties.get("tasks", {}).get("failed", None)

    @property
    def actions_in_progress_count(self):
        if not self._current_body:
            return None
        return self._current_body.additional_properties.get("tasks", {}).get("inProgress", None)

    @property
    def actions_succeeded_count(self):
        if not self._current_body:
            return None
        return self._current_body.additional_properties.get("tasks", {}).get("completed", None)

    @property
    def last_modified_on(self):
        if not self._current_body:
            return None
        return self._current_body.last_update_date_time

    @property
    def total_actions_count(self):
        if not self._current_body:
            return None
        return self._current_body.additional_properties.get("tasks", {}).get("total", None)

    @property
    def id(self):
        if not self._current_body:
            return None
        return self._current_body.job_id

    def get_continuation_token(self):
        # type: () -> str
        import pickle
        self._initial_response.context.options["doc_id_order"] = self._doc_id_order
        self._initial_response.context.options["task_id_order"] = self._task_id_order
        self._initial_response.context.options["show_stats"] = self._show_stats
        return base64.b64encode(pickle.dumps(self._initial_response)).decode('ascii')


class AsyncAnalyzeActionsLROPoller(AsyncLROPoller[PollingReturnType]):
    def polling_method(self) -> AsyncAnalyzeActionsLROPollingMethod:  # type: ignore
        """Return the polling method associated to this poller."""
        return self._polling_method  # type: ignore

    @property
    def details(self) -> Mapping[str, Any]:
        return {
            "id": self.polling_method().id,
            "created_on": self.polling_method().created_on,
            "expires_on": self.polling_method().expires_on,
            "display_name": self.polling_method().display_name,
            "last_modified_on": self.polling_method().last_modified_on,
            "actions_failed_count": self.polling_method().actions_failed_count,
            "actions_in_progress_count": self.polling_method().actions_in_progress_count,
            "actions_succeeded_count": self.polling_method().actions_succeeded_count,
            "total_actions_count": self.polling_method().total_actions_count,
        }

    def __getattr__(self, item):
        attrs = [
            "created_on",
            "expires_on",
            "display_name",
            "actions_failed_count",
            "actions_in_progress_count",
            "actions_succeeded_count",
            "total_actions_count",
            "last_modified_on",
            "id"
        ]
        if item in attrs:
            return self.details[item]
        return self.__getattribute__(item)

    @classmethod
    def from_continuation_token(  # type: ignore
        cls,
        polling_method: AsyncAnalyzeActionsLROPollingMethod,
        continuation_token: str,
        **kwargs: Any
    ) -> "AsyncAnalyzeActionsLROPoller":  # type: ignore
        """
        :meta private:
        """
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        polling_method._lro_algorithms = [  # pylint: disable=protected-access
            TextAnalyticsOperationResourcePolling(
                show_stats=initial_response.context.options["show_stats"]
            )
        ]
        return cls(
            client,
            initial_response,
            functools.partial(deserialization_callback, initial_response),
            polling_method  # type: ignore
        )
