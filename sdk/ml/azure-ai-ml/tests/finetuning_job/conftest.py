from typing import Tuple

import pytest
import uuid

from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input

TEST_CONFIG_PATH = "tests/test_configs/finetuning_job"
TEST_DATASETS_PATH = TEST_CONFIG_PATH + "/" + "test_datasets"

TEXT_COMPLETION_TRAIN_DATASET = TEST_DATASETS_PATH + "/" + "text_completion/train.jsonl"
TEXT_COMPLETION_VALIDATION_DATASET = TEST_DATASETS_PATH + "/" + "text_completion/validation.jsonl"


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
def mlflow_model_llama() -> Input:
    # Classification Dataset
    mlflow_model = Input(
        type=AssetTypes.MLFLOW_MODEL,
        path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9",
    )
    return mlflow_model


@pytest.fixture
def mlflow_model_gpt4() -> Input:
    # Classification Dataset
    # Once backend is ready to be able to handle AOAI models, update the path
    mlflow_model = Input(
        type=AssetTypes.MLFLOW_MODEL,
        path="azureml://registries/azureml-meta/models/Llama-2-7b/versions/9",
    )
    return mlflow_model
