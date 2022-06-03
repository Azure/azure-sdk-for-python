# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
import subprocess
import sys
import time
from azure.ai.ml._ml_exceptions import MlException, ErrorCategory, ErrorTarget


def _print_command_results(test_passed, time_taken, output):
    print("Command {}.".format("successful" if test_passed else "failed"))
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

    # We do this join to construct a command because "shell=True" flag, used below, doesn't work with the vector
    # argv form on a mac OS.
    command_to_execute = " ".join(cmd_arguments)

    if not do_not_print:  # Avoid printing the az login service principal password, for example
        print("Preparing to run CLI command: \n{}\n".format(command_to_execute))
        print("Current directory: {}".format(os.getcwd()))

    start_time = time.time()
    try:
        # We redirect stderr to stdout, so that in the case of an error, especially in negative tests,
        # we get the error reply back to check if the error is expected or not.
        # We need "shell=True" flag so that the "az" wrapper works.

        # We also pass the environment variables, because for some tests we modify
        # the environment variables.

        subprocess_args = {"shell": True, "stderr": subprocess.STDOUT, "env": custom_environment}

        if not stderr_to_stdout:
            subprocess_args = {"shell": True, "env": custom_environment}

        if sys.version_info[0] != 2:
            subprocess_args["timeout"] = timeout

        output = subprocess.check_output(command_to_execute, **subprocess_args).decode(encoding="UTF-8")

        time_taken = time.time() - start_time
        if not do_not_print:
            _print_command_results(True, time_taken, output)

        if return_json:
            try:
                return json.loads(exclude_warnings(output))
            except Exception:
                msg = "Expected JSON, instead got: \n{}\n"
                raise MlException(
                    message=msg.format(output),
                    no_personal_data_message=msg.format("[something else]"),
                    target=ErrorTarget.LOCAL_ENDPOINT,
                    error_category=ErrorCategory.SYSTEM_ERROR,
                )
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
        if (curr_index >= start_index) and (curr_index <= end_index):
            if len(json_output) == 0:
                json_output = cmd_line
            else:
                json_output = json_output + "\n" + cmd_line

        curr_index = curr_index + 1

    return json_output
