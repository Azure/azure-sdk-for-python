# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from itertools import product
import logging
from platform import python_version
import re
import subprocess
import sys
import time
from unittest.mock import Mock, patch

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzurePowerShellCredential, CredentialUnavailableError
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


POPEN = AzurePowerShellCredential.__module__ + ".subprocess.Popen"

# an example of harmless stderr output
PREPARING_MODULES = """#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><Obj S="progress" RefId="0"><TN RefId="0"><T>System.Management.Automation.PSCustomObject</T><T>System.Object</T></TN><MS><I64 N="SourceId">1</I64><PR N="Record"><AV>Preparing modules for first use.</AV><AI>0</AI><Nil /><PI>-1</PI><PC>-1</PC><T>Completed</T><SR>-1</SR><SD> </SD></PR></MS></Obj><Obj S="progress" RefId="1"><TNRef RefId="0" /><MS><I64 N="SourceId">2</I64><PR N="Record"><AV>Preparing modules for first use.</AV><AI>0</AI><Nil /><PI>-1</PI><PC>-1</PC><T>Completed</T><SR>-1</SR><SD> </SD></PR></MS></Obj></Objs>"""


def raise_called_process_error(return_code, stdout, stderr="", cmd="..."):
    error = subprocess.CalledProcessError(return_code, cmd=cmd, output=stdout, stderr=stderr)
    return Mock(side_effect=error)


def get_mock_Popen(return_code=0, stdout="", stderr=""):
    communicate = Mock(return_value=(stdout, stderr))
    return Mock(return_value=Mock(communicate=communicate, returncode=return_code))


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_no_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        getattr(AzurePowerShellCredential(), get_token_method)()


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multiple_scopes(get_token_method):
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with pytest.raises(ValueError):
        getattr(AzurePowerShellCredential(), get_token_method)("one scope", "and another")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_cannot_execute_shell(get_token_method):
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with patch(POPEN, Mock(side_effect=OSError)):
        with pytest.raises(CredentialUnavailableError):
            getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_invalid_tenant_id(get_token_method):
    """Invalid tenant IDs should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            AzurePowerShellCredential(tenant_id="tenant" + c)

        with pytest.raises(ValueError):
            kwargs = {"tenant_id": "tenant" + c}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            getattr(AzurePowerShellCredential(), get_token_method)("scope", **kwargs)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_invalid_scopes(get_token_method):
    """Scopes with invalid characters should raise ValueErrors."""

    for c in INVALID_CHARACTERS:
        with pytest.raises(ValueError):
            getattr(AzurePowerShellCredential(), get_token_method)("scope" + c)


@pytest.mark.parametrize("stderr,get_token_method", product(("", PREPARING_MODULES), GET_TOKEN_METHODS))
def test_get_token(stderr, get_token_method):
    """The credential should parse Azure PowerShell's output to an AccessToken"""

    expected_access_token = "access"
    expected_expires_on = 1617923581
    scope = "scope"
    stdout = "azsdk%{}%{}".format(expected_access_token, expected_expires_on)

    Popen = get_mock_Popen(stdout=stdout, stderr=stderr)
    with patch(POPEN, Popen):
        token = getattr(AzurePowerShellCredential(), get_token_method)(scope)

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on

    assert Popen.call_count == 1
    args, kwargs = Popen.call_args
    command = args[0][-1]
    assert command.startswith("pwsh -NoProfile -NonInteractive -EncodedCommand ")

    match = re.search(r"-EncodedCommand\s+(\S+)", command)
    assert match, "couldn't find encoded script in command line"
    encoded_script = match.groups()[0]
    decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
    assert "tenantId = ''" in decoded_script
    assert f"'ResourceUrl' = '{scope}'" in decoded_script

    assert Popen().communicate.call_count == 1
    args, kwargs = Popen().communicate.call_args
    if python_version() >= "3.3":
        assert "timeout" in kwargs


