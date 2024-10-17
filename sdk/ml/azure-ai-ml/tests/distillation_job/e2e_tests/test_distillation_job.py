# # ---------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # ---------------------------------------------------------

import uuid

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import Input, MLClient, Output, distillation
from azure.ai.ml.constants import AssetTypes, DataGenerationTaskType, DataGenerationType
from azure.ai.ml.distillation import DistillationPromptSettings, EndpointRequestSettings
from azure.ai.ml.entities import ResourceConfiguration
from azure.ai.ml.operations._run_history_constants import JobStatus


@pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
@pytest.mark.usefixtures("recorded_test")
class TestDistillationJob(AzureRecordedTestCase):
    def test_distillation_job(self, client: MLClient) -> None:
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]

        distillation_job = distillation(
            experiment_name=f"Llama-distillation-{short_guid}",
            data_generation_type=DataGenerationType.LabelGeneration,
            data_generation_task_type=DataGenerationTaskType.NLI,
            teacher_model_endpoint="Llama-3-1-405B-Instruct-BASE",
            student_model=Input(
                type=AssetTypes.MLFLOW_MODEL,
                path="azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B/versions/1",
            ),
            training_data=Input(type=AssetTypes.URI_FILE, path=""),
            validation_data=Input(type=AssetTypes.URI_FILE, path=""),
            inference_parameters={},
            endpoint_request_settings=EndpointRequestSettings(),
            prompt_settings=DistillationPromptSettings(),
            hyperparameters={},
            resources=ResourceConfiguration(instance_type="Standard_Dv2"),
            outputs={"registered_model": Output(type="mlflow_model", name=f"llama-distilled-registered-{short_guid}")},
        )

        created_job = client.jobs.create_or_update(distillation_job)
        returned_job = client.jobs.get(created_job.name)

        assert returned_job is not None
        assert created_job.id is not None
        assert created_job.type == "distillation"
        assert (
            created_job.experiment_name == f"Llama-distillation-{short_guid}"
        ), "Expected experiment name to be llama-distillation-experiment"
        assert created_job.status == JobStatus.RUNNING
