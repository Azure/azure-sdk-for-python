import json
from pathlib import Path

import pydash
import pytest
import yaml
from marshmallow import ValidationError
from pytest_mock import MockFixture

from dsl._util import get_predecessors
from test_utilities.utils import omit_with_wildcard, verify_entity_load_and_dump

from azure.ai.ml import MLClient, dsl, load_component, load_job
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase as RestJob
from azure.ai.ml._schema.automl import AutoMLRegressionSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file, load_yaml
from azure.ai.ml.automl import classification
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.dsl._group_decorator import group
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities._builders import Spark, DataTransfer
from azure.ai.ml.entities._job.automl.image import (
    ImageClassificationJob,
    ImageClassificationMultilabelJob,
    ImageInstanceSegmentationJob,
    ImageObjectDetectionJob,
)
from azure.ai.ml.entities._job.automl.nlp import TextClassificationJob, TextClassificationMultilabelJob, TextNerJob
from azure.ai.ml.entities._job.automl.tabular import ClassificationJob, ForecastingJob, RegressionJob
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, _GroupAttrDict
from azure.ai.ml.exceptions import ValidationException

from .._util import _PIPELINE_JOB_TIMEOUT_SECOND


def load_pipeline_entity_from_rest_json(job_dict) -> PipelineJob:
    """Rest pipeline json -> rest pipeline object -> pipeline entity"""
    rest_obj = RestJob.from_dict(json.loads(json.dumps(job_dict)))
    internal_pipeline = PipelineJob._from_rest_object(rest_obj)
    return internal_pipeline


