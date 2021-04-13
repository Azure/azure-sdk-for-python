# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import random
import logging
from typing import Any, TYPE_CHECKING

from azure.core.pipeline.policies import AsyncHTTPPolicy, AsyncRetryPolicy
from azure.core.exceptions import AzureError

from .._policies import is_retry, increment, TablesRetryPolicy

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest, PipelineResponse


_LOGGER = logging.getLogger(__name__)


async def retry_hook(settings, **kwargs):
    if settings["hook"]:
        if asyncio.iscoroutine(settings["hook"]):
            await settings["hook"](
                retry_count=settings["count"] - 1,
                location_mode=settings["mode"],
                **kwargs
            )
        else:
            settings["hook"](
                retry_count=settings["count"] - 1,
                location_mode=settings["mode"],
                **kwargs
            )


class AsyncTablesRetryPolicy(AsyncRetryPolicy, TablesRetryPolicy):
    """Exponential retry."""

    def __init__(
        self,
        initial_backoff=15,
        increment_base=3,
        retry_total=3,
        retry_to_secondary=False,
        random_jitter_range=3,
        **kwargs
    ):
        """
        Constructs an Exponential retry object. The initial_backoff is used for
        the first retry. Subsequent retries are retried after initial_backoff +
        increment_power^retry_count seconds. For example, by default the first retry
        occurs after 15 seconds, the second after (15+3^1) = 18 seconds, and the
        third after (15+3^2) = 24 seconds.

        :param int initial_backoff:
            The initial backoff interval, in seconds, for the first retry.
        :param int increment_base:
            The base, in seconds, to increment the initial_backoff by after the
            first retry.
        :param int max_attempts:
            The maximum number of retry attempts.
        :param bool retry_to_secondary:
            Whether the request should be retried to secondary, if able. This should
            only be enabled of RA-GRS accounts are used and potentially stale data
            can be handled.
        :param int random_jitter_range:
            A number in seconds which indicates a range to jitter/randomize for the back-off interval.
            For example, a random_jitter_range of 3 results in the back-off interval x to vary between x+3 and x-3.
        """
        self.initial_backoff = initial_backoff
        self.increment_base = increment_base
        self.random_jitter_range = random_jitter_range
        super(AsyncTablesRetryPolicy, self).__init__(
            retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs
        )

    def get_backoff_time(self, settings):
        """
        Calculates how long to sleep before retrying.

        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        backoff = self.initial_backoff + (
            0 if settings["count"] == 0 else pow(self.increment_base, settings["count"])
        )
        random_range_start = (
            backoff - self.random_jitter_range
            if backoff > self.random_jitter_range
            else 0
        )
        random_range_end = backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)

    async def sleep(  # pylint: disable=arguments-differ
        self, settings, transport
    ):
        backoff = self.get_backoff_time(settings)
        if not backoff or backoff < 0:
            return
        await transport.sleep(backoff)

    async def send(self, request):
        retries_remaining = True
        response = None
        retry_settings = self.configure_retries(request)
        while retries_remaining:
            try:
                response = await self.next.send(request)
                if is_retry(response, retry_settings["mode"]):
                    retries_remaining = increment(
                        retry_settings,
                        request=request.http_request,
                        response=response.http_response
                    )
                    if retries_remaining:
                        await retry_hook(
                            retry_settings,
                            request=request.http_request,
                            response=response.http_response,
                            error=None,
                        )
                        await self.sleep(retry_settings, request.context.transport)
                        continue
                break
            except AzureError as err:
                retries_remaining = increment(
                    retry_settings, request=request.http_request, error=err)
                if retries_remaining:
                    await retry_hook(
                        retry_settings,
                        request=request.http_request,
                        response=None,
                        error=err,
                    )
                    await self.sleep(retry_settings, request.context.transport)
                    continue
                raise err
        if retry_settings["history"]:
            response.context["history"] = retry_settings["history"]
        response.http_response.location_mode = retry_settings["mode"]
        return response


class ExponentialRetry(AsyncTablesRetryPolicy):
    """Exponential retry."""

    def __init__(
        self,
        initial_backoff=15,
        increment_base=3,
        retry_total=3,
        retry_to_secondary=False,
        random_jitter_range=3,
        **kwargs
    ):
        """
        Constructs an Exponential retry object. The initial_backoff is used for
        the first retry. Subsequent retries are retried after initial_backoff +
        increment_power^retry_count seconds. For example, by default the first retry
        occurs after 15 seconds, the second after (15+3^1) = 18 seconds, and the
        third after (15+3^2) = 24 seconds.

        :param int initial_backoff:
            The initial backoff interval, in seconds, for the first retry.
        :param int increment_base:
            The base, in seconds, to increment the initial_backoff by after the
            first retry.
        :param int max_attempts:
            The maximum number of retry attempts.
        :param bool retry_to_secondary:
            Whether the request should be retried to secondary, if able. This should
            only be enabled of RA-GRS accounts are used and potentially stale data
            can be handled.
        :param int random_jitter_range:
            A number in seconds which indicates a range to jitter/randomize for the back-off interval.
            For example, a random_jitter_range of 3 results in the back-off interval x to vary between x+3 and x-3.
        """
        self.initial_backoff = initial_backoff
        self.increment_base = increment_base
        self.random_jitter_range = random_jitter_range
        super(ExponentialRetry, self).__init__(
            retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs
        )

    def get_backoff_time(self, settings):
        """
        Calculates how long to sleep before retrying.

        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        backoff = self.initial_backoff + (
            0 if settings["count"] == 0 else pow(self.increment_base, settings["count"])
        )
        random_range_start = (
            backoff - self.random_jitter_range
            if backoff > self.random_jitter_range
            else 0
        )
        random_range_end = backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)


class LinearRetry(AsyncTablesRetryPolicy):
    """Linear retry."""

    def __init__(
        self,
        backoff=15,
        retry_total=3,
        retry_to_secondary=False,
        random_jitter_range=3,
        **kwargs
    ):
        """
        Constructs a Linear retry object.

        :param int backoff:
            The backoff interval, in seconds, between retries.
        :param int max_attempts:
            The maximum number of retry attempts.
        :param bool retry_to_secondary:
            Whether the request should be retried to secondary, if able. This should
            only be enabled of RA-GRS accounts are used and potentially stale data
            can be handled.
        :param int random_jitter_range:
            A number in seconds which indicates a range to jitter/randomize for the back-off interval.
            For example, a random_jitter_range of 3 results in the back-off interval x to vary between x+3 and x-3.
        """
        self.backoff = backoff
        self.random_jitter_range = random_jitter_range
        super(LinearRetry, self).__init__(
            retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs
        )

    def get_backoff_time(self, settings, **kwargs):  # pylint: disable=unused-argument
        """
        Calculates how long to sleep before retrying.

        :param **kwargs:
        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        # the backoff interval normally does not change, however there is the possibility
        # that it was modified by accessing the property directly after initializing the object
        random_range_start = (
            self.backoff - self.random_jitter_range
            if self.backoff > self.random_jitter_range
            else 0
        )
        random_range_end = self.backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)
