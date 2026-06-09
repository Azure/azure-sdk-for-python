# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json

import pytest

from azure.ai.ml._restclient.v2023_02_01_preview_tsp.models import BatchDeployment as RestBatchDeployment
from azure.ai.ml.entities import PipelineComponent
from azure.ai.ml.entities._deployment.pipeline_component_batch_deployment import PipelineComponentBatchDeployment
from azure.ai.ml.entities._load_functions import load_pipeline_component_batch_deployment


@pytest.mark.unittest
class TestPipelineComponentBatchDeployment:
    HELLO_BATCH_DEPLOYMENT = "tests/test_configs/deployments/batch/pipeline_component_batch_deployment.yml"
    HELLO_BATCH_DEPLOYMENT_REST = "tests/test_configs/deployments/batch/batch_pipeline_component_rest.json"

    def test_to_rest_object(self) -> None:
        pipeline_component = load_pipeline_component_batch_deployment(
            TestPipelineComponentBatchDeployment.HELLO_BATCH_DEPLOYMENT
        )
        assert pipeline_component.type == "pipeline"
        pipeline_component_rest = pipeline_component._to_rest_object(location="eastus")
        assert pipeline_component_rest.properties.deployment_configuration.settings == pipeline_component.settings
        assert (
            pipeline_component_rest.properties.deployment_configuration.component_id.asset_id
            == pipeline_component.component
        )
        assert pipeline_component_rest.properties.description == pipeline_component.description
        assert pipeline_component_rest.tags == pipeline_component.tags
        assert pipeline_component_rest.location == "eastus"

    def test_to_rest_object_for_component_obj(self) -> None:
        pipeline_component = load_pipeline_component_batch_deployment(
            TestPipelineComponentBatchDeployment.HELLO_BATCH_DEPLOYMENT
        )

        pipeline_component.component = PipelineComponent(
            id=pipeline_component.component,
            name="test_component",
            description="component description",
            tags={"tag1": "tag_value"},
        )
        pipeline_component_rest = pipeline_component._to_rest_object(location="eastus")

        assert pipeline_component_rest.properties.deployment_configuration.settings == pipeline_component.settings
        assert (
            pipeline_component_rest.properties.deployment_configuration.component_id.asset_id
            == pipeline_component.component.id
        )
        assert pipeline_component_rest.properties.deployment_configuration.tags == pipeline_component.component.tags
        assert (
            pipeline_component_rest.properties.deployment_configuration.description
            == pipeline_component.component.description
        )
        assert pipeline_component_rest.properties.description == pipeline_component.description
        assert pipeline_component_rest.tags == pipeline_component.tags
        assert pipeline_component_rest.location == "eastus"

    def test_to_dict(self) -> None:
        pipeline_component = load_pipeline_component_batch_deployment(
            TestPipelineComponentBatchDeployment.HELLO_BATCH_DEPLOYMENT,
            params_override=[{"endpoint_name": "azureml:hello_batch2@latest"}],
        )
        pipeline_component_dict = pipeline_component._to_dict()
        assert pipeline_component_dict["name"] == pipeline_component.name
        assert pipeline_component_dict["tags"] == pipeline_component.tags
        assert pipeline_component_dict["description"] == pipeline_component.description
        assert pipeline_component_dict["endpoint_name"] == "azureml:hello_batch2@latest"
        assert pipeline_component_dict["component"] == "azureml:hello_batch@latest"
        assert pipeline_component_dict["settings"] == pipeline_component.settings

    def test_from_rest_object(self) -> None:

        with open(TestPipelineComponentBatchDeployment.HELLO_BATCH_DEPLOYMENT_REST, "r") as file:
            raw = json.load(file)
            raw["properties"]["deploymentConfiguration"] = {
                "deploymentConfigurationType": "PipelineComponent",
                "componentId": {"referenceType": "Id", "assetId": "azureml:hello_batch@latest"},
                "settings": {"componentId": "azureml:hello_batch@latest"},
            }
            pipeline_component_rest = RestBatchDeployment._deserialize(raw, [])
            pipeline_component_from_rest = PipelineComponentBatchDeployment._from_rest_object(pipeline_component_rest)
            assert pipeline_component_from_rest.component == "azureml:hello_batch@latest"
            assert pipeline_component_from_rest.settings["componentId"] == "azureml:hello_batch@latest"
            assert pipeline_component_from_rest.endpoint_name == "achauhan-endpoint-name"

    def test_to_rest_object_is_json_serializable_by_tsp_encoder(self) -> None:
        """Regression test: the body produced by ``_to_rest_object`` is passed as ``body=`` to
        ``v2023_02_01_preview_tsp.BatchDeploymentsOperations.begin_create_or_update``, which
        serializes via ``SdkJSONEncoder``. The encoder fails with
        ``TypeError: Object of type BatchDeployment is not JSON serializable`` if the body is
        a non-TSP (msrest) object. Caught only by sample-pipelines previously."""
        from azure.ai.ml._restclient.v2023_02_01_preview_tsp._utils.model_base import SdkJSONEncoder

        pipeline_component = load_pipeline_component_batch_deployment(
            TestPipelineComponentBatchDeployment.HELLO_BATCH_DEPLOYMENT
        )
        rest_obj = pipeline_component._to_rest_object(location="eastus")
        payload = json.loads(json.dumps(rest_obj, cls=SdkJSONEncoder, exclude_readonly=True))
        assert payload["location"] == "eastus"
        assert (
            payload["properties"]["deploymentConfiguration"]["componentId"]["assetId"]
            == pipeline_component.component
        )
        assert payload["properties"]["deploymentConfiguration"]["deploymentConfigurationType"] == "PipelineComponent"
