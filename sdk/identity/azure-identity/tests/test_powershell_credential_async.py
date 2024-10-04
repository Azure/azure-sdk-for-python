# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import base64
from itertools import product
import logging
import re
import sys
import time
from unittest.mock import Mock, patch

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import CredentialUnavailableError
from azure.identity.aio import AzurePowerShellCredential
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.azure_powershell import (
    AZ_ACCOUNT_NOT_INSTALLED,
    BLOCKED_BY_EXECUTION_POLICY,
    NO_AZ_ACCOUNT_MODULE,
    POWERSHELL_NOT_INSTALLED,
    RUN_CONNECT_AZ_ACCOUNT,
)
import pytest

from credscan_ignore import POWERSHELL_INVALID_OPERATION_EXCEPTION, POWERSHELL_NOT_LOGGED_IN_ERROR
from helpers import INVALID_CHARACTERS, GET_TOKEN_METHODS
from helpers_async import get_completed_future
from test_powershell_credential import PREPARING_MODULES

pytestmark = pytest.mark.asyncio

CREATE_SUBPROCESS_EXEC = AzurePowerShellCredential.__module__ + ".asyncio.create_subprocess_exec"


def get_mock_exec(return_code=0, stdout="", stderr=""):
    communicate = Mock(return_value=get_completed_future((stdout.encode(), stderr.encode())))
    return Mock(return_value=get_completed_future(Mock(communicate=communicate, returncode=return_code)))


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        await getattr(AzurePowerShellCredential(), get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_multiple_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with pytest.raises(ValueError):
        await getattr(AzurePowerShellCredential(), get_token_method)("one scope", "and another")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cannot_execute_shell(get_token_method):
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with patch(CREATE_SUBPROCESS_EXEC, Mock(side_effect=OSError)):
        with pytest.raises(CredentialUnavailableError):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_invalid_tenant_id(get_token_method):
    """Invalid tenant IDs should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            AzurePowerShellCredential(tenant_id="tenant" + c)

        with pytest.raises(ValueError):
            kwargs = {"tenant_id": "tenant" + c}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            await getattr(AzurePowerShellCredential(), get_token_method)("scope", **kwargs)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_invalid_scopes(get_token_method):
    """Scopes with invalid characters should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope" + c)


@pytest.mark.parametrize("stderr,get_token_method", product(("", PREPARING_MODULES), GET_TOKEN_METHODS))
async def test_get_token(stderr, get_token_method):
    """The credential should parse Azure PowerShell's output to an AccessToken"""

    expected_access_token = "access"
    expected_expires_on = 1617923581
    scope = "scope"
    stdout = "azsdk%{}%{}".format(expected_access_token, expected_expires_on)

    mock_exec = get_mock_exec(stdout=stdout, stderr=stderr)
    with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
        token = await getattr(AzurePowerShellCredential(), get_token_method)(scope)

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on

    assert mock_exec.call_count == 1
    args, kwargs = mock_exec.call_args
    command = args[-1]
    assert command.startswith("pwsh -NoProfile -NonInteractive -EncodedCommand ")

    match = re.search(r"-EncodedCommand\s+(\S+)", command)
    assert match, "couldn't find encoded script in command line"
    encoded_script = match.groups()[0]
    decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
    assert "tenantId = ''" in decoded_script
    assert f"'ResourceUrl' = '{scope}'" in decoded_script

    assert mock_exec().result().communicate.call_count == 1


@pytest.mark.parametrize("stderr,get_token_method", product(("", PREPARING_MODULES), GET_TOKEN_METHODS))
async def test_get_token_tenant_id(stderr, get_token_method):
    expected_access_token = "access"
    expected_expires_on = 1617923581
    scope = "scope"
    stdout = "azsdk%{}%{}".format(expected_access_token, expected_expires_on)

    mock_exec = get_mock_exec(stdout=stdout, stderr=stderr)
    with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
        kwargs = {"tenant_id": "tenant-id"}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = await getattr(AzurePowerShellCredential(), get_token_method)(scope, **kwargs)

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_ignores_extraneous_stdout_content(get_token_method):
    expected_access_token = "access"
    expected_expires_on = 1617923581
    motd = "MOTD: Customize your experience: save your profile to $HOME/.config/PowerShell\n"
    mock_exec = get_mock_exec(stdout=motd + "azsdk%{}%{}".format(expected_access_token, expected_expires_on))

    with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
        token = await getattr(AzurePowerShellCredential(), get_token_method)("scope")

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_az_powershell_not_installed(get_token_method):
    """The credential should raise CredentialUnavailableError when Azure PowerShell isn't installed"""

    with patch(CREATE_SUBPROCESS_EXEC, get_mock_exec(stdout=NO_AZ_ACCOUNT_MODULE)):
        with pytest.raises(CredentialUnavailableError, match=AZ_ACCOUNT_NOT_INSTALLED):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize(
    "stderr,get_token_method",
    product(
        (
            "'pwsh' is not recognized as an internal or external command,\r\noperable program or batch file.",
            "'powershell' is not recognized as an internal or external command,\r\noperable program or batch file.",
        ),
        GET_TOKEN_METHODS,
    ),
)
async def test_powershell_not_installed_cmd(stderr, get_token_method):
    """The credential should raise CredentialUnavailableError when PowerShell isn't installed"""

    mock_exec = get_mock_exec(return_code=1, stderr=stderr)
    with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
        with pytest.raises(CredentialUnavailableError, match=POWERSHELL_NOT_INSTALLED):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_powershell_not_installed_sh(get_token_method):
    """The credential should raise CredentialUnavailableError when PowerShell isn't installed"""

    mock_exec = get_mock_exec(return_code=127, stderr="/bin/sh: 0: Can't open pwsh")
    with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
        with pytest.raises(CredentialUnavailableError, match=POWERSHELL_NOT_INSTALLED):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize(
    "stderr,get_token_method",
    product((POWERSHELL_INVALID_OPERATION_EXCEPTION, POWERSHELL_NOT_LOGGED_IN_ERROR), GET_TOKEN_METHODS),
)
async def test_not_logged_in(stderr, get_token_method):
    """The credential should raise CredentialUnavailableError when a user isn't logged in to Azure PowerShell"""

    mock_exec = get_mock_exec(return_code=1, stderr=stderr)
    with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
        with pytest.raises(CredentialUnavailableError, match=RUN_CONNECT_AZ_ACCOUNT):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_blocked_by_execution_policy(get_token_method):
    """The credential should raise CredentialUnavailableError when execution policy blocks Get-AzAccessToken"""

    stderr = r"""#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><S S="Error">Import-Module : Errors occurred while loading the format data file: _x000D__x000A_</S><S S="Error">C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.format.ps1xml, , C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.format.ps1xml: The file was skipped because of the _x000D__x000A_</S><S S="Error">following validation exception: AuthorizationManager check failed.._x000D__x000A_</S><S S="Error">C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.generated.format.ps1xml, , C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.generated.format.ps1xml: The file was skipped _x000D__x000A_</S><S S="Error">because of the following validation exception: AuthorizationManager check failed.._x000D__x000A_</S><S S="Error">At line:4 char:6_x000D__x000A_</S><S S="Error">+ $m = Import-Module Az.Accounts -MinimumVersion $minimumVersion -PassT ..._x000D__x000A_</S><S S="Error">+      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~_x000D__x000A_</S><S S="Error">    + CategoryInfo          : InvalidOperation: (:) [Import-Module], RuntimeException_x000D__x000A_</S><S S="Error">    + FullyQualifiedErrorId : FormatXmlUpdateException,Microsoft.PowerShell.Commands.ImportModuleCommand_x000D__x000A_</S><S S="Error"> _x000D__x000A_</S></Objs>"""
    mock_exec = get_mock_exec(return_code=1, stderr=stderr)
    with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
        with pytest.raises(CredentialUnavailableError, match=BLOCKED_BY_EXECUTION_POLICY):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_timeout(get_token_method):
    """The credential should kill the subprocess after a timeout"""

    proc = Mock(communicate=Mock(side_effect=asyncio.TimeoutError), returncode=None)
    with patch(CREATE_SUBPROCESS_EXEC, Mock(return_value=get_completed_future(proc))):
        with pytest.raises(CredentialUnavailableError):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope")

    assert proc.communicate.call_count == 1


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_unexpected_error(get_token_method):
    """The credential should log stderr when Get-AzAccessToken returns an unexpected error"""

    class MockHandler(logging.Handler):
        def __init__(self):
            super(MockHandler, self).__init__()
            self.messages = []

        def emit(self, record):
            self.messages.append(record)

    mock_handler = MockHandler()
    logger = logging.getLogger("azure.identity")
    logger.addHandler(mock_handler)
    logger.setLevel(logging.DEBUG)

    expected_output = "something went wrong"
    mock_exec = get_mock_exec(return_code=42, stderr=expected_output)
    with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
        with pytest.raises(ClientAuthenticationError):
            await getattr(AzurePowerShellCredential(), get_token_method)("scope")

    for message in mock_handler.messages:
        if message.levelname == "DEBUG" and expected_output in message.message:
            return

    assert False, "Credential should have included stderr in a DEBUG level message"


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_windows_event_loop(get_token_method):
    """The credential should fall back to the sync implementation when not using ProactorEventLoop on Windows"""

    sync_get_token = Mock()
    credential = AzurePowerShellCredential()

    with patch(AzurePowerShellCredential.__module__ + "._SyncCredential") as fallback:
        fallback.return_value = Mock(
            spec_set=["get_token", "get_token_info"],
            get_token=sync_get_token,
            get_token_info=sync_get_token,
        )
        with patch(AzurePowerShellCredential.__module__ + ".asyncio.get_event_loop"):
            # asyncio.get_event_loop now returns Mock, i.e. never ProactorEventLoop
            await getattr(credential, get_token_method)("scope")

    assert sync_get_token.call_count == 1


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
@pytest.mark.parametrize(
    "error_message",
    (
        "'pwsh' is not recognized as an internal or external command,\r\noperable program or batch file.",
        "some other message",
    ),
)
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_windows_powershell_fallback(error_message, get_token_method):
    """On Windows, the credential should fall back to powershell.exe when pwsh.exe isn't on the path"""

    calls = 0

    async def mock_exec(*args, **kwargs):
        assert args[:2] == ("cmd", "/c")
        nonlocal calls
        calls += 1
        if args[-1].startswith("pwsh"):
            assert calls == 1, 'credential should invoke "pwsh" only once'
            stdout = ""
            stderr = error_message
            return_code = 9009
        else:
            assert args[-1].startswith("powershell"), 'credential should fall back to "powershell"'
            stdout = NO_AZ_ACCOUNT_MODULE
            stderr = ""
            return_code = 0

        communicate = Mock(return_value=get_completed_future((stdout.encode(), stderr.encode())))
        return Mock(communicate=communicate, returncode=return_code)

    credential = AzurePowerShellCredential()
    with pytest.raises(CredentialUnavailableError, match=AZ_ACCOUNT_NOT_INSTALLED):
        with patch(CREATE_SUBPROCESS_EXEC, mock_exec):
            await getattr(credential, get_token_method)("scope")

    assert calls == 2


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_multitenant_authentication(get_token_method):
    first_token = "***"
    second_tenant = "12345"
    second_token = first_token * 2

    async def fake_exec(*args, **_):
        command = args[2]
        assert command.startswith("pwsh -NoProfile -NonInteractive -EncodedCommand ")
        match = re.search(r"-EncodedCommand\s+(\S+)", command)
        assert match, "couldn't find encoded script in command line"
        encoded_script = match.groups()[0]
        decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
        match = re.search(r"\$tenantId\s*=\s*'([^']*)'", decoded_script)
        assert match
        tenant = match.group(1)

        assert not tenant or tenant == second_tenant, 'unexpected tenant "{}"'.format(tenant)
        token = first_token if not tenant else second_token
        stdout = "azsdk%{}%{}".format(token, int(time.time()) + 3600)

        communicate = Mock(return_value=get_completed_future((stdout.encode(), b"")))
        return Mock(communicate=communicate, returncode=0)

    credential = AzurePowerShellCredential()
    with patch(CREATE_SUBPROCESS_EXEC, fake_exec):
        token = await getattr(credential, get_token_method)("scope")
        assert token.token == first_token

        kwargs = {"tenant_id": second_tenant}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = await getattr(credential, get_token_method)("scope", **kwargs)
        assert token.token == second_token

        # should still default to the first tenant
        token = await getattr(credential, get_token_method)("scope")
        assert token.token == first_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_multitenant_authentication_not_allowed(get_token_method):
    expected_token = "***"

    async def fake_exec(*args, **_):
        command = args[2]
        assert command.startswith("pwsh -NoProfile -NonInteractive -EncodedCommand ")
        match = re.search(r"-EncodedCommand\s+(\S+)", command)
        assert match, "couldn't find encoded script in command line"
        encoded_script = match.groups()[0]
        decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
        match = re.search(r"\$tenantId\s*=\s*'([^']*)'", decoded_script)
        assert match
        tenant = match.group(1)

        assert not tenant, "credential shouldn't accept an explicit tenant ID"
        stdout = "azsdk%{}%{}".format(expected_token, int(time.time()) + 3600)
        communicate = Mock(return_value=get_completed_future((stdout.encode(), b"")))
        return Mock(communicate=communicate, returncode=0)

    credential = AzurePowerShellCredential()
    with patch(CREATE_SUBPROCESS_EXEC, fake_exec):
        token = await getattr(credential, get_token_method)("scope")
        assert token.token == expected_token

        with patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
            kwargs = {"tenant_id": "12345"}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = await getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == expected_token
