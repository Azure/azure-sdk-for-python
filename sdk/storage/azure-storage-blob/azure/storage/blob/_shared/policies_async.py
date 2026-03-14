# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=invalid-overridden-method

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import random
from typing import Any, Dict, TYPE_CHECKING

from azure.core.exceptions import AzureError, StreamClosedError, StreamConsumedError
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, AsyncHTTPPolicy

from .authentication import AzureSigningError, StorageHttpChallenge
from .constants import DATA_BLOCK_SIZE, DEFAULT_OAUTH_SCOPE
from .policies import (
    CONTENT_LENGTH_HEADER,
    CRC64_HEADER,
    MD5_HEADER,
    SM_HEADER,
    SM_HEADER_V1_CRC64,
    SM_LENGTH_HEADER,
    encode_base64,
    is_retry,
    StorageRetryPolicy,
)
from .streams import StructuredMessageEncodeStream, StructuredMessageProperties
from .streams_async import AsyncStructuredMessageDecoder
from .validation import (
    CV_TYPE_ERROR_MSG,
    ChecksumAlgorithm,
    calculate_content_md5,
    calculate_crc64_bytes,
    is_md5_validation,
)

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import
        PipelineRequest,
        PipelineResponse,
    )


_LOGGER = logging.getLogger(__name__)


async def retry_hook(settings, **kwargs):
    if settings["hook"]:
        if asyncio.iscoroutine(settings["hook"]):
            await settings["hook"](retry_count=settings["count"] - 1, location_mode=settings["mode"], **kwargs)
        else:
            settings["hook"](retry_count=settings["count"] - 1, location_mode=settings["mode"], **kwargs)


async def is_checksum_retry(response):
    validate_content = response.context.get("validate_content", False)
    if not validate_content:
        return False

    # Legacy code - evaluate retry only on validate_content=True
    if validate_content is True and response.http_response.headers.get("content-md5"):
        if hasattr(response.http_response, "load_body"):
            try:
                await response.http_response.load_body()  # Load the body in memory and close the socket
            except (StreamClosedError, StreamConsumedError):
                pass
        computed_md5 = response.http_request.headers.get("content-md5", None) or encode_base64(
            calculate_content_md5(response.http_response.body())
        )
        if response.http_response.headers["content-md5"] != computed_md5:
            return True
    return False


