from pathlib import Path
import pytest
import yaml

from azure.ai.ml._schema._deployment.batch.batch_deployment import BatchDeploymentSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, BatchDeploymentOutputAction
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities import BatchDeployment


def load_batch_deployment_entity_from_yaml(path: str, context={}) -> BatchDeployment:
    """batch deployment yaml -> batch deployment entity"""
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    context.update({BASE_PATH_CONTEXT_KEY: Path(path).parent})
    deployment = load_from_dict(BatchDeploymentSchema, cfg, context)
    return deployment


@pytest.mark.unittest
class TestBatchDeploymentSchema:
    def test_serialize_batch_deployment(self) -> None:
        test_path = "./tests/test_configs/deployments/batch/batch_deployment_1.yaml"
        batch_deployment_entity = load_batch_deployment_entity_from_yaml(test_path)

        assert batch_deployment_entity
        assert batch_deployment_entity.environment == "AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1"
        assert batch_deployment_entity.compute == "cpu-cluster"
        assert batch_deployment_entity.output_action == BatchDeploymentOutputAction.APPEND_ROW
        assert batch_deployment_entity.output_file_name == "append_row.txt"
        assert batch_deployment_entity.error_threshold == 10
        assert batch_deployment_entity.mini_batch_size == 5
        assert batch_deployment_entity.max_concurrency_per_instance == 5
        assert batch_deployment_entity.resources.instance_count == 2
