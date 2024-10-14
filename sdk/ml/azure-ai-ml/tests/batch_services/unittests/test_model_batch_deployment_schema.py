from pathlib import Path

import pytest
import yaml

from azure.ai.ml._schema._deployment.batch.model_batch_deployment import ModelBatchDeploymentSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities import BatchDeployment
from azure.ai.ml.entities._util import load_from_dict


def load_batch_deployment_entity_from_yaml(path: str, context={}) -> BatchDeployment:
    """batch deployment yaml -> batch deployment entity"""
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    context.update({BASE_PATH_CONTEXT_KEY: Path(path).parent})
    deployment = load_from_dict(ModelBatchDeploymentSchema, cfg, context)
    return deployment


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestModelBatchDeploymentSchema:
    def test_serialize_model_batch_deployment(self) -> None:
        test_path = "./tests/test_configs/deployments/batch/model_batch_deployment.yaml"
        mbd_entity = load_batch_deployment_entity_from_yaml(test_path)

        assert mbd_entity
        assert mbd_entity.environment == "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33"
        assert mbd_entity.compute == "cpu-cluster"
        assert mbd_entity.settings.output_action == BatchDeploymentOutputAction.APPEND_ROW
        assert mbd_entity.settings.output_file_name == "append_row.txt"
        assert mbd_entity.settings.error_threshold == 10
        assert mbd_entity.settings.mini_batch_size == 5
        assert mbd_entity.settings.max_concurrency_per_instance == 5
        assert mbd_entity.resources.instance_count == 2
