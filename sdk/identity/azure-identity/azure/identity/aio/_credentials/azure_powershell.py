# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import sys
from typing import cast, TYPE_CHECKING

from .._internal.decorators import log_get_token_async
from ... import CredentialUnavailableError
from ..._credentials.azure_powershell import (
    AzurePowerShellCredential as _SyncCredential,
    get_command_line,
    get_safe_working_dir,
    raise_for_error,
    parse_token,
)

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any, Tuple
    from azure.core.credentials import AccessToken



class AzurePowerShellCredential:
    """Authenticates by requesting a token from Azure PowerShell.

    This requires previously logging in to Azure via "Connect-AzAccount", and will use the currently logged in identity.

    :keyword bool use_legacy_powershell: Can only be set on Windows. Defaults to False. If True, the credential will
        use PowerShell version 5 or lower, i.e. not PowerShell Core (version 6+).
    """

    def __init__(self, **kwargs: "Any") -> None:
        self._use_legacy_powershell = kwargs.get("use_legacy_powershell", False)
        if self._use_legacy_powershell and not sys.platform.startswith("win"):
            raise ValueError('"use_legacy_powershell" is supported only on Windows')

    @log_get_token_async
    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients. Applications calling this method directly must
        also handle token caching because this credential doesn't cache the tokens it acquires.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises ~azure.identity.CredentialUnavailableError: the credential was unable to invoke Azure PowerShell, or
          no account is authenticated
        :raises ~azure.core.exceptions.ClientAuthenticationError: the credential invoked Azure PowerShell but didn't
          receive an access token
        """
        # only ProactorEventLoop supports subprocesses on Windows (and it isn't the default loop on Python < 3.8)
        if sys.platform.startswith("win") and not isinstance(asyncio.get_event_loop(), asyncio.ProactorEventLoop):
            return _SyncCredential(use_legacy_powershell=self._use_legacy_powershell).get_token(*scopes, **kwargs)

        command_line = get_command_line(scopes, self._use_legacy_powershell)
        output = await run_command(command_line)
        token = parse_token(output)
        return token


async def run_command(args: "Tuple") -> str:
    working_directory = get_safe_working_dir()

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=working_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), 10)
    except OSError as ex:
        # failed to execute 'cmd' or '/bin/sh'; Azure PowerShell may or may not be installed
        error = CredentialUnavailableError(message='Failed to execute "{}"'.format(args[0]))
        raise error from ex
    except asyncio.TimeoutError as ex:
        raise CredentialUnavailableError(message="Timed out waiting for Azure PowerShell") from ex

    decoded_stdout = stdout.decode()

    # casting because mypy infers Optional[int]; however, when proc.returncode is None,
    # we handled TimeoutError above and therefore don't execute this line
    raise_for_error(cast(int, proc.returncode), decoded_stdout, stderr.decode())
    return decoded_stdout
