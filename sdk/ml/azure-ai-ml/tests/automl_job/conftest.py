from typing import Tuple

import pytest
from test_utilities.utils import download_dataset

from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings

TEST_CONFIG_PATH = "tests/test_configs/automl_job"
TEST_DATASETS_PATH = TEST_CONFIG_PATH + "/" + "test_datasets"

BANK_MARKETING_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "bank_marketing/train"
BANK_MARKETING_TEST_DATASET_PATH = TEST_DATASETS_PATH + "/" + "bank_marketing/valid"

BEER_FORECASTING_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "beer_forecasting/train"

CONLL_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "conll2003/train"
CONLL_VALID_DATASET_PATH = TEST_DATASETS_PATH + "/" + "conll2003/valid"

CREDIT_CARD_FRAUD_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "credit_card_fraud/train"
CREDIT_CARD_FRAUD_TEST_DATASET_PATH = TEST_DATASETS_PATH + "/" + "credit_card_fraud/test"
CREDIT_CARD_FRAUD_VALID_DATASET_PATH = TEST_DATASETS_PATH + "/" + "credit_card_fraud/valid"

MACHINE_DATA_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "machine_data/train"

NEWSGROUP_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "newsgroup/train"
NEWSGROUP_VALID_DATASET_PATH = TEST_DATASETS_PATH + "/" + "newsgroup/valid"

PAPER_CATEGORIZATION_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "paper_categorization/train"
PAPER_CATEGORIZATION_VALID_DATASET_PATH = TEST_DATASETS_PATH + "/" + "paper_categorization/valid"

IMAGE_CLASSIFICATION_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "image_classification/train"
IMAGE_CLASSIFICATION_VALID_DATASET_PATH = TEST_DATASETS_PATH + "/" + "image_classification/valid"

IMAGE_CLASSIFICATION_MULTILABEL_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "image_classification_multilabel/train"
IMAGE_CLASSIFICATION_MULTILABEL_VALID_DATASET_PATH = TEST_DATASETS_PATH + "/" + "image_classification_multilabel/valid"

IMAGE_OBJECT_DETECTION_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "image_object_detection/train"
IMAGE_OBJECT_DETECTION_VALID_DATASET_PATH = TEST_DATASETS_PATH + "/" + "image_object_detection/valid"

IMAGE_SEGMENTATION_TRAIN_DATASET_PATH = TEST_DATASETS_PATH + "/" + "image_instance_segmentation/train"
IMAGE_SEGMENTATION_VALID_DATASET_PATH = TEST_DATASETS_PATH + "/" + "image_instance_segmentation/valid"


@pytest.fixture
def bankmarketing_dataset() -> Tuple[Input, Input, str]:
    # Classification Dataset
    training_data = Input(type=AssetTypes.MLTABLE, path=BANK_MARKETING_TRAIN_DATASET_PATH)
    validation_data = Input(type=AssetTypes.MLTABLE, path=BANK_MARKETING_TEST_DATASET_PATH)
    label_column_name = "y"
    return training_data, validation_data, label_column_name


@pytest.fixture
def credit_card_fraud_dataset() -> Tuple[Input, Input, str]:
    # Classification Dataset
    training_data = Input(type=AssetTypes.MLTABLE, path=CREDIT_CARD_FRAUD_TRAIN_DATASET_PATH)
    validation_data = Input(type=AssetTypes.MLTABLE, path=CREDIT_CARD_FRAUD_VALID_DATASET_PATH)
    label_column_name = "Class"
    return training_data, validation_data, label_column_name


@pytest.fixture
def machinedata_dataset() -> Tuple[Input, str]:
    # Regression Dataset
    training_data = Input(type=AssetTypes.MLTABLE, path=MACHINE_DATA_TRAIN_DATASET_PATH)
    label_column_name = "ERP"
    return training_data, label_column_name


