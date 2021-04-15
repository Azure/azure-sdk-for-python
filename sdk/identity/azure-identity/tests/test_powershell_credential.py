# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import logging
from platform import python_version
import subprocess
import sys

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzurePowerShellCredential, CredentialUnavailableError
from azure.identity._credentials.azure_powershell import (
    AZ_ACCOUNT_NOT_INSTALLED,
    BLOCKED_BY_EXECUTION_POLICY,
    NO_AZ_ACCOUNT_MODULE,
    POWERSHELL_NOT_INSTALLED,
    RUN_CONNECT_AZ_ACCOUNT,
)
import pytest

from helpers import mock


POPEN = AzurePowerShellCredential.__module__ + ".subprocess.Popen"

# an example of harmless stderr output
PREPARING_MODULES = """#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><Obj S="progress" RefId="0"><TN RefId="0"><T>System.Management.Automation.PSCustomObject</T><T>System.Object</T></TN><MS><I64 N="SourceId">1</I64><PR N="Record"><AV>Preparing modules for first use.</AV><AI>0</AI><Nil /><PI>-1</PI><PC>-1</PC><T>Completed</T><SR>-1</SR><SD> </SD></PR></MS></Obj><Obj S="progress" RefId="1"><TNRef RefId="0" /><MS><I64 N="SourceId">2</I64><PR N="Record"><AV>Preparing modules for first use.</AV><AI>0</AI><Nil /><PI>-1</PI><PC>-1</PC><T>Completed</T><SR>-1</SR><SD> </SD></PR></MS></Obj></Objs>"""


def raise_called_process_error(return_code, stdout, stderr="", cmd="..."):
    error = subprocess.CalledProcessError(return_code, cmd=cmd, output=stdout, stderr=stderr)
    return mock.Mock(side_effect=error)


def get_mock_Popen(return_code=0, stdout="", stderr=""):
    communicate = mock.Mock(return_value=(stdout, stderr))
    return mock.Mock(return_value=mock.Mock(communicate=communicate, returncode=return_code))


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

    with mock.patch(POPEN, mock.Mock(side_effect=OSError)):
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
    with mock.patch(POPEN, Popen):
        token = AzurePowerShellCredential().get_token(scope)

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on

    assert Popen.call_count == 1
    args, kwargs = Popen.call_args
    command = args[0][-1]
    assert command.startswith("pwsh -NonInteractive -EncodedCommand ")

    encoded_script = command.split()[-1]
    decoded_script = base64.urlsafe_b64decode(encoded_script).decode("utf-16-le")
    assert "Get-AzAccessToken -ResourceUrl '{}'".format(scope) in decoded_script

    assert Popen().communicate.call_count == 1
    args, kwargs = Popen().communicate.call_args
    if python_version() >= "3.3":
        assert "timeout" in kwargs


def test_ignores_extraneous_stdout_content():
    expected_access_token = "access"
    expected_expires_on = 1617923581
    motd = "MOTD: Customize your experience: save your profile to $HOME/.config/PowerShell\n"
    Popen = get_mock_Popen(stdout=motd + "azsdk%{}%{}".format(expected_access_token, expected_expires_on))

    with mock.patch(POPEN, Popen):
        token = AzurePowerShellCredential().get_token("scope")

    assert token.token == expected_access_token
    assert token.expires_on == expected_expires_on


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="tests Windows-specific behavior")
def test_legacy_powershell():
    Popen = get_mock_Popen(stdout="azsdk%***%42")
    with mock.patch(POPEN, Popen):
        AzurePowerShellCredential(use_legacy_powershell=True).get_token("scope")

    assert Popen.call_count == 1
    args, kwargs = Popen.call_args
    command = args[0][-1]
    assert command.startswith("powershell")


@pytest.mark.parametrize("platform", ("darwin", "linux"))
def test_legacy_powershell_non_windows(platform):
    """The credential should raise ValueError when configured to use legacy PowerShell on non-Windows platforms"""

    with mock.patch(AzurePowerShellCredential.__module__ + ".sys.platform", platform):
        with pytest.raises(ValueError, match=".*Windows.*"):
            AzurePowerShellCredential(use_legacy_powershell=True)


def test_az_powershell_not_installed():
    """The credential should raise CredentialUnavailableError when Azure PowerShell isn't installed"""

    with mock.patch(POPEN, get_mock_Popen(stdout=NO_AZ_ACCOUNT_MODULE)):
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
    with mock.patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=POWERSHELL_NOT_INSTALLED):
            AzurePowerShellCredential().get_token("scope")


def test_powershell_not_installed_sh():
    """The credential should raise CredentialUnavailableError when PowerShell isn't installed"""

    Popen = get_mock_Popen(return_code=127, stderr="/bin/sh: 0: Can't open pwsh")
    with mock.patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=POWERSHELL_NOT_INSTALLED):
            AzurePowerShellCredential().get_token("scope")


