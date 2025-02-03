import pytest
from azure.ai.ml.entities._deployment.pipeline_component_batch_deployment import PipelineComponentBatchDeployment
from azure.ai.ml.entities._builders import BaseNode


@pytest.mark.unittest
class TestPipelineComponentBatchDeployment:
    def test_to_rest_object(self) -> None:
        BaseNode.__init__()
        pipeline_component = PipelineComponentBatchDeployment(
            name="test_pipeline_component",
            endpoint_name="test_endpoint_name",
            component="test_component",
            settings={"test_key": "test_value"},
            tags={"test_key": "test_value"},
            job_definition={"job1": BaseNode()},
        )
        assert True
