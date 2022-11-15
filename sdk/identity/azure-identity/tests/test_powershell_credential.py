# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import logging
from platform import python_version
import re
import subprocess
import sys
import time

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

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


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    with pytest.raises(ValueError):
        AzurePowerShellCredential().get_token()


def test_multiple_scopes():
    """The credential should raise ValueError when get_token is called with more than one scope"""

    with pytest.raises(ValueError):
        AzurePowerShellCredential().get_token("one scope", "and another")


def test_cannot_execute_shell():
    """The credential should raise CredentialUnavailableError when the subprocess doesn't start"""

    with patch(POPEN, Mock(side_effect=OSError)):
        with pytest.raises(CredentialUnavailableError):
            AzurePowerShellCredential().get_token("scope")


@pytest.mark.parametrize("stderr", ("", PREPARING_MODULES))
def test_get_token(stderr):
    """The credential should parse Azure PowerShell's output to an AccessToken"""

    expected_access_token = "access"
    expected_expires_on = 1617923581
    scope = "scope"
    stdout = "azsdk%{}%{}".format(expected_access_token, expected_expires_on)

    Popen = get_mock_Popen(stdout=stdout, stderr=stderr)
    with patch(POPEN, Popen):
        token = AzurePowerShellCredential().get_token(scope)

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on

    assert Popen.call_count == 1
    args, kwargs = Popen.call_args
    command = args[0][-1]
    assert command.startswith("pwsh -NonInteractive -EncodedCommand ")

    encoded_script = command.split()[-1]
    decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
    assert "TenantId" not in decoded_script
    assert "Get-AzAccessToken -ResourceUrl '{}'".format(scope) in decoded_script

    assert Popen().communicate.call_count == 1
    args, kwargs = Popen().communicate.call_args
    if python_version() >= "3.3":
        assert "timeout" in kwargs


@pytest.mark.parametrize("stderr", ("", PREPARING_MODULES))
def test_get_token_tenant_id(stderr):
    expected_access_token = "access"
    expected_expires_on = 1617923581
    scope = "scope"
    stdout = "azsdk%{}%{}".format(expected_access_token, expected_expires_on)

    Popen = get_mock_Popen(stdout=stdout, stderr=stderr)
    with patch(POPEN, Popen):
        token = AzurePowerShellCredential().get_token(scope, tenant_id="tenant_id")

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on


def test_ignores_extraneous_stdout_content():
    expected_access_token = "access"
    expected_expires_on = 1617923581
    motd = "MOTD: Customize your experience: save your profile to $HOME/.config/PowerShell\n"
    Popen = get_mock_Popen(stdout=motd + "azsdk%{}%{}".format(expected_access_token, expected_expires_on))

    with patch(POPEN, Popen):
        token = AzurePowerShellCredential().get_token("scope")

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on


def test_az_powershell_not_installed():
    """The credential should raise CredentialUnavailableError when Azure PowerShell isn't installed"""

    with patch(POPEN, get_mock_Popen(stdout=NO_AZ_ACCOUNT_MODULE)):
        with pytest.raises(CredentialUnavailableError, match=AZ_ACCOUNT_NOT_INSTALLED):
            AzurePowerShellCredential().get_token("scope")


@pytest.mark.parametrize(
    "stderr",
    (
        "'pwsh' is not recognized as an internal or external command,\r\noperable program or batch file.",
        "'powershell' is not recognized as an internal or external command,\r\noperable program or batch file.",
    ),
)
def test_powershell_not_installed_cmd(stderr):
    """The credential should raise CredentialUnavailableError when PowerShell isn't installed"""

    Popen = get_mock_Popen(return_code=1, stderr=stderr)
    with patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=POWERSHELL_NOT_INSTALLED):
            AzurePowerShellCredential().get_token("scope")


def test_powershell_not_installed_sh():
    """The credential should raise CredentialUnavailableError when PowerShell isn't installed"""

    Popen = get_mock_Popen(return_code=127, stderr="/bin/sh: 0: Can't open pwsh")
    with patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=POWERSHELL_NOT_INSTALLED):
            AzurePowerShellCredential().get_token("scope")


@pytest.mark.parametrize("stderr", (POWERSHELL_INVALID_OPERATION_EXCEPTION, POWERSHELL_NOT_LOGGED_IN_ERROR))
def test_not_logged_in(stderr):
    """The credential should raise CredentialUnavailableError when a user isn't logged in to Azure PowerShell"""

    Popen = get_mock_Popen(return_code=1, stderr=stderr)
    with patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=RUN_CONNECT_AZ_ACCOUNT):
            AzurePowerShellCredential().get_token("scope")


