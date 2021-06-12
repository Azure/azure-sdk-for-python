# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
import email.utils
from typing import TYPE_CHECKING
from requests.structures import CaseInsensitiveDict

from azure.core.polling.base_polling import BadStatus

if TYPE_CHECKING:
    from typing import Union
    from azure.core.pipeline.transport import HttpResponse, AsyncHttpResponse

    ResponseType = Union[HttpResponse, AsyncHttpResponse]


_FAILED = frozenset(["canceled", "failed"])


def _failed(status):
    if hasattr(status, "value"):
        status = status.value
    return str(status).lower() in _FAILED


def _get_retry_after(response):
    """Get the value of Retry-After in seconds.

    :param response: The PipelineResponse object
    :type response: ~azure.core.pipeline.PipelineResponse
    :return: Value of Retry-After in seconds.
    :rtype: float or None
    """
    headers = CaseInsensitiveDict(response.http_response.headers)
    retry_after = headers.get("retry-after")
    if retry_after:
        return _parse_retry_after(retry_after)
    for ms_header in ["retry-after-ms", "x-ms-retry-after-ms"]:
        retry_after = headers.get(ms_header)
        if retry_after:
            parsed_retry_after = _parse_retry_after(retry_after)
            return parsed_retry_after / 1000.0
    return None


def _parse_http_date(text):
    """Parse a HTTP date format into datetime."""
    parsed_date = email.utils.parsedate_tz(text)
    return datetime.datetime(*parsed_date[:6], tzinfo=_FixedOffset(parsed_date[9] / 60))


def _parse_retry_after(retry_after):
    """Helper to parse Retry-After and get value in seconds.

    :param str retry_after: Retry-After header
    :rtype: int
    """
    try:
        delay = int(retry_after)
    except ValueError:
        # Not an integer? Try HTTP date
        retry_date = _parse_http_date(retry_after)
        delay = (retry_date - datetime.datetime.now(retry_date.tzinfo)).total_seconds()
    return max(0, delay)


def _raise_if_bad_http_status_and_method(response):
    # type: (ResponseType) -> None
    """Check response status code is valid.

    Must be 200, 201, 202, or 204.

    :raises: BadStatus if invalid status.
    """
    code = response.status_code
    if code in {200, 201, 202, 204}:
        return
    raise BadStatus("Invalid return status {!r} for {!r} operation".format(code, response.request.method))


class _FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC.

    Copy/pasted from Python doc

    :param int offset: offset in minutes
    """

    def __init__(self, offset):
        self.__offset = datetime.timedelta(minutes=offset)

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return str(self.__offset.total_seconds() / 3600)

    def __repr__(self):
        return "<FixedOffset {}>".format(self.tzname(None))

    def dst(self, dt):
        return datetime.timedelta(0)
