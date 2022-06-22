# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import requests
from typing import TYPE_CHECKING

from .config import PROXY_URL
from .helpers import get_recording_id, is_live, is_live_and_not_recording

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


def set_bodiless_matcher():
    # type: () -> None
    """Adjusts the "match" operation to EXCLUDE the body when matching a request to a recording's entries.

    This method must be called during test case execution, rather than at a session, module, or class level.
    """

    x_recording_id = get_recording_id()
    _send_matcher_request("BodilessMatcher", {"x-recording-id": x_recording_id})


def set_custom_default_matcher(**kwargs):
    # type: (**Any) -> None
    """Exposes the default matcher in a customizable way.

    All optional settings are safely defaulted. This means that providing zero additional configuration will produce a
    sanitizer that is functionally identical to the default.

    :keyword bool compare_bodies: True to enable body matching (default behavior), or False to disable body matching.
    :keyword str excluded_headers: A comma separated list of headers that should be excluded during matching. The
        presence of these headers will not be taken into account while matching. Should look like
        "Authorization, Content-Length", for example.
    :keyword str ignored_headers: A comma separated list of headers that should be ignored during matching. The header
        values won't be matched, but the presence of these headers will be taken into account while matching. Should
        look like "Authorization, Content-Length", for example.
    :keyword bool ignore_query_ordering: By default, the test proxy does not sort query params before matching. Setting
        to True will sort query params alphabetically before comparing URIs.
    :keyword str ignored_query_parameters: A comma separated list of query parameters that should be ignored during
        matching. The parameter values won't be matched, but the presence of these parameters will be taken into account
        while matching. Should look like "param1, param2", for example.
    """

    x_recording_id = get_recording_id()
    request_args = _get_request_args(**kwargs)
    _send_matcher_request("CustomDefaultMatcher", {"x-recording-id": x_recording_id}, request_args)


def set_default_settings():
    # type: () -> None
    """Resets all active sanitizers, matchers, and transforms for the test proxy to their default settings.

    This will reset any setting customizations for a single test if it is called during test case execution, rather than
    at a session, module, or class level. Otherwise, it will reset setting customizations at the session level (i.e. for
    all tests).
    """

    x_recording_id = get_recording_id()
    _send_reset_request({"x-recording-id": x_recording_id})


def add_body_key_sanitizer(**kwargs):
    # type: (**Any) -> None
    """Registers a sanitizer that offers regex update of a specific JTokenPath within a returned body.

    For example, "TableName" within a json response body having its value replaced by whatever substitution is offered.

    :keyword str json_path: The SelectToken path (which could possibly match multiple entries) that will be used to
        select JTokens for value replacement.
    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex replace OR if groupForReplace is set, a substitution
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

    :keyword str key: The name of the header whose value will be replaced from response -> next request.
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
    if "compare_bodies" in kwargs:
        request_args["compareBodies"] = kwargs.get("compare_bodies")
    if "excluded_headers" in kwargs:
        request_args["excludedHeaders"] = kwargs.get("excluded_headers")
    if "group_for_replace" in kwargs:
        request_args["groupForReplace"] = kwargs.get("group_for_replace")
    if "headers" in kwargs:
        request_args["headersForRemoval"] = kwargs.get("headers")
    if "ignored_headers" in kwargs:
        request_args["ignoredHeaders"] = kwargs.get("ignored_headers")
    if "ignore_query_ordering" in kwargs:
        request_args["ignoreQueryOrdering"] = kwargs.get("ignore_query_ordering")
    if "ignored_query_parameters" in kwargs:
        request_args["ignoredQueryParameters"] = kwargs.get("ignored_query_parameters")
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


def _send_matcher_request(matcher, headers, parameters=None):
    # type: (str, Dict, Optional[Dict]) -> None
    """Sends a POST request to the test proxy endpoint to register the specified matcher.

    If live tests are being run, no request will be sent.

    :param str matcher: The name of the matcher to set.
    :param dict headers: Any matcher headers, as a dictionary.
    """

    if is_live():
        return

    headers_to_send = {"x-abstraction-identifier": matcher}
    headers_to_send.update(headers)
    response = requests.post(
        "{}/Admin/SetMatcher".format(PROXY_URL),
        headers=headers_to_send,
        json=parameters
    )
    response.raise_for_status()


def _send_reset_request(headers):
    # type: (Dict) -> None
    """Sends a POST request to the test proxy endpoint to reset setting customizations.

    If live tests are being run with recording turned off via the AZURE_SKIP_LIVE_RECORDING environment variable, no
    request will be sent.

    :param dict headers: Any reset request headers, as a dictionary.
    """

    if is_live_and_not_recording():
        return

    response = requests.post(
        "{}/Admin/Reset".format(PROXY_URL),
        headers=headers
    )
    response.raise_for_status()


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

    response = requests.post(
        "{}/Admin/AddSanitizer".format(PROXY_URL),
        headers={"x-abstraction-identifier": sanitizer, "Content-Type": "application/json"},
        json=parameters
    )
    response.raise_for_status()
