# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
from urllib.parse import urlparse
from ._common import (
    EXPANDED_JSON_FILE_EXT,
    INVALID_DTMI_FORMAT,
    JSON_FILE_EXT,
)

def is_valid_dtmi(dtmi):
    """Checks validity of a DTMI

    A DTMI has three components: scheme, path, and version.
    Scheme and path are separated by a colon. Path and version are separated by a semicolon
    i.e. <scheme> : <path> ; <version>.
    The scheme is the string literal "dtmi" in lowercase. The path is a sequence of one or more segments,
    separated by colons.
    The version is a sequence of one or more digits. Each path segment is a non-empty string containing
    only letters, digits, and underscores.
    The first character may not be a digit, and the last character may not be an underscore.
    The version length is limited to nine digits, because the number 999,999,999 fits in a 32-bit signed
    integer value.
    The first digit may not be zero, so there is no ambiguity regarding whether version 1 matches version
    01 since the latter is invalid.

    :param str dtmi: DTMI

    :returns: Boolean indicating if DTMI is valid
    :rtype: bool
    """
    if not isinstance(dtmi, str):
        return False
    pattern = re.compile(
        "^dtmi:[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?(?::[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?)*;[1-9][0-9]{0,8}$"
    )
    if not pattern.match(dtmi):
        return False
    return True


def get_model_uri(dtmi, repository_uri, expanded=False):
    """Get the URI representing the absolute location of a model in a Models Repository

    :param str dtmi: DTMI for a model
    :param str repository_uri: URI for a Models Repository
    :param bool expanded: Indicates if the URI should be for an expanded model (Default: False)

    :raises: ValueError if given an invalid DTMI

    :returns: The URI for the model in the Models Repository
    :rtype: str
    """
    repository_uri = _add_scheme(repository_uri)
    if not repository_uri.endswith("/"):
        repository_uri += "/"

    dtmi_path = _convert_dtmi_to_path(dtmi, expanded)
    if not dtmi_path:
        raise ValueError(INVALID_DTMI_FORMAT.format(dtmi))

    return repository_uri + dtmi_path


def _convert_dtmi_to_path(dtmi, expanded=False):
    """Returns the relative path for a model given a DTMI
    E.g:
    dtmi:com:example:Thermostat;1 -> dtmi/com/example/thermostat-1.json
    Returns an empty string if the DTMI is invalid.

    :param str dtmi : DTMI for a model
    :param bool expanded: Indicates if the relative path should be for an exapnded model

    :returns: Relative path of the model in a Models Repository
    :rtype: str
    """
    if not is_valid_dtmi(dtmi):
        return ""
    dtmi_path = dtmi.lower().replace(":", "/").replace(";", "-") + JSON_FILE_EXT
    if expanded:
        dtmi_path = dtmi_path.replace(JSON_FILE_EXT, EXPANDED_JSON_FILE_EXT)
    return dtmi_path


def _add_scheme(uri):
    """Add the file scheme to local repository uri if needed.

    Specifically checks if the uri is a filesystem path with drive letters or not a web url
    with an unspecified protocol.

    :param str uri: URI for a Models Repository

    :returns: The URI for the metadata in the Models Repository
    :rtype: str
    """
    scheme = urlparse(uri).scheme
    if len(scheme) == 1 and scheme.isalpha():
        uri = "file:///" + uri.replace("\\", "/")
    elif scheme == "" and not re.search(
            r"\.[a-zA-z]{2,63}$",
            uri[: uri.find("/") if uri.find("/") >= 0 else len(uri)],
    ):
        uri = "file://" + uri.strip("\\").replace("\\", "/")

    return uri