@pytest.fixture
def beer_forecasting_dataset() -> Tuple[Input, ForecastingSettings, str]:
    # Forecasting Dataset
    training_data = Input(type=AssetTypes.MLTABLE, path=BEER_FORECASTING_TRAIN_DATASET_PATH)
    label_column_name = "BeerProduction"
    time_column_name = "DATE"
    forecast_horizon = 12
    frequency = "MS"
    forecasting_settings = ForecastingSettings(
        time_column_name=time_column_name, forecast_horizon=forecast_horizon, frequency=frequency
    )

    return training_data, forecasting_settings, label_column_name


@pytest.fixture
def image_classification_dataset() -> Tuple[str, str]:
    # Download data
    download_url = "https://cvbp-secondary.z19.web.core.windows.net/datasets/image_classification/fridgeObjects.zip"
    data_file = "./fridgeObjects.zip"
    download_dataset(download_url=download_url, data_file=data_file)

    # Classification dataset MLTable paths
    return IMAGE_CLASSIFICATION_TRAIN_DATASET_PATH, IMAGE_CLASSIFICATION_VALID_DATASET_PATH


@pytest.fixture
def image_classification_multilabel_dataset() -> Tuple[str, str]:
    # Download data
    download_url = (
        "https://cvbp-secondary.z19.web.core.windows.net/datasets/image_classification/multilabelFridgeObjects.zip"
    )
    data_file = "./multilabelFridgeObjects.zip"
    download_dataset(download_url=download_url, data_file=data_file)

    # Multilabel classification dataset MLTable paths
    return IMAGE_CLASSIFICATION_MULTILABEL_TRAIN_DATASET_PATH, IMAGE_CLASSIFICATION_MULTILABEL_VALID_DATASET_PATH


@pytest.fixture
def image_object_detection_dataset() -> Tuple[str, str]:
    # Download data
    download_url = "https://cvbp-secondary.z19.web.core.windows.net/datasets/object_detection/odFridgeObjects.zip"
    data_file = "./odFridgeObjects.zip"
    download_dataset(download_url=download_url, data_file=data_file)

    # Image Object Dataset
    return IMAGE_OBJECT_DETECTION_TRAIN_DATASET_PATH, IMAGE_OBJECT_DETECTION_VALID_DATASET_PATH


@pytest.fixture
def image_segmentation_dataset() -> Tuple[str, str]:
    # Download data
    download_url = "https://cvbp-secondary.z19.web.core.windows.net/datasets/object_detection/odFridgeObjectsMask.zip"
    data_file = "./odFridgeObjectsMask.zip"
    download_dataset(download_url=download_url, data_file=data_file)

    # Image Object Dataset
    return IMAGE_SEGMENTATION_TRAIN_DATASET_PATH, IMAGE_SEGMENTATION_VALID_DATASET_PATH


# Text Classification Dataset
@pytest.fixture
def newsgroup() -> Tuple[Input, Input, str]:
    training_data = Input(type=AssetTypes.MLTABLE, path=NEWSGROUP_TRAIN_DATASET_PATH)
    validation_data = Input(type=AssetTypes.MLTABLE, path=NEWSGROUP_VALID_DATASET_PATH)
    target_column_name = "y"

    return training_data, validation_data, target_column_name


# Text Classification Multilabel Dataset
@pytest.fixture
def paper_categorization() -> Tuple[Input, Input, str]:
    training_data = Input(type=AssetTypes.MLTABLE, path=PAPER_CATEGORIZATION_TRAIN_DATASET_PATH)
    validation_data = Input(type=AssetTypes.MLTABLE, path=PAPER_CATEGORIZATION_VALID_DATASET_PATH)
    target_column_name = "terms"

    return training_data, validation_data, target_column_name


# Text NER Dataset
@pytest.fixture
def conll() -> Tuple[Input, Input]:
    training_data = Input(type=AssetTypes.MLTABLE, path=CONLL_TRAIN_DATASET_PATH)
    validation_data = Input(type=AssetTypes.MLTABLE, path=CONLL_VALID_DATASET_PATH)

    return training_data, validation_data
