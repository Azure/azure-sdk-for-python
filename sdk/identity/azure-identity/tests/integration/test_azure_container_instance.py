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

        client_id = os.environ.get("IDENTITY_CLIENT_ID")
        client_secret = os.environ.get("IDENTITY_CLIENT_SECRET")
        tenant_id = os.environ.get("IDENTITY_TENANT_ID")
        resource_group = os.environ.get("IDENTITY_RESOURCE_GROUP")
        subscription_id = os.environ.get("IDENTITY_SUBSCRIPTION_ID")

        container_instance_name = os.environ.get("IDENTITY_CONTAINER_INSTANCE_NAME", "python-container-app")

        az_path = run_command(["which", "az"])
        run_command(
            [az_path, "login", "--service-principal", "-u", client_id, "-p", client_secret, "--tenant", tenant_id]
        )
        run_command([az_path, "account", "set", "--subscription", subscription_id])

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
