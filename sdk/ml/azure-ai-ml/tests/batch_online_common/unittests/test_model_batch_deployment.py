# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest

from azure.ai.ml._restclient.v2022_05_01.models import BatchOutputAction
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities import ModelBatchDeployment
from azure.ai.ml.entities._load_functions import load_model_batch_deployment
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.unittest
class TestModelBatchDeployment:
    MODEL_BATCH_DEPLOYMNET = "./tests/test_configs/deployments/batch/model_batch_deployment.yaml"

    def test_to_rest_object(self) -> None:
        deployment = load_model_batch_deployment(
            TestModelBatchDeployment.MODEL_BATCH_DEPLOYMNET, params_override=[{"endpoint_name": "some-en-name"}]
        )
        assert deployment.type == "model"
        rest_deployment = deployment._to_rest_object(location="eastus")
        assert rest_deployment.location == "eastus"
        assert rest_deployment.properties.description == deployment.description
        assert rest_deployment.properties.environment_id == deployment.environment
        assert rest_deployment.properties.model.asset_id.name == "model-1"
        assert rest_deployment.properties.code_configuration.code_id == deployment.code_configuration.code
        assert (
            rest_deployment.properties.code_configuration.scoring_script == deployment.code_configuration.scoring_script
        )
        assert rest_deployment.properties.output_file_name == deployment.settings.output_file_name
        assert str(rest_deployment.properties.output_action) == "BatchOutputAction.APPEND_ROW"
        assert rest_deployment.properties.resources.instance_count == deployment.resources.instance_count
        assert rest_deployment.properties.retry_settings.max_retries == deployment.settings.retry_settings.max_retries
        assert (
            rest_deployment.properties.max_concurrency_per_instance == deployment.settings.max_concurrency_per_instance
        )
        assert rest_deployment.properties.environment_variables == deployment.settings.environment_variables
        assert rest_deployment.properties.compute == deployment.compute
        assert rest_deployment.properties.properties == deployment.properties
        assert rest_deployment.tags == deployment.tags

    def test_output_action_yaml_to_rest(self):
        assert (
            ModelBatchDeployment._yaml_output_action_to_rest_output_action(BatchDeploymentOutputAction.APPEND_ROW)
            == BatchOutputAction.APPEND_ROW
        )
        assert (
            ModelBatchDeployment._yaml_output_action_to_rest_output_action(BatchDeploymentOutputAction.SUMMARY_ONLY)
            == BatchOutputAction.SUMMARY_ONLY
        )

    def test_validation_fails_if_output_file_name_and_summary_output_action(self) -> None:
        deployment = load_model_batch_deployment(TestModelBatchDeployment.MODEL_BATCH_DEPLOYMNET)
        deployment.settings.output_action = BatchDeploymentOutputAction.SUMMARY_ONLY
        deployment.settings.output_file_name = "some_file_name"
        with pytest.raises(ValidationException) as ex:
            deployment._to_rest_object(location="westus")
        assert "When output_action is set to summary_only, the output_file_name need not to be specified." == str(
            ex.value
        )

    def test_to_dict(self) -> None:
        deployment = load_model_batch_deployment(TestModelBatchDeployment.MODEL_BATCH_DEPLOYMNET)
        deployment_dict = deployment._to_dict()
        assert deployment_dict["name"] == deployment.name
        assert deployment_dict["endpoint_name"] == deployment.endpoint_name
        assert deployment_dict["model"]["name"] == deployment.model.name
        assert deployment_dict["compute"] == "azureml:cpu-cluster"
        assert deployment_dict["resources"]["instance_count"] == deployment.resources.instance_count
        assert deployment_dict["settings"]["error_threshold"] == deployment.settings.error_threshold
        assert deployment_dict["settings"]["output_action"] == "append_row"

    def test_settings_getter_setter(self) -> None:
        """Test getter and setter for settings in ModelBatchDeployment."""
        # Create a minimal batch deployment
        deployment = ModelBatchDeployment(
            name="test-deployment",
            endpoint_name="test-endpoint",
            model="azureml:model:1",
            compute="azureml:cpu-cluster",
            resources={"instance_count": 2},
        )
        assert deployment.compute == "azureml:cpu-cluster"
        assert deployment.resources["instance_count"] == 2

        # Test setting individual settings properties
        deployment.settings.output_file_name = "results.csv"
        deployment.settings.output_action = BatchDeploymentOutputAction.APPEND_ROW
        deployment.settings.error_threshold = 10
        deployment.settings.max_concurrency_per_instance = 4
        deployment.settings.mini_batch_size = 5
        deployment.settings.environment_variables = {"ENV_VAR1": "value1", "ENV_VAR2": "value2"}

        # Verify individual settings can be retrieved correctly
        assert deployment.settings.output_file_name == "results.csv"
        assert deployment.settings.output_action == BatchDeploymentOutputAction.APPEND_ROW
        assert deployment.settings.error_threshold == 10
        assert deployment.settings.max_concurrency_per_instance == 4
        assert deployment.settings.mini_batch_size == 5
        assert deployment.settings.environment_variables == {"ENV_VAR1": "value1", "ENV_VAR2": "value2"}
