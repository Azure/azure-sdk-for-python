# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import logging
import platform
import subprocess
import sys
from typing import List, Any, Tuple

import six

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .azure_cli import get_safe_working_dir
from .. import CredentialUnavailableError
from .._internal import _scopes_to_resource, resolve_tenant
from .._internal.decorators import log_get_token


_LOGGER = logging.getLogger(__name__)

AZ_ACCOUNT_NOT_INSTALLED = "Az.Account module >= 2.2.0 is not installed"
BLOCKED_BY_EXECUTION_POLICY = "Execution policy prevented invoking Azure PowerShell"
NO_AZ_ACCOUNT_MODULE = "NO_AZ_ACCOUNT_MODULE"
POWERSHELL_NOT_INSTALLED = "PowerShell is not installed"
RUN_CONNECT_AZ_ACCOUNT = 'Please run "Connect-AzAccount" to set up account'
SCRIPT = """$ErrorActionPreference = 'Stop'
[version]$minimumVersion = '2.2.0'

$m = Import-Module Az.Accounts -MinimumVersion $minimumVersion -PassThru -ErrorAction SilentlyContinue

if (! $m) {{
    Write-Output {}
    exit
}}

$token = Get-AzAccessToken -ResourceUrl '{}'{}

Write-Output "`nazsdk%$($token.Token)%$($token.ExpiresOn.ToUnixTimeSeconds())`n"
"""


class AzurePowerShellCredential(object):
    """Authenticates by requesting a token from Azure PowerShell.

    This requires previously logging in to Azure via "Connect-AzAccount", and will use the currently logged in identity.

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

    @log_get_token("AzurePowerShellCredential")
    def get_token(self, *scopes: str, **kwargs) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients. Applications calling this method directly must
        also handle token caching because this credential doesn't cache the tokens it acquires.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :keyword str tenant_id: optional tenant to include in the token request.

        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke Azure PowerShell, or
          no account is authenticated
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked Azure PowerShell but didn't
          receive an access token
        """
        tenant_id = resolve_tenant(
            default_tenant=self.tenant_id,
            additionally_allowed_tenants=self._additionally_allowed_tenants,
            **kwargs
        )
        command_line = get_command_line(scopes, tenant_id)
        output = run_command_line(command_line)
        token = parse_token(output)
        return token


def run_command_line(command_line: List[str]) -> str:
    stdout = stderr = ""
    proc = None
    kwargs = {}
    if platform.python_version() >= "3.3":
        kwargs["timeout"] = 10

    try:
        proc = start_process(command_line)
        stdout, stderr = proc.communicate(**kwargs)
        if sys.platform.startswith("win") and "' is not recognized" in stderr:
            # pwsh.exe isn't on the path; try powershell.exe
            command_line[-1] = command_line[-1].replace("pwsh", "powershell", 1)
            proc = start_process(command_line)
            stdout, stderr = proc.communicate(**kwargs)

    except Exception as ex:  # pylint:disable=broad-except
        # failed to execute "cmd" or "/bin/sh", or timed out; PowerShell and Az.Account may or may not be installed
        # (handling Exception here because subprocess.SubprocessError and .TimeoutExpired were added in 3.3)
        if proc and not proc.returncode:
            proc.kill()
        error = CredentialUnavailableError(
            message="Failed to invoke PowerShell.\n"
                    "To mitigate this issue, please refer to the troubleshooting guidelines here at "
                    "https://aka.ms/azsdk/python/identity/powershellcredential/troubleshoot.")
        six.raise_from(error, ex)

    raise_for_error(proc.returncode, stdout, stderr)
    return stdout


def start_process(args):
    # type: (List[str]) -> subprocess.Popen
    working_directory = get_safe_working_dir()
    proc = subprocess.Popen(
        args,
        cwd=working_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    return proc


def parse_token(output):
    # type: (str) -> AccessToken
    for line in output.split():
        if line.startswith("azsdk%"):
            _, token, expires_on = line.split("%")
            return AccessToken(token, int(expires_on))

    raise ClientAuthenticationError(message='Unexpected output from Get-AzAccessToken: "{}"'.format(output))


def get_command_line(scopes, tenant_id):
    # type: (Tuple, str) -> List[str]
    if tenant_id:
        tenant_argument = " -TenantId " + tenant_id
    else:
        tenant_argument = ""
    resource = _scopes_to_resource(*scopes)
    script = SCRIPT.format(NO_AZ_ACCOUNT_MODULE, resource, tenant_argument)
    encoded_script = base64.b64encode(script.encode("utf-16-le")).decode()

    command = "pwsh -NonInteractive -EncodedCommand " + encoded_script
    if sys.platform.startswith("win"):
        return ["cmd", "/c", command]
    return ["/bin/sh", "-c", command]


def raise_for_error(return_code, stdout, stderr):
    # type: (int, str, str) -> None
    if return_code == 0:
        if NO_AZ_ACCOUNT_MODULE in stdout:
            raise CredentialUnavailableError(AZ_ACCOUNT_NOT_INSTALLED)
        return

    if return_code == 127 or "' is not recognized" in stderr:
        raise CredentialUnavailableError(message=POWERSHELL_NOT_INSTALLED)
    if "Run Connect-AzAccount to login" in stderr:
        raise CredentialUnavailableError(message=RUN_CONNECT_AZ_ACCOUNT)
    if "AuthorizationManager check failed" in stderr:
        raise CredentialUnavailableError(message=BLOCKED_BY_EXECUTION_POLICY)

    if stderr:
        # stderr is too noisy to include with an exception but may be useful for debugging
        _LOGGER.debug('%s received an error from Azure PowerShell: "%s"', AzurePowerShellCredential.__name__, stderr)
    raise CredentialUnavailableError(message="Failed to invoke PowerShell")
