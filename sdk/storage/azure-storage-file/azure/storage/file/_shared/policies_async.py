# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import base64
import hashlib
import re
import random
from time import time
from io import SEEK_SET, UnsupportedOperation
import logging
import uuid
import types
import platform
from typing import Any, TYPE_CHECKING
from wsgiref.handlers import format_date_time
try:
    from urllib.parse import (
        urlparse,
        parse_qsl,
        urlunparse,
        urlencode,
    )
except ImportError:
    from urllib import urlencode # type: ignore
    from urlparse import ( # type: ignore
        urlparse,
        parse_qsl,
        urlunparse,
    )

from azure.core.pipeline.policies import (
    HeadersPolicy,
    SansIOHTTPPolicy,
    NetworkTraceLoggingPolicy,
    HTTPPolicy)
from azure.core.pipeline.policies.base import RequestHistory
from azure.core.exceptions import AzureError, ServiceRequestError, ServiceResponseError

from ..version import VERSION
from .models import LocationMode
from .policies import is_retry, StorageRetryPolicy

try:
    _unicode_type = unicode # type: ignore
except NameError:
    _unicode_type = str

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest, PipelineResponse


_LOGGER = logging.getLogger(__name__)



class AsyncStorageRetryPolicy(StorageRetryPolicy):
    """
    The base class for Exponential and Linear retries containing shared code.
    """

    async def sleep(self, settings, transport):
        backoff = self.get_backoff_time(settings)
        if not backoff or backoff < 0:
            return
        await transport.sleep(backoff)

    async def retry_hook(self, settings, **kwargs):
        if retry_settings['hook']:
            if asyncio.iscoroutine(retry_settings['hook']):
                await retry_settings['hook'](
                    retry_count=retry_settings['count'] - 1,
                    location_mode=retry_settings['mode'],
                    **kwargs)
            else:
                retry_settings['hook'](
                    retry_count=retry_settings['count'] - 1,
                    location_mode=retry_settings['mode'],
                    **kwargs)

    async def send(self, request):
        retries_remaining = True
        response = None
        retry_settings = self.configure_retries(request)
        while retries_remaining:
            try:
                response = await self.next.send(request)
                if is_retry(response, retry_settings['mode']):
                    retries_remaining = self.increment(
                        retry_settings,
                        request=request.http_request,
                        response=response.http_response)
                    if retries_remaining:
                        await self.retry_hook(
                            retry_settings,
                            request=request.http_request,
                            response=response.http_response,
                            error=None)
                        self.sleep(retry_settings, request.context.transport)
                        continue
                break
            except AzureError as err:
                retries_remaining = self.increment(
                    retry_settings, request=request.http_request, error=err)
                if retries_remaining:
                    await self.retry_hook(
                        retry_settings,
                        request=request.http_request,
                        response=None,
                        error=err)
                    self.sleep(retry_settings, request.context.transport)
                    continue
                raise err
        if retry_settings['history']:
            response.context['history'] = retry_settings['history']
        response.http_response.location_mode = retry_settings['mode']
        return response


class NoRetry(AsyncStorageRetryPolicy):

    def __init__(self):
        super(NoRetry, self).__init__(retry_total=0)

    def increment(self, *args, **kwargs):  # pylint: disable=unused-argument,arguments-differ
        return False


class ExponentialRetry(AsyncStorageRetryPolicy):
    """Exponential retry."""

    def __init__(self, initial_backoff=15, increment_base=3, retry_total=3,
                 retry_to_secondary=False, random_jitter_range=3, **kwargs):
        '''
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
        '''
        self.initial_backoff = initial_backoff
        self.increment_base = increment_base
        self.random_jitter_range = random_jitter_range
        super(ExponentialRetry, self).__init__(
            retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs)

    def get_backoff_time(self, settings):
        """
        Calculates how long to sleep before retrying.

        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        backoff = self.initial_backoff + (0 if settings['count'] == 0 else pow(self.increment_base, settings['count']))
        random_range_start = backoff - self.random_jitter_range if backoff > self.random_jitter_range else 0
        random_range_end = backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)


class LinearRetry(AsyncStorageRetryPolicy):
    """Linear retry."""

    def __init__(self, backoff=15, retry_total=3, retry_to_secondary=False, random_jitter_range=3, **kwargs):
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
            retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs)

    def get_backoff_time(self, settings):
        """
        Calculates how long to sleep before retrying.

        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        # the backoff interval normally does not change, however there is the possibility
        # that it was modified by accessing the property directly after initializing the object
        random_range_start = self.backoff - self.random_jitter_range \
            if self.backoff > self.random_jitter_range else 0
        random_range_end = self.backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)
