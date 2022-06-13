import yaml
import json
import pydash
import pytest
from marshmallow import ValidationError
from pytest_mock import MockFixture

from azure.ai.ml import MLClient
from azure.ai.ml.automl import classification
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import PipelineJob, Job
from azure.ai.ml._schema.automl import AutoMLRegressionSchema
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobBaseData as RestJob
from azure.ai.ml.entities._job.automl.tabular import RegressionJob, ClassificationJob, ForecastingJob
from azure.ai.ml.entities._job.automl.image import (
    ImageClassificationJob,
    ImageClassificationMultilabelJob,
    ImageObjectDetectionJob,
    ImageInstanceSegmentationJob,
)
from azure.ai.ml.entities._job.automl.nlp import (
    TextClassificationJob,
    TextClassificationMultilabelJob,
    TextNerJob,
)


def load_pipeline_entity_from_rest_json(job_dict) -> PipelineJob:
    """Rest pipeline json -> rest pipeline object -> pipeline entity"""
    rest_obj = RestJob.from_dict(json.loads(json.dumps(job_dict)))
    internal_pipeline = PipelineJob._from_rest_object(rest_obj)
    return internal_pipeline


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.unittest
class TestPipelineJobEntity:
    def test_automl_node_in_pipeline_regression(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_regression.yml"

        # overwrite some fields to data bindings to make sure it's supported
        params_override = [
            {"jobs.hello_automl_regression.primary_metric": "${{parent.inputs.primary_metric}}"},
            {"jobs.hello_automl_regression.limits.max_trials": "${{parent.inputs.max_trials}}"},
        ]
        job = Job.load(path=test_path, params_override=params_override)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, RegressionJob)

        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["hello_automl_regression"], omit_fields)

        expected_dict = {
            "featurization": {"mode": "off"},
            "limits": {"max_concurrent_trials": 1, "max_trials": "${{parent.inputs.max_trials}}"},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "${{parent.inputs.primary_metric}}",
            "tags": {},
            "target_column_name": "SalePrice",
            "task": "regression",
            "test_data": "${{parent.inputs.automl_test_data}}",
            "training": {"enable_stack_ensemble": False, "enable_vote_ensemble": False},
            "training_data": "${{parent.inputs.automl_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.automl_valid_data}}",
        }
        assert actual_dict == expected_dict

        # same regression node won't load as AutoMLRegressionSchema since there's data binding
        with pytest.raises(ValidationError) as e:
            AutoMLRegressionSchema(context={"base_path": "./"}).load(expected_dict)
        assert "Value ${{parent.inputs.primary_metric}} passed is not in set" in str(e.value)

    def test_automl_node_in_pipeline_classification(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_classification.yml"
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ClassificationJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["hello_automl_classification"], omit_fields)

        assert actual_dict == {
            "featurization": {"mode": "auto"},
            "limits": {"max_concurrent_trials": 1, "max_trials": 1},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "test_data": "${{parent.inputs.classification_test_data}}",
            "target_column_name": "y",
            "task": "classification",
            "training": {"enable_stack_ensemble": False, "enable_vote_ensemble": False},
            "training_data": "${{parent.inputs.classification_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.classification_validate_data}}",
        }

    def test_automl_node_in_pipeline_forecasting(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_forecasting.yml"
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ForecastingJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["hello_automl_forecasting"], omit_fields)

        assert actual_dict == {
            "limits": {"max_concurrent_trials": 1, "max_trials": 1},
            "featurization": {"mode": "auto"},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "normalized_root_mean_squared_error",
            "tags": {},
            "target_column_name": "BeerProduction",
            "task": "forecasting",
            "training": {"enable_stack_ensemble": False, "enable_vote_ensemble": False},
            "training_data": "${{parent.inputs.forecasting_train_data}}",
            "type": "automl",
            "forecasting": {"forecast_horizon": 12, "time_column_name": "DATE", "frequency": "MS"},
            "n_cross_validations": 2,
        }

    @pytest.mark.parametrize(
        "rest_job_file, node_name",
        [
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_regression.json",
                "hello_automl_regression",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/rest_pipeline_with_automl_output_binding.json",
                "classification_node",
            ),
            (
                "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/rest_pipeline_with_automl_output.json",
                "hello_automl_regression",
            ),
        ],
    )
    def test_automl_job_in_pipeline_deserialize(self, rest_job_file, node_name):
        with open(rest_job_file, "r") as f:
            job_dict = yaml.safe_load(f)
        pipeline = load_pipeline_entity_from_rest_json(job_dict)
        assert isinstance(pipeline, PipelineJob)
        expected_automl_job = job_dict["properties"]["jobs"][node_name]
        actual_automl_job = pipeline._to_rest_object().as_dict()["properties"]["jobs"][node_name]
        assert actual_automl_job == expected_automl_job

    def test_automl_node_in_pipeline_with_binding(self):
        # classification node
        automl_classif_job = classification(
            training_data=PipelineInput(name="main_data_input", owner="pipeline", meta=None),
            # validation_data_size=PipelineInput(name="validation_data_size", owner="pipeline", meta=None),
            # test_data = test_data_input # Optional, since testing is explicit below with TEST COMPONENT
            target_column_name=PipelineInput(name="target_column_name_input", owner="pipeline", meta=None),
            # primary_metric=PipelineInput(name="primary_metric", owner="pipeline", meta=None),
            enable_model_explainability=True,
        )
        pipeline_job = PipelineJob(jobs={"automl_classif_job": automl_classif_job})
        rest_pipeline_job_dict = pipeline_job._to_rest_object().as_dict()
        rest_automl_node_dict = pydash.omit(
            rest_pipeline_job_dict["properties"]["jobs"]["automl_classif_job"],
            ["name", "display_name", "experiment_name", "properties"],
        )
        assert rest_automl_node_dict == {
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "${{parent.inputs.target_column_name_input}}",
            "task": "classification",
            "training": {"enable_model_explainability": True},
            "training_data": "${{parent.inputs.main_data_input}}",
            "type": "automl",
        }

    def test_pipeline_job_automl_regression_output(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/automl_regression_with_command_node.yml"
        pipeline: PipelineJob = Job.load(path=test_path)

        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(pipeline)

        pipeline_dict = pipeline._to_rest_object().as_dict()

        fields_to_omit = ["name", "display_name", "training_data", "validation_data", "experiment_name", "properties"]

        automl_actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["regression_node"], fields_to_omit)

        assert automl_actual_dict == {
            "featurization": {"mode": "off"},
            "limits": {"max_concurrent_trials": 1, "max_trials": 1},
            "log_verbosity": "info",
            "outputs": {"best_model": {"job_output_type": "MLFlowModel", "mode": "ReadWriteMount"}},
            "primary_metric": "r2_score",
            "tags": {},
            "target_column_name": "SalePrice",
            "task": "regression",
            "test_data": "${{parent.inputs.automl_test_data}}",
            "training": {"enable_stack_ensemble": False, "enable_vote_ensemble": False},
            "type": "automl",
        }

        command_actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["command_node"], fields_to_omit)

        assert command_actual_dict == {
            "componentId": "xxx",
            "computeId": "xxx",
            "distribution": None,
            "environment_variables": {},
            "inputs": {
                "mltable_output": {
                    "job_input_type": "Literal",
                    "value": "${{parent.jobs.regression_node.outputs.best_model}}",
                }
            },
            "limits": None,
            "outputs": {},
            "resources": None,
            "tags": {},
        }

    def test_automl_node_in_pipeline_text_classification(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_classification.yml"
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, TextClassificationJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["automl_text_classification"], omit_fields)

        assert actual_dict == {
            "featurization": {"dataset_language": "eng"},
            "limits": {"max_trials": 1, "timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "y",
            "task": "text_classification",
            "training_data": "${{parent.inputs.text_classification_training_data}}",
            "validation_data": "${{parent.inputs.text_classification_validation_data}}",
            "type": "automl",
        }

    def test_automl_node_in_pipeline_text_classification_multilabel(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = (
            "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_classification_multilabel.yml"
        )
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, TextClassificationMultilabelJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["automl_text_classification_multilabel"], omit_fields
        )

        assert actual_dict == {
            "limits": {"max_trials": 1, "timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "terms",
            "task": "text_classification_multilabel",
            "training_data": "${{parent.inputs.text_classification_multilabel_training_data}}",
            "validation_data": "${{parent.inputs.text_classification_multilabel_validation_data}}",
            "type": "automl",
        }

    def test_automl_node_in_pipeline_text_ner(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_ner.yml"
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, TextNerJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["automl_text_ner"], omit_fields)

        assert actual_dict == {
            "limits": {"max_trials": 1, "timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "label",
            "task": "text_ner",
            "training_data": "${{parent.inputs.text_ner_training_data}}",
            "validation_data": "${{parent.inputs.text_ner_validation_data}}",
            "type": "automl",
        }

    def test_automl_node_in_pipeline_image_multiclass_classification(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multiclass_classification.yml"
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ImageClassificationJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["hello_automl_image_multiclass_classification"], omit_fields
        )

        assert actual_dict == {
            "limits": {"timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "target_column_name": "label",
            "task": "image_classification",
            "training_data": "${{parent.inputs.image_multiclass_classification_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_multiclass_classification_validate_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "limits": {"max_concurrent_trials": 4, "max_trials": 20},
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "image_model": {
                "checkpoint_frequency": 1,
                "early_stopping": True,
                "early_stopping_delay": 2,
                "early_stopping_patience": 2,
                "evaluation_frequency": 1,
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.005,0.05)",
                    "model_name": "choice('vitb16r224')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "warmup_cosine_lr_warmup_epochs": "choice(0,3)",
                }
            ],
        }

    def test_automl_node_in_pipeline_image_multilabel_classification(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multilabel_classification.yml"
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ImageClassificationMultilabelJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["hello_automl_image_multilabel_classification"], omit_fields
        )

        assert actual_dict == {
            "limits": {"timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "iou",
            "tags": {},
            "target_column_name": "label",
            "task": "image_classification_multilabel",
            "training_data": "${{parent.inputs.image_multilabel_classification_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_multilabel_classification_validate_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "limits": {"max_concurrent_trials": 4, "max_trials": 20},
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "image_model": {
                "checkpoint_frequency": 1,
                "early_stopping": True,
                "early_stopping_delay": 2,
                "early_stopping_patience": 2,
                "evaluation_frequency": 1,
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.005,0.05)",
                    "model_name": "choice('vitb16r224')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "warmup_cosine_lr_warmup_epochs": "choice(0,3)",
                }
            ],
        }

    def test_automl_node_in_pipeline_image_object_detection(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_object_detection.yml"
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ImageObjectDetectionJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["hello_automl_image_object_detection"], omit_fields
        )

        assert actual_dict == {
            "limits": {"timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "mean_average_precision",
            "tags": {},
            "target_column_name": "label",
            "task": "image_object_detection",
            "training_data": "${{parent.inputs.image_object_detection_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_object_detection_validate_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "limits": {"max_concurrent_trials": 4, "max_trials": 20},
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "image_model": {
                "checkpoint_frequency": 1,
                "early_stopping": True,
                "early_stopping_delay": 2,
                "early_stopping_patience": 2,
                "evaluation_frequency": 1,
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.005,0.05)",
                    "model_name": "choice('fasterrcnn_resnet50_fpn')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "warmup_cosine_lr_warmup_epochs": "choice(0,3)",
                    "min_size": "choice(600,800)",
                }
            ],
        }

    def test_automl_node_in_pipeline_image_instance_segmentation(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = (
            "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_instance_segmentation.yml"
        )
        job = Job.load(path=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ImageInstanceSegmentationJob)
        mocker.patch("azure.ai.ml.operations.OperationOrchestrator.get_asset_arm_id", return_value="xxx")
        mocker.patch("azure.ai.ml.operations.job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["hello_automl_image_instance_segmentation"], omit_fields
        )

        assert actual_dict == {
            "limits": {"timeout_minutes": 60},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "mean_average_precision",
            "tags": {},
            "target_column_name": "label",
            "task": "image_instance_segmentation",
            "training_data": "${{parent.inputs.image_instance_segmentation_train_data}}",
            "type": "automl",
            "validation_data": "${{parent.inputs.image_instance_segmentation_validate_data}}",
            "sweep": {
                "sampling_algorithm": "random",
                "limits": {"max_concurrent_trials": 4, "max_trials": 20},
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "image_model": {
                "checkpoint_frequency": 1,
                "early_stopping": True,
                "early_stopping_delay": 2,
                "early_stopping_patience": 2,
                "evaluation_frequency": 1,
            },
            "search_space": [
                {
                    "learning_rate": "uniform(0.005,0.05)",
                    "model_name": "choice('maskrcnn_resnet50_fpn')",
                    "optimizer": "choice('sgd','adam','adamw')",
                    "warmup_cosine_lr_warmup_epochs": "choice(0,3)",
                    "min_size": "choice(600,800)",
                }
            ],
        }

    def test_infer_pipeline_output_type_as_node_type(
        self,
    ) -> None:
        pipeline_job = Job.load(
            path="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_with_parallel_job_tabular_input_e2e.yml",
        )
        assert (
            pipeline_job.jobs["hello_world_inline_parallel_tabular_job_1"].outputs["job_output_file"].type
            == AssetTypes.URI_FILE
        )
