# # ---------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # ---------------------------------------------------------

# from typing import Tuple

import uuid

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.distillation.distillation_types import (
    DistillationPromptSettings,
    EndpointRequestSettings,
    TeacherModelEndpoint,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distillation.distillation_job import DistillationJob
from azure.ai.ml.operations._run_history_constants import JobStatus
from azure.identity import DefaultAzureCredential

TEST_DIRECTORY = "tests/test_configs/distillation_job/test_datasets/math"
TRAINING_PATH = TEST_DIRECTORY + "/" + "train.jsonl"
VALIDATION_PATH = TEST_DIRECTORY + "/" + "validation.jsonl"
MODEL_PATH = "azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B/versions/1"


@pytest.mark.skipif(condition=not is_live(), reason="This test requires a live endpoint")
@pytest.mark.usefixtures("recorded_test")
class TestDistillationJob(AzureRecordedTestCase):
    def test_distillation_job(self, client: MLClient) -> None:
        guid = uuid.uuid4()
        short_guid = str(guid)[:8]

        # import os

        # os.environ["MSI_ENDPOINT"] = "http://127.0.0.1:46808/MSI/auth"
        # os.environ["MSI_SECRET"] = "glIo6tMNfNekK7C9l0W7Su1VNhKyz35w"

        # credential = DefaultAzureCredential()
        # credential.get_token("https://login.windows.net/7f292395-a08f-4cc0-b3d0-a400b023b0d2")
        # SUBSCRIPTION_ID = "75703df0-38f9-4e2e-8328-45f6fc810286"
        # RESOURCE_GROUP = "rg-sasumai"
        # WORKSPACE_NAME = "sasum-westus3-ws"
        # client = MLClient(
        #     credential=credential,
        #     subscription_id=SUBSCRIPTION_ID,
        #     resource_group_name=RESOURCE_GROUP,
        #     workspace_name=WORKSPACE_NAME
        # )
        teacher_model = TeacherModelEndpoint(name="Llama-3-1-405B-Instruct-BASE")
        student_model = Input(type=AssetTypes.MLFLOW_MODEL, path=MODEL_PATH)
        training_data = Input(type=AssetTypes.URI_FILE, path=TRAINING_PATH)
        validation_data = Input(type=AssetTypes.URI_FILE, path=VALIDATION_PATH)

        distillation_job = DistillationJob(
            data_generation_type="abel_generation",
            data_generation_task_type="Math",
            teacher_model_endpoint=teacher_model,
            student_model=student_model,
            training_data=training_data,
            validation_data=validation_data,
            inference_parameters={},
            endpoint_request_settings=None,
            prompt_settings=None,
            hyperparameters=None,
            evaluation_settings=None,
            resources=None,
            name=f"llama-{short_guid}",
            experiment_name="llama-distillation-experiment",
            display_name=f"llama-display-name-{short_guid}",
            outputs={"registered_model": Output(type="mlflow_model", name=f"llama-distilled-registered-{short_guid}")},
        )

        created_job = client.jobs.create_or_update(distillation_job)
        returned_job = client.jobs.get(created_job.name)

        assert returned_job is not None
        assert created_job.id is not None
        assert created_job.name == f"llama-{short_guid}", f"Expected job name to be llama-{short_guid}"
        assert (
            created_job.display_name == f"llama-display-name-{short_guid}"
        ), f"Expected display name to be llama-display-name-{short_guid}"
        assert (
            created_job.experiment_name == "llama-distillation-experiment"
        ), "Expected experiment name to be llama-distillation-experiment"
        assert created_job.status == JobStatus.RUNNING