class AsyncContentValidationPolicy(AsyncHTTPPolicy):
    """A pipeline policy that performs content validation on uploads and downloads when enabled by the user.
    This is enabled by setting the "validate_content" key in the request context. When enabled, this policy will
    calculate and verify content checksums for uploads and downloads, and raise an exception if a mismatch is detected.
    """
    def __init__(self, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        super().__init__()

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        validate_content = request.context.options.pop("validate_content", False)

        # Download
        if request.http_request.method == "GET":
            if validate_content == ChecksumAlgorithm.CRC64:
                request.http_request.headers[SM_HEADER] = SM_HEADER_V1_CRC64

        # Upload
        else:
            # Since HTTP does not differentiate between no content and empty content,
            # we have to perform a None check.
            data = request.http_request.data or b""
            if is_md5_validation(validate_content):
                computed_md5 = encode_base64(calculate_content_md5(data))
                request.http_request.headers[MD5_HEADER] = computed_md5
                request.context["validate_content_md5"] = computed_md5

            elif validate_content == ChecksumAlgorithm.CRC64:
                if isinstance(data, bytes):
                    request.http_request.headers[CRC64_HEADER] = encode_base64(calculate_crc64_bytes(data))
                elif hasattr(data, "read"):
                    content_length = int(request.http_request.headers.get(CONTENT_LENGTH_HEADER))
                    # Wrap data in structured message stream and adjust HTTP request
                    sm_stream = StructuredMessageEncodeStream(data, content_length, StructuredMessageProperties.CRC64)
                    request.http_request.data = sm_stream
                    request.http_request.headers[CONTENT_LENGTH_HEADER] = str(len(sm_stream))
                    request.http_request.headers[SM_LENGTH_HEADER] = str(content_length)
                    request.http_request.headers[SM_HEADER] = SM_HEADER_V1_CRC64
                else:
                    raise ValueError(CV_TYPE_ERROR_MSG)

        request.context["validate_content"] = validate_content

        response = await self.next.send(request)

        if is_md5_validation(validate_content) and response.http_response.headers.get("content-md5"):
            if hasattr(response.http_response, "load_body"):
                try:
                    await response.http_response.load_body()  # Load the body in memory and close the socket
                except (StreamClosedError, StreamConsumedError):
                    pass
            computed_md5 = request.context.get("validate_content_md5") or encode_base64(
                calculate_content_md5(response.http_response.body())
            )
            if response.http_response.headers["content-md5"] != computed_md5:
                raise AzureError(
                    (
                        f"MD5 mismatch. Expected value is '{response.http_response.headers['content-md5']}', "
                        f"computed value is '{computed_md5}'."
                    ),
                    response=response.http_response,
                )

        elif validate_content == ChecksumAlgorithm.CRC64:
            # For upload and download verify structured message header present in response if provided in request.
            sm_request = request.http_request.headers.get(SM_HEADER)
            sm_response = response.http_response.headers.get(SM_HEADER)
            if sm_request != sm_response:
                raise AzureError(
                    (
                        f"Expected structured message header in response does not match request. "
                        f"Request: {sm_request}, Response: {sm_response}",
                    ),
                    response=response.http_response,
                )

            if response.http_request.method == "GET":
                # Raises exception if missing
                content_length = int(response.http_response.headers[CONTENT_LENGTH_HEADER])

                # Patch response to return response iterator wrapped in structured message decoder
                original_stream_download = response.http_response.stream_download
                def wrapped_stream_download(*args, **kwargs):
                    iterator = original_stream_download(*args, **kwargs)
                    decoder = AsyncStructuredMessageDecoder(iterator, content_length, block_size=DATA_BLOCK_SIZE)
                    decoder.request = iterator.request  # type: ignore
                    decoder.response = iterator.response  # type: ignore
                    return decoder

                response.http_response.stream_download = wrapped_stream_download

        return response


class AsyncStorageResponseHook(AsyncHTTPPolicy):

    def __init__(self, **kwargs):
        self._response_callback = kwargs.get("raw_response_hook")
        super(AsyncStorageResponseHook, self).__init__()

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        # Values could be 0
        data_stream_total = request.context.get("data_stream_total")
        if data_stream_total is None:
            data_stream_total = request.context.options.pop("data_stream_total", None)
        download_stream_current = request.context.get("download_stream_current")
        if download_stream_current is None:
            download_stream_current = request.context.options.pop("download_stream_current", None)
        upload_stream_current = request.context.get("upload_stream_current")
        if upload_stream_current is None:
            upload_stream_current = request.context.options.pop("upload_stream_current", None)

        response_callback = request.context.get("response_callback") or request.context.options.pop(
            "raw_response_hook", self._response_callback
        )

        response = await self.next.send(request)
        will_retry = is_retry(response, request.context.options.get("mode")) or await is_checksum_retry(response)

        # Auth error could come from Bearer challenge, in which case this request will be made again
        is_auth_error = response.http_response.status_code == 401
        should_update_counts = not (will_retry or is_auth_error)

        if should_update_counts and download_stream_current is not None:
            download_stream_current += int(response.http_response.headers.get("Content-Length", 0))
            if data_stream_total is None:
                content_range = response.http_response.headers.get("Content-Range")
                if content_range:
                    data_stream_total = int(content_range.split(" ", 1)[1].split("/", 1)[1])
                else:
                    data_stream_total = download_stream_current
        elif should_update_counts and upload_stream_current is not None:
            upload_stream_current += int(response.http_request.headers.get("Content-Length", 0))
        for pipeline_obj in [request, response]:
            if hasattr(pipeline_obj, "context"):
                pipeline_obj.context["data_stream_total"] = data_stream_total
                pipeline_obj.context["download_stream_current"] = download_stream_current
                pipeline_obj.context["upload_stream_current"] = upload_stream_current
        if response_callback:
            if asyncio.iscoroutine(response_callback):
                await response_callback(response)  # type: ignore
            else:
                response_callback(response)
            request.context["response_callback"] = response_callback
        return response


class AsyncStorageRetryPolicy(StorageRetryPolicy):
    """
    The base class for Exponential and Linear retries containing shared code.
    """

    async def sleep(self, settings, transport):
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
                if is_retry(response, retry_settings["mode"]) or await is_checksum_retry(response):
                    retries_remaining = self.increment(
                        retry_settings, request=request.http_request, response=response.http_response
                    )
                    if retries_remaining:
                        await retry_hook(
                            retry_settings, request=request.http_request, response=response.http_response, error=None
                        )
                        await self.sleep(retry_settings, request.context.transport)
                        continue
                break
            except AzureError as err:
                if isinstance(err, AzureSigningError):
                    raise
                retries_remaining = self.increment(retry_settings, request=request.http_request, error=err)
                if retries_remaining:
                    await retry_hook(retry_settings, request=request.http_request, response=None, error=err)
                    await self.sleep(retry_settings, request.context.transport)
                    continue
                raise err
        if retry_settings["history"]:
            response.context["history"] = retry_settings["history"]
        response.http_response.location_mode = retry_settings["mode"]
        return response


class ExponentialRetry(AsyncStorageRetryPolicy):
    """Exponential retry."""

    initial_backoff: int
    """The initial backoff interval, in seconds, for the first retry."""
    increment_base: int
    """The base, in seconds, to increment the initial_backoff by after the
    first retry."""
    random_jitter_range: int
    """A number in seconds which indicates a range to jitter/randomize for the back-off interval."""

    def __init__(
        self,
        initial_backoff: int = 15,
        increment_base: int = 3,
        retry_total: int = 3,
        retry_to_secondary: bool = False,
        random_jitter_range: int = 3,
        **kwargs
    ) -> None:
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
        super(ExponentialRetry, self).__init__(retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs)

    def get_backoff_time(self, settings: Dict[str, Any]) -> float:
        """
        Calculates how long to sleep before retrying.

        :param Dict[str, Any] settings: The configurable values pertaining to the backoff time.
        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        backoff = self.initial_backoff + (0 if settings["count"] == 0 else pow(self.increment_base, settings["count"]))
        random_range_start = backoff - self.random_jitter_range if backoff > self.random_jitter_range else 0
        random_range_end = backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)


class LinearRetry(AsyncStorageRetryPolicy):
    """Linear retry."""

    initial_backoff: int
    """The backoff interval, in seconds, between retries."""
    random_jitter_range: int
    """A number in seconds which indicates a range to jitter/randomize for the back-off interval."""

    def __init__(
        self,
        backoff: int = 15,
        retry_total: int = 3,
        retry_to_secondary: bool = False,
        random_jitter_range: int = 3,
        **kwargs: Any
    ) -> None:
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
        super(LinearRetry, self).__init__(retry_total=retry_total, retry_to_secondary=retry_to_secondary, **kwargs)

    def get_backoff_time(self, settings: Dict[str, Any]) -> float:
        """
        Calculates how long to sleep before retrying.

        :param Dict[str, Any] settings: The configurable values pertaining to the backoff time.
        :return:
            An integer indicating how long to wait before retrying the request,
            or None to indicate no retry should be performed.
        :rtype: int or None
        """
        random_generator = random.Random()
        # the backoff interval normally does not change, however there is the possibility
        # that it was modified by accessing the property directly after initializing the object
        random_range_start = self.backoff - self.random_jitter_range if self.backoff > self.random_jitter_range else 0
        random_range_end = self.backoff + self.random_jitter_range
        return random_generator.uniform(random_range_start, random_range_end)


class AsyncStorageBearerTokenCredentialPolicy(AsyncBearerTokenCredentialPolicy):
    """Custom Bearer token credential policy for following Storage Bearer challenges"""

    def __init__(self, credential: "AsyncTokenCredential", audience: str, **kwargs: Any) -> None:
        super(AsyncStorageBearerTokenCredentialPolicy, self).__init__(credential, audience, **kwargs)

    async def on_challenge(self, request: "PipelineRequest", response: "PipelineResponse") -> bool:
        try:
            auth_header = response.http_response.headers.get("WWW-Authenticate")
            challenge = StorageHttpChallenge(auth_header)
        except ValueError:
            return False

        scope = challenge.resource_id + DEFAULT_OAUTH_SCOPE
        await self.authorize_request(request, scope, tenant_id=challenge.tenant_id)

        return True
