# # ---------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # ---------------------------------------------------------


import uuid

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.constants import AssetTypes, DataGenerationTaskType, DataGenerationType
from azure.ai.ml.model_customization import EndpointRequestSettings, PromptSettings, distillation
from azure.ai.ml.entities import ServerlessConnection
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.operations._run_history_constants import JobStatus

TEST_DATASET_PATH = "tests/test_configs/distillation_job/test_datasets"
TRAINING_DATA_PATH = TEST_DATASET_PATH + "/train.jsonl"
VALIDATION_DATA_PATH = TEST_DATASET_PATH + "/validation.jsonl"
TEACHER_MODEL_ENDPOINT_NAME = "Llama-3-1-405B-Instruct-BASE"


@pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
@pytest.mark.usefixtures("recorded_test")
class TestDistillationJob(AzureRecordedTestCase):
    def test_distillation_job(self, client: MLClient) -> None:
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]

        training_data = Input(type=AssetTypes.URI_FILE, path=TRAINING_DATA_PATH)
        validation_data = Input(type=AssetTypes.URI_FILE, path=VALIDATION_DATA_PATH)
        distillation_job = distillation(
            experiment_name=f"Llama-distillation-{short_guid}",
            data_generation_type=DataGenerationType.LABEL_GENERATION,
            data_generation_task_type=DataGenerationTaskType.MATH,
            teacher_model_endpoint_connection=ServerlessConnection(
                name=TEACHER_MODEL_ENDPOINT_NAME, endpoint="", api_key="e"
            ),
            student_model="azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B-Instruct/versions/2",
            training_data=training_data,
            validation_data=validation_data,
            outputs={"registered_model": Output(type="mlflow_model", name=f"llama-distilled-registered-{short_guid}")},
        )

        distillation_job.set_teacher_model_settings(
            inference_parameters={"max_token": 100},
            endpoint_request_settings=EndpointRequestSettings(
                min_endpoint_success_ratio=0.8,
            ),
        )

        distillation_job.set_prompt_settings(prompt_settings=PromptSettings(enable_chain_of_thought=True))

        distillation_job.set_finetuning_settings(hyperparameters={})

        created_job = client.jobs.create_or_update(distillation_job)
        returned_job = client.jobs.get(created_job.name)

        assert returned_job is not None
        assert created_job.id is not None
        assert created_job.type == "distillation"
        assert (
            created_job.experiment_name == f"Llama-distillation-{short_guid}"
        ), "Expected experiment name to be llama-distillation-experiment"
        assert created_job.status == JobStatus.RUNNING
