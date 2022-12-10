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
from .._internal.decorators import log_get_token

CLI_NOT_FOUND = "Azure Developer CLI could not be found. Please visit https://aka.ms/azure-dev for installation instructions and then, once installed, authenticate to your Azure account using 'azd login'."
COMMAND_LINE = "azd auth token --output json --scope {}"
NOT_LOGGED_IN = "Please run 'azd login' from a command prompt to authenticate before using this credential."


class AzureDeveloperCliCredential(object):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def close(self) -> None:
        """Calling this method is unnecessary."""

    @log_get_token("AzureDeveloperCliCredential")
    def get_token(self, *scopes: str, **kwargs) -> AccessToken:
        commandString = ' --scope '.join(scopes)
        command = COMMAND_LINE.format(commandString)
        output = _run_command(command)
        token = parse_token(output)
        if not token:
            sanitized_output = sanitize_output(output)
            raise ClientAuthenticationError(
                message="Unexpected output from Azure Developer CLI: '{}'. \n".format(sanitized_output))

        return token


def parse_token(output):
    try:
        token = json.loads(output)
        dt = datetime.strptime(token["expiresOn"], "%Y-%m-%dT%H:%M:%SZ")
        expires_on = dt.timestamp()

        return AccessToken(token["token"], int(expires_on))
    except (KeyError, ValueError):
        return None


def get_safe_working_dir():
    if sys.platform.startswith("win"):
        path = os.environ.get("SYSTEMROOT")
        if not path:
            raise CredentialUnavailableError(message="Azure Developer CLI credential expects a 'SystemRoot' environment variable")
        return path

    return "/bin"


def sanitize_output(output):
    """Redact tokens from CLI output to prevent error messages revealing them"""
    return re.sub(r"\"token\": \"(.*?)(\"|$)", "****", output)


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
            "env": dict(os.environ, NO_COLOR="true"),
            "timeout": 10,
        }

        return subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError as ex:
        # non-zero return from shell
        if ex.returncode == 127 or ex.stderr.startswith("'azd' is not recognized"):
            raise CredentialUnavailableError(message=CLI_NOT_FOUND)
        if "not logged in, run `azd login` to login" in ex.stderr:
            raise CredentialUnavailableError(message=NOT_LOGGED_IN)

        # return code is from the CLI -> propagate its output
        if ex.stderr:
            message = sanitize_output(ex.stderr)
        else:
            message = "Failed to invoke Azure Developer CLI"
        raise ClientAuthenticationError(message=message)
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'; CLI may or may not be installed
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
        six.raise_from(error, ex)
    except Exception as ex:  # pylint:disable=broad-except
        # could be a timeout, for example
        error = CredentialUnavailableError(message="Failed to invoke the Azure Developer CLI")
        six.raise_from(error, ex)
        