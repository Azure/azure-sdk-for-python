# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import re

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