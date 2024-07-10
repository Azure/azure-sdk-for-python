# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest

from utils import run_command


class TestAzureContainerInstanceIntegration:
    @pytest.mark.live_test_only
    @pytest.mark.skipif(
        not os.environ.get("IDENTITY_LIVE_RESOURCES_PROVISIONED"), reason="Integration resources not provisioned."
    )
    def test_azure_container_instance(self):

        resource_group = os.environ.get("IDENTITY_RESOURCE_GROUP")
        container_instance_name = os.environ.get("IDENTITY_CONTAINER_INSTANCE_NAME", "python-container-app")

        az_path = run_command(["which", "az"])

        # Using "script" as a workaround for "az container exec" requiring a tty.
        # https://github.com/Azure/azure-cli/issues/17530
        command = (
            f"{az_path} container exec -g {resource_group} -n {container_instance_name} --exec-command 'python /app.py'"
        )
        output = run_command(
            [
                "script",
                "-q",
                "-c",
                command,
            ]
        )

        assert "Passed!" in output
