# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
from six import string_types
from six.moves import urllib
from ._common import INVALID_DTMI_FORMAT

def is_valid_dtmi(dtmi):
    """Checks validity of a DTMI

    :param str dtmi: DTMI

    :returns: Boolean indicating if DTMI is valid
    :rtype: bool
    """
    if not isinstance(dtmi, string_types):
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
    dtmi_path = dtmi.lower().replace(":", "/").replace(";", "-") + ".json"
    if expanded:
        dtmi_path = dtmi_path.replace(".json", ".expanded.json")
    return dtmi_path


def _add_scheme(uri):
    """Add the file scheme to local repository uri if needed.

    Specifically checks if the uri is a filesystem path with drive letters or not a web url
    with an unspecified protocol.

    :param str uri: URI for a Models Repository

    :returns: The URI for the metadata in the Models Repository
    :rtype: str
    """
    scheme = urllib.parse.urlparse(uri).scheme
    if len(scheme) == 1 and scheme.isalpha():
        uri = "file:///" + uri.replace("\\", "/")
    elif scheme == "" and not re.search(
            r"\.[a-zA-z]{2,63}$",
            uri[: uri.find("/") if uri.find("/") >= 0 else len(uri)],
    ):
        uri = "file://" + uri.strip("\\").replace("\\", "/")

    return uri
