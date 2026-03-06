# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

COMMUNICATION_CUSTOM_ENDPOINT_ENABLED = "COMMUNICATION_CUSTOM_ENDPOINT_ENABLED"
COMMUNICATION_CUSTOM_URL = "COMMUNICATION_CUSTOM_URL"


def get_custom_enabled():
    """From environment variable, get whether to use a custom endpoint.
    This is only for development purposes.

    :return: custom_enabled
    :rtype: bool
    """
    custom_enabled_str = get_environment_variable(COMMUNICATION_CUSTOM_ENDPOINT_ENABLED)

    if custom_enabled_str is not None:
        return custom_enabled_str.lower() == "true"
    return False


def get_custom_url():
    """From environment variable, get the acs endpoint to call.
    This is only for development purposes.

    :return: custom_url
    :rtype: str
    """
    return get_environment_variable(COMMUNICATION_CUSTOM_URL)


def get_environment_variable(variable_name):
    """From environment variable, from variable name.
    This is only for development purposes

    :param variable_name: key of the environment variable
    :type variable_name: str
    :return: environment variable value
    :rtype: str
    """
    return os.environ.get(variable_name)
