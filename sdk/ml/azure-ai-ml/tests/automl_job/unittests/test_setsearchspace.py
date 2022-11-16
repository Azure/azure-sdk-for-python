import pytest

from azure.ai.ml.automl import SearchSpace, image_classification, image_object_detection
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.image import ImageClassificationSearchSpace, ImageObjectDetectionSearchSpace
from azure.ai.ml.entities._job.sweep.search_space import Choice, Uniform
from azure.ai.ml.exceptions import ValidationException


@pytest.mark.automl_test
@pytest.mark.parametrize(
    "task_name, expected_type",
    [(image_classification, ImageClassificationSearchSpace), (image_object_detection, ImageObjectDetectionSearchSpace)],
)
def test_searchspace(task_name, expected_type):
    settings = [
        Choice(["vitb16r224", "vits16r224"]),
        Uniform(0.001, 0.01),
        Choice([1, 5]),
    ]
    automl_job = task_name(
        training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
        target_column_name="label",
    )
    searchspace = SearchSpace(
        model_name=settings[0],
        learning_rate=settings[1],
        number_of_epochs=settings[2],
    )
    automl_job.search_space = [searchspace]
    assert automl_job.search_space[-1].model_name == settings[0]
    assert automl_job.search_space[-1].learning_rate == settings[1]
    assert automl_job.search_space[-1].number_of_epochs == settings[2]
    assert isinstance(automl_job.search_space[-1], expected_type)

    searchspace_dict = {
        "model_name": settings[0],
        "learning_rate": settings[1],
        "number_of_epochs": settings[2],
    }

    automl_job.search_space = [searchspace_dict]
    assert automl_job.search_space[-1].model_name == settings[0]
    assert automl_job.search_space[-1].learning_rate == settings[1]
    assert automl_job.search_space[-1].number_of_epochs == settings[2]
    assert isinstance(automl_job.search_space[-1], expected_type)

    automl_job.extend_search_space(searchspace)
    assert automl_job.search_space[-1].model_name == settings[0]
    assert automl_job.search_space[-1].learning_rate == settings[1]
    assert automl_job.search_space[-1].number_of_epochs == settings[2]
    assert isinstance(automl_job.search_space[-1], expected_type)

    assert len(automl_job.search_space) == 2


@pytest.mark.automl_test
@pytest.mark.parametrize(
    "task_name",
    [
        image_classification,
        image_object_detection,
    ],
)
def test_searchspace_invalid(task_name):
    automl_job = task_name(
        training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
        target_column_name="label",
    )
    searchspace = SearchSpace(
        unspported_param=1,
    )
    with pytest.raises(ValidationException):
        automl_job.search_space = [searchspace]
    with pytest.raises(ValidationException):
        automl_job.search_space = [
            {
                "unspported_param": 1,
            }
        ]
    with pytest.raises(ValidationException):
        automl_job.extend_search_space([searchspace])
