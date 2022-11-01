# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import json
import os
import platform
import re
import subprocess
import sys
import time
from typing import Any, List

import six

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .. import CredentialUnavailableError
from .._internal import _scopes_to_resource, resolve_tenant
from .._internal.decorators import log_get_token


CLI_NOT_FOUND = "Azure CLI not found on path"
COMMAND_LINE = "az account get-access-token --output json --resource {}"
NOT_LOGGED_IN = "Please run 'az login' to set up an account"


class AzureCliCredential(object):
    """Authenticates by requesting a token from the Azure CLI.

    This requires previously logging in to Azure via "az login", and will use the CLI's currently logged in identity.

    :keyword str tenant_id: Optional tenant to include in the token request.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """
    def __init__(self, *, tenant_id: str = "", additionally_allowed_tenants: List[str] = None):

        self.tenant_id = tenant_id
        self._additionally_allowed_tenants = additionally_allowed_tenants or []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def close(self) -> None:
        """Calling this method is unnecessary."""

    @log_get_token("AzureCliCredential")
    def get_token(self, *scopes: str, **kwargs) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients. Applications calling this method directly must
        also handle token caching because this credential doesn't cache the tokens it acquires.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :keyword str tenant_id: optional tenant to include in the token request.

        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke the Azure CLI.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked the Azure CLI but didn't
          receive an access token.
        """

        resource = _scopes_to_resource(*scopes)
        command = COMMAND_LINE.format(resource)
        tenant = resolve_tenant(
            default_tenant=self.tenant_id,
            additionally_allowed_tenants=self._additionally_allowed_tenants,
            **kwargs
        )
        if tenant:
            command += " --tenant " + tenant
        output = _run_command(command)

        token = parse_token(output)
        if not token:
            sanitized_output = sanitize_output(output)
            raise ClientAuthenticationError(
                message="Unexpected output from Azure CLI: '{}'. \n"
                        "To mitigate this issue, please refer to the troubleshooting guidelines here at "
                        "https://aka.ms/azsdk/python/identity/azclicredential/troubleshoot.".format(sanitized_output))

        return token


def parse_token(output):
    """Parse output of 'az account get-access-token' to an AccessToken.

    In particular, convert the "expiresOn" value to epoch seconds. This value is a naive local datetime as returned by
    datetime.fromtimestamp.
    """
    try:
        token = json.loads(output)
        dt = datetime.strptime(token["expiresOn"], "%Y-%m-%d %H:%M:%S.%f")
        if hasattr(dt, "timestamp"):
            # Python >= 3.3
            expires_on = dt.timestamp()
        else:
            # taken from Python 3.5's datetime.timestamp()
            expires_on = time.mktime((dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, -1, -1, -1))

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

        kwargs = {
            "stderr": subprocess.PIPE,
            "cwd": working_directory,
            "universal_newlines": True,
            "env": dict(os.environ, AZURE_CORE_NO_COLOR="true"),
        }
        if platform.python_version() >= "3.3":
            kwargs["timeout"] = 10

        return subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError as ex:
        # non-zero return from shell
        if ex.returncode == 127 or ex.stderr.startswith("'az' is not recognized"):
            raise CredentialUnavailableError(message=CLI_NOT_FOUND)
        if "az login" in ex.stderr or "az account set" in ex.stderr:
            raise CredentialUnavailableError(message=NOT_LOGGED_IN)

        # return code is from the CLI -> propagate its output
        if ex.stderr:
            message = sanitize_output(ex.stderr)
        else:
            message = "Failed to invoke Azure CLI"
        raise ClientAuthenticationError(message=message)
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'; CLI may or may not be installed
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
        six.raise_from(error, ex)
    except Exception as ex:  # pylint:disable=broad-except
        # could be a timeout, for example
        error = CredentialUnavailableError(message="Failed to invoke the Azure CLI")
        six.raise_from(error, ex)
