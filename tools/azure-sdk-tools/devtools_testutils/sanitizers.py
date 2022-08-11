# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from urllib.error import HTTPError
import requests

from .config import PROXY_URL
from .helpers import get_recording_id, is_live, is_live_and_not_recording

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional


# This file contains methods for adjusting many aspects of test proxy behavior:
#
# - Sanitizers: record stand-in values to hide secrets and/or enable playback when behavior is inconsistent
# - Transforms: extend test proxy functionality by changing how recordings are processed in playback mode
# - Matchers: modify the conditions that are used to match request and response content with recorded values
# - Recording options: further customization for advanced scenarios, such as providing certificates to the transport
#
# Methods for a given category are grouped together under a header containing more details.


def set_default_function_settings() -> None:
    """Resets sanitizers, matchers, and transforms for the test proxy to their default settings, for the current test.

    This will reset any setting customizations for a single test. This must be called during test case execution, rather
    than at a session, module, or class level. To reset setting customizations for all tests, use
    `set_default_session_settings` instead.
    """

    x_recording_id = get_recording_id()
    if x_recording_id is None:
        raise RuntimeError(
            "This method must be called during test case execution. To reset test proxy settings at a session level, "
            "use `set_default_session_settings` instead."
        )
    _send_reset_request({"x-recording-id": x_recording_id})


def set_default_session_settings() -> None:
    """Resets sanitizers, matchers, and transforms for the test proxy to their default settings, for all tests.

    This will reset any setting customizations for an entire test session. To reset setting customizations for a single
    test -- which is recommended -- use `set_default_function_settings` instead.
    """

    _send_reset_request({})


# ----------MATCHERS----------
#
# A matcher is applied during a playback session. The default matcher matches a request on headers, URI, and the body.
#
# This is the least used customization as most adjustments to matching really come down to sanitizing properly before
# storing the recording. Further, when using this customization, it is recommended that one registers matchers during
# individual test case execution so that the adjusting matching only occurs for a specific recording during playback.
#
# ----------------------------


def set_bodiless_matcher() -> None:
    """Adjusts the "match" operation to EXCLUDE the body when matching a request to a recording's entries.

    This method should be called during test case execution, rather than at a session, module, or class level.
    """

    x_recording_id = get_recording_id()
    _send_matcher_request("BodilessMatcher", {"x-recording-id": x_recording_id})


def set_custom_default_matcher(**kwargs: "Any") -> None:
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


def set_headerless_matcher() -> None:
    """Adjusts the "match" operation to ignore header differences when matching a request.

    Be aware that wholly ignoring headers during matching might incur unexpected issues down the line. This method
    should be called during test case execution, rather than at a session, module, or class level.
    """

    x_recording_id = get_recording_id()
    _send_matcher_request("HeaderlessMatcher", {"x-recording-id": x_recording_id})


# ----------SANITIZERS----------
#
# A sanitizer is applied to recordings in two locations:
#
# - Before they are saved. (Affects the session as a whole as well as individual entries)
# - During playback, when a request comes in from a client. This means that only individual entry sanitizers apply in
#   this case.
#
# Sanitizers are optionally prefixed with a title that indicates where each sanitizer applies. These prefixes are:
#
# - Uri
# - Header
# - Body
# 
# For example, A sanitizer prefixed with Body will only ever operate on the request/response body. The target URI and
# request/response headers will be left unaffected.
#
# ------------------------------


def add_body_key_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that offers regex update of a specific JTokenPath within a returned body.

    For example, "TableName" within a json response body having its value replaced by whatever substitution is offered.

    :keyword str json_path: The SelectToken path (which could possibly match multiple entries) that will be used to
        select JTokens for value replacement.
    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex replace OR if groupForReplace is set, a substitution
        operation. Defaults to replacing the entire string.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("BodyKeySanitizer", request_args)


def add_body_regex_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that offers regex replace within a returned body.

    Specifically, this regex applies to the raw JSON of a body. If you are attempting to simply replace a specific key,
    add_body_key_sanitizer is probably more suitable.

    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex, or if a ``group_for_replace`` is provided, a
        substitution operation.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("BodyRegexSanitizer", request_args)


