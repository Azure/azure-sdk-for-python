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
