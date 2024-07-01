# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest

from utils import run_command


class TestAzureKubernetesServiceIntegration:
    @pytest.mark.live_test_only
    @pytest.mark.skipif(
        not os.environ.get("IDENTITY_LIVE_RESOURCES_PROVISIONED"), reason="Integration resources not provisioned."
    )
    def test_azure_kubernetes(self):

        resource_group = os.environ.get("IDENTITY_RESOURCE_GROUP")
        aks_cluster_name = os.environ.get("IDENTITY_AKS_CLUSTER_NAME")
        pod_name = os.environ.get("IDENTITY_AKS_POD_NAME", "python-test-app")

        az_path = run_command(["which", "az"])
        kubectl_path = run_command(["which", "kubectl"])
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

        output = run_command([kubectl_path, "exec", pod_name, "--", "python3", "/app.py"])
        assert "Passed!" in output
