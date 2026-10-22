# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest

from utils import run_command


class TestAzureVirtualMachinesIntegration:
    @pytest.mark.live_test_only
    @pytest.mark.skipif(
        not os.environ.get("IDENTITY_LIVE_RESOURCES_PROVISIONED"), reason="Integration resources not provisioned."
    )
    def test_azure_virtual_machine(self):

        resource_group = os.environ.get("IDENTITY_RESOURCE_GROUP")

        user_assigned_client_id = os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID")
        storage_1 = os.environ.get("IDENTITY_STORAGE_NAME_1")
        storage_2 = os.environ.get("IDENTITY_STORAGE_NAME_2")
        vm_name = os.environ.get("IDENTITY_VM_NAME", "python-test-app")

        az_path = run_command(["which", "az"])

        script_string = (
            f"export IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID={user_assigned_client_id} && "
            f"export IDENTITY_STORAGE_NAME_1={storage_1} && "
            f"export IDENTITY_STORAGE_NAME_2={storage_2} && "
            "python3 /sdk/sdk/identity/azure-identity/tests/integration/azure-vms/app.py"
        )
        output = run_command(
            [
                az_path,
                "vm",
                "run-command",
                "invoke",
                "-n",
                vm_name,
                "-g",
                resource_group,
                "--command-id",
                "RunShellScript",
                "--scripts",
                script_string,
            ]
        )
        assert "Passed!" in output