def add_body_string_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that cleans request and response bodies via straightforward string replacement.

    Specifically, this replacement applies to the raw JSON of a body. If you are attempting to simply replace a specific
    key, add_body_key_sanitizer is probably more suitable.

    :keyword str value: The substitution value.
    :keyword str target: A target string. This could contain special regex characters like "?()+*" but they will be
        treated as a literal.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("BodyStringSanitizer", request_args)


def add_continuation_sanitizer(**kwargs: "Any") -> None:
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


def add_general_regex_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that offers a general regex replace across request/response Body, Headers, and URI.

    For the body, this means regex applying to the raw JSON.

    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex, or if a ``group_for_replace`` is provided, a
        substitution operation.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("GeneralRegexSanitizer", request_args)


def add_general_string_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that cleans request and response URIs, headers, and bodies via string replacement.

    This sanitizer offers a value replace across request/response bodies, headers, and URIs. For the body, this means a
    string replacement applied directly to the raw JSON.

    :keyword str value: The substitution value.
    :keyword str target: A target string. This could contain special regex characters like "?()+*" but they will be
        treated as a literal.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("GeneralStringSanitizer", request_args)


def add_header_regex_sanitizer(**kwargs: "Any") -> None:
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
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("HeaderRegexSanitizer", request_args)


def add_header_string_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that cleans headers in a recording via straightforward string replacement.

    This sanitizer ONLY applies to the request/response headers -- bodies and URIs are left untouched.

    :keyword str key: The name of the header we're operating against.
    :keyword str target: A target string. This could contain special regex characters like "?()+*" but they will be
        treated as a literal.
    :keyword str value: The substitution value.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("HeaderStringSanitizer", request_args)


def add_oauth_response_sanitizer() -> None:
    """Registers a sanitizer that cleans out all request/response pairs that match an oauth regex in their URI."""

    _send_sanitizer_request("OAuthResponseSanitizer", {})


def add_remove_header_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that removes specified headers before saving a recording.

    :keyword str headers: A comma separated list. Should look like "Location, Transfer-Encoding" or something along
        those lines. Don't worry about whitespace between the commas separating each key. They will be ignored.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("RemoveHeaderSanitizer", request_args)


def add_uri_regex_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer for cleaning URIs via regex.

    :keyword str value: The substitution value.
    :keyword str regex: A regex. Can be defined as a simple regex, or if a ``group_for_replace`` is provided, a
        substitution operation.
    :keyword str group_for_replace: The capture group that needs to be operated upon. Do not provide if you're invoking
        a simple replacement operation.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("UriRegexSanitizer", request_args)


def add_uri_string_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that cleans URIs via straightforward string replacement.

    Runs a simple string replacement against the request/response URIs.

    :keyword str value: The substitution value.
    :keyword str target: A target string. This could contain special regex characters like "?()+*" but they will be
        treated as a literal.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("UriStringSanitizer", request_args)


def add_uri_subscription_id_sanitizer(**kwargs: "Any") -> None:
    """Registers a sanitizer that replaces subscription IDs in URIs.

    This sanitizer ONLY affects the URI of a request/response pair. Subscription IDs are replaced with
    "00000000-0000-0000-0000-000000000000" by default.

    :keyword str value: The fake subscription ID that will be placed where the real one is in the real request.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_sanitizer_request("UriSubscriptionIdSanitizer", request_args)


# ----------TRANSFORMS----------
#
# A transform extends functionality of the test proxy by applying to responses just before they are returned during
# playback mode.
#
# ------------------------------


def add_api_version_transform() -> None:
    """Registers a transform that copies a request's "api-version" header onto the response before returning it."""

    _send_transform_request("ApiVersionTransform", {})


def add_client_id_transform() -> None:
    """Registers a transform that copies a request's "x-ms-client-id" header onto the response before returning it."""

    _send_transform_request("ClientIdTransform", {})


