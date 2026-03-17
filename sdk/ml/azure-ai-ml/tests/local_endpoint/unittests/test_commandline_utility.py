# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Unit tests for commandline_utility module."""

import os
import subprocess
from unittest import mock

import pytest

from azure.ai.ml._local_endpoints.utilities.commandline_utility import run_cli_command


class TestRunCliCommand:
    """Tests for run_cli_command function."""

    def test_stderr_to_stdout_true_passes_correct_args(self):
        """Verify stderr=STDOUT is passed when stderr_to_stdout=True."""
        cmd = ["echo", "hello"]
        custom_env = {"FOO": "BAR"}

        with mock.patch("subprocess.check_output") as check_output_mock:
            check_output_mock.return_value = b"hello"
            run_cli_command(
                cmd_arguments=cmd,
                custom_environment=custom_env,
                return_json=False,
                timeout=None,
                do_not_print=True,
                stderr_to_stdout=True,
            )

            assert check_output_mock.call_args is not None
            called_args, called_kwargs = check_output_mock.call_args

            if os.name == "nt":
                assert called_args[0] == subprocess.list2cmdline(cmd)
                assert called_kwargs.get("shell") is True
            else:
                assert called_args[0] == cmd
                assert called_kwargs.get("shell") is False

            assert called_kwargs.get("stderr") is subprocess.STDOUT
            assert called_kwargs.get("env") == custom_env

    def test_stderr_to_stdout_false_omits_stderr(self):
        """Verify stderr is not passed when stderr_to_stdout=False."""
        cmd = ["echo", "hello"]
        custom_env = {"FOO": "BAR"}

        with mock.patch("subprocess.check_output") as check_output_mock:
            check_output_mock.return_value = b"hello"
            run_cli_command(
                cmd_arguments=cmd,
                custom_environment=custom_env,
                return_json=False,
                timeout=None,
                do_not_print=True,
                stderr_to_stdout=False,
            )

            assert check_output_mock.call_args is not None
            _, called_kwargs = check_output_mock.call_args

            assert "stderr" not in called_kwargs
            assert called_kwargs.get("env") == custom_env

    def test_shell_metacharacters_not_interpreted(self):
        """Verify shell metacharacters are not interpreted in arguments."""
        malicious_arg = "safe_path; echo INJECTED; #"
        cmd = ["echo", malicious_arg]

        with mock.patch("subprocess.check_output") as check_output_mock:
            check_output_mock.return_value = b"output"
            run_cli_command(
                cmd_arguments=cmd,
                do_not_print=True,
            )

            assert check_output_mock.call_args is not None
            called_args, called_kwargs = check_output_mock.call_args

            if os.name == "nt":
                command_str = called_args[0]
                assert called_kwargs.get("shell") is True
                assert command_str == subprocess.list2cmdline(cmd)
            else:
                assert called_args[0] == cmd
                assert called_kwargs.get("shell") is False

    def test_return_json_parses_output(self):
        """Verify JSON output is parsed correctly."""
        cmd = ["echo", "test"]
        # exclude_warnings expects { and } on separate lines
        json_output = b'{\n"key": "value"\n}'

        with mock.patch("subprocess.check_output") as check_output_mock:
            check_output_mock.return_value = json_output
            result = run_cli_command(
                cmd_arguments=cmd,
                return_json=True,
                do_not_print=True,
            )

            assert result == {"key": "value"}

    def test_called_process_error_is_raised(self):
        """Verify CalledProcessError propagates correctly."""
        cmd = ["bad_command"]

        with mock.patch("subprocess.check_output") as check_output_mock:
            check_output_mock.side_effect = subprocess.CalledProcessError(1, cmd, output=b"error output")
            with pytest.raises(subprocess.CalledProcessError):
                run_cli_command(
                    cmd_arguments=cmd,
                    do_not_print=True,
                )
