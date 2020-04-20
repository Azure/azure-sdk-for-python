# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import json
import os
import platform
import re
import sys
from typing import TYPE_CHECKING

import subprocess

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .. import CredentialUnavailableError
from .._internal import _scopes_to_resource

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any

CLI_NOT_FOUND = "Azure CLI not found on path"
COMMAND_LINE = "az account get-access-token --output json --resource {}"

# CLI's "expiresOn" is naive, so we use this naive datetime for the epoch to calculate expires_on in UTC
EPOCH = datetime.fromtimestamp(0)


class AzureCliCredential(object):
    """Authenticates by requesting a token from the Azure CLI.

    This requires previously logging in to Azure via "az login", and will use the CLI's currently logged in identity.
    """

    def get_token(self, *scopes, **kwargs):  # pylint:disable=no-self-use,unused-argument
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        This credential won't cache tokens. Every call invokes the Azure CLI.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke the Azure CLI.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked the Azure CLI but didn't
          receive an access token.
        """

        resource = _scopes_to_resource(*scopes)
        output, error = _run_command(COMMAND_LINE.format(resource))
        if error:
            raise error

        token = parse_token(output)
        if not token:
            sanitized_output = sanitize_output(output)
            raise ClientAuthenticationError(message="Unexpected output from Azure CLI: '{}'".format(sanitized_output))

        return token


def parse_token(output):
    """Parse output of 'az account get-access-token' to an AccessToken.

    In particular, convert the CLI's "expiresOn" value, the string representation of a naive datetime, to epoch seconds.
    """
    try:
        token = json.loads(output)
        parsed_expires_on = datetime.strptime(token["expiresOn"], "%Y-%m-%d %H:%M:%S.%f")

        # calculate seconds since the epoch; parsed_expires_on and EPOCH are naive
        expires_on = (parsed_expires_on - EPOCH).total_seconds()

        return AccessToken(token["accessToken"], int(expires_on))
    except (KeyError, ValueError):
        return None


def get_safe_working_dir():
    """Invoke 'az' from a directory controlled by the OS, not the executing program's directory"""

    if sys.platform.startswith("win"):
        path = os.environ.get("SYSTEMROOT")
        if not path:
            raise CredentialUnavailableError(message="Environment variable 'SYSTEMROOT' has no value")
        return path

    return "/bin"


def sanitize_output(output):
    """Redact access tokens from CLI output to prevent error messages revealing them"""
    return re.sub(r"\"accessToken\": \"(.*?)(\"|$)", "****", output)


def _run_command(command):
    if sys.platform.startswith("win"):
        args = ["cmd", "/c", command]
    else:
        args = ["/bin/sh", "-c", command]
    try:
        working_directory = get_safe_working_dir()

        kwargs = {"stderr": subprocess.STDOUT, "cwd": working_directory, "universal_newlines": True}
        if platform.python_version() >= "3.3":
            kwargs["timeout"] = 10

        output = subprocess.check_output(args, **kwargs)
        return output, None
    except subprocess.CalledProcessError as ex:
        # non-zero return from shell
        if ex.returncode == 127 or ex.output.startswith("'az' is not recognized"):
            error = CredentialUnavailableError(message=CLI_NOT_FOUND)
        else:
            # return code is from the CLI -> propagate its output
            if ex.output:
                message = sanitize_output(ex.output)
            else:
                message = "Failed to invoke Azure CLI"
            error = ClientAuthenticationError(message=message)
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'; CLI may or may not be installed
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
    except Exception as ex:  # pylint:disable=broad-except
        error = ex

    return None, error
