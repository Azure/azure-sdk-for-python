# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re


def is_valid_dtmi(dtmi):
    """Checks validity of a DTMI

    :param str dtmi: DTMI

    :returns: Boolean indicating if DTMI is valid
    :rtype: bool
    """
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
    if not repository_uri.endswith("/"):
        repository_uri += "/"
    model_uri = repository_uri + _convert_dtmi_to_path(dtmi, expanded)
    return model_uri


def _convert_dtmi_to_path(dtmi, expanded=False):
    """Returns the relative path for a model given a DTMI
    E.g:
    dtmi:com:example:Thermostat;1 -> dtmi/com/example/thermostat-1.json

    :param str dtmi : DTMI for a model
    :param bool expanded: Indicates if the relative path should be for an exapnded model

    :raises ValueError if DTMI is invalid

    :returns: Relative path of the model in a Models Repository
    :rtype: str
    """
    if not is_valid_dtmi(dtmi):
        raise ValueError("Invalid DTMI")
    dtmi_path = dtmi.lower().replace(":", "/").replace(";", "-") + ".json"
    if expanded:
        dtmi_path = dtmi_path.replace(".json", ".expanded.json")
    return dtmi_path
