# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
from typing import Optional
from azure.core.exceptions import HttpResponseError
from azure.core.polling import AsyncLROPoller
from azure.core.polling.base_polling import OperationFailed, BadStatus
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling._async_poller import PollingReturnType


_FINISHED = frozenset(["succeeded", "cancelled", "failed", "partiallycompleted"])
_FAILED = frozenset(["failed"])
_SUCCEEDED = frozenset(["succeeded", "partiallycompleted"])


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
            raise OperationFailed("Operation failed or canceled")

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
        super(AsyncAnalyzeHealthcareEntitiesLROPollingMethod, self).__init__(
            *args, **kwargs
        )

    @property
    def _current_body(self):
        from .._generated.models import JobMetadata

        return JobMetadata.deserialize(self._pipeline_response)

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
            return await getattr(
                self._polling_method, "_text_analytics_client"
            ).begin_cancel_health_job(
                self.id,
                polling=TextAnalyticsAsyncLROPollingMethod(timeout=polling_interval),
            )

        except HttpResponseError as error:
            from .._response_handlers import process_http_response_error

            process_http_response_error(error)


class AsyncAnalyzeActionsLROPollingMethod(TextAnalyticsAsyncLROPollingMethod):
    @property
    def _current_body(self):
        from .._generated.models import AnalyzeJobMetadata

        return AnalyzeJobMetadata.deserialize(self._pipeline_response)

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
