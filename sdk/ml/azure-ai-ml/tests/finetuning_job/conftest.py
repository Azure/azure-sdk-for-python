from pathlib import Path
from typing import Tuple

import pytest
import uuid

from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities import JobResources, QueueSettings
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.finetuning import FineTuningTaskType, create_finetuning_job
from azure.ai.ml import load_job
from azure.ai.ml.entities import JobResources, QueueSettings
from azure.ai.ml.entities._job.finetuning.custom_model_finetuning_job import (
    CustomModelFineTuningJob,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._restclient.v2024_10_01_preview.models import (
    FineTuningJob as RestFineTuningJob,
)

TEST_CONFIG_PATH = "tests/test_configs/finetuning_job"
TEST_DATASETS_PATH = TEST_CONFIG_PATH + "/" + "test_datasets"

TEXT_COMPLETION_TRAIN_DATASET = TEST_DATASETS_PATH + "/" + "text_completion/train.jsonl"
TEXT_COMPLETION_VALIDATION_DATASET = TEST_DATASETS_PATH + "/" + "text_completion/validation.jsonl"


@pytest.fixture
def finetuning_job_compute_yaml():
    return Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_maap_finetuning_job_compute.yaml"
    )


@pytest.fixture
def finetuning_job_instance_types_yaml():
    return Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_maap_finetuning_job_instance_types.yaml"
    )


@pytest.fixture
def finetuning_job_queue_settings_yaml():
    return Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_maap_finetuning_job_queue_settings.yaml"
    )


@pytest.fixture
def maas_finetuning_job() -> CustomModelFineTuningJob:
    test_schema_path = Path(
        "./tests/test_configs/finetuning_job/e2e_configs/custom_model_finetuning_job/mock_custom_model_finetuning_job_full.yaml"
    )
    job = load_job(test_schema_path)
    job = CustomModelFineTuningJob._from_rest_object(CustomModelFineTuningJob._to_rest_object(job))
    return job


@pytest.fixture
def maap_finetuning_job_compute(finetuning_job_compute_yaml) -> RestFineTuningJob:
    job = load_job(finetuning_job_compute_yaml)
    rest_object = CustomModelFineTuningJob._from_rest_object(CustomModelFineTuningJob._to_rest_object(job))
    return rest_object


@pytest.fixture
def maap_finetuning_job_instance_types(
    finetuning_job_instance_types_yaml,
) -> RestFineTuningJob:
    job = load_job(finetuning_job_instance_types_yaml)
    rest_object = CustomModelFineTuningJob._from_rest_object(CustomModelFineTuningJob._to_rest_object(job))
    return rest_object


@pytest.fixture
def maap_finetuning_job_queue_settings(
    finetuning_job_queue_settings_yaml,
) -> RestFineTuningJob:
    job = load_job(finetuning_job_queue_settings_yaml)
    rest_object = CustomModelFineTuningJob._from_rest_object(CustomModelFineTuningJob._to_rest_object(job))
    return rest_object


@pytest.fixture
def text_completion_dataset() -> Tuple[Input, Input]:
    training_data = Input(
        type=AssetTypes.URI_FILE,
        path=TEXT_COMPLETION_TRAIN_DATASET,
        # "azureml://locations/westus3/workspaces/a7cd11a2-80c5-41ab-b56d-161c57f62fbd/data/samsum-train-data-small/versions/3",
    )
    validation_data = Input(
        type=AssetTypes.URI_FILE,
        path=TEXT_COMPLETION_VALIDATION_DATASET,
        # "azureml://locations/westus3/workspaces/a7cd11a2-80c5-41ab-b56d-161c57f62fbd/data/samsum-train-data-small/versions/3",
    )
    return training_data, validation_data


@pytest.fixture
def text_completion_train_data() -> str:
    return TEXT_COMPLETION_TRAIN_DATASET


@pytest.fixture
def text_completion_validation_data() -> str:
    return TEXT_COMPLETION_VALIDATION_DATASET


@pytest.fixture
def mlflow_model_llama3_8B() -> str:
    return "azureml://registries/azureml-meta/models/Meta-Llama-3-8B/versions/8"


