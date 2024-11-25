# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import subprocess
import sys

from azure.core import PipelineClient
from azure.core.pipeline import policies


def run_command(command, exit_on_failure=True) -> str:
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8").strip()
        return result
    except subprocess.CalledProcessError as ex:
        result = ex.output.decode("utf-8").strip()
        if exit_on_failure:
            print(result)
            sys.exit(1)
        return result


def get_pipeline_client(base_url: str) -> PipelineClient:
    policy_list = [
        policies.RetryPolicy(),
        policies.ContentDecodePolicy(),
    ]
    return PipelineClient(base_url, policies=policy_list)
