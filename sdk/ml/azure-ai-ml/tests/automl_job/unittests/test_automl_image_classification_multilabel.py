# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    MLTableJobInput,
    ClassificationMultilabelPrimaryMetrics,
    SamplingAlgorithmType,
    UserIdentity,
    StochasticOptimizer,
    LearningRateScheduler,
    ImageModelSettingsClassification,
)
from azure.ai.ml.automl import image_classification_multilabel
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.sweep import (
    BanditPolicy,
    Choice,
    Uniform,
)
from azure.ai.ml.entities._job.automl.image import (
    ImageClassificationMultilabelJob,
    ImageClassificationSearchSpace,
)


@pytest.mark.unittest
class TestAutoMLImageClassificationMultilabel:
    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_image_classification_multilabel_task(self, run_type):
        # Create AutoML Image Classification Multilabel task
        identity = UserIdentity()
        image_classification_multilabel_job = image_classification_multilabel(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
            primary_metric=ClassificationMultilabelPrimaryMetrics.IOU,
            validation_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/valid.csv"),
            # Job attributes
            compute="gpu_cluster",
            name="image_classifier_multilabel_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            identity=identity,
        )  # type: ImageClassificationMultilabelJob

        if (run_type == "single") or (run_type == "sweep"):
            # image_classification_multilabel_job.limits = {"timeout": 60, "max_trials": 1, "max_concurrent_trials": 1}
            image_classification_multilabel_job.set_limits(timeout_minutes=60)
        elif run_type == "automode":
            # image_classification_multilabel_job.limits = {"timeout": 60, "max_trials": 2, "max_concurrent_trials": 1}
            image_classification_multilabel_job.set_limits(timeout_minutes=60, max_trials=2, max_concurrent_trials=1)

        # image_classification_multilabel_job.image_model = {
        #     "checkpoint_frequency": 1,
        #     "early_stopping": True,
        #     "early_stopping_delay": 2,
        #     "early_stopping_patience": 2,
        #     "evaluation_frequency": 1,
        # }
        image_classification_multilabel_job.set_image_model(
            checkpoint_frequency=1,
            early_stopping=True,
            early_stopping_delay=2,
            early_stopping_patience=2,
            evaluation_frequency=1,
        )

        if run_type == "sweep":
            """
            image_classification_multilabel_job.search_space = [
                {
                    "model_name": 'vitb16r224',
                    "learning_rate": Uniform(0.005, 0.05),
                    "number_of_epochs": Choice([15, 30]),
                    "gradient_accumulation_step": Choice([1, 2]),
                },
                {
                    "model_name": 'seresnext',
                    "learning_rate": Uniform(0.005, 0.05),
                    "validation_resize_size": Choice([288, 320, 352]),
                    "validation_crop_size": Choice([224, 256]),
                    "training_crop_size": Choice([224, 256]),
                },
            ]
            """
            search_sub_space_1 = ImageClassificationSearchSpace(
                model_name="vitb16r224",
                learning_rate=Uniform(0.005, 0.05),
                number_of_epochs=Choice([15, 30]),
                gradient_accumulation_step=Choice([1, 2]),
            )
            search_sub_space_2 = ImageClassificationSearchSpace(
                model_name="seresnext",
                learning_rate=Uniform(0.005, 0.05),
                validation_resize_size=Choice([288, 320, 352]),
                validation_crop_size=Choice([224, 256]),
                training_crop_size=Choice([224, 256]),
            )
            image_classification_multilabel_job.extend_search_space([search_sub_space_1, search_sub_space_2])

            early_termination_policy = BanditPolicy(evaluation_interval=10, slack_factor=0.2)
            # image_classification_multilabel_job.sweep = {
            #     "max_concurrent_trials": 4,
            #     "max_trials": 20,
            #     "sampling_algorithm": SamplingAlgorithmType.GRID,
            #     "early_termination": early_termination_policy,
            # }
            image_classification_multilabel_job.set_sweep(
                sampling_algorithm=SamplingAlgorithmType.GRID,
                max_concurrent_trials=4,
                max_trials=20,
                early_termination=early_termination_policy,
            )

        # check the rest object
        rest_obj = image_classification_multilabel_job._to_rest_object()
        assert rest_obj.properties.identity == identity

        def _check_data_type(data, expected_type, expected_path, msg):
            if expected_type == MLTableJobInput:
                assert isinstance(data, MLTableJobInput), "{} data is not MLTableJobInput".format(msg)
            elif expected_type == Input:
                assert isinstance(data, Input), "{} data is not Input".format(msg)
                assert data.type == AssetTypes.MLTABLE, "{} data type not set correctly".format(msg)
                assert data.path == expected_path, "{} data path not set correctly".format(msg)

        _check_data_type(
            rest_obj.properties.task_details.data_settings.training_data.data, MLTableJobInput, None, "Training"
        )
        _check_data_type(
            rest_obj.properties.task_details.data_settings.validation_data.data, MLTableJobInput, None, "Validation"
        )

        original_obj = ImageClassificationMultilabelJob._from_rest_object(rest_obj)
        assert image_classification_multilabel_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.compute == "gpu_cluster", "Compute not set correctly"
        assert original_obj.name == "image_classifier_multilabel_job", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        assert original_obj.identity == identity
        # check if the original job inputs were restored
        _check_data_type(original_obj._data.training_data.data, Input, "https://foo/bar/train.csv", "Training")
        _check_data_type(original_obj._data.validation_data.data, Input, "https://foo/bar/valid.csv", "Validation")

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (("adam", "warmup_cosine"), (StochasticOptimizer.ADAM, LearningRateScheduler.WARMUP_COSINE)),
            (
                ("Adam", "WarmupCosine"),
                (StochasticOptimizer.ADAM, LearningRateScheduler.WARMUP_COSINE),
            ),
            (
                (None, None),
                (None, None),
            ),
        ],
        ids=["snake case", "camel case", "none values"],
    )
    def test_set_image_model_with_valid_values(self, settings, expected):
        image_classification_multilabel_job = image_classification_multilabel(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
        )  # type: ImageClassificationJob
        image_classification_multilabel_job.set_image_model(
            optimizer=settings[0],
            learning_rate_scheduler=settings[1],
        )
        assert image_classification_multilabel_job.image_model.optimizer == expected[0]
        assert image_classification_multilabel_job.image_model.learning_rate_scheduler == expected[1]

    @pytest.mark.parametrize(
        "settings, expected",
        [(("adamW", None), pytest.raises(KeyError)), ((None, "Warmup_Cosine"), pytest.raises(KeyError))],
        ids=["optimizer_invalid", "learning_rate_scheduler_invalid"],
    )
    def test_set_image_model_with_invalid_values(self, settings, expected):
        with expected:
            image_classification_multilabel_job = image_classification_multilabel(
                training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
                target_column_name="label",
            )  # type: ImageClassificationJob
            image_classification_multilabel_job.set_image_model(
                optimizer=settings[0], learning_rate_scheduler=settings[1]
            )

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (("adam", "warmup_cosine"), (StochasticOptimizer.ADAM, LearningRateScheduler.WARMUP_COSINE)),
            (
                ("Adam", "WarmupCosine"),
                (StochasticOptimizer.ADAM, LearningRateScheduler.WARMUP_COSINE),
            ),
            (
                (None, None),
                (None, None),
            ),
        ],
        ids=["snake case", "camel case", "none values"],
    )
    def test_set_image_model_with_settings_object(self, settings, expected):
        image_model_settings = ImageModelSettingsClassification(
            optimizer=settings[0], learning_rate_scheduler=settings[1]
        )

        image_classification_multilabel_job = image_classification_multilabel(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
            image_model=image_model_settings,
        )  # type: ImageClassificationJob

        assert image_classification_multilabel_job.image_model.optimizer == expected[0]
        assert image_classification_multilabel_job.image_model.learning_rate_scheduler == expected[1]
