from pathlib import Path
import pytest
import yaml

from azure.ai.ml._schema._deployment.online.online_deployment import (
    OnlineDeploymentSchema,
    KubernetesOnlineDeploymentSchema,
)
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._util import load_from_dict


@pytest.mark.unittest
class TestDeploymentSchema:
    def test_deserialize(self) -> None:
        path = Path("./tests/test_configs/deployments/online/online_deployment_mir.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            deployment = load_from_dict(OnlineDeploymentSchema, target, context)
            assert deployment

    def test_deserialize_k8s_deployment(self) -> None:
        path = Path("./tests/test_configs/deployments/online/online_deployment_mir.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            k8s_deployment = load_from_dict(KubernetesOnlineDeploymentSchema, target, context)
            assert k8s_deployment