@pytest.fixture
def output_model_name_prefix() -> str:
    guid = uuid.uuid4()
    short_guid = str(guid)[:8]
    return f"llama-3-8B-finetuned-{short_guid}"


@pytest.fixture
def mlflow_model_gpt4() -> Input:
    # Classification Dataset
    # Once backend is ready to be able to handle AOAI models, update the path
    mlflow_model = Input(
        type=AssetTypes.MLFLOW_MODEL,
        path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9",
    )
    return mlflow_model


@pytest.fixture
def finetuning_job(
    text_completion_train_data: str,
    text_completion_validation_data: str,
    mlflow_model_llama3_8B: str,
):
    display_name = "llama-3-8B-display-name"
    name = "llama-3-8B"
    experiment_name = "llama-3-8B-finetuning-experiment"
    finetuning_job = create_finetuning_job(
        task=FineTuningTaskType.TEXT_COMPLETION,
        training_data=text_completion_train_data,
        validation_data=text_completion_validation_data,
        hyperparameters={
            "per_device_train_batch_size": "1",
            "learning_rate": "0.00002",
            "num_train_epochs": "1",
        },
        model=mlflow_model_llama3_8B,
        display_name=display_name,
        name=name,
        experiment_name=experiment_name,
        tags={"foo_tag": "bar"},
        properties={"my_property": "my_value"},
        output_model_name_prefix="llama-finetune-registered-1234",
    )

    return finetuning_job


@pytest.fixture
def finetuning_job_with_name_updated(finetuning_job: CustomModelFineTuningJob, output_model_name_prefix):
    guid = uuid.uuid4()
    short_guid = str(guid)[:8]
    display_name = f"llama-3-8B-display-name-{short_guid}"
    name = f"llama-3-8B-{short_guid}"
    finetuning_job.name = name
    finetuning_job.display_name = display_name
    finetuning_job.outputs["registered_model"].name = output_model_name_prefix
    return finetuning_job


@pytest.fixture
def finetuning_job_compute(finetuning_job_with_name_updated):
    finetuning_job_with_name_updated.compute = "gpu-compute-low-pri"
    return finetuning_job_with_name_updated


@pytest.fixture
def finetuning_job_queue_settings(finetuning_job_with_name_updated):
    # Currently queue_settings are not used in backend.
    # For job to run, we set the compute to aml compute cluster.
    # When we support running on singularity we can set the compute to singularity VC
    # and set the queue_settings as per need which will be honored in the backend.
    finetuning_job_with_name_updated.compute = "gpu-compute-low-pri"
    finetuning_job_with_name_updated.queue_settings = QueueSettings(job_tier="Standard")
    return finetuning_job_with_name_updated


@pytest.fixture
def finetuning_job_instance_types(finetuning_job_with_name_updated):
    finetuning_job_with_name_updated.resources = JobResources(
        instance_types=["Standard_NC96ads_A100_v4", "Standard_E4s_v3"]
    )
    return finetuning_job_with_name_updated


@pytest.fixture
def expected_maas_finetuning_job(finetuning_job) -> CustomModelFineTuningJob:
    return finetuning_job


@pytest.fixture
def expected_maap_finetuning_job_compute(finetuning_job) -> CustomModelFineTuningJob:
    finetuning_job.name = "llama-3-8B-with-compute"
    finetuning_job.compute = "gpu-compute-low-pri"
    return finetuning_job


@pytest.fixture
def expected_maap_finetuning_job_instance_types(finetuning_job) -> CustomModelFineTuningJob:
    finetuning_job.name = "llama-3-8B-with-instance-types"
    finetuning_job.resources = JobResources(instance_types=["Standard_NC96ads_A100_v4", "Standard_E4s_v3"])
    return finetuning_job


@pytest.fixture
def expected_maap_finetuning_job_queue_settings(
    finetuning_job,
) -> CustomModelFineTuningJob:
    finetuning_job.compute = "gpu-compute-low-pri"
    finetuning_job.name = "llama-3-8B-with-queue-settings"
    finetuning_job.queue_settings = QueueSettings(job_tier="Standard")
    return finetuning_job
