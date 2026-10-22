# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from __future__ import annotations
import datetime
import email.utils
import urllib.parse
from typing import AbstractSet, Optional, cast, Union, TYPE_CHECKING
from urllib.parse import urlparse

from ...rest import HttpResponse, AsyncHttpResponse, HttpRequest
from ...utils._utils import case_insensitive_dict, CaseInsensitiveSet

if TYPE_CHECKING:
    from ...runtime.pipeline import PipelineResponse

AllHttpResponseType = Union[HttpResponse, AsyncHttpResponse]


def _parse_http_date(text: str) -> datetime.datetime:
    """Parse a HTTP date format into datetime.

    :param str text: Text containing a date in HTTP format
    :rtype: datetime.datetime
    :return: The parsed datetime
    """
    parsed_date = email.utils.parsedate_tz(text)
    if not parsed_date:
        raise ValueError("Invalid HTTP date")
    tz_offset = cast(int, parsed_date[9])  # Look at the code, tz_offset is always an int, at worst 0
    return datetime.datetime(*parsed_date[:6], tzinfo=datetime.timezone(datetime.timedelta(seconds=tz_offset)))


def parse_retry_after(retry_after: str) -> float:
    """Helper to parse Retry-After and get value in seconds.

    :param str retry_after: Retry-After header
    :rtype: float
    :return: Value of Retry-After in seconds.
    """
    delay: float  # Using the Mypy recommendation to use float for "int or float"
    try:
        delay = float(retry_after)
    except ValueError:
        # Not an integer? Try HTTP date
        retry_date = _parse_http_date(retry_after)
        delay = (retry_date - datetime.datetime.now(retry_date.tzinfo)).total_seconds()
    return max(0, delay)


def get_retry_after(response: PipelineResponse[HttpRequest, AllHttpResponseType]) -> Optional[float]:
    """Get the value of Retry-After in seconds.

    :param response: The PipelineResponse object
    :type response: ~corehttp.runtime.pipeline.PipelineResponse
    :return: Value of Retry-After in seconds.
    :rtype: float or None
    """
    headers = case_insensitive_dict(response.http_response.headers)
    retry_after = headers.get("retry-after")
    if retry_after:
        return parse_retry_after(retry_after)
    return None


def get_domain(url: str) -> str:
    """Get the domain of an url.

    :param str url: The url.
    :rtype: str
    :return: The domain of the url.
    """
    return str(urlparse(url).netloc).lower()


def sanitize_url(url: str, allowed_query_params: AbstractSet[str], redacted_placeholder: str = "REDACTED") -> str:
    """Redact query parameter values not in the allowlist.

    :param str url: The URL to sanitize.
    :param set[str] allowed_query_params: Set of query parameter names whose values should not be redacted.
        If a :class:`~corehttp.utils._utils.CaseInsensitiveSet` is provided, lookups are case-insensitive
        without per-call normalization.
    :param str redacted_placeholder: The placeholder to use for redacted values.
    :return: The sanitized URL with redacted query parameter values.
    :rtype: str
    """
    parsed_url = urllib.parse.urlparse(url)
    if not parsed_url.query:
        return url

    if not isinstance(allowed_query_params, CaseInsensitiveSet):
        allowed_query_params = CaseInsensitiveSet(allowed_query_params)

    parts = []
    for param in parsed_url.query.split("&"):
        eq_idx = param.find("=")
        if eq_idx == -1:
            # No value to redact, keep as-is.
            parts.append(param)
        else:
            key = param[:eq_idx]
            parts.append(param if key in allowed_query_params else f"{key}={redacted_placeholder}")

    sanitized_query = "&".join(parts)
    sanitized_url = parsed_url._replace(query=sanitized_query)
    return urllib.parse.urlunparse(sanitized_url)
