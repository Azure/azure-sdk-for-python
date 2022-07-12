# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
import base64
import functools
import json
from typing import Optional, Any, MutableMapping
from azure.core.exceptions import HttpResponseError
from azure.core.polling import AsyncLROPoller
from azure.core.polling.base_polling import OperationFailed, BadStatus
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling._async_poller import PollingReturnType
from .._lro import TextAnalyticsOperationResourcePolling
from .._generated.v2022_05_01.models import JobState


_FINISHED = frozenset(["succeeded", "cancelled", "failed", "partiallycompleted", "partiallysucceeded"])
_FAILED = frozenset(["failed"])
_SUCCEEDED = frozenset(["succeeded", "partiallycompleted", "partiallysucceeded"])


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
    def created_on(self) -> datetime.datetime:
        """When your healthcare entities job was created

        :return: When your healthcare entities job was created
        :rtype: ~datetime.datetime
        """
        return self.polling_method().created_on

    @property
    def expires_on(self) -> datetime.datetime:
        """When your healthcare entities job will expire

        :return: When your healthcare entities job will expire
        :rtype: ~datetime.datetime
        """
        return self.polling_method().expires_on

    @property
    def last_modified_on(self) -> datetime.datetime:
        """When your healthcare entities job was last modified

        :return: When your healthcare entities job was last modified
        :rtype: ~datetime.datetime
        """
        return self.polling_method().last_modified_on

    @property
    def id(self) -> str:
        """ID of your call to :func:`begin_analyze_healthcare_entities`

        :return: ID of your call to :func:`begin_analyze_healthcare_entities`
        :rtype: str
        """
        return self.polling_method().id

    @property
    def display_name(self) -> str:
        """Given display_name to the healthcare entities job

        :return: Display name of the healthcare entities job.
        :rtype: str

        .. versionadded:: 2022-04-01-preview
            *display_name* property.
        """
        return self.polling_method().display_name

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
        self._text_analytics_client = kwargs.pop("text_analytics_client", None)
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
        return self._current_body.additional_properties["tasks"]["failed"]

    @property
    def actions_in_progress_count(self):
        if not self._current_body:
            return None
        return self._current_body.additional_properties["tasks"]["inProgress"]

    @property
    def actions_succeeded_count(self):
        if not self._current_body:
            return None
        return self._current_body.additional_properties["tasks"]["completed"]

    @property
    def last_modified_on(self):
        if not self._current_body:
            return None
        return self._current_body.last_update_date_time

    @property
    def total_actions_count(self):
        if not self._current_body:
            return None
        return self._current_body.additional_properties["tasks"]["total"]

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
    def created_on(self) -> datetime.datetime:
        """When your analyze job was created

        :return: When your analyze job was created
        :rtype: ~datetime.datetime
        """
        return self.polling_method().created_on

    @property
    def display_name(self) -> Optional[str]:
        """The display name of your :func:`begin_analyze_actions` call.

        Corresponds to the `display_name` kwarg you pass to your
        :func:`begin_analyze_actions` call.

        :return: The display name of your :func:`begin_analyze_actions` call.
        :rtype: str
        """
        return self.polling_method().display_name

    @property
    def expires_on(self) -> datetime.datetime:
        """When your analyze job will expire

        :return: When your analyze job will expire
        :rtype: ~datetime.datetime
        """
        return self.polling_method().expires_on

    @property
    def actions_failed_count(self) -> int:
        """Total number of actions that have failed

        :return: Total number of actions that have failed
        :rtype: int
        """
        return self.polling_method().actions_failed_count

    @property
    def actions_in_progress_count(self) -> int:
        """Total number of actions currently in progress

        :return: Total number of actions currently in progress
        :rtype: int
        """
        return self.polling_method().actions_in_progress_count

    @property
    def actions_succeeded_count(self) -> int:
        """Total number of actions that succeeded

        :return: Total number of actions that succeeded
        :rtype: int
        """
        return self.polling_method().actions_succeeded_count

    @property
    def last_modified_on(self) -> datetime.datetime:
        """The last time your actions results were updated

        :return: The last time your actions results were updated
        :rtype: ~datetime.datetime
        """
        return self.polling_method().last_modified_on

    @property
    def total_actions_count(self) -> int:
        """Total number of actions you submitted

        :return: Total number of actions submitted
        :rtype: int
        """
        return self.polling_method().total_actions_count

    @property
    def id(self) -> str:
        """ID of your :func:`begin_analyze_actions` call.

        :return: ID of your :func:`begin_analyze_actions` call.
        :rtype: str
        """
        return self.polling_method().id

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

    async def cancel(self, **kwargs: Any) -> None: # pylint: disable=unused-argument
        """Cancel the operation currently being polled.

        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError: When the operation has already reached a terminal state.
        """

        client = getattr(
            self._polling_method, "_text_analytics_client"
        )

        # Get a final status update.
        await getattr(self._polling_method, "update_status")()

        try:
            await client.begin_analyze_text_cancel_job(self.id, polling=False)
        except ValueError:
            raise ValueError("Cancellation not supported by API versions v3.0, v3.1.")


class AsyncTextAnalyticsLROPoller(AsyncLROPoller[PollingReturnType]):
    def polling_method(self) -> AsyncAnalyzeActionsLROPollingMethod:  # type: ignore
        """Return the polling method associated to this poller."""
        return self._polling_method  # type: ignore

    @property
    def details(self) -> MutableMapping[str, Any]:
        return {
            "id": self.polling_method().id,
            "created_on": self.polling_method().created_on,
            "expires_on": self.polling_method().expires_on,
            "display_name": self.polling_method().display_name,
            "last_modified_on": self.polling_method().last_modified_on,
        }

    @classmethod
    def from_continuation_token(  # type: ignore
        cls,
        polling_method: AsyncAnalyzeActionsLROPollingMethod,
        continuation_token: str,
        **kwargs: Any
    ) -> "AsyncTextAnalyticsLROPoller":  # type: ignore
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

    async def cancel(self, **kwargs: Any) -> None: # pylint: disable=unused-argument
        """Cancel the operation currently being polled.

        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError: When the operation has already reached a terminal state.
        """

        client = getattr(
            self._polling_method, "_text_analytics_client"
        )

        # Get a final status update.
        await getattr(self._polling_method, "update_status")()

        try:
            await client.begin_analyze_text_cancel_job(self.polling_method().id, polling=False)
        except ValueError:
            raise ValueError("Cancellation not supported by API versions v3.0, v3.1.")