def add_header_transform(**kwargs: "Any") -> None:
    """Registers a transform that sets a header in a response.

    :keyword str key: The key for the header.
    :keyword str value: The value for the header.
    :keyword str condition: A condition that dictates when this sanitizer applies to a request/response pair. The
        content of this should be a JSON object that contains configuration keys. Currently, that only includes the key
        "uriRegex". This translates to an object that looks like '{ "uriRegex": "when this regex matches, apply the
        sanitizer" }'. Defaults to "apply always".
    """

    request_args = _get_request_args(**kwargs)
    _send_transform_request("HeaderTransform", request_args)


def add_storage_request_id_transform() -> None:
    """Registers a transform that ensures a response's "x-ms-client-request-id" header matches the request's."""

    _send_transform_request("StorageRequestIdTransform", {})


# ----------RECORDING OPTIONS----------
#
# Recording options enable customization beyond what is offered by sanitizers, matchers, and transforms. These are
# intended for advanced scenarios and are generally not applicable.
#
# -------------------------------------


def set_function_recording_options(**kwargs: "Any") -> None:
    """Sets custom recording options for the current test only.

    This must be called during test case execution, rather than at a session, module, or class level. To set recording
    options for all tests, use `set_session_recording_options` instead.

    :keyword bool handle_redirects: The test proxy does not perform transparent follow directs by default. That means
        that if the initial request sent through the test proxy results in a 3XX redirect status, the test proxy will
        not follow. It will return that redirect response to the client and allow it to handle the redirect. Setting
        `handle_redirects` to True will set the proxy to instead handle redirects itself.
    :keyword str context_directory: This changes the "root" path that the test proxy uses when loading a recording.
    :keyword certificates: A list of `PemCertificate`s. Any number of certificates is allowed.
    :type certificates: Iterable[PemCertificate]
    :keyword str tls_certificate: The public key portion of a TLS certificate, as a string. This is used specifically so
        that an SSL connection presenting a non-standard certificate can still be validated.
    """

    x_recording_id = get_recording_id()
    request_args = _get_recording_option_args(**kwargs)
    _send_recording_options_request(request_args, {"x-recording-id": x_recording_id})


def set_session_recording_options(**kwargs: "Any") -> None:
    """Sets custom recording options for all tests.

    This will set the specified recording options for an entire test session. To set recording options for a single test
    -- which is recommended -- use `set_function_recording_options` instead.

    :keyword bool handle_redirects: The test proxy does not perform transparent follow directs by default. That means
        that if the initial request sent through the test proxy results in a 3XX redirect status, the test proxy will
        not follow. It will return that redirect response to the client and allow it to handle the redirect. Setting
        `handle_redirects` to True will set the proxy to instead handle redirects itself.
    :keyword str context_directory: This changes the "root" path that the test proxy uses when loading a recording.
    :keyword certificates: A list of `PemCertificate`s. Any number of certificates is allowed.
    :type certificates: Iterable[PemCertificate]
    :keyword str tls_certificate: The public key portion of a TLS certificate, as a string. This is used specifically so
        that an SSL connection presenting a non-standard certificate can still be validated.
    """

    request_args = _get_recording_option_args(**kwargs)
    _send_recording_options_request(request_args)


class PemCertificate:
    """Represents a PEM certificate that can be sent to and used by the test proxy.

    :param str data: The content of the certificate, as a string.
    :param str key: The certificate key, as a string.
    """

    def __init__(self, data: str, key: str) -> None:
        self.data = data
        self.key = key


# ----------HELPERS----------


def _get_recording_option_args(**kwargs: "Any") -> dict:
    """Returns a dictionary of recording option request arguments, formatted for test proxy consumption."""

    certificates = kwargs.pop("certificates", None)
    tls_certificate = kwargs.pop("tls_certificate", None)
    tls_certificate_host = kwargs.pop("tls_certificate_host", None)
    request_args = _get_request_args(**kwargs)

    if certificates or tls_certificate:
        transport = {}

        if certificates:
            cert_pairs = [{"PemValue": cert.data, "PemKey": cert.key} for cert in certificates]
            transport["Certificates"] = cert_pairs

        if tls_certificate:
            transport["TLSValidationCert"] = tls_certificate

        if tls_certificate_host:
            transport["TLSValidationCertHost"] = tls_certificate_host

        request_args["Transport"] = transport

    return request_args


