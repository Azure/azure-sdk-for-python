# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import json
import re
import time
from typing import TYPE_CHECKING, List, Dict
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from azure.core.exceptions import ServiceRequestError

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest

BEARER = "Bearer"
AUTHENTICATION_CHALLENGE_PARAMS_PATTERN = re.compile('(?:(\\w+)="([^""]*)")+')


def _is_tag(tag_or_digest):
    # type: (str) -> bool
    tag = tag_or_digest.split(":")
    return not (len(tag) == 2 and tag[0].startswith(u"sha"))


def _clean(matches):
    # type: (List[str]) -> None
    """This method removes empty strings and commas from the regex matching of the Challenge header"""
    while True:
        try:
            matches.remove("")
        except ValueError:
            break

    while True:
        try:
            matches.remove(",")
        except ValueError:
            return


def _parse_challenge(header):
    # type: (str) -> Dict[str, str]
    """Parse challenge header into service and scope"""
    ret = {}
    if header.startswith(BEARER):
        challenge_params = header[len(BEARER) + 1 :]

        matches = re.split(AUTHENTICATION_CHALLENGE_PARAMS_PATTERN, challenge_params)
        _clean(matches)
        ret = {}
        for i in range(0, len(matches), 2):
            ret[matches[i]] = matches[i + 1]

    return ret


def _parse_next_link(link_string):
    # type: (str) -> str
    """Parses the next link in the list operations response URL

    Per the Docker v2 HTTP API spec, the Link header is an RFC5988
    compliant rel='next' with URL to next result set, if available.
    See: https://docs.docker.com/registry/spec/api/

    The URI reference can be obtained from link-value as follows:
    Link       = "Link" ":" #link-value
    link-value = "<" URI-Reference ">" * (";" link-param )
    See: https://tools.ietf.org/html/rfc5988#section-5
    """
    if not link_string:
        return None
    return link_string[1 : link_string.find(">")]


def _enforce_https(request):
    # type: (PipelineRequest) -> None
    """Raise ServiceRequestError if the request URL is non-HTTPS and the sender did not specify enforce_https=False"""

    # move 'enforce_https' from options to context so it persists
    # across retries but isn't passed to a transport implementation
    option = request.context.options.pop("enforce_https", None)

    # True is the default setting; we needn't preserve an explicit opt in to the default behavior
    if option is False:
        request.context["enforce_https"] = option

    enforce_https = request.context.get("enforce_https", True)
    if enforce_https and not request.http_request.url.lower().startswith("https"):
        raise ServiceRequestError(
            "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
        )


def _host_only(url):
    # type: (str) -> str
    return urlparse(url).netloc


def _strip_alg(digest):
    if len(digest.split(":")) == 2:
        return digest.split(":")[1]
    return digest


def _parse_exp_time(raw_token):
    # type: (bytes) -> float
    value = raw_token.split(".")
    if len(value) > 2:
        value = value[1]
        padding = len(value) % 4
        if padding > 0:
            value += "=" * padding
        byte_value = base64.b64decode(value).decode("utf-8")
        web_token = json.loads(byte_value)
        return web_token.get("exp", time.time())

    return time.time()
