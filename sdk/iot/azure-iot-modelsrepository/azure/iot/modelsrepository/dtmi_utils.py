# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
import pathlib


def is_valid_dtmi(dtmi):
    """Checks validity of a DTMI

    :param dtmi str: DTMI

    :returns: Boolean indicating if DTMI is valid
    :rtype: bool
    """
    pattern = re.compile(
        "^dtmi:[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?(?::[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?)*;[1-9][0-9]{0,8}$"
    )
    if not pattern.match(dtmi):
        return False
    else:
        return True


def get_model_uri(dtmi, repository_uri, expanded=False):
    """Get the URI representing the absolute location of a model in a Models Repository 
    
    :param dtmi str: DTMI for a model
    :param repository_uri str: URI for a Models Repository
    :param expanded bool: Indicates if the URI should be for an expanded model (Default: False)

    :raises: ValueError if given an invalid DTMI

    :returns: The URI for the model in the Models Repository
    :rtype: str
    """
    if not repository_uri.endswith("/"):
        repository_uri += "/"
    model_uri = repository_uri + _convert_dtmi_to_path(dtmi)
    if expanded:
        model_uri.replace(".json", ".expanded.json")
    return model_uri


def _convert_dtmi_to_path(dtmi):
    """Returns the DTMI path for a DTMI
    E.g:
    dtmi:com:example:Thermostat;1 -> dtmi/com/example/thermostat-1.json

    :param dtmi str: DTMI

    :raises ValueError if DTMI is invalid

    :returns: Relative path 
    """
    pattern = re.compile(
        "^dtmi:[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?(?::[A-Za-z](?:[A-Za-z0-9_]*[A-Za-z0-9])?)*;[1-9][0-9]{0,8}$"
    )
    if not pattern.match(dtmi):
        raise ValueError("Invalid DTMI")
    else:
        return dtmi.lower().replace(":", "/").replace(";", "-") + ".json"