def _get_request_args(**kwargs: "Any") -> dict:
    """Returns a dictionary of request arguments, formatted for test proxy consumption."""

    request_args = {}
    if "compare_bodies" in kwargs:
        request_args["compareBodies"] = kwargs.get("compare_bodies")
    if "condition" in kwargs:
        request_args["condition"] = kwargs.get("condition")
    if "context_directory" in kwargs:
        request_args["ContextDirectory"] = kwargs.get("context_directory")
    if "excluded_headers" in kwargs:
        request_args["excludedHeaders"] = kwargs.get("excluded_headers")
    if "group_for_replace" in kwargs:
        request_args["groupForReplace"] = kwargs.get("group_for_replace")
    if "handle_redirects" in kwargs:
        request_args["HandleRedirects"] = kwargs.get("handle_redirects")
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
    if "target" in kwargs:
        request_args["target"] = kwargs.get("target")
    if "value" in kwargs:
        request_args["value"] = kwargs.get("value")
    return request_args


def _send_matcher_request(matcher: str, headers: dict, parameters: "Optional[dict]" = None) -> None:
    """Sends a POST request to the test proxy endpoint to register the specified matcher.

    If live tests are being run, no request will be sent.

    :param str matcher: The name of the matcher to set.
    :param dict headers: Any matcher headers, as a dictionary.
    :param parameters: Any matcher constructor parameters, as a dictionary. Defaults to None.
    :type parameters: Optional[dict]
    """

    if is_live():
        return

    headers_to_send = {"x-abstraction-identifier": matcher}
    headers_to_send.update(headers)
    response = requests.post(
        f"{PROXY_URL}/Admin/SetMatcher",
        headers=headers_to_send,
        json=parameters
    )
    response.raise_for_status()


def _send_recording_options_request(parameters: dict, headers: "Optional[dict]" = None) -> None:
    """Sends a POST request to the test proxy endpoint to set the specified recording options.

    If live tests are being run with recording turned off via the AZURE_SKIP_LIVE_RECORDING environment variable, no
    request will be sent.

    :param dict parameters: The recording options, as a dictionary.
    :param headers: Any recording option request headers, as a dictionary. Defaults to None.
    :type headers: Optional[dict]
    """

    if is_live_and_not_recording():
        return

    response = requests.post(
        f"{PROXY_URL}/Admin/SetRecordingOptions",
        headers=headers,
        json=parameters
    )
    response.raise_for_status()


def _send_reset_request(headers: dict) -> None:
    """Sends a POST request to the test proxy endpoint to reset setting customizations.

    If live tests are being run with recording turned off via the AZURE_SKIP_LIVE_RECORDING environment variable, no
    request will be sent.

    :param dict headers: Any reset request headers, as a dictionary.
    """

    if is_live_and_not_recording():
        return

    response = requests.post(
        f"{PROXY_URL}/Admin/Reset",
        headers=headers
    )
    response.raise_for_status()


def _send_sanitizer_request(sanitizer: str, parameters: dict) -> None:
    """Sends a POST request to the test proxy endpoint to register the specified sanitizer.

    If live tests are being run with recording turned off via the AZURE_SKIP_LIVE_RECORDING environment variable, no
    request will be sent.

    :param str sanitizer: The name of the sanitizer to add.
    :param dict parameters: The sanitizer constructor parameters, as a dictionary.
    """

    if is_live_and_not_recording():
        return

    response = requests.post(
        f"{PROXY_URL}/Admin/AddSanitizer",
        headers={"x-abstraction-identifier": sanitizer, "Content-Type": "application/json"},
        json=parameters
    )
    response.raise_for_status()


def _send_transform_request(transform: str, parameters: dict) -> None:
    """Sends a POST request to the test proxy endpoint to register the specified transform.

    If live tests are being run, no request will be sent.

    :param str transform: The name of the transform to add.
    :param dict parameters: The transform constructor parameters, as a dictionary.
    """

    if is_live():
        return

    response = requests.post(
        f"{PROXY_URL}/Admin/AddTransform",
        headers={"x-abstraction-identifier": transform, "Content-Type": "application/json"},
        json=parameters
    )
    response.raise_for_status()