@pytest.mark.parametrize("stderr,get_token_method", product(("", PREPARING_MODULES), GET_TOKEN_METHODS))
def test_get_token_tenant_id(stderr, get_token_method):
    expected_access_token = "access"
    expected_expires_on = 1617923581
    scope = "scope"
    stdout = "azsdk%{}%{}".format(expected_access_token, expected_expires_on)

    Popen = get_mock_Popen(stdout=stdout, stderr=stderr)
    with patch(POPEN, Popen):
        kwargs = {"tenant_id": "tenant-id"}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(AzurePowerShellCredential(), get_token_method)(scope, **kwargs)

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_ignores_extraneous_stdout_content(get_token_method):
    expected_access_token = "access"
    expected_expires_on = 1617923581
    motd = "MOTD: Customize your experience: save your profile to $HOME/.config/PowerShell\n"
    Popen = get_mock_Popen(stdout=motd + "azsdk%{}%{}".format(expected_access_token, expected_expires_on))

    with patch(POPEN, Popen):
        token = getattr(AzurePowerShellCredential(), get_token_method)("scope")

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_az_powershell_not_installed(get_token_method):
    """The credential should raise CredentialUnavailableError when Azure PowerShell isn't installed"""

    with patch(POPEN, get_mock_Popen(stdout=NO_AZ_ACCOUNT_MODULE)):
        with pytest.raises(CredentialUnavailableError, match=AZ_ACCOUNT_NOT_INSTALLED):
            getattr(AzurePowerShellCredential(), get_token_method)("scope")


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
def test_powershell_not_installed_cmd(stderr, get_token_method):
    """The credential should raise CredentialUnavailableError when PowerShell isn't installed"""

    Popen = get_mock_Popen(return_code=1, stderr=stderr)
    with patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=POWERSHELL_NOT_INSTALLED):
            getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_powershell_not_installed_sh(get_token_method):
    """The credential should raise CredentialUnavailableError when PowerShell isn't installed"""

    Popen = get_mock_Popen(return_code=127, stderr="/bin/sh: 0: Can't open pwsh")
    with patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=POWERSHELL_NOT_INSTALLED):
            getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize(
    "stderr,get_token_method",
    product((POWERSHELL_INVALID_OPERATION_EXCEPTION, POWERSHELL_NOT_LOGGED_IN_ERROR), GET_TOKEN_METHODS),
)
def test_not_logged_in(stderr, get_token_method):
    """The credential should raise CredentialUnavailableError when a user isn't logged in to Azure PowerShell"""

    Popen = get_mock_Popen(return_code=1, stderr=stderr)
    with patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=RUN_CONNECT_AZ_ACCOUNT):
            getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_blocked_by_execution_policy(get_token_method):
    """The credential should raise CredentialUnavailableError when execution policy blocks Get-AzAccessToken"""

    stderr = r"""#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><S S="Error">Import-Module : Errors occurred while loading the format data file: _x000D__x000A_</S><S S="Error">C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.format.ps1xml, , C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.format.ps1xml: The file was skipped because of the _x000D__x000A_</S><S S="Error">following validation exception: AuthorizationManager check failed.._x000D__x000A_</S><S S="Error">C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.generated.format.ps1xml, , C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.generated.format.ps1xml: The file was skipped _x000D__x000A_</S><S S="Error">because of the following validation exception: AuthorizationManager check failed.._x000D__x000A_</S><S S="Error">At line:4 char:6_x000D__x000A_</S><S S="Error">+ $m = Import-Module Az.Accounts -MinimumVersion $minimumVersion -PassT ..._x000D__x000A_</S><S S="Error">+      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~_x000D__x000A_</S><S S="Error">    + CategoryInfo          : InvalidOperation: (:) [Import-Module], RuntimeException_x000D__x000A_</S><S S="Error">    + FullyQualifiedErrorId : FormatXmlUpdateException,Microsoft.PowerShell.Commands.ImportModuleCommand_x000D__x000A_</S><S S="Error"> _x000D__x000A_</S></Objs>"""
    Popen = get_mock_Popen(return_code=1, stderr=stderr)
    with patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=BLOCKED_BY_EXECUTION_POLICY):
            getattr(AzurePowerShellCredential(), get_token_method)("scope")


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_timeout(get_token_method):
    """The credential should kill the subprocess after a timeout"""

    from subprocess import TimeoutExpired

    proc = Mock(communicate=Mock(side_effect=TimeoutExpired("", 42)), returncode=None)
    with patch(POPEN, Mock(return_value=proc)):
        with pytest.raises(CredentialUnavailableError):
            getattr(AzurePowerShellCredential(process_timeout=42), get_token_method)("scope")

    assert proc.communicate.call_count == 1
    # Ensure custom timeout is passed to subprocess
    _, kwargs = proc.communicate.call_args
    assert "timeout" in kwargs
    assert kwargs["timeout"] == 42


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_unexpected_error(get_token_method):
    """The credential should log stderr when Get-AzAccessToken returns an unexpected error"""

    class MockHandler(logging.Handler):
        def __init__(self):
            super(MockHandler, self).__init__()
            self.messages = []

        def emit(self, record):
            self.messages.append(record)

    mock_handler = MockHandler()
    logger = logging.getLogger(AzurePowerShellCredential.__module__)
    logger.addHandler(mock_handler)
    logger.setLevel(logging.DEBUG)

    expected_output = "something went wrong"
    Popen = get_mock_Popen(return_code=42, stderr=expected_output)
    with patch(POPEN, Popen):
        with pytest.raises(ClientAuthenticationError):
            getattr(AzurePowerShellCredential(), get_token_method)("scope")

    for message in mock_handler.messages:
        if message.levelname == "DEBUG" and expected_output in message.message:
            return

    assert False, "Credential should have included stderr in a DEBUG level message"