def test_blocked_by_execution_policy():
    """The credential should raise CredentialUnavailableError when execution policy blocks Get-AzAccessToken"""

    stderr = r"""#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><S S="Error">Import-Module : Errors occurred while loading the format data file: _x000D__x000A_</S><S S="Error">C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.format.ps1xml, , C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.format.ps1xml: The file was skipped because of the _x000D__x000A_</S><S S="Error">following validation exception: AuthorizationManager check failed.._x000D__x000A_</S><S S="Error">C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.generated.format.ps1xml, , C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.generated.format.ps1xml: The file was skipped _x000D__x000A_</S><S S="Error">because of the following validation exception: AuthorizationManager check failed.._x000D__x000A_</S><S S="Error">At line:4 char:6_x000D__x000A_</S><S S="Error">+ $m = Import-Module Az.Accounts -MinimumVersion $minimumVersion -PassT ..._x000D__x000A_</S><S S="Error">+      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~_x000D__x000A_</S><S S="Error">    + CategoryInfo          : InvalidOperation: (:) [Import-Module], RuntimeException_x000D__x000A_</S><S S="Error">    + FullyQualifiedErrorId : FormatXmlUpdateException,Microsoft.PowerShell.Commands.ImportModuleCommand_x000D__x000A_</S><S S="Error"> _x000D__x000A_</S></Objs>"""
    Popen = get_mock_Popen(return_code=1, stderr=stderr)
    with patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=BLOCKED_BY_EXECUTION_POLICY):
            AzurePowerShellCredential().get_token("scope")


@pytest.mark.skipif(sys.version_info < (3, 3), reason="Python 3.3 added timeout support to Popen")
def test_timeout():
    """The credential should kill the subprocess after a timeout"""

    from subprocess import TimeoutExpired

    proc = Mock(communicate=Mock(side_effect=TimeoutExpired("", 42)), returncode=None)
    with patch(POPEN, Mock(return_value=proc)):
        with pytest.raises(CredentialUnavailableError):
            AzurePowerShellCredential().get_token("scope")

    assert proc.communicate.call_count == 1


def test_unexpected_error():
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
            AzurePowerShellCredential().get_token("scope")

    for message in mock_handler.messages:
        if message.levelname == "DEBUG" and expected_output in message.message:
            return

    assert False, "Credential should have included stderr in a DEBUG level message"


def test_windows_powershell_fallback():
    """On Windows, the credential should fall back to powershell.exe when pwsh.exe isn't on the path"""

    class Fake:
        calls = 0

    def Popen(args, **kwargs):
        assert args[:2] == ["cmd", "/c"]
        Fake.calls += 1
        if args[-1].startswith("pwsh"):
            assert Fake.calls == 1, 'credential should invoke "pwsh" only once'
            stdout = ""
            stderr = "'pwsh' is not recognized as an internal or external command,\r\noperable program or batch file."
            return_code = 1
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
                    AzurePowerShellCredential().get_token("scope")

    assert Fake.calls == 2


def test_multitenant_authentication():
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def fake_Popen(command, **_):
        assert command[-1].startswith("pwsh -NonInteractive -EncodedCommand ")
        encoded_script = command[-1].split()[-1]
        decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
        match = re.search(r"Get-AzAccessToken -ResourceUrl '(\S+)'(?: -TenantId (\S+))?", decoded_script)
        tenant = match.groups()[1]

        assert tenant is None or tenant == second_tenant, 'unexpected tenant "{}"'.format(tenant)
        token = first_token if tenant is None else second_token
        stdout = "azsdk%{}%{}".format(token, int(time.time()) + 3600)

        communicate = Mock(return_value=(stdout, ""))
        return Mock(communicate=communicate, returncode=0)

    credential = AzurePowerShellCredential()
    with patch(POPEN, fake_Popen):
        token = credential.get_token("scope")
        assert token.token == first_token

        token = credential.get_token("scope", tenant_id=second_tenant)
        assert token.token == second_token

        # should still default to the first tenant
        token = credential.get_token("scope")
        assert token.token == first_token

def test_multitenant_authentication_not_allowed():
    expected_token = "***"

    def fake_Popen(command, **_):
        assert command[-1].startswith("pwsh -NonInteractive -EncodedCommand ")
        encoded_script = command[-1].split()[-1]
        decoded_script = base64.b64decode(encoded_script).decode("utf-16-le")
        match = re.search(r"Get-AzAccessToken -ResourceUrl '(\S+)'(?: -TenantId (\S+))?", decoded_script)
        tenant = match.groups()[1]

        assert tenant is None, "credential shouldn't accept an explicit tenant ID"
        stdout = "azsdk%{}%{}".format(expected_token, int(time.time()) + 3600)

        communicate = Mock(return_value=(stdout, ""))
        return Mock(communicate=communicate, returncode=0)

    credential = AzurePowerShellCredential()
    with patch(POPEN, fake_Popen):
        token = credential.get_token("scope")
        assert token.token == expected_token

        with patch.dict("os.environ", {EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH: "true"}):
            token = credential.get_token("scope", tenant_id="some tenant")
            assert token.token == expected_token
