# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
import subprocess
import sys
import time
from unittest import mock
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException


def _print_command_results(test_passed, time_taken, output):
    print(
        "Command {} in {} seconds.".format(
            "successful" if test_passed else "failed", time_taken
        )
    )
    print("Output: \n{}\n".format(output))


def run_cli_command(
    cmd_arguments,
    custom_environment=None,
    return_json=False,
    timeout=None,
    do_not_print=True,
    stderr_to_stdout=True,
):
    if not custom_environment:
        custom_environment = os.environ

    # Use argv form with shell=False to avoid shell injection risks while keeping behavior
    # consistent across platforms (including macOS).
    # On Windows, many CLI tools (e.g., "code") are .cmd/.bat shims that require shell
    # execution. We use subprocess.list2cmdline to safely quote the arguments before
    # passing them to the shell, preventing command injection.

    if (
        not do_not_print
    ):  # Avoid printing the az login service principal password, for example
        print("Preparing to run CLI command: \n{}\n".format(" ".join(cmd_arguments)))
        print("Current directory: {}".format(os.getcwd()))

    start_time = time.time()
    try:
        # We redirect stderr to stdout, so that in the case of an error, especially in negative tests,
        # we get the error reply back to check if the error is expected or not.

        # We also pass the environment variables, because for some tests we modify
        # the environment variables.

        subprocess_args = {
            "stderr": subprocess.STDOUT,
            "env": custom_environment,
        }

        if not stderr_to_stdout:
            subprocess_args = {"env": custom_environment}

        if sys.version_info[0] != 2:
            subprocess_args["timeout"] = timeout

        # On Windows, many CLI commands are provided as .cmd/.bat shims that require
        # shell execution. Use list2cmdline to build a safely quoted command string
        # when invoking via the shell.
        if os.name == "nt":
            command_to_execute = subprocess.list2cmdline(cmd_arguments)
            subprocess_args["shell"] = True
            cmd_to_run = command_to_execute
        else:
            subprocess_args["shell"] = False
            cmd_to_run = cmd_arguments

        output = subprocess.check_output(cmd_to_run, **subprocess_args).decode(
            encoding="UTF-8"
        )

        time_taken = time.time() - start_time
        if not do_not_print:
            _print_command_results(True, time_taken, output)

        if return_json:
            try:
                return json.loads(exclude_warnings(output))
            except Exception as e:
                msg = "Expected JSON, instead got: \n{}\n"
                raise MlException(
                    message=msg.format(output),
                    no_personal_data_message=msg.format("[something else]"),
                    target=ErrorTarget.LOCAL_ENDPOINT,
                    error_category=ErrorCategory.SYSTEM_ERROR,
                ) from e
        else:
            return output
    except subprocess.CalledProcessError as e:
        time_taken = time.time() - start_time
        output = e.output.decode(encoding="UTF-8")
        if not do_not_print:
            _print_command_results(False, time_taken, output)

        raise e


def exclude_warnings(cmd_output):
    json_output = ""
    start_index = None
    end_index = None
    curr_index = 0
    for cmd_line in cmd_output.splitlines():
        if cmd_line.startswith("{") and start_index is None:
            start_index = curr_index

        if cmd_line.startswith("}"):
            end_index = curr_index

        curr_index = curr_index + 1

    curr_index = 0
    for cmd_line in cmd_output.splitlines():
        if start_index <= curr_index <= end_index:
            if len(json_output) == 0:
                json_output = cmd_line
            else:
                json_output = json_output + "\n" + cmd_line

        curr_index = curr_index + 1

    return json_output


def _test_run_cli_command_stderr_to_stdout_true():
    """Internal test to validate subprocess arguments when stderr_to_stdout is True."""
    cmd = ["echo", "hello"]
    custom_env = {"FOO": "BAR"}
    with mock.patch("subprocess.check_output") as check_output_mock:
        check_output_mock.return_value = b""
        run_cli_command(
            cmd_arguments=cmd,
            custom_environment=custom_env,
            return_json=False,
            timeout=None,
            do_not_print=True,
            stderr_to_stdout=True,
        )
        # Verify argv (first positional argument) is passed through unchanged.
        assert check_output_mock.call_args is not None
        called_args, called_kwargs = check_output_mock.call_args
        assert called_args[0] == cmd
        # Verify shell and stderr behavior.
        assert called_kwargs.get("shell") is False
        assert called_kwargs.get("stderr") is subprocess.STDOUT
        # Verify environment is forwarded.
        assert called_kwargs.get("env") == custom_env


def _test_run_cli_command_stderr_to_stdout_false():
    """Internal test to validate subprocess arguments when stderr_to_stdout is False."""
    cmd = ["echo", "hello"]
    custom_env = {"FOO": "BAR"}
    with mock.patch("subprocess.check_output") as check_output_mock:
        check_output_mock.return_value = b""
        run_cli_command(
            cmd_arguments=cmd,
            custom_environment=custom_env,
            return_json=False,
            timeout=None,
            do_not_print=True,
            stderr_to_stdout=False,
        )
        # Verify argv (first positional argument) is passed through unchanged.
        assert check_output_mock.call_args is not None
        called_args, called_kwargs = check_output_mock.call_args
        assert called_args[0] == cmd
        # Verify shell behavior and absence of stderr redirection.
        assert called_kwargs.get("shell") is False
        assert "stderr" not in called_kwargs
        # Verify environment is forwarded.
        assert called_kwargs.get("env") == custom_env
