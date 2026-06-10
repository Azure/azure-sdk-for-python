# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import os
import shlex
import subprocess
from unittest.mock import patch

import pytest

from azure.ai.ml._local_endpoints.utilities.commandline_utility import run_cli_command


def _expected_command(args):
    return subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)


@pytest.mark.unittest
class TestRunCliCommand:
    def test_arguments_are_quoted_before_shell_execution(self):
        # An argument carrying shell metacharacters (e.g. a deployment-derived path component).
        args = ["echo", "x$(touch pwned)"]

        with patch(
            "azure.ai.ml._local_endpoints.utilities.commandline_utility.subprocess.check_output",
            return_value=b"",
        ) as mock_check_output:
            run_cli_command(args)

        command_to_execute = mock_check_output.call_args[0][0]
        # The raw space-join would let the shell evaluate the $(...) substitution.
        assert command_to_execute != " ".join(args)
        assert command_to_execute == _expected_command(args)

    def test_plain_uri_argument_is_unchanged(self):
        uri = "vscode-remote://dev-container+deadbeef/var/azureml-app/onlinescoring"
        args = ["code", "--folder-uri", uri]

        with patch(
            "azure.ai.ml._local_endpoints.utilities.commandline_utility.subprocess.check_output",
            return_value=b"",
        ) as mock_check_output:
            run_cli_command(args)

        command_to_execute = mock_check_output.call_args[0][0]
        assert command_to_execute == _expected_command(args)
        if os.name != "nt":
            assert command_to_execute == f"code --folder-uri {uri}"