@pytest.mark.parametrize(
    "stderr",
    (
        """#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><Obj S="progress" RefId="0"><TN RefId="0"><T>System.Management.Automation.PSCustomObject</T><T>System.Object</T></TN><MS><I64 N="SourceId">1</I64><PR N="Record"><AV>Preparing modules for first use.</AV><AI>0</AI><Nil /><PI>-1</PI><PC>-1</PC><T>Completed</T><SR>-1</SR><SD> </SD></PR></MS></Obj><Obj S="progress" RefId="1"><TNRef RefId="0" /><MS><I64 N="SourceId">2</I64><PR N="Record"><AV>Preparing modules for first use.</AV><AI>0</AI><Nil /><PI>-1</PI><PC>-1</PC><T>Completed</T><SR>-1</SR><SD> </SD></PR></MS></Obj><S S="Error">Get-AzAccessToken : Run Connect-AzAccount to login._x000D__x000A_</S><S S="Error">At line:11 char:10_x000D__x000A_</S><S S="Error">+ $token = Get-AzAccessToken -ResourceUrl 'scope'_x000D__x000A_</S><S S="Error">+          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~_x000D__x000A_</S><S S="Error">    + CategoryInfo          : CloseError: (:) [Get-AzAccessToken], PSInvalidOperationException_x000D__x000A_</S><S S="Error">    + FullyQualifiedErrorId : Microsoft.Azure.Commands.Profile.GetAzureRmAccessTokenCommand_x000D__x000A_</S><S S="Error"> _x000D__x000A_</S></Objs>""",
        """#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><S S="Error">_x001B_[91mGet-AzAccessToken: _x000D__x000A_</S><S S="Error">_x001B_[96mLine |_x000D__x000A_</S><S S="Error">_x001B_[96m  11 | _x001B_[0m $token = _x001B_[96mGet-AzAccessToken -ResourceUrl 'scope'_x001B_[0m_x000D__x000A_</S><S S="Error">_x001B_[96m     | _x001B_[91m          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~_x000D__x000A_</S><S S="Error">_x001B_[91m_x001B_[96m     | _x001B_[91mRun Connect-AzAccount to login._x001B_[0m_x000D__x000A_</S></Objs>""",
    ),
)
def test_not_logged_in(stderr):
    """The credential should raise CredentialUnavailableError when a user isn't logged in to Azure PowerShell"""

    Popen = get_mock_Popen(return_code=1, stderr=stderr)
    with mock.patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=RUN_CONNECT_AZ_ACCOUNT):
            AzurePowerShellCredential().get_token("scope")


def test_blocked_by_execution_policy():
    """The credential should raise CredentialUnavailableError when execution policy blocks Get-AzAccessToken"""

    stderr = r"""#< CLIXML
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><S S="Error">Import-Module : Errors occurred while loading the format data file: _x000D__x000A_</S><S S="Error">C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.format.ps1xml, , C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.format.ps1xml: The file was skipped because of the _x000D__x000A_</S><S S="Error">following validation exception: AuthorizationManager check failed.._x000D__x000A_</S><S S="Error">C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.generated.format.ps1xml, , C:\Users\foo\Documents\WindowsPowerShell\Modules\Az.Accounts\2.2.7\Accounts.generated.format.ps1xml: The file was skipped _x000D__x000A_</S><S S="Error">because of the following validation exception: AuthorizationManager check failed.._x000D__x000A_</S><S S="Error">At line:4 char:6_x000D__x000A_</S><S S="Error">+ $m = Import-Module Az.Accounts -MinimumVersion $minimumVersion -PassT ..._x000D__x000A_</S><S S="Error">+      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~_x000D__x000A_</S><S S="Error">    + CategoryInfo          : InvalidOperation: (:) [Import-Module], RuntimeException_x000D__x000A_</S><S S="Error">    + FullyQualifiedErrorId : FormatXmlUpdateException,Microsoft.PowerShell.Commands.ImportModuleCommand_x000D__x000A_</S><S S="Error"> _x000D__x000A_</S></Objs>"""
    Popen = get_mock_Popen(return_code=1, stderr=stderr)
    with mock.patch(POPEN, Popen):
        with pytest.raises(CredentialUnavailableError, match=BLOCKED_BY_EXECUTION_POLICY):
            AzurePowerShellCredential().get_token("scope")


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
    with mock.patch(POPEN, Popen):
        with pytest.raises(ClientAuthenticationError):
            AzurePowerShellCredential().get_token("scope")

    for message in mock_handler.messages:
        if message.levelname == "DEBUG" and expected_output in message.message:
            return

    assert False, "Credential should have included stderr in a DEBUG level message"
