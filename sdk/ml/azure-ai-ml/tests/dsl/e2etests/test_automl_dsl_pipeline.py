from pathlib import Path

import pydash
import pytest
from test_utilities.utils import assert_final_job_status

from azure.ai.ml import Input, MLClient, automl, dsl
from azure.ai.ml.automl import (
    classification,
    forecasting,
    regression,
    text_classification,
    text_classification_multilabel,
    text_ner,
)
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities._job.automl import SearchSpace
from azure.ai.ml.entities._job.automl.image import ImageClassificationSearchSpace, ImageObjectDetectionSearchSpace
from azure.ai.ml.entities._job.automl.nlp import NlpFeaturizationSettings
from azure.ai.ml.entities._job.automl.tabular import TabularFeaturizationSettings
from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings
from azure.ai.ml.operations._run_history_constants import JobStatus
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform

from devtools_testutils import AzureRecordedTestCase

tests_root_dir = Path(__file__).parent.parent.parent


@pytest.mark.automle2etest
@pytest.mark.skip(reason="migration skip: gpu-cluster is not available yet.")
@pytest.mark.pipeline_test
class TestAutomlDSLPipeline(AzureRecordedTestCase):
    def test_automl_classification_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_automl_classification_in_pipeline", default_compute_target="automl-cpu-cluster")
        def train_automl_classification_in_pipeline(
            class_train_data,
            class_valid_data,
        ):
            classification_node = classification(
                training_data=class_train_data,
                validation_data=class_valid_data,
                test_data=class_valid_data,
                target_column_name="y",
                primary_metric="accuracy",
                featurization=TabularFeaturizationSettings(mode="Auto"),
            )
            classification_node.set_limits(max_trials=1)
            classification_node.set_training(enable_stack_ensemble=False, enable_vote_ensemble=False)

        class_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/bank_marketing/train",
        )
        class_valid = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/bank_marketing/valid",
        )

        pipeline_job: PipelineJob = train_automl_classification_in_pipeline(class_train, class_valid)

        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        classification_dict = pydash.omit(actual_dict["properties"]["jobs"]["classification_node"], fields_to_omit)
        assert classification_dict == {
            "test_data": "${{parent.inputs.class_valid_data}}",
            "validation_data": "${{parent.inputs.class_valid_data}}",
            "training_data": "${{parent.inputs.class_train_data}}",
            "target_column_name": "y",
            "tags": {},
            "type": "automl",
            "outputs": {},
            "log_verbosity": "info",
            "limits": {"max_trials": 1},
            "featurization": {"mode": "auto"},
            "training": {
                "enable_model_explainability": True,
                "enable_stack_ensemble": False,
                "enable_vote_ensemble": False,
            },
            "task": "classification",
            "primary_metric": "accuracy",
        }

    def test_automl_regression_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_automl_regression_in_pipeline", default_compute_target="automl-cpu-cluster")
        def train_automl_regression_in_pipeline(regression_train_data):
            regression_node = regression(
                primary_metric="r2_score",
                target_column_name="ERP",
                training_data=regression_train_data,
            )
            regression_node.set_limits(max_trials=1)
            regression_node.set_training(enable_stack_ensemble=False, enable_vote_ensemble=False)
            regression_node.set_featurization(mode="auto")

        regression_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/machine_data/train",
        )

        pipeline_job: PipelineJob = train_automl_regression_in_pipeline(regression_train)

        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        regression_dict = pydash.omit(actual_dict["properties"]["jobs"]["regression_node"], fields_to_omit)
        assert regression_dict == {
            "training_data": "${{parent.inputs.regression_train_data}}",
            "target_column_name": "ERP",
            "tags": {},
            "type": "automl",
            "outputs": {},
            "log_verbosity": "info",
            "limits": {"max_trials": 1},
            "featurization": {"mode": "auto"},
            "training": {
                "enable_model_explainability": True,
                "enable_stack_ensemble": False,
                "enable_vote_ensemble": False,
            },
            "task": "regression",
            "primary_metric": "r2_score",
        }

    def test_automl_forecasting_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_with_automl_in_pipeline", default_compute_target="automl-cpu-cluster")
        def train_automl_forecasting_in_pipeline(
            forecasting_train_data,
        ):
            forecasting_settings = ForecastingSettings(time_column_name="DATE", forecast_horizon=12, frequency="MS")

            forecasting_node = forecasting(
                primary_metric="normalized_root_mean_squared_error",
                target_column_name="BeerProduction",
                training_data=forecasting_train_data,
                n_cross_validations=2,
                forecasting_settings=forecasting_settings,
            )
            forecasting_node.set_limits(max_trials=1)
            forecasting_node.set_training(enable_stack_ensemble=False, enable_vote_ensemble=False)
            forecasting_node.set_featurization(mode="auto")

        forecasting_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/beer_forecasting/train",
        )

        pipeline_job: PipelineJob = train_automl_forecasting_in_pipeline(forecasting_train_data=forecasting_train)

        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        forecasting_dict = pydash.omit(actual_dict["properties"]["jobs"]["forecasting_node"], fields_to_omit)
        assert forecasting_dict == {
            "training_data": "${{parent.inputs.forecasting_train_data}}",
            "n_cross_validations": 2,
            "target_column_name": "BeerProduction",
            "tags": {},
            "type": "automl",
            "outputs": {},
            "log_verbosity": "info",
            "limits": {"max_trials": 1},
            "featurization": {"mode": "auto"},
            "training": {
                "enable_model_explainability": True,
                "enable_stack_ensemble": False,
                "enable_vote_ensemble": False,
            },
            "task": "forecasting",
            "forecasting": {"forecast_horizon": 12, "time_column_name": "DATE", "frequency": "MS"},
            "primary_metric": "normalized_root_mean_squared_error",
        }

    def test_automl_text_classification_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_automl_text_class_in_pipeline", default_compute_target="gpu-cluster")
        def train_automl_text_class_in_pipeline(
            text_classification_train,
            text_classification_valid,
        ):
            text_classification_node = text_classification(
                training_data=text_classification_train,
                validation_data=text_classification_valid,
                target_column_name="y",
                primary_metric="accuracy",
                featurization=NlpFeaturizationSettings(dataset_language="eng"),
            )
            text_classification_node.set_limits(max_concurrent_trials=1)

        text_classification_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/newsgroup/train",
        )
        text_classification_valid = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/newsgroup/valid",
        )

        pipeline_job: PipelineJob = train_automl_text_class_in_pipeline(
            text_classification_train, text_classification_valid
        )
        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        job_dict = pydash.omit(actual_dict["properties"]["jobs"]["text_classification_node"], fields_to_omit)
        assert job_dict == {
            "training_data": "${{parent.inputs.text_classification_train}}",
            "validation_data": "${{parent.inputs.text_classification_valid}}",
            "target_column_name": "y",
            "tags": {},
            "type": "automl",
            "outputs": {},
            "limits": {"max_trials": 1, "max_concurrent_trials": 1},
            "featurization": {"dataset_language": "eng"},
            "task": "text_classification",
            "primary_metric": "accuracy",
        }

    def test_automl_text_classification_multilabel_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_automl_text_class_multilabel_in_pipeline", default_compute_target="gpu-cluster")
        def train_automl_text_class_multilabel_in_pipeline(
            text_classification_multilabel_train,
            text_classification_multilabel_valid,
        ):
            text_classification_multilabel_node = text_classification_multilabel(
                training_data=text_classification_multilabel_train,
                validation_data=text_classification_multilabel_valid,
                target_column_name="terms",
                primary_metric="accuracy",
            )
            text_classification_multilabel_node.set_limits(max_concurrent_trials=1)

        text_classification_multilabel_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/paper_categorization/train",
        )

        text_classification_multilabel_valid = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/paper_categorization/valid",
        )

        pipeline_job: PipelineJob = train_automl_text_class_multilabel_in_pipeline(
            text_classification_multilabel_train, text_classification_multilabel_valid
        )
        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        job_dict = pydash.omit(actual_dict["properties"]["jobs"]["text_classification_multilabel_node"], fields_to_omit)
        assert job_dict == {
            "training_data": "${{parent.inputs.text_classification_multilabel_train}}",
            "validation_data": "${{parent.inputs.text_classification_multilabel_valid}}",
            "target_column_name": "terms",
            "tags": {},
            "type": "automl",
            "outputs": {},
            "limits": {"max_trials": 1, "max_concurrent_trials": 1},
            "task": "text_classification_multilabel",
            "primary_metric": "accuracy",
        }

    def test_automl_text_ner_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_automl_text_ner_in_pipeline", default_compute_target="gpu-cluster")
        def train_automl_text_ner_in_pipeline(
            text_ner_train,
            text_ner_valid,
        ):
            text_ner_node = text_ner(
                training_data=text_ner_train,
                validation_data=text_ner_valid,
                target_column_name="label",
                primary_metric="accuracy",
            )
            text_ner_node.set_limits(max_concurrent_trials=1)

        text_ner_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/conll2003/train",
        )
        text_ner_valid = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/conll2003/valid",
        )

        pipeline_job: PipelineJob = train_automl_text_ner_in_pipeline(text_ner_train, text_ner_valid)
        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        job_dict = pydash.omit(actual_dict["properties"]["jobs"]["text_ner_node"], fields_to_omit)
        assert job_dict == {
            "training_data": "${{parent.inputs.text_ner_train}}",
            "validation_data": "${{parent.inputs.text_ner_valid}}",
            "target_column_name": "label",
            "tags": {},
            "type": "automl",
            "outputs": {},
            "limits": {"max_trials": 1, "max_concurrent_trials": 1},
            "task": "text_ner",
            "primary_metric": "accuracy",
        }

    def test_automl_vision_multiclass_node_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_multiclass_with_automl_in_pipeline", default_compute_target="gpu-cluster")
        def train_multiclass_with_automl_in_pipeline(
            image_multiclass_train_data,
            image_multiclass_valid_data,
        ):
            image_multiclass_node = automl.image_classification(
                training_data=image_multiclass_train_data,
                validation_data=image_multiclass_valid_data,
                target_column_name="label",
                primary_metric="Accuracy",
            )
            image_multiclass_node.set_limits(
                timeout_minutes=60,
            )
            image_multiclass_node.extend_search_space(
                [
                    SearchSpace(
                        model_name=Choice(["vits16r224"]),
                        learning_rate=Uniform(0.001, 0.01),
                    ),
                    SearchSpace(
                        model_name=Choice(["seresnext"]),
                        learning_rate=Uniform(0.001, 0.01),
                    ),
                ]
            )
            image_multiclass_node.set_sweep(
                max_trials=1,
                max_concurrent_trials=1,
                sampling_algorithm="Random",
                early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
            )

        multiclass_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/image_classification/train",
        )
        multiclass_valid = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/image_classification/valid",
        )

        pipeline_job: PipelineJob = train_multiclass_with_automl_in_pipeline(multiclass_train, multiclass_valid)

        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        image_multiclass_dict = pydash.omit(actual_dict["properties"]["jobs"]["image_multiclass_node"], fields_to_omit)
        assert image_multiclass_dict == {
            "limits": {"timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "label",
            "task": "image_classification",
            "training_data": "${{parent.inputs.image_multiclass_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_multiclass_valid_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "limits": {"max_concurrent_trials": 1, "max_trials": 1},
                "early_termination": {
                    "evaluation_interval": 2,
                    "delay_evaluation": 6,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.001,0.01)",
                    "model_name": "choice('vits16r224')",
                },
                {
                    "learning_rate": "uniform(0.001,0.01)",
                    "model_name": "choice('seresnext')",
                },
            ],
        }

    def test_automl_vision_multilabel_node_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_multilabel_with_automl_in_pipeline", default_compute_target="gpu-cluster")
        def train_multilabel_with_automl_in_pipeline(
            image_multilabel_train_data,
            image_multilabel_valid_data,
        ):
            image_multilabel_node = automl.image_classification_multilabel(
                training_data=image_multilabel_train_data,
                validation_data=image_multilabel_valid_data,
                target_column_name="label",
                primary_metric="iou",
            )
            image_multilabel_node.set_limits(
                timeout_minutes=60,
            )
            image_multilabel_node.extend_search_space(
                [
                    SearchSpace(
                        model_name=Choice(["vitb16r224"]),
                        learning_rate=Uniform(0.001, 0.01),
                    ),
                    SearchSpace(
                        model_name=Choice(["seresnext"]),
                        learning_rate=Uniform(0.001, 0.01),
                    ),
                ]
            )
            image_multilabel_node.set_sweep(
                max_trials=1,
                max_concurrent_trials=1,
                sampling_algorithm="Random",
                early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
            )

        multilabel_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/image_classification_multilabel/train",
        )
        multilabel_valid = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/image_classification_multilabel/valid",
        )

        pipeline_job: PipelineJob = train_multilabel_with_automl_in_pipeline(multilabel_train, multilabel_valid)

        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        image_multilabel_dict = pydash.omit(actual_dict["properties"]["jobs"]["image_multilabel_node"], fields_to_omit)
        assert image_multilabel_dict == {
            "limits": {"timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "iou",
            "tags": {},
            "target_column_name": "label",
            "task": "image_classification_multilabel",
            "training_data": "${{parent.inputs.image_multilabel_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_multilabel_valid_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "limits": {"max_concurrent_trials": 1, "max_trials": 1},
                "early_termination": {
                    "evaluation_interval": 2,
                    "delay_evaluation": 6,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "search_space": [
                {
                    "model_name": "choice('vitb16r224')",
                    "learning_rate": "uniform(0.001,0.01)",
                },
                {
                    "model_name": "choice('seresnext')",
                    "learning_rate": "uniform(0.001,0.01)",
                },
            ],
        }

    def test_automl_vision_od_node_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_od_with_automl_in_pipeline", default_compute_target="gpu-cluster")
        def train_od_with_automl_in_pipeline(
            image_object_detection_train_data,
            image_object_detection_valid_data,
        ):
            image_object_detection_node = automl.image_object_detection(
                training_data=image_object_detection_train_data,
                validation_data=image_object_detection_valid_data,
                target_column_name="label",
                primary_metric="MeanAveragePrecision",
            )

            image_object_detection_node.extend_search_space(
                [
                    SearchSpace(
                        model_name=Choice(["yolov5"]),
                        learning_rate=Uniform(0.0001, 0.01),
                        model_size=Choice(["small", "medium"]),  # model-specific
                    ),
                    SearchSpace(
                        model_name=Choice(["fasterrcnn_resnet50_fpn"]),
                        learning_rate=Uniform(0.0001, 0.001),
                        optimizer=Choice(["sgd", "adam", "adamw"]),
                        min_size=Choice([600, 800]),  # model-specific
                    ),
                ]
            )
            image_object_detection_node.set_training_parameters(nms_iou_threshold=0.7)
            image_object_detection_node.set_limits(
                timeout_minutes=60,
            )
            image_object_detection_node.set_sweep(
                max_trials=1,
                max_concurrent_trials=1,
                sampling_algorithm="Random",
                early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
            )

        object_detection_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/image_object_detection/train",
        )
        object_detection_valid = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/image_object_detection/valid",
        )

        pipeline_job: PipelineJob = train_od_with_automl_in_pipeline(object_detection_train, object_detection_valid)

        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        image_object_detection_dict = pydash.omit(
            actual_dict["properties"]["jobs"]["image_object_detection_node"], fields_to_omit
        )
        assert image_object_detection_dict == {
            "limits": {"timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "mean_average_precision",
            "tags": {},
            "target_column_name": "label",
            "task": "image_object_detection",
            "training_data": "${{parent.inputs.image_object_detection_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_object_detection_valid_data}}",
            "training_parameters": {"nms_iou_threshold": 0.7},
            "sweep": {
                "sampling_algorithm": "random",
                "limits": {"max_concurrent_trials": 1, "max_trials": 1},
                "early_termination": {
                    "evaluation_interval": 2,
                    "delay_evaluation": 6,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.0001,0.01)",
                    "model_name": "choice('yolov5')",
                    "model_size": "choice('small','medium')",
                },
                {
                    "learning_rate": "uniform(0.0001,0.001)",
                    "min_size": "choice(600,800)",
                    "model_name": "choice('fasterrcnn_resnet50_fpn')",
                    "optimizer": "choice('sgd','adam','adamw')",
                },
            ],
        }

    def test_automl_vision_segmentation_node_in_pipeline(self, client: MLClient):
        @dsl.pipeline(name="train_with_automl_in_pipeline", default_compute_target="gpu-cluster")
        def train_segmentation_with_automl_in_pipeline(
            image_instance_segmentation_train_data,
            image_instance_segmentation_valid_data,
        ):

            image_instance_segmentation_node = automl.image_instance_segmentation(
                primary_metric="MeanAveragePrecision",
                target_column_name="label",
                training_data=image_instance_segmentation_train_data,
                validation_data=image_instance_segmentation_valid_data,
            )
            image_instance_segmentation_node.set_limits(
                timeout_minutes=60,
            )
            image_instance_segmentation_node.set_training_parameters(nms_iou_threshold=0.7)
            image_instance_segmentation_node.extend_search_space(
                [
                    SearchSpace(
                        model_name=Choice(["maskrcnn_resnet50_fpn"]),
                        learning_rate=Uniform(0.0001, 0.001),
                        optimizer=Choice(["sgd", "adam", "adamw"]),
                        min_size=Choice([600, 800]),
                    ),
                ]
            )

            image_instance_segmentation_node.set_sweep(
                max_trials=10,
                max_concurrent_trials=2,
                sampling_algorithm="Random",
                early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
            )

        instance_segmentation_train = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/image_instance_segmentation/train",
        )
        instance_segmentation_valid = Input(
            type=AssetTypes.MLTABLE,
            path=tests_root_dir / "test_configs/automl_job/test_datasets/image_instance_segmentation/valid",
        )

        pipeline_job: PipelineJob = train_segmentation_with_automl_in_pipeline(
            instance_segmentation_train, instance_segmentation_valid
        )

        from_rest_pipeline_job = client.jobs.create_or_update(pipeline_job)
        assert_final_job_status(from_rest_pipeline_job, client, PipelineJob, JobStatus.COMPLETED)

        actual_dict = from_rest_pipeline_job._to_rest_object().as_dict()
        fields_to_omit = ["name", "display_name", "experiment_name", "properties"]

        image_instance_segmentation_dict = pydash.omit(
            actual_dict["properties"]["jobs"]["image_instance_segmentation_node"], fields_to_omit
        )
        assert image_instance_segmentation_dict == {
            "limits": {"timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "mean_average_precision",
            "tags": {},
            "target_column_name": "label",
            "task": "image_instance_segmentation",
            "training_data": "${{parent.inputs.image_instance_segmentation_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_instance_segmentation_valid_data}}",
            "training_parameters": {"nms_iou_threshold": 0.7},
            "sweep": {
                "sampling_algorithm": "random",
                "limits": {"max_concurrent_trials": 2, "max_trials": 10},
                "early_termination": {
                    "evaluation_interval": 2,
                    "delay_evaluation": 6,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.0001,0.001)",
                    "model_name": "choice('maskrcnn_resnet50_fpn')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "min_size": "choice(600,800)",
                }
            ],
        }
