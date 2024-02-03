# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import subprocess
import sys

import pytest


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


class TestAzureKubernetesServiceIntegration:
    @pytest.mark.live_test_only
    @pytest.mark.skipif(
        not os.environ.get("IDENTITY_LIVE_RESOURCES_PROVISIONED"), reason="Integration resources not provisioned."
    )
    def test_azure_kubernetes(self):

        client_id = os.environ.get("IDENTITY_CLIENT_ID")
        client_secret = os.environ.get("IDENTITY_CLIENT_SECRET")
        tenant_id = os.environ.get("IDENTITY_TENANT_ID")
        resource_group = os.environ.get("IDENTITY_RESOURCE_GROUP")
        aks_cluster_name = os.environ.get("IDENTITY_AKS_CLUSTER_NAME")
        subscription_id = os.environ.get("IDENTITY_SUBSCRIPTION_ID")
        pod_name = os.environ.get("IDENTITY_AKS_POD_NAME", "python-test-app")

        az_path = run_command(["which", "az"])
        kubectl_path = run_command(["which", "kubectl"])
        run_command(
            [az_path, "login", "--service-principal", "-u", client_id, "-p", client_secret, "--tenant", tenant_id]
        )
        run_command([az_path, "account", "set", "--subscription", subscription_id])
        run_command(
            [
                az_path,
                "aks",
                "get-credentials",
                "--resource-group",
                resource_group,
                "--name",
                aks_cluster_name,
                "--overwrite-existing",
            ]
        )
        pod_output = run_command([kubectl_path, "get", "pods", "-o", "jsonpath='{.items[0].metadata.name}'"])
        assert pod_name in pod_output

        output = run_command([kubectl_path, "exec", pod_name, "--", "python", "/app.py"])
        assert "Passed!" in output
