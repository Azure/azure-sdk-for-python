from pathlib import Path

import pytest
import yaml

from azure.ai.ml._schema._deployment.batch.batch_deployment import BatchDeploymentSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities import BatchDeployment
from azure.ai.ml.entities._util import load_from_dict


def load_batch_deployment_entity_from_yaml(path: str, context={}) -> BatchDeployment:
    """batch deployment yaml -> batch deployment entity"""
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    context.update({BASE_PATH_CONTEXT_KEY: Path(path).parent})
    deployment = load_from_dict(BatchDeploymentSchema, cfg, context)
    return deployment


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestBatchDeploymentSchema:
    def test_serialize_batch_deployment(self) -> None:
        test_path = "./tests/test_configs/deployments/batch/batch_deployment_1.yaml"
        batch_deployment_entity = load_batch_deployment_entity_from_yaml(test_path)

        assert batch_deployment_entity
        assert batch_deployment_entity.environment == "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert batch_deployment_entity.compute == "cpu-cluster"
        assert batch_deployment_entity.output_action == BatchDeploymentOutputAction.APPEND_ROW
        assert batch_deployment_entity.output_file_name == "append_row.txt"
        assert batch_deployment_entity.error_threshold == 10
        assert batch_deployment_entity.mini_batch_size == 5
        assert batch_deployment_entity.max_concurrency_per_instance == 5
        assert batch_deployment_entity.resources.instance_count == 2

    def test_registry_assets_batch_deployment(self) -> None:
        test_path = "./tests/test_configs/deployments/batch/batch_deployment_registry.yaml"
        batch_deployment_entity = load_batch_deployment_entity_from_yaml(test_path)
        assert batch_deployment_entity
        assert batch_deployment_entity.model == "azureml://registries/testFeed/models/model_version_e2e/versions/1"
        assert (
            batch_deployment_entity.environment
            == "azureml://registries/testfeed/environments/4c99f460-20cd-4821-8745-202aa7555604/versions/93435847-704b-4280-83f3-f735d8b5eff7"
        )
        assert batch_deployment_entity.compute == "cpu-cluster"
        assert batch_deployment_entity.output_action == BatchDeploymentOutputAction.APPEND_ROW
        assert batch_deployment_entity.output_file_name == "append_row.txt"
        assert batch_deployment_entity.error_threshold == 10
        assert batch_deployment_entity.mini_batch_size == 5
        assert batch_deployment_entity.max_concurrency_per_instance == 5
        assert batch_deployment_entity.resources.instance_count == 2
