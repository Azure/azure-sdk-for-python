# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import requests
from typing import TYPE_CHECKING

from .config import PROXY_URL
from .helpers import is_live_and_not_recording
from .proxy_testcase import get_recording_id

if TYPE_CHECKING:
    from typing import Any, Dict


def set_bodiless_matcher():
    # type: () -> None
    """Adjusts the "match" operation to EXCLUDE the body when matching a request to a recording's entries.

    This method must be called during test case execution, rather than at a session, module, or class level.
    """

    x_recording_id = get_recording_id()
    _send_matcher_request("BodilessMatcher", {"x-recording-id": x_recording_id})


def add_body_key_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer that offers regex update of a specific JTokenPath within a returned body.

    For example, "TableName" within a json response body having its value replaced by whatever substitution is offered.

    :keyword str json_path: The SelectToken path (which could possibly match multiple entries) that will be used to
        select JTokens for value replacement.
    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex replace OR if groupForReplace is set, a subsitution
        operation. Defaults to replacing the entire string.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("BodyKeySanitizer", request_args)


def add_body_regex_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer that offers regex replace within a returned body.

    Specifically, this means regex applying to the raw JSON. If you are attempting to simply replace a specific key, the
    BodyKeySanitizer is probably the way to go.

    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex, or if a ``group_for_replace`` is provided, a
        substitution operation.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("BodyRegexSanitizer", request_args)


def add_continuation_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer that's used to anonymize private keys in response/request pairs.

    For instance, a request hands back a "sessionId" that needs to be present in the next request. Supports "all further
    requests get this key" as well as "single response/request pair". Defaults to maintaining same key for rest of
    recording.

    :keyword str key: The name of the header whos value will be replaced from response -> next request.
    :keyword str method: The method by which the value of the targeted key will be replaced. Defaults to guid
        replacement.
    :keyword str reset_after_first: Do we need multiple pairs replaced? Or do we want to replace each value with the
        same value?
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("ContinuationSanitizer", request_args)


def add_general_regex_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer that offers a general regex replace across request/response Body, Headers, and URI.

    For the body, this means regex applying to the raw JSON.

    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex, or if a ``group_for_replace`` is provided, a
        substitution operation.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("GeneralRegexSanitizer", request_args)


def add_header_regex_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer that offers regex replace on returned headers.

    Can be used for multiple purposes: 1) To replace a key with a specific value, do not set "regex" value. 2) To do a
    simple regex replace operation, define arguments "key", "value", and "regex". 3) To do a targeted substitution of a
    specific group, define all arguments "key", "value", and "regex".

    :keyword str key: The name of the header we're operating against.
    :keyword str value: The substitution or whole new header value, depending on "regex" setting.
    :keyword str regex: A regex. Can be defined as a simple regex, or if a ``group_for_replace`` is provided, a
        substitution operation.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("HeaderRegexSanitizer", request_args)


def add_oauth_response_sanitizer():
    # type: () -> None
    """Registers a sanitizer that cleans out all request/response pairs that match an oauth regex in their URI."""

    _send_sanitizer_request("OAuthResponseSanitizer", {})


def add_remove_header_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer that removes specified headers before saving a recording.

    :keyword str headers: A comma separated list. Should look like "Location, Transfer-Encoding" or something along
        those lines. Don't worry about whitespace between the commas separating each key. They will be ignored.
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("RemoveHeaderSanitizer", request_args)


def add_request_subscription_id_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer that replaces subscription IDs in requests.

    Subscription IDs are replaced with "00000000-0000-0000-0000-000000000000" by default.

    :keyword str value: The fake subscriptionId that will be placed where the real one is in the real request.
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("ReplaceRequestSubscriptionId", request_args)


def add_uri_regex_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer for cleaning URIs via regex.

    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex, or if a ``group_for_replace`` is provided, a
        substitution operation.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("UriRegexSanitizer", request_args)


def _get_request_args(**kwargs):
    # type: (**Any) -> Dict
    """Returns a dictionary of sanitizer constructor headers"""

    request_args = {}
    if "group_for_replace" in kwargs:
        request_args["groupForReplace"] = kwargs.get("group_for_replace")
    if "headers" in kwargs:
        request_args["headersForRemoval"] = kwargs.get("headers")
    if "json_path" in kwargs:
        request_args["jsonPath"] = kwargs.get("json_path")
    if "key" in kwargs:
        request_args["key"] = kwargs.get("key")
    if "method" in kwargs:
        request_args["method"] = kwargs.get("method")
    if "regex" in kwargs:
        request_args["regex"] = kwargs.get("regex")
    if "reset_after_first" in kwargs:
        request_args["resetAfterFirst"] = kwargs.get("reset_after_first")
    if "value" in kwargs:
        request_args["value"] = kwargs.get("value")
    return request_args


def _send_matcher_request(matcher, headers):
    # type: (str, Dict) -> None
    """Sends a POST request to the test proxy endpoint to register the specified matcher.

    If live tests are being run with recording turned off via the AZURE_SKIP_LIVE_RECORDING environment variable, no
    request will be sent.

    :param str matcher: The name of the matcher to set.
    :param dict headers: Any matcher headers, as a dictionary.
    """

    if is_live_and_not_recording():
        return

    headers_to_send = {"x-abstraction-identifier": matcher}
    headers_to_send.update(headers)
    requests.post(
        "{}/Admin/SetMatcher".format(PROXY_URL),
        headers=headers_to_send,
    )


def _send_sanitizer_request(sanitizer, parameters):
    # type: (str, Dict) -> None
    """Sends a POST request to the test proxy endpoint to register the specified sanitizer.

    If live tests are being run with recording turned off via the AZURE_SKIP_LIVE_RECORDING environment variable, no
    request will be sent.

    :param str sanitizer: The name of the sanitizer to add.
    :param dict parameters: The sanitizer constructor parameters, as a dictionary.
    """

    if is_live_and_not_recording():
        return

    requests.post(
        "{}/Admin/AddSanitizer".format(PROXY_URL),
        headers={"x-abstraction-identifier": sanitizer, "Content-Type": "application/json"},
        json=parameters,
    )
