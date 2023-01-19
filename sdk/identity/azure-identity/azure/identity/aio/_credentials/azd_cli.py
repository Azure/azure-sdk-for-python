# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
import shutil
import sys
from typing import Any, List, Optional

from azure.core.exceptions import ClientAuthenticationError
from azure.core.credentials import AccessToken
from .._internal import AsyncContextManager
from .._internal.decorators import log_get_token_async
from ... import CredentialUnavailableError
from ..._credentials.azd_cli import (
    AzureDeveloperCliCredential as _SyncAzureDeveloperCliCredential,
    CLI_NOT_FOUND,
    COMMAND_LINE,
    EXECUTABLE_NAME,
    get_safe_working_dir,
    NOT_LOGGED_IN,
    parse_token,
    sanitize_output,
)
from ..._internal import resolve_tenant


class AzureDeveloperCliCredential(AsyncContextManager):
    """Authenticates by requesting a token from the Azure Developer CLI.

    This requires previously logging in to Azure via "azd login", and will use the CLI's currently logged in identity.

    :keyword str tenant_id: Optional tenant to include in the token request.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(self, *, tenant_id: str = "", additionally_allowed_tenants: Optional[List[str]] = None):

        self.tenant_id = tenant_id
        self._additionally_allowed_tenants = additionally_allowed_tenants or []

    @log_get_token_async
    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients. Applications calling this method directly must
        also handle token caching because this credential doesn't cache the tokens it acquires.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
            For more information about scopes, see
            https://learn.microsoft.com/azure/active-directory/develop/scopes-oidc.
        :keyword str tenant_id: optional tenant to include in the token request.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke the Azure Developer CLI.
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked the Azure Developer CLI
          but didn't receive an access token.
        """
        # only ProactorEventLoop supports subprocesses on Windows (and it isn't the default loop on Python < 3.8)
        if sys.platform.startswith("win") and not isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
            return _SyncAzureDeveloperCliCredential().get_token(*scopes, **kwargs)

        if not scopes:
            raise ValueError("Missing scope in request. \n")

        commandString = " --scope ".join(scopes)
        command = COMMAND_LINE.format(commandString)
        tenant = resolve_tenant(
            default_tenant=self.tenant_id, additionally_allowed_tenants=self._additionally_allowed_tenants, **kwargs
        )

        if tenant:
            command += " --tenant-id " + tenant
        output = await _run_command(command)

        token = parse_token(output)
        if not token:
            sanitized_output = sanitize_output(output)
            raise ClientAuthenticationError(
                message="Unexpected output from Azure Developer CLI: '{}'. \n".format(sanitized_output)
            )

        return token

    async def close(self) -> None:
        """Calling this method is unnecessary"""


async def _run_command(command: str) -> str:
    # Ensure executable exists in PATH first. This avoids a subprocess call that would fail anyway.
    if shutil.which(EXECUTABLE_NAME) is None:
        raise CredentialUnavailableError(message=CLI_NOT_FOUND)

    if sys.platform.startswith("win"):
        args = ("cmd", "/c " + command)
    else:
        args = ("/bin/sh", "-c", command)

    working_directory = get_safe_working_dir()

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_directory,
            env=dict(os.environ, NO_COLOR="true")
        )
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), 10)
        output = stdout_b.decode()
        stderr = stderr_b.decode()
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'
        error = CredentialUnavailableError(message="Failed to execute '{}'".format(args[0]))
        raise error from ex
    except asyncio.TimeoutError as ex:
        proc.kill()
        raise CredentialUnavailableError(message="Timed out waiting for Azure Developer CLI") from ex

    if proc.returncode == 0:
        return output

    # Fallback check in case the executable is not found while executing subprocess.
    if proc.returncode == 127 or stderr.startswith("'azd' is not recognized"):
        raise CredentialUnavailableError(CLI_NOT_FOUND)

    if "not logged in, run `azd login` to login" in stderr:
        raise CredentialUnavailableError(message=NOT_LOGGED_IN)

    message = sanitize_output(stderr) if stderr else "Failed to invoke Azure Developer CLI"
    raise ClientAuthenticationError(message=message)