@pytest.mark.parametrize(
    "error_message,get_token_method",
    product(
        (
            "'pwsh' is not recognized as an internal or external command,\r\noperable program or batch file.",
            "some other message",
        ),
        GET_TOKEN_METHODS,
    ),
)
def test_windows_powershell_fallback(error_message, get_token_method):
    """On Windows, the credential should fall back to powershell.exe when pwsh.exe isn't on the path"""

    class Fake:
        calls = 0

    def Popen(args, **kwargs):
        assert args[:2] == ["cmd", "/c"]
        Fake.calls += 1
        if args[-1].startswith("pwsh"):
            assert Fake.calls == 1, 'credential should invoke "pwsh" only once'
            stdout = ""
            stderr = error_message
            return_code = 9009
        else:
            assert args[-1].startswith("powershell"), 'credential should fall back to "powershell"'
            stdout = NO_AZ_ACCOUNT_MODULE
            stderr = ""
            return_code = 0

        return Mock(communicate=Mock(return_value=(stdout, stderr)), returncode=return_code)

    with patch(AzurePowerShellCredential.__module__ + ".sys.platform", "win32"):
        with patch.dict("os.environ", {"SYSTEMROOT": "foo"}):
            with patch(POPEN, Popen):
                with pytest.raises(CredentialUnavailableError, match=AZ_ACCOUNT_NOT_INSTALLED):
                    getattr(AzurePowerShellCredential(), get_token_method)("scope")

    assert Fake.calls == 2


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication(get_token_method):
    first_token = "***"
    second_tenant = "12345"
    second_token = first_token * 2

    def fake_Popen(command, **_):
        assert command[-1].startswith("pwsh -NoProfile -NonInteractive -EncodedCommand ")
        match = re.search(r"-EncodedCommand\s+(\S+)", command[-1])
        assert match, "couldn't find encoded script in command line"
        encoded_script = match.groups()[0]
        decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
        match = re.search(r"\$tenantId\s*=\s*'([^']*)'", decoded_script)
        assert match
        tenant = match.group(1)

        assert not tenant or tenant == second_tenant, 'unexpected tenant "{}"'.format(tenant)
        token = first_token if not tenant else second_token
        stdout = "azsdk%{}%{}".format(token, int(time.time()) + 3600)

        communicate = Mock(return_value=(stdout, ""))
        return Mock(communicate=communicate, returncode=0)

    credential = AzurePowerShellCredential()
    with patch(POPEN, fake_Popen):
        token = getattr(credential, get_token_method)("scope")
        assert token.token == first_token

        kwargs = {"tenant_id": second_tenant}
        if get_token_method == "get_token_info":
            kwargs = {"options": kwargs}
        token = getattr(credential, get_token_method)("scope", **kwargs)
        assert token.token == second_token

        # should still default to the first tenant
        token = getattr(credential, get_token_method)("scope")
        assert token.token == first_token


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_multitenant_authentication_not_allowed(get_token_method):
    expected_token = "***"

    def fake_Popen(command, **_):
        assert command[-1].startswith("pwsh -NoProfile -NonInteractive -EncodedCommand ")
        match = re.search(r"-EncodedCommand\s+(\S+)", command[-1])
        assert match, "couldn't find encoded script in command line"
        encoded_script = match.groups()[0]
        decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
        match = re.search(r"\$tenantId\s*=\s*'([^']*)'", decoded_script)
        assert match
        tenant = match.group(1)

        assert not tenant, "credential shouldn't accept an explicit tenant ID"
        stdout = "azsdk%{}%{}".format(expected_token, int(time.time()) + 3600)

        communicate = Mock(return_value=(stdout, ""))
        return Mock(communicate=communicate, returncode=0)

    credential = AzurePowerShellCredential()
    with patch(POPEN, fake_Popen):
        token = getattr(credential, get_token_method)("scope")
        assert token.token == expected_token

        with patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
            kwargs = {"tenant_id": "12345"}
            if get_token_method == "get_token_info":
                kwargs = {"options": kwargs}
            token = getattr(credential, get_token_method)("scope", **kwargs)
            assert token.token == expected_token