@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
@pytest.mark.timeout(_PIPELINE_JOB_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPipelineJobEntity:
    def test_automl_node_in_pipeline_regression(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_regression.yml"

        # overwrite some fields to data bindings to make sure it's supported
        params_override = [
            {"jobs.hello_automl_regression.primary_metric": "${{parent.inputs.primary_metric}}"},
            {"jobs.hello_automl_regression.limits.max_trials": "${{parent.inputs.max_trials}}"},
        ]

        def simple_job_validation(job):
            assert isinstance(job, PipelineJob)
            node = next(iter(job.jobs.values()))
            assert isinstance(node, RegressionJob)

        job = verify_entity_load_and_dump(load_job, simple_job_validation, test_path, params_override=params_override)[
            0
        ]

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
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
        assert "Value '${{parent.inputs.primary_metric}}' passed is not in set" in str(e.value)

    def test_automl_node_in_pipeline_classification(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_classification.yml"
        job = load_job(source=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ClassificationJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
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
        job = load_job(source=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ForecastingJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
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

    @pytest.mark.parametrize(
        "invalid_pipeline_job_without_jobs",
        [
            "./tests/test_configs/pipeline_jobs/invalid_pipeline_job_without_jobs.json",
        ],
    )
    def test_invalid_pipeline_jobs_descerialize(self, invalid_pipeline_job_without_jobs):
        with open(invalid_pipeline_job_without_jobs, "r") as f:
            job_dict = yaml.safe_load(f)
        pipeline = load_pipeline_entity_from_rest_json(job_dict)
        assert pipeline.jobs == {}

    def test_command_job_with_invalid_mode_type_in_pipeline_deserialize(self):
        # this json file is to test whether the client can handle the dirty data of node type/mode of the originally
        # submitted job due to API switching
        rest_job_file = "./tests/test_configs/pipeline_jobs/invalid/with_invalid_job_input_type_mode.json"
        with open(rest_job_file, "r") as f:
            job_dict = yaml.safe_load(f)
        rest_obj = RestJob.from_dict(json.loads(json.dumps(job_dict)))
        pipeline = PipelineJob._from_rest_object(rest_obj)
        pipeline_dict = pipeline._to_dict()
        assert pydash.omit(pipeline_dict["jobs"], *["properties", "hello_python_world_job.properties"]) == {
            "hello_python_world_job": {
                "inputs": {
                    "sample_input_data": {
                        "mode": "ro_mount",
                        "type": "uri_folder",
                        "path": "azureml://datastores/workspaceblobstore/paths/LocalUpload/22fd2a62-9759-4843-ab92-5bd79c35f6f0/data/",
                    },
                    "sample_input_string": {
                        "mode": "ro_mount",
                        "path": "${{parent.inputs.pipeline_sample_input_string}}",
                    },
                },
                "outputs": {"sample_output_data": "${{parent.outputs.pipeline_sample_output_data}}"},
                "component": "azureml:/subscriptions/96aede12-2f73-41cb-b983-6d11a904839b/resourceGroups/chenyin-test-eastus/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/components/azureml_anonymous/versions/9904ff48-9cb2-4733-ad1c-eb1eb9940a19",
                "type": "command",
                "compute": "azureml:cpu-cluster",
            }
        }
        assert pipeline_dict["inputs"] == {"pipeline_sample_input_string": "Hello_Pipeline_World"}
        assert pipeline_dict["outputs"] == {"pipeline_sample_output_data": {"mode": "upload", "type": "uri_folder"}}

        pipeline_rest_dict = pipeline._to_rest_object().as_dict()
        pipeline_rest_dict["properties"]["inputs"] == {
            "pipeline_sample_input_string": {"job_input_type": "literal", "value": "Hello_Pipeline_World"}
        }
        pipeline_rest_dict["properties"]["outputs"] == {
            "pipeline_sample_output_data": {"mode": "Upload", "job_output_type": "uri_folder"}
        }
        pipeline_rest_dict["properties"]["jobs"] == {
            "hello_python_world_job": {
                "name": "hello_python_world_job",
                "type": "command",
                "computeId": "cpu-cluster",
                "inputs": {
                    "sample_input_string": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.pipeline_sample_input_string}}",
                        "mode": "ReadOnlyMount",
                    },
                    "sample_input_data": {
                        "uri": "azureml://datastores/workspaceblobstore/paths/LocalUpload/553d1a28-7933-4017-8321-96c2a9f1fc44/data/",
                        "job_input_type": "uri_folder",
                    },
                },
                "outputs": {
                    "sample_output_data": {
                        "value": "${{parent.outputs.pipeline_sample_output_data}}",
                        "type": "literal",
                    }
                },
                "_source": "REMOTE.WORKSPACE.COMPONENT",
                "componentId": "/subscriptions/96aede12-2f73-41cb-b983-6d11a904839b/resourceGroups/sdk/providers/Microsoft.MachineLearningServices/workspaces/sdk-master/components/azureml_anonymous/versions/6ffc3ff9-8801-4cc4-9285-9f8052b946fe",
            }
        }

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
        pipeline: PipelineJob = load_job(source=test_path)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(pipeline)

        pipeline_dict = pipeline._to_rest_object().as_dict()

        fields_to_omit = ["name", "display_name", "training_data", "validation_data", "experiment_name", "properties"]

        automl_actual_dict = pydash.omit(pipeline_dict["properties"]["jobs"]["regression_node"], fields_to_omit)

        assert automl_actual_dict == {
            "featurization": {"mode": "off"},
            "limits": {"max_concurrent_trials": 1, "max_trials": 1},
            "log_verbosity": "info",
            "outputs": {"best_model": {"job_output_type": "mlflow_model"}},
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
            "_source": "YAML.JOB",
            "componentId": "xxx",
            "computeId": "xxx",
            "inputs": {
                "mltable_output": {
                    "job_input_type": "literal",
                    "value": "${{parent.jobs.regression_node.outputs.best_model}}",
                }
            },
            "type": "command",
        }

    def test_automl_node_in_pipeline_text_classification(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_text_classification.yml"
        job = load_job(source=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, TextClassificationJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["automl_text_classification"], omit_fields)

        assert actual_dict == {
            "featurization": {"dataset_language": "eng"},
            "limits": {"max_trials": 1, "timeout_minutes": 60, "max_nodes": 1},
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
        job = load_job(source=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, TextClassificationMultilabelJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["automl_text_classification_multilabel"], omit_fields
        )

        assert actual_dict == {
            "limits": {"max_trials": 1, "timeout_minutes": 60, "max_nodes": 1},
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
        job = load_job(source=test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, TextNerJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["automl_text_ner"], omit_fields)

        assert actual_dict == {
            "limits": {"max_trials": 1, "timeout_minutes": 60, "max_nodes": 1},
            "log_verbosity": "info",
            "outputs": {},
            "primary_metric": "accuracy",
            "tags": {},
            "task": "text_ner",
            "training_data": "${{parent.inputs.text_ner_training_data}}",
            "validation_data": "${{parent.inputs.text_ner_validation_data}}",
            "type": "automl",
        }

    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_automl_node_in_pipeline_image_multiclass_classification(
        self,
        mock_machinelearning_client: MLClient,
        mocker: MockFixture,
        run_type: str,
        tmp_path: Path,
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multiclass_classification.yml"

        test_config = load_yaml(test_path)
        if (run_type == "single") or (run_type == "automode"):
            # Remove search_space and sweep sections from the config
            del test_config["jobs"]["hello_automl_image_multiclass_classification"]["search_space"]
            del test_config["jobs"]["hello_automl_image_multiclass_classification"]["sweep"]

        test_yaml_file = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_file, test_config)
        job = load_job(source=test_yaml_file)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ImageClassificationJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["hello_automl_image_multiclass_classification"], omit_fields
        )

        expected_dict = {
            "limits": {"timeout_minutes": 60, "max_concurrent_trials": 4, "max_trials": 20},
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
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "training_parameters": {
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
        if (run_type == "single") or (run_type == "automode"):
            del expected_dict["search_space"]
            del expected_dict["sweep"]
        assert actual_dict == expected_dict

    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_automl_node_in_pipeline_image_multilabel_classification(
        self,
        mock_machinelearning_client: MLClient,
        mocker: MockFixture,
        run_type: str,
        tmp_path: Path,
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_multilabel_classification.yml"

        test_config = load_yaml(test_path)
        if (run_type == "single") or (run_type == "automode"):
            # Remove search_space and sweep sections from the config
            del test_config["jobs"]["hello_automl_image_multilabel_classification"]["search_space"]
            del test_config["jobs"]["hello_automl_image_multilabel_classification"]["sweep"]

        test_yaml_file = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_file, test_config)
        job = load_job(source=test_yaml_file)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ImageClassificationMultilabelJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["hello_automl_image_multilabel_classification"], omit_fields
        )

        expected_dict = {
            "limits": {"timeout_minutes": 60, "max_concurrent_trials": 4, "max_trials": 20},
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
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "training_parameters": {
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
        if (run_type == "single") or (run_type == "automode"):
            del expected_dict["search_space"]
            del expected_dict["sweep"]
        assert actual_dict == expected_dict

    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_automl_node_in_pipeline_image_object_detection(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture, run_type: str, tmp_path: Path
    ):
        test_path = "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_object_detection.yml"

        test_config = load_yaml(test_path)
        if (run_type == "single") or (run_type == "automode"):
            # Remove search_space and sweep sections from the config
            del test_config["jobs"]["hello_automl_image_object_detection"]["search_space"]
            del test_config["jobs"]["hello_automl_image_object_detection"]["sweep"]

        test_yaml_file = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_file, test_config)
        job = load_job(source=test_yaml_file)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ImageObjectDetectionJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["hello_automl_image_object_detection"], omit_fields
        )

        expected_dict = {
            "limits": {"timeout_minutes": 60, "max_concurrent_trials": 4, "max_trials": 20},
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
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "training_parameters": {
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
        if (run_type == "single") or (run_type == "automode"):
            del expected_dict["search_space"]
            del expected_dict["sweep"]
        assert actual_dict == expected_dict

    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_automl_node_in_pipeline_image_instance_segmentation(
        self,
        mock_machinelearning_client: MLClient,
        mocker: MockFixture,
        run_type: str,
        tmp_path: Path,
    ):
        test_path = (
            "./tests/test_configs/pipeline_jobs/jobs_with_automl_nodes/onejob_automl_image_instance_segmentation.yml"
        )

        test_config = load_yaml(test_path)
        if (run_type == "single") or (run_type == "automode"):
            # Remove search_space and sweep sections from the config
            del test_config["jobs"]["hello_automl_image_instance_segmentation"]["search_space"]
            del test_config["jobs"]["hello_automl_image_instance_segmentation"]["sweep"]

        test_yaml_file = tmp_path / "job.yml"
        dump_yaml_to_file(test_yaml_file, test_config)
        job = load_job(source=test_yaml_file)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, ImageInstanceSegmentationJob)
        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id",
            return_value="xxx",
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["name", "display_name", "experiment_name", "properties"]
        actual_dict = pydash.omit(
            rest_job_dict["properties"]["jobs"]["hello_automl_image_instance_segmentation"], omit_fields
        )

        expected_dict = {
            "limits": {"timeout_minutes": 60, "max_concurrent_trials": 4, "max_trials": 20},
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
                "early_termination": {
                    "evaluation_interval": 10,
                    "delay_evaluation": 0,
                    "type": "bandit",
                    "slack_factor": 0.2,
                    "slack_amount": 0.0,
                },
            },
            "training_parameters": {
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
        if (run_type == "single") or (run_type == "automode"):
            del expected_dict["search_space"]
            del expected_dict["sweep"]
        assert actual_dict == expected_dict

    def test_spark_node_in_pipeline(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/pipeline.yml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, Spark)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["properties"]  # "name", "display_name", "experiment_name", "properties"
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["add_greeting_column"], omit_fields)

        expected_dict = {
            "_source": "YAML.COMPONENT",
            "args": "--file_input ${{inputs.file_input}}",
            "componentId": "",
            "computeId": "",
            "conf": {
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.instances": 1,
                "spark.executor.memory": "1g",
            },
            "entry": {"file": "add_greeting_column.py", "spark_job_entry_type": "SparkJobPythonEntry"},
            "files": ["my_files.txt"],
            "identity": {"identity_type": "Managed"},
            "inputs": {"file_input": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"}},
            "name": "add_greeting_column",
            "py_files": ["utils.zip"],
            "resources": {"instance_type": "standard_e4s_v3", "runtime_version": "3.2.0"},
            "type": "spark",
        }
        assert actual_dict == expected_dict

        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["count_by_row"], omit_fields)

        expected_dict = {
            "_source": "YAML.COMPONENT",
            "args": "--file_input ${{inputs.file_input}} --output ${{outputs.output}}",
            "componentId": "",
            "computeId": "",
            "conf": {
                "spark.driver.cores": 2,
                "spark.driver.memory": "1g",
                "spark.executor.cores": 1,
                "spark.executor.instances": 1,
                "spark.executor.memory": "1g",
            },
            "entry": {"file": "count_by_row.py", "spark_job_entry_type": "SparkJobPythonEntry"},
            "files": ["my_files.txt"],
            "identity": {"identity_type": "Managed"},
            "inputs": {"file_input": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"}},
            "jars": ["scalaproj.jar"],
            "name": "count_by_row",
            "outputs": {"output": {"type": "literal", "value": "${{parent.outputs.output}}"}},
            "resources": {"instance_type": "standard_e4s_v3", "runtime_version": "3.2.0"},
            "type": "spark",
        }
        assert actual_dict == expected_dict

    def test_data_transfer_copy_node_in_pipeline(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/copy_files.yaml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, DataTransfer)

        result = job._validate()
        assert result.passed is True

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["copy_files"], *omit_fields)

        expected_dict = {
            "_source": "YAML.COMPONENT",
            "componentId": "",
            "computeId": "",
            "data_copy_mode": "merge_with_overwrite",
            "inputs": {"folder1": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"}},
            "name": "copy_files",
            "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
            "task": "copy_data",
            "type": "data_transfer",
        }
        assert actual_dict == expected_dict

    def test_data_transfer_merge_node_in_pipeline(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/merge_files.yaml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, DataTransfer)

        result = job._validate()
        assert result.passed is True

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["merge_files"], *omit_fields)

        expected_dict = {
            "_source": "YAML.COMPONENT",
            "componentId": "",
            "computeId": "",
            "data_copy_mode": "merge_with_overwrite",
            "inputs": {
                "folder1": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"},
                "folder2": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder_dup}}"},
            },
            "name": "merge_files",
            "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
            "task": "copy_data",
            "type": "data_transfer",
        }
        assert actual_dict == expected_dict

    def test_inline_data_transfer_merge_node_in_pipeline(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/merge_files_job.yaml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, DataTransfer)

        result = job._validate()
        assert result.passed is True

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = ["properties"]
        actual_dict = pydash.omit(rest_job_dict["properties"]["jobs"]["merge_files_job"], *omit_fields)

        expected_dict = {
            "data_copy_mode": "merge_with_overwrite",
            "_source": "YAML.JOB",
            "componentId": "",
            "computeId": "",
            "inputs": {
                "folder1": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"},
                "folder2": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder_dup}}"},
            },
            "name": "merge_files_job",
            "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
            "type": "data_transfer",
            "task": "copy_data",
        }
        assert actual_dict == expected_dict

    def test_inline_data_transfer_import_database_node_in_pipeline(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/import_database_to_blob.yaml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, DataTransfer)

        result = job._validate()
        assert result.passed is True

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        omit_fields = [
            "properties.jobs.snowflake_blob.componentId",
            "properties.jobs.snowflake_blob_node_input.componentId",
        ]
        rest_job_dict = pydash.omit(job._to_rest_object().as_dict(), *omit_fields)

        assert rest_job_dict == {
            "properties": {
                "compute_id": "",
                "description": "pipeline with data transfer components",
                "inputs": {
                    "query_source_snowflake": {
                        "job_input_type": "literal",
                        "value": "select * from TPCH_SF1000.PARTSUPP limit 10",
                    }
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "snowflake_blob": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "name": "snowflake_blob",
                        "outputs": {
                            "sink": {
                                "job_output_type": "mltable",
                                "uri": "azureml://datastores/workspaceblobstore_sas/paths/importjob/${{name}}/output_dir/snowflake/",
                            }
                        },
                        "source": {
                            "connection": "azureml:my_snowflake_connection",
                            "query": "${{parent.inputs.query_source_snowflake}}",
                            "type": "database",
                        },
                        "task": "import_data",
                        "type": "data_transfer",
                    },
                    "snowflake_blob_node_input": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "name": "snowflake_blob_node_input",
                        "outputs": {
                            "sink": {
                                "job_output_type": "mltable",
                                "uri": "azureml://datastores/workspaceblobstore_sas/paths/importjob/${{name}}/output_dir/snowflake/",
                            }
                        },
                        "source": {
                            "connection": "azureml:my_snowflake_connection",
                            "query": "select * from TPCH_SF1000.PARTSUPP limit 10",
                            "type": "database",
                        },
                        "task": "import_data",
                        "type": "data_transfer",
                    },
                },
                "outputs": {},
                "properties": {},
                "settings": {"_source": "YAML.JOB", "default_compute": "", "default_datastore": ""},
                "tags": {},
            }
        }

    def test_inline_data_transfer_import_stored_database_node_in_pipeline(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/import_stored_database_to_blob.yaml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, DataTransfer)

        result = job._validate()
        assert result.passed is True

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        omit_fields = [
            "properties.jobs.snowflake_blob.componentId",
        ]
        rest_job_dict = pydash.omit(job._to_rest_object().as_dict(), *omit_fields)

        assert rest_job_dict == {
            "properties": {
                "compute_id": "",
                "description": "pipeline with data transfer components",
                "inputs": {},
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "snowflake_blob": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "name": "snowflake_blob",
                        "outputs": {"sink": {"job_output_type": "mltable"}},
                        "source": {
                            "connection": "azureml:my_sql_connection",
                            "stored_procedure": "SelectEmployeeByJobAndDepartment",
                            "stored_procedure_params": [
                                {"name": "job", "type": "String", "value": "Engineer"},
                                {"name": "department", "type": "String", "value": "Engineering"},
                            ],
                            "type": "database",
                        },
                        "task": "import_data",
                        "type": "data_transfer",
                    }
                },
                "outputs": {},
                "properties": {},
                "settings": {"_source": "YAML.JOB", "default_compute": "", "default_datastore": ""},
                "tags": {},
            }
        }

    def test_inline_data_transfer_import_file_system_node_in_pipeline(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/import_file_system_to_blob.yaml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, DataTransfer)

        result = job._validate()
        assert result.passed is True

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        omit_fields = [
            "properties.jobs.s3_blob.componentId",
            "properties.jobs.s3_blob_input.componentId",
        ]
        rest_job_dict = pydash.omit(job._to_rest_object().as_dict(), *omit_fields)

        assert rest_job_dict == {
            "properties": {
                "compute_id": "",
                "description": "pipeline with data transfer components",
                "inputs": {
                    "connection_target": {"job_input_type": "literal", "value": "azureml:my-s3-connection"},
                    "path_source_s3": {"job_input_type": "literal", "value": "test1/*"},
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "s3_blob": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "name": "s3_blob",
                        "outputs": {
                            "sink": {
                                "job_output_type": "uri_folder",
                                "uri": "azureml://datastores/workspaceblobstore/paths/importjob/${{name}}/output_dir/s3//",
                            }
                        },
                        "source": {
                            "connection": "${{parent.inputs.connection_target}}",
                            "path": "${{parent.inputs.path_source_s3}}",
                            "type": "file_system",
                        },
                        "task": "import_data",
                        "type": "data_transfer",
                    },
                    "s3_blob_input": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "name": "s3_blob_input",
                        "outputs": {
                            "sink": {
                                "job_output_type": "uri_folder",
                                "uri": "azureml://datastores/workspaceblobstore/paths/importjob/${{name}}/output_dir/s3//",
                            }
                        },
                        "source": {"connection": "azureml:my-s3-connection", "path": "test1/*", "type": "file_system"},
                        "task": "import_data",
                        "type": "data_transfer",
                    },
                },
                "outputs": {},
                "properties": {},
                "settings": {"_source": "YAML.JOB", "default_compute": "", "default_datastore": ""},
                "tags": {},
            }
        }

    def test_inline_data_transfer_export_database_node_in_pipeline(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/export_database_to_blob.yaml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, DataTransfer)

        result = job._validate()
        assert result.passed is True

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        omit_fields = [
            "properties.jobs.blob_azuresql.componentId",
            "properties.jobs.blob_azuresql_node_input.componentId",
        ]
        rest_job_dict = pydash.omit(job._to_rest_object().as_dict(), *omit_fields)

        assert rest_job_dict == {
            "properties": {
                "compute_id": "",
                "description": "pipeline with data transfer components",
                "inputs": {
                    "connection_target_azuresql": {
                        "job_input_type": "literal",
                        "value": "azureml:my_export_azuresqldb_connection",
                    },
                    "cosmos_folder": {"job_input_type": "uri_file", "uri": "yyy"},
                    "table_name": {"job_input_type": "literal", "value": "dbo.Persons"},
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "blob_azuresql": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "inputs": {
                            "source": {"job_input_type": "literal", "value": "${{parent.inputs.cosmos_folder}}"}
                        },
                        "name": "blob_azuresql",
                        "sink": {
                            "connection": "${{parent.inputs.connection_target_azuresql}}",
                            "table_name": "${{parent.inputs.table_name}}",
                            "type": "database",
                        },
                        "task": "export_data",
                        "type": "data_transfer",
                    },
                    "blob_azuresql_node_input": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "inputs": {"source": {"job_input_type": "uri_file", "uri": "yyy"}},
                        "name": "blob_azuresql_node_input",
                        "sink": {
                            "connection": "azureml:my_export_azuresqldb_connection",
                            "table_name": "dbo.Persons",
                            "type": "database",
                        },
                        "task": "export_data",
                        "type": "data_transfer",
                    },
                },
                "outputs": {},
                "properties": {},
                "settings": {"_source": "YAML.JOB", "default_compute": "", "default_datastore": ""},
                "tags": {},
            }
        }

    def test_data_transfer_multi_node_in_pipeline(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/pipeline_jobs/data_transfer/pipeline_with_mutil_task.yaml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, DataTransfer)

        result = job._validate()
        assert result.passed is True

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        rest_job_dict = job._to_rest_object().as_dict()
        omit_fields = [
            "properties.jobs.*.componentId",
        ]
        actual_dict = omit_with_wildcard(rest_job_dict, *omit_fields)

        assert actual_dict == {
            "properties": {
                "compute_id": "",
                "description": "pipeline with data transfer components",
                "inputs": {
                    "path_source_s3": {"job_input_type": "literal", "value": "test1/*"},
                    "query_source_sql": {
                        "job_input_type": "literal",
                        "value": "select top(10) Name " "from " "SalesLT.ProductCategory",
                    },
                },
                "is_archived": False,
                "job_type": "Pipeline",
                "jobs": {
                    "blob_azuresql": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "inputs": {"source": {"job_input_type": "uri_file", "uri": "yyy"}},
                        "name": "blob_azuresql",
                        "sink": {
                            "connection": "azureml:my_export_azuresqldb_connection",
                            "table_name": "dbo.Persons",
                            "type": "database",
                        },
                        "task": "export_data",
                        "type": "data_transfer",
                    },
                    "merge_files": {
                        "_source": "YAML.COMPONENT",
                        "computeId": "",
                        "data_copy_mode": "merge_with_overwrite",
                        "inputs": {
                            "folder1": {"job_input_type": "literal", "value": "${{parent.jobs.s3_blob.outputs.sink}}"},
                            "folder2": {
                                "job_input_type": "literal",
                                "value": "${{parent.jobs.snowflake_blob.outputs.sink}}",
                            },
                        },
                        "name": "merge_files",
                        "outputs": {"output_folder": {"type": "literal", "value": "${{parent.outputs.merged_blob}}"}},
                        "task": "copy_data",
                        "type": "data_transfer",
                    },
                    "s3_blob": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "name": "s3_blob",
                        "outputs": {"sink": {"job_output_type": "uri_folder"}},
                        "source": {
                            "connection": "azureml:my-s3-connection",
                            "path": "${{parent.inputs.path_source_s3}}",
                            "type": "file_system",
                        },
                        "task": "import_data",
                        "type": "data_transfer",
                    },
                    "snowflake_blob": {
                        "_source": "BUILTIN",
                        "computeId": "",
                        "name": "snowflake_blob",
                        "outputs": {"sink": {"job_output_type": "mltable"}},
                        "source": {
                            "connection": "azureml:my_azuresqldb_connection",
                            "query": "${{parent.inputs.query_source_sql}}",
                            "type": "database",
                        },
                        "task": "import_data",
                        "type": "data_transfer",
                    },
                },
                "outputs": {"merged_blob": {"job_output_type": "uri_folder"}},
                "properties": {},
                "settings": {"_source": "YAML.JOB", "default_compute": "", "default_datastore": ""},
                "tags": {},
            }
        }

    def test_default_user_identity_if_empty_identity_input(self):
        test_path = "./tests/test_configs/pipeline_jobs/shakespear_sample/pipeline.yml"
        job = load_job(test_path)
        omit_fields = [
            "jobs.sample_word.componentId",
            "jobs.count_word.componentId",
            "jobs.sample_word.properties",
            "jobs.count_word.properties",
        ]
        actual_job = pydash.omit(job._to_rest_object().properties.as_dict(), *omit_fields)
        assert actual_job == {
            "description": "submit a shakespear sample and word spark job in pipeline",
            "inputs": {
                "input1": {"job_input_type": "uri_file", "mode": "Direct", "uri": "./dataset/shakespeare.txt"},
                "sample_rate": {"job_input_type": "literal", "value": "0.01"},
            },
            "is_archived": False,
            "job_type": "Pipeline",
            "jobs": {
                "count_word": {
                    "_source": "YAML.JOB",
                    "args": "--input1 ${{inputs.input1}}",
                    "conf": {
                        "spark.driver.cores": 1,
                        "spark.driver.memory": "2g",
                        "spark.executor.cores": 2,
                        "spark.executor.instances": 4,
                        "spark.executor.memory": "2g",
                    },
                    "entry": {"file": "wordcount.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                    "identity": {"identity_type": "UserIdentity"},
                    "inputs": {
                        "input1": {"job_input_type": "literal", "value": "${{parent.jobs.sample_word.outputs.output1}}"}
                    },
                    "name": "count_word",
                    "resources": {"instance_type": "standard_e4s_v3", "runtime_version": "3.2.0"},
                    "type": "spark",
                },
                "sample_word": {
                    "_source": "YAML.JOB",
                    "args": "--input1 ${{inputs.input1}} --output2 "
                    "${{outputs.output1}} --my_sample_rate "
                    "${{inputs.sample_rate}}",
                    "conf": {
                        "spark.driver.cores": 1,
                        "spark.driver.memory": "2g",
                        "spark.dynamicAllocation.enabled": True,
                        "spark.dynamicAllocation.maxExecutors": 4,
                        "spark.dynamicAllocation.minExecutors": 1,
                        "spark.executor.cores": 2,
                        "spark.executor.instances": 1,
                        "spark.executor.memory": "2g",
                    },
                    "entry": {"file": "sampleword.py", "spark_job_entry_type": "SparkJobPythonEntry"},
                    "identity": {"identity_type": "UserIdentity"},
                    "inputs": {
                        "input1": {"job_input_type": "literal", "value": "${{parent.inputs.input1}}"},
                        "sample_rate": {"job_input_type": "literal", "value": "${{parent.inputs.sample_rate}}"},
                    },
                    "name": "sample_word",
                    "outputs": {"output1": {"type": "literal", "value": "${{parent.outputs.output1}}"}},
                    "resources": {"instance_type": "standard_e4s_v3", "runtime_version": "3.2.0"},
                    "type": "spark",
                },
            },
            "outputs": {"output1": {"job_output_type": "uri_file", "mode": "Direct"}},
            "properties": {},
            "settings": {"_source": "YAML.JOB"},
            "tags": {},
        }

    def test_spark_node_in_pipeline_with_dynamic_allocation_disabled(
        self,
    ):
        test_path = "./tests/test_configs/pipeline_jobs/invalid/pipeline_job_with_spark_job_with_dynamic_allocation_disabled.yml"
        job = load_job(test_path)
        result = job._validate()
        assert (
            "jobs.hello_world" in result.error_messages
            and "Should not specify min or max executors when dynamic allocation is disabled."
            == result.error_messages["jobs.hello_world"]
        )

    def test_spark_node_in_pipeline_with_invalid_code(
        self,
    ):
        test_path = "./tests/test_configs/pipeline_jobs/invalid/pipeline_job_with_spark_job_with_invalid_code.yml"
        job = load_job(test_path)
        result = job._validate()
        assert "jobs.hello_world.component.entry" in result.error_messages

    def test_spark_node_in_pipeline_with_git_code(
        self,
    ):
        test_path = "./tests/test_configs/pipeline_jobs/invalid/pipeline_job_with_spark_job_with_git_code.yml"
        job = load_job(test_path)
        job._validate()

    def test_spark_node_with_remote_component_in_pipeline(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/dsl_pipeline/spark_job_in_pipeline/kmeans_sample/pipeline.yml"

        job = load_job(test_path)
        assert isinstance(job, PipelineJob)
        node = next(iter(job.jobs.values()))
        assert isinstance(node, Spark)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value=""
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)
        result = job._validate()
        assert result.passed is True
        rest_job_dict = job._to_rest_object().as_dict()
        actual_dict = rest_job_dict["properties"]["jobs"]["kmeans_cluster"]

        expected_dict = {
            "_source": "REMOTE.WORKSPACE.COMPONENT",
            "componentId": "",
            "computeId": "",
            "identity": {"identity_type": "Managed"},
            "inputs": {"file_input": {"job_input_type": "literal", "value": "${{parent.inputs.iris_data}}"}},
            "name": "kmeans_cluster",
            "outputs": {"output": {"type": "literal", "value": "${{parent.outputs.output}}"}},
            "resources": {"instance_type": "standard_e4s_v3", "runtime_version": "3.2.0"},
            "type": "spark",
        }
        assert actual_dict == expected_dict

    @pytest.mark.parametrize(
        "test_path, error_messages",
        [
            (
                "./tests/test_configs/pipeline_jobs/invalid/pipeline_job_with_spark_job_with_invalid_input_mode.yml",
                "Input 'file_input1' is using 'None' mode, only 'direct' is supported for Spark job",
            ),
            (
                "./tests/test_configs/pipeline_jobs/invalid/pipeline_job_with_spark_job_with_invalid_component_input_mode.yml",
                "Input 'input1' is using 'mount' mode, only 'direct' is supported for Spark job",
            ),
        ],
    )
    def test_spark_node_in_pipeline_with_invalid_input_mode(self, test_path, error_messages):
        job = load_job(test_path)
        result = job._validate()
        assert error_messages == result.error_messages["jobs.hello_world"]

    @pytest.mark.parametrize(
        "test_path, error_messages",
        [
            (
                "./tests/test_configs/pipeline_jobs/invalid/pipeline_job_with_spark_job_with_invalid_output_mode.yml",
                "Output 'output' is using 'None' mode, only 'direct' is supported for Spark job",
            ),
            (
                "./tests/test_configs/pipeline_jobs/invalid/pipeline_job_with_spark_job_with_invalid_component_output_mode.yml",
                "Output 'output1' is using 'upload' mode, only 'direct' is supported for Spark job",
            ),
        ],
    )
    def test_spark_node_in_pipeline_with_invalid_output_mode(self, test_path, error_messages):
        job = load_job(test_path)
        result = job._validate()
        assert error_messages == result.error_messages["jobs.hello_world"]

    def test_infer_pipeline_output_type_as_node_type(
        self,
    ) -> None:
        pipeline_job = load_job(
            source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_defaults_with_parallel_job_tabular_input_e2e.yml",
        )
        assert (
            pipeline_job.jobs["hello_world_inline_parallel_tabular_job_1"].outputs["job_output_file"].type
            == AssetTypes.URI_FILE
        )

    @pytest.mark.parametrize(
        "pipeline_job_path, expected_type, expected_components",
        [
            (
                "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_registered_component_literal_output_binding_to_inline_job_input.yml",
                "uri_folder",
                {
                    "score_job": {
                        "_source": "YAML.JOB",
                        "command": 'echo "hello" && echo "world" && echo "train" > world.txt',
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {"model_input": {"type": "uri_folder"}, "test_data": {"type": "uri_folder"}},
                        "is_deterministic": True,
                        "outputs": {"score_output": {"type": "uri_folder"}},
                        "type": "command",
                        "version": "1",
                    },
                },
            ),
            (
                "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_registered_component_literal_output_binding_to_inline_job_input2.yml",
                "mltable",
                {
                    "score_job": {
                        "_source": "YAML.JOB",
                        "command": 'echo "hello" && echo "world" && echo "train" > world.txt',
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {"model_input": {"type": "mltable"}, "test_data": {"type": "uri_folder"}},
                        "is_deterministic": True,
                        "outputs": {"score_output": {"type": "uri_folder"}},
                        "type": "command",
                        "version": "1",
                    },
                },
            ),
            (
                "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_registered_component_output_binding_to_inline_job_input.yml",
                "uri_folder",
                {
                    "score_job": {
                        "_source": "YAML.JOB",
                        "command": 'echo "hello" && echo "world" && echo "train" > world.txt',
                        "environment": "azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
                        "inputs": {"model_input": {"type": "uri_folder"}, "test_data": {"type": "uri_folder"}},
                        "is_deterministic": True,
                        "outputs": {"score_output": {"type": "uri_folder"}},
                        "type": "command",
                        "version": "1",
                    },
                },
            ),
        ],
    )
    def test_pipeline_job_with_inline_command_job_input_binding_to_registered_component_job_output(
        self,
        client: MLClient,
        pipeline_job_path: str,
        expected_type,
        expected_components,
    ) -> None:
        pipeline_job = load_job(
            source=pipeline_job_path,
        )
        actual_type = pipeline_job.jobs["score_job"].inputs.model_input.type
        assert actual_type == expected_type
        actual_type = pipeline_job.jobs["score_job"].component.inputs["model_input"].type
        assert actual_type == expected_type

        # check component of pipeline job is expected
        for name, expected_dict in expected_components.items():
            actual_dict = pipeline_job.jobs[name].component._to_rest_object().as_dict()
            omit_fields = [
                "name",
            ]

            actual_dict = pydash.omit(actual_dict["properties"]["component_spec"], omit_fields)
            assert actual_dict == expected_dict

    def test_pipeline_without_setting_binding_node(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_without_setting_binding_node.yml"
        job = load_job(source=test_path)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        actual_dict = job._to_rest_object().as_dict()["properties"]

        assert actual_dict == {
            "properties": {},
            "tags": {},
            "is_archived": False,
            "compute_id": "xxx",
            "job_type": "Pipeline",
            "inputs": {
                "training_input": {"uri": "yyy/", "job_input_type": "uri_folder"},
                "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
            },
            "jobs": {
                "train_job": {
                    "type": "command",
                    "_source": "YAML.JOB",
                    "name": "train_job",
                    "computeId": "xxx",
                    "inputs": {
                        "training_data": {"job_input_type": "literal", "value": "${{parent.inputs.training_input}}"},
                        "learning_rate": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_learning_rate}}",
                        },
                        "learning_rate_schedule": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.learning_rate_schedule}}",
                        },
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
                    },
                    "outputs": {"model_output": {"value": "${{parent.outputs.trained_model}}", "type": "literal"}},
                    "componentId": "xxx",
                }
            },
            "outputs": {"trained_model": {"job_output_type": "uri_folder"}},
            "settings": {"_source": "YAML.JOB"},
        }

    def test_pipeline_with_only_setting_pipeline_level(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_with_only_setting_pipeline_level.yml"
        job = load_job(source=test_path)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        actual_dict = job._to_rest_object().as_dict()["properties"]

        assert actual_dict == {
            "properties": {},
            "tags": {},
            "is_archived": False,
            "compute_id": "xxx",
            "job_type": "Pipeline",
            "inputs": {
                "training_input": {"uri": "yyy/", "job_input_type": "uri_folder", "mode": "ReadOnlyMount"},
                "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
            },
            "jobs": {
                "train_job": {
                    "type": "command",
                    "_source": "YAML.JOB",
                    "name": "train_job",
                    "computeId": "xxx",
                    "inputs": {
                        "training_data": {"job_input_type": "literal", "value": "${{parent.inputs.training_input}}"},
                        "learning_rate": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_learning_rate}}",
                        },
                        "learning_rate_schedule": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.learning_rate_schedule}}",
                        },
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
                    },
                    "outputs": {"model_output": {"value": "${{parent.outputs.trained_model}}", "type": "literal"}},
                    "componentId": "xxx",
                }
            },
            "outputs": {"trained_model": {"job_output_type": "uri_folder", "mode": "Upload"}},
            "settings": {
                "_source": "YAML.JOB",
            },
        }

    def test_pipeline_with_only_setting_binding_node(self, mock_machinelearning_client: MLClient, mocker: MockFixture):
        test_path = "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_with_only_setting_binding_node.yml"
        job = load_job(source=test_path)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        actual_dict = job._to_rest_object().as_dict()["properties"]

        assert pydash.omit(actual_dict, *["properties", "jobs.train_job.properties"]) == {
            "tags": {},
            "is_archived": False,
            "compute_id": "xxx",
            "job_type": "Pipeline",
            "inputs": {
                "training_input": {
                    "uri": "yyy/",
                    "job_input_type": "uri_folder",
                },
                "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
            },
            "jobs": {
                "train_job": {
                    "type": "command",
                    "_source": "YAML.JOB",
                    "name": "train_job",
                    "computeId": "xxx",
                    "inputs": {
                        "training_data": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_input}}",
                            "mode": "ReadOnlyMount",
                        },
                        "learning_rate": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_learning_rate}}",
                        },
                        "learning_rate_schedule": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.learning_rate_schedule}}",
                        },
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
                    },
                    "outputs": {
                        # add mode in rest if binding output set mode
                        "model_output": {
                            "value": "${{parent.outputs.trained_model}}",
                            "type": "literal",
                            "mode": "Upload",
                        }
                    },
                    "componentId": "xxx",
                }
            },
            "outputs": {"trained_model": {"job_output_type": "uri_folder"}},
            "settings": {"_source": "YAML.JOB"},
        }

    def test_pipeline_with_setting_binding_node_and_pipeline_level(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_with_setting_binding_node_and_pipeline_level.yml"
        job = load_job(source=test_path)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        actual_dict = job._to_rest_object().as_dict()["properties"]

        assert pydash.omit(actual_dict, *["properties", "jobs.train_job.properties"]) == {
            "tags": {},
            "is_archived": False,
            "compute_id": "xxx",
            "job_type": "Pipeline",
            "inputs": {
                "training_input": {"uri": "yyy/", "job_input_type": "uri_folder", "mode": "Download"},
                "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
            },
            "jobs": {
                "train_job": {
                    "type": "command",
                    "_source": "YAML.JOB",
                    "name": "train_job",
                    "computeId": "xxx",
                    "inputs": {
                        "training_data": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_input}}",
                            "mode": "ReadOnlyMount",
                        },
                        "learning_rate": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_learning_rate}}",
                        },
                        "learning_rate_schedule": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.learning_rate_schedule}}",
                        },
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
                    },
                    "outputs": {
                        # add mode in rest if binding output set mode
                        "model_output": {
                            "value": "${{parent.outputs.trained_model}}",
                            "type": "literal",
                            "mode": "Upload",
                        }
                    },
                    "componentId": "xxx",
                }
            },
            "outputs": {"trained_model": {"job_output_type": "uri_folder", "mode": "ReadWriteMount"}},
            "settings": {"_source": "YAML.JOB"},
        }

    def test_pipeline_with_inline_job_setting_binding_node_and_pipeline_level(
        self, mock_machinelearning_client: MLClient, mocker: MockFixture
    ):
        test_path = "./tests/test_configs/dsl_pipeline/pipeline_with_set_binding_output_input/pipeline_with_inline_job_setting_binding_node_and_pipeline_level.yml"
        job = load_job(source=test_path)

        mocker.patch(
            "azure.ai.ml.operations._operation_orchestrator.OperationOrchestrator.get_asset_arm_id", return_value="xxx"
        )
        mocker.patch("azure.ai.ml.operations._job_operations._upload_and_generate_remote_uri", return_value="yyy")
        mock_machinelearning_client.jobs._resolve_arm_id_or_upload_dependencies(job)

        actual_dict = job._to_rest_object().as_dict()["properties"]

        assert pydash.omit(actual_dict, *["properties", "jobs.train_job.properties"]) == {
            "tags": {},
            "is_archived": False,
            "compute_id": "xxx",
            "job_type": "Pipeline",
            "inputs": {
                "training_input": {"uri": "yyy/", "job_input_type": "uri_folder", "mode": "Download"},
                "training_max_epochs": {"job_input_type": "literal", "value": "20"},
                "training_learning_rate": {"job_input_type": "literal", "value": "1.8"},
                "learning_rate_schedule": {"job_input_type": "literal", "value": "time-based"},
            },
            "jobs": {
                "train_job": {
                    "type": "command",
                    "_source": "YAML.JOB",
                    "name": "train_job",
                    "computeId": "xxx",
                    "inputs": {
                        "training_data": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_input}}",
                            "mode": "ReadOnlyMount",
                        },
                        "learning_rate": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.training_learning_rate}}",
                        },
                        "learning_rate_schedule": {
                            "job_input_type": "literal",
                            "value": "${{parent.inputs.learning_rate_schedule}}",
                        },
                        "max_epochs": {"job_input_type": "literal", "value": "${{parent.inputs.training_max_epochs}}"},
                    },
                    "outputs": {
                        # add mode in rest if binding output set mode
                        "model_output": {
                            "value": "${{parent.outputs.trained_model}}",
                            "type": "literal",
                            "mode": "Upload",
                        }
                    },
                    "componentId": "xxx",
                }
            },
            "outputs": {"trained_model": {"job_output_type": "uri_folder", "mode": "ReadWriteMount"}},
            "settings": {"_source": "YAML.JOB"},
        }

    def test_pipeline_job_with_parameter_group(self):
        test_path = "./tests/test_configs/pipeline_jobs/pipeline_job_with_parameter_group.yml"
        job: PipelineJob = load_job(test_path)
        assert isinstance(job.inputs.group, _GroupAttrDict)
        job.inputs.group.int_param = 5
        job.inputs.group.sub_group.str_param = "str"
        job_dict = job._to_dict()
        assert job_dict["inputs"] == {
            "group.int_param": 5,
            "group.enum_param": "hello",
            "group.number_param": 4,
            "group.sub_group.str_param": "str",
            "group.sub_group.bool_param": 1,
        }
        assert job_dict["jobs"]["hello_world_component_1"]["inputs"] == {
            "component_in_string": {"path": "${{parent.inputs.group.sub_group.str_param}}"},
            "component_in_ranged_integer": {"path": "${{parent.inputs.group.int_param}}"},
            "component_in_enum": {"path": "${{parent.inputs.group.enum_param}}"},
            "component_in_boolean": {"path": "${{parent.inputs.group.sub_group.bool_param}}"},
            "component_in_ranged_number": {"path": "${{parent.inputs.group.number_param}}"},
        }
        rest_job = job._to_rest_object().as_dict()["properties"]
        assert rest_job["inputs"] == {
            "group.int_param": {"job_input_type": "literal", "value": "5"},
            "group.enum_param": {"job_input_type": "literal", "value": "hello"},
            "group.number_param": {"job_input_type": "literal", "value": "4.0"},
            "group.sub_group.str_param": {"job_input_type": "literal", "value": "str"},
            "group.sub_group.bool_param": {"job_input_type": "literal", "value": "True"},
        }
        assert rest_job["jobs"]["hello_world_component_1"]["inputs"] == {
            "component_in_string": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.group.sub_group.str_param}}",
            },
            "component_in_ranged_integer": {"job_input_type": "literal", "value": "${{parent.inputs.group.int_param}}"},
            "component_in_enum": {"job_input_type": "literal", "value": "${{parent.inputs.group.enum_param}}"},
            "component_in_boolean": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.group.sub_group.bool_param}}",
            },
            "component_in_ranged_number": {
                "job_input_type": "literal",
                "value": "${{parent.inputs.group.number_param}}",
            },
        }

    def test_non_string_pipeline_node_input(self):
        test_path = "./tests/test_configs/pipeline_jobs/rest_non_string_input_pipeline.json"
        with open(test_path, "r") as f:
            job_dict = yaml.safe_load(f)
        pipeline = load_pipeline_entity_from_rest_json(job_dict)
        pipeline_dict = pipeline._to_dict()
        node_input_dict = pipeline_dict["jobs"]["error_analysis_job"]["inputs"]
        # Assert integer value became str
        assert node_input_dict == {
            "max_depth": "3",
            "min_child_samples": "20",
            "num_leaves": "31",
            "rai_insights_dashboard": {"path": "${{parent.jobs.create_rai_job.outputs.rai_insights_dashboard}}"},
        }
        rest_pipeline_dict = pipeline._to_rest_object().as_dict()
        rest_node_dict = pydash.omit_by(rest_pipeline_dict["properties"]["jobs"]["error_analysis_job"], lambda x: not x)
        # Assert integer value became str
        assert rest_node_dict == {
            "_source": "REMOTE.REGISTRY",
            "componentId": "azureml://registries/rai-test/components/microsoft_azureml_rai_tabular_erroranalysis/versions/dev.0.0.1.1662509117.preview",
            "inputs": {
                "max_depth": {"job_input_type": "literal", "value": "3"},
                "min_child_samples": {"job_input_type": "literal", "value": "20"},
                "num_leaves": {"job_input_type": "literal", "value": "31"},
                "rai_insights_dashboard": {
                    "job_input_type": "literal",
                    "value": "${{parent.jobs.create_rai_job.outputs.rai_insights_dashboard}}",
                },
            },
            "type": "command",
        }

    def test_job_properties(self):
        pipeline_job: PipelineJob = load_job(
            source="./tests/test_configs/pipeline_jobs/pipeline_job_with_properties.yml"
        )
        pipeline_dict = pipeline_job._to_dict()
        rest_pipeline_dict = pipeline_job._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["properties"] == {"AZURE_ML_PathOnCompute_input_data": "/tmp/test"}
        assert rest_pipeline_dict["properties"] == pipeline_dict["properties"]
        for name, node_dict in pipeline_dict["jobs"].items():
            rest_node_dict = rest_pipeline_dict["jobs"][name]
            assert len(node_dict["properties"]) == 1
            assert "AZURE_ML_PathOnCompute_" in list(node_dict["properties"].keys())[0]
            assert node_dict["properties"] == rest_node_dict["properties"]

    def test_comment_in_pipeline(self) -> None:
        pipeline_job = load_job(source="./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_comment.yml")
        pipeline_dict = pipeline_job._to_dict()
        rest_pipeline_dict = pipeline_job._to_rest_object().as_dict()["properties"]
        assert pipeline_dict["jobs"]["hello_world_component"]["comment"] == "arbitrary string"
        assert rest_pipeline_dict["jobs"]["hello_world_component"]["comment"] == "arbitrary string"

    def test_pipeline_node_default_output(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_component_output.yml"
        pipeline: PipelineJob = load_job(source=test_path)

        # pipeline level output
        pipeline_output = pipeline.outputs["job_out_path_2"]
        assert pipeline_output.mode == "upload"

        # other node level output tests can be found in
        # dsl/unittests/test_component_func.py::TestComponentFunc::test_component_outputs
        # data-binding-expression
        with pytest.raises(ValidationException, match="<class '.*'> does not support setting path."):
            pipeline.jobs["merge_component_outputs"].outputs["component_out_path_1"].path = "xxx"

    def test_pipeline_node_with_identity(self):
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_identity.yml"
        pipeline_job: PipelineJob = load_job(source=test_path)

        omit_fields = ["jobs.*.componentId", "jobs.*._source"]
        actual_dict = omit_with_wildcard(pipeline_job._to_rest_object().as_dict()["properties"], *omit_fields)
        assert actual_dict["jobs"] == {
            "hello_world_component": {
                "computeId": "cpu-cluster",
                "identity": {"type": "user_identity"},
                "inputs": {
                    "component_in_number": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_number}}"},
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "name": "hello_world_component",
                "type": "command",
            },
            "hello_world_component_2": {
                "computeId": "cpu-cluster",
                "identity": {"type": "aml_token"},
                "inputs": {
                    "component_in_number": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.job_in_other_number}}",
                    },
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "name": "hello_world_component_2",
                "type": "command",
            },
            "hello_world_component_3": {
                "computeId": "cpu-cluster",
                "identity": {"type": "user_identity"},
                "inputs": {
                    "component_in_number": {
                        "job_input_type": "literal",
                        "value": "${{parent.inputs.job_in_other_number}}",
                    },
                    "component_in_path": {"job_input_type": "literal", "value": "${{parent.inputs.job_in_path}}"},
                },
                "name": "hello_world_component_3",
                "type": "command",
            },
        }

    def test_pipeline_parameter_with_empty_value(self, client: MLClient) -> None:
        input_types_func = load_component(source="./tests/test_configs/components/input_types_component.yml")

        @group
        class InputGroup:
            group_empty_str: str = ""
            group_none_str: str = None

        # Construct pipeline
        @dsl.pipeline(
            default_compute="cpu-cluster",
            description="This is the basic pipeline with empty_value",
        )
        def empty_value_pipeline(
            integer: int, boolean: bool, number: float, str_param: str, empty_str: str, input_group: InputGroup
        ):
            input_types_func(
                component_in_string=str_param,
                component_in_ranged_integer=integer,
                component_in_boolean=boolean,
                component_in_ranged_number=number,
            )
            input_types_func(component_in_string=empty_str)
            input_types_func(component_in_string=input_group.group_empty_str)
            input_types_func(component_in_string=input_group.group_none_str)

        pipeline = empty_value_pipeline(
            integer=0, boolean=False, number=0, str_param="str_param", empty_str="", input_group=InputGroup()
        )
        rest_obj = pipeline._to_rest_object()
        # Currently MFE not support pass empty str or None as pipeline input.
        assert len(rest_obj.properties.inputs) == 4
        assert "integer" in rest_obj.properties.inputs
        assert "boolean" in rest_obj.properties.inputs
        assert "number" in rest_obj.properties.inputs
        assert "str_param" in rest_obj.properties.inputs

    def test_pipeline_input_as_runsettings_value(self, client: MLClient) -> None:
        input_types_func = load_component(source="./tests/test_configs/components/input_types_component.yml")

        @dsl.pipeline(
            default_compute="cpu-cluster",
            description="Set pipeline input to runsettings",
        )
        def empty_value_pipeline(integer: int, boolean: bool, number: float, str_param: str, shm_size: str):
            component = input_types_func(
                component_in_string=str_param,
                component_in_ranged_integer=integer,
                component_in_boolean=boolean,
                component_in_ranged_number=number,
            )
            component.resources = JobResourceConfiguration(
                instance_count=integer,
                shm_size=shm_size,
            )

        pipeline = empty_value_pipeline(integer=0, boolean=False, number=0, str_param="str_param", shm_size="20g")
        rest_obj = pipeline._to_rest_object()
        expect_resource = {"instance_count": "${{parent.inputs.integer}}", "shm_size": "${{parent.inputs.shm_size}}"}
        assert rest_obj.properties.jobs["component"]["resources"] == expect_resource

    def test_pipeline_job_serverless_compute_with_job_tier(self) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/serverless_compute/job_tier/pipeline_with_job_tier.yml"
        pipeline_job = load_job(yaml_path)
        rest_obj = pipeline_job._to_rest_object()
        assert rest_obj.properties.jobs["spot_job_tier"]["queue_settings"] == {"job_tier": "Spot"}
        assert rest_obj.properties.jobs["standard_job_tier"]["queue_settings"] == {"job_tier": "Standard"}

    def test_pipeline_job_sweep_with_job_tier_in_pipeline(self) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/serverless_compute/job_tier/sweep_in_pipeline/pipeline.yml"
        pipeline_job = load_job(yaml_path)
        # for sweep job, its job_tier value will be lowercase due to its implementation,
        # and service side shall accept both capital and lowercase, so it is expected for now.
        rest_obj = pipeline_job._to_rest_object()
        assert rest_obj.properties.jobs["node"]["queue_settings"] == {"job_tier": "standard"}

    def test_pipeline_job_automl_with_job_tier_in_pipeline(self) -> None:
        yaml_path = "./tests/test_configs/pipeline_jobs/serverless_compute/job_tier/automl_in_pipeline/pipeline.yml"
        pipeline_job = load_job(yaml_path)
        # similar to sweep job, automl job job_tier value is also lowercase.
        rest_obj = pipeline_job._to_rest_object()
        assert rest_obj.properties.jobs["text_ner_node"]["queue_settings"] == {"job_tier": "spot"}

    def test_get_predecessors_for_pipeline_job(self) -> None:
        test_path = "./tests/test_configs/pipeline_jobs/helloworld_pipeline_job_with_component_output.yml"
        pipeline: PipelineJob = load_job(source=test_path)
        # get_predecessors is not supported for YAML job
        assert get_predecessors(pipeline.jobs["hello_world_component_1"]) == []
        assert get_predecessors(pipeline.jobs["hello_world_component_2"]) == []
        assert get_predecessors(pipeline.jobs["merge_component_outputs"]) == []
