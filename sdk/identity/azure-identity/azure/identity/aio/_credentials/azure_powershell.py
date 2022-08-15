# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import sys
from typing import cast, TYPE_CHECKING

from .._internal import AsyncContextManager
from .._internal.decorators import log_get_token_async
from ... import CredentialUnavailableError
from ..._credentials.azure_powershell import (
    AzurePowerShellCredential as _SyncCredential,
    get_command_line,
    get_safe_working_dir,
    raise_for_error,
    parse_token,
)
from ..._internal import resolve_tenant

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any, List
    from azure.core.credentials import AccessToken


class AzurePowerShellCredential(AsyncContextManager):
    """Authenticates by requesting a token from Azure PowerShell.

    This requires previously logging in to Azure via "Connect-AzAccount", and will use the currently logged in identity.
    """

    @log_get_token_async
    async def get_token(
        self, *scopes: str, **kwargs: "Any"
    ) -> "AccessToken":  # pylint:disable=no-self-use,unused-argument
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
        # only ProactorEventLoop supports subprocesses on Windows (and it isn't the default loop on Python < 3.8)
        if sys.platform.startswith("win") and not isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
            return _SyncCredential().get_token(*scopes, **kwargs)

        tenant_id = resolve_tenant("", **kwargs)
        command_line = get_command_line(scopes, tenant_id)
        output = await run_command_line(command_line)
        token = parse_token(output)
        return token

    async def close(self) -> None:
        """Calling this method is unnecessary"""


async def run_command_line(command_line: "List[str]") -> str:
    try:
        proc = await start_process(command_line)
        stdout, stderr = await asyncio.wait_for(proc.communicate(), 10)
        if sys.platform.startswith("win") and b"' is not recognized" in stderr:
            # pwsh.exe isn't on the path; try powershell.exe
            command_line[-1] = command_line[-1].replace("pwsh", "powershell", 1)
            proc = await start_process(command_line)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), 10)

    except OSError as ex:
        # failed to execute "cmd" or "/bin/sh"; Azure PowerShell may or may not be installed
        error = CredentialUnavailableError(
            message='Failed to execute "{}".\n'
                    'To mitigate this issue, please refer to the troubleshooting guidelines here at '
                    'https://aka.ms/azsdk/python/identity/powershellcredential/troubleshoot.'.format(command_line[0]))
        raise error from ex
    except asyncio.TimeoutError as ex:
        proc.kill()
        raise CredentialUnavailableError(
            message="Timed out waiting for Azure PowerShell.\n"
                    "To mitigate this issue, please refer to the troubleshooting guidelines here at "
                    "https://aka.ms/azsdk/python/identity/powershellcredential/troubleshoot.") from ex

    decoded_stdout = stdout.decode()

    # casting because mypy infers Optional[int]; however, when proc.returncode is None,
    # we handled TimeoutError above and therefore don't execute this line
    raise_for_error(cast(int, proc.returncode), decoded_stdout, stderr.decode())
    return decoded_stdout


async def start_process(command_line):
    working_directory = get_safe_working_dir()
    proc = await asyncio.create_subprocess_exec(
        *command_line,
        cwd=working_directory,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return proc
