from lib2to3.pytree import convert

import pytest

from azure.ai.ml import UserIdentityConfiguration
from azure.ai.ml._restclient.v2023_04_01_preview.models import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2023_04_01_preview.models import BanditPolicy as RestBanditPolicy
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    JobBase,
    LogVerbosity,
    NlpFixedParameters,
    NlpParameterSubspace,
    NlpSweepSettings,
    NlpVerticalFeaturizationSettings,
    NlpVerticalLimitSettings,
    SamplingAlgorithmType,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import UserIdentity as RestUserIdentity
from azure.ai.ml._restclient.v2023_04_01_preview.models._azure_machine_learning_workspaces_enums import (
    ClassificationPrimaryMetrics,
)
from azure.ai.ml._restclient.v2024_01_01_preview.models import MLTableJobInput, TextClassificationMultilabel
from azure.ai.ml._utils.utils import to_iso_duration_format_mins
from azure.ai.ml.automl import text_classification_multilabel
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl import SearchSpace
from azure.ai.ml.entities._job.automl.nlp.text_classification_multilabel_job import TextClassificationMultilabelJob
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform


@pytest.mark.automl_test
@pytest.mark.unittest
class TestAutoMLTextClassificationMultilabelJob:
    """Tests for AutoML NLP Text Classification Multilabel Job."""

    def test_automl_nlp_text_classification_multilabel_default(self):
        label_column = "label_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        job = text_classification_multilabel(
            target_column_name=label_column,
            training_data=Input(type=AssetTypes.MLTABLE, path=training_data_uri),
            validation_data=Input(type=AssetTypes.MLTABLE, path=validation_data_uri),
        )
        assert isinstance(job, TextClassificationMultilabelJob)
        assert job.task_type == "TextClassificationMultilabel"
        assert job.primary_metric == TextClassificationMultilabelJob._DEFAULT_PRIMARY_METRIC
        assert job.target_column_name == label_column
        assert job.training_data.type == AssetTypes.MLTABLE
        assert job.training_data.path == training_data_uri
        assert job.validation_data.type == AssetTypes.MLTABLE
        assert job.validation_data.path == validation_data_uri
        assert job.target_column_name == label_column
        assert job.training_data.path == training_data_uri
        assert job.validation_data.path == validation_data_uri
        assert job._limits is not None
        assert job._limits.max_trials == 1
        assert job._limits.max_concurrent_trials is None
        assert job._limits.max_nodes == 1
        assert job._limits.trial_timeout_minutes is None
        assert job._limits.timeout_minutes is None
        assert job._sweep is None
        assert job._training_parameters is None
        assert job._search_space is None
        assert job._featurization is None
        assert job.log_verbosity is None

    @pytest.mark.parametrize("run_type", ["single", "sweep"])
    def test_automl_nlp_text_classification_multilabel_init(self, run_type):
        label_column = "label_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        log_verbosity = "Debug"
        dataset_language = "deu"
        job = text_classification_multilabel(
            log_verbosity=log_verbosity,
            target_column_name=label_column,
            training_data=Input(type=AssetTypes.MLTABLE, path=training_data_uri),
            validation_data=Input(type=AssetTypes.MLTABLE, path=validation_data_uri),
        )

        if run_type == "sweep":
            job.set_limits(
                max_concurrent_trials=2, max_trials=1, timeout_minutes=30, trial_timeout_minutes=10, max_nodes=4
            )
            early_termination_policy = BanditPolicy(evaluation_interval=10, slack_amount=0.02)
            job.set_sweep(sampling_algorithm=SamplingAlgorithmType.GRID, early_termination=early_termination_policy)
            job.extend_search_space(
                [
                    SearchSpace(model_name="bert-base-cased", learning_rate=Uniform(5e-6, 5e-5)),
                    SearchSpace(model_name="bert-large-cased", number_of_epochs=Choice([3, 4, 5])),
                ]
            )
        else:
            job.set_limits(timeout_minutes=30)
        job.set_training_parameters(training_batch_size=16)
        job.set_featurization(dataset_language=dataset_language)
        assert isinstance(job, TextClassificationMultilabelJob)
        if run_type == "sweep":
            assert job.limits.max_concurrent_trials == 2
            assert job.limits.max_trials == 1
            assert job.limits.max_nodes == 4
            assert job.limits.timeout_minutes == 30
            assert job.limits.trial_timeout_minutes == 10

            assert job.sweep.sampling_algorithm == SamplingAlgorithmType.GRID
            assert job.sweep.early_termination == early_termination_policy

            assert job.search_space[0].model_name == "bert-base-cased"
            assert job.search_space[0].learning_rate == Uniform(5e-6, 5e-5)

            assert job.search_space[1].model_name == "bert-large-cased"
            assert job.search_space[1].number_of_epochs == Choice([3, 4, 5])
        else:
            assert job.limits.max_concurrent_trials == 1
            assert job.limits.max_trials == 1
            assert job.limits.max_nodes == 1
            assert job.limits.timeout_minutes == 30
            assert job.limits.trial_timeout_minutes is None
        assert job.training_parameters.training_batch_size == 16
        assert job.training_parameters.validation_batch_size is None
        assert job.featurization.dataset_language == dataset_language
        assert job.log_verbosity == LogVerbosity.DEBUG.value

    def test_automl_nlp_text_classification_multilabel_init_with_dictionary(self):
        label_column = "label_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        log_verbosity = "Debug"
        max_nodes = 2
        timeout = 30
        validation_batch_size = 32
        dataset_language = "deu"
        job = text_classification_multilabel(
            log_verbosity=log_verbosity,
            target_column_name=label_column,
            training_data=Input(type=AssetTypes.MLTABLE, path=training_data_uri),
            validation_data=Input(type=AssetTypes.MLTABLE, path=validation_data_uri),
        )
        job.limits = {"timeout_minutes": timeout, "max_nodes": max_nodes}
        job.featurization = {"dataset_language": dataset_language}
        job.training_parameters = {"validation_batch_size": validation_batch_size}
        job.search_space = [{"model_name": Choice(["xlnet-base-cased", "xlm-roberta-large"])}]
        job.sweep = {"sampling_algorithm": "random"}
        assert job.limits.timeout_minutes == timeout
        assert job.limits.max_trials == 1  # default value
        assert job.limits.max_nodes == 2
        assert job.featurization.dataset_language == dataset_language
        assert job.training_parameters.validation_batch_size == validation_batch_size
        assert job.search_space[0].model_name == Choice(["xlnet-base-cased", "xlm-roberta-large"])
        assert job.sweep.sampling_algorithm == "random"
        assert job.sweep.early_termination is None
        assert job.log_verbosity == LogVerbosity.DEBUG.value

    @pytest.mark.parametrize("run_type", ["single", "sweep"])
    def test_automl_nlp_text_classification_multilabel_to_rest_object(self, run_type):
        primary_metric = ClassificationPrimaryMetrics.ACCURACY
        log_verbosity = "Debug"
        label_column = "label_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        dataset_language = "eng"

        timeout = 30
        if run_type == "sweep":
            max_concurrent_trials = 2
            max_nodes = 4
            max_trials = 2
        else:
            max_concurrent_trials = 1
            max_nodes = 1
            max_trials = 1

        identity = UserIdentityConfiguration()
        job = text_classification_multilabel(
            primary_metric=primary_metric,
            log_verbosity=log_verbosity,
            target_column_name=label_column,
            identity=identity,
            training_data=Input(type=AssetTypes.MLTABLE, path=training_data_uri),
            validation_data=Input(type=AssetTypes.MLTABLE, path=validation_data_uri),
        )
        job.set_limits(
            max_concurrent_trials=max_concurrent_trials,
            max_trials=max_trials,
            max_nodes=max_nodes,
            timeout_minutes=timeout,
        )
        job.set_featurization(dataset_language=dataset_language)
        job.set_training_parameters(weight_decay=0.01)

        rest_sweep = None
        rest_search_space = None
        if run_type == "sweep":
            job.set_sweep(
                sampling_algorithm=SamplingAlgorithmType.GRID,
                early_termination=BanditPolicy(slack_factor=0.2, evaluation_interval=2),
            )
            job.extend_search_space([SearchSpace(model_name=Choice(["bert-base-cased", "distilbert-base-cased"]))])
            rest_sweep = NlpSweepSettings(
                sampling_algorithm=SamplingAlgorithmType.GRID,
                early_termination=RestBanditPolicy(slack_factor=0.2, evaluation_interval=2),
            )
            rest_search_space = [NlpParameterSubspace(model_name="choice('bert-base-cased','distilbert-base-cased')")]

        expected = TextClassificationMultilabel(
            primary_metric=primary_metric,
            log_verbosity=log_verbosity,
            target_column_name=label_column,
            training_data=MLTableJobInput(uri=training_data_uri),
            validation_data=MLTableJobInput(uri=validation_data_uri),
            limit_settings=NlpVerticalLimitSettings(
                max_concurrent_trials=max_concurrent_trials,
                max_trials=max_trials,
                max_nodes=max_nodes,
                timeout=to_iso_duration_format_mins(timeout),
            ),
            fixed_parameters=NlpFixedParameters(weight_decay=0.01),
            sweep_settings=rest_sweep,
            search_space=rest_search_space,
            featurization_settings=NlpVerticalFeaturizationSettings(dataset_language=dataset_language),
        )

        # Test converting Job to REST object
        converted_to_rest_obj = job._to_rest_object()
        assert isinstance(converted_to_rest_obj.properties.identity, RestUserIdentity)
        assert isinstance(converted_to_rest_obj, JobBase)
        assert converted_to_rest_obj.properties.task_details == expected
        result = converted_to_rest_obj.properties.task_details
        assert result.task_type == "TextClassificationMultilabel"
        assert expected.task_type == result.task_type
        assert expected.primary_metric == result.primary_metric
        assert expected.training_data == result.training_data
        assert expected.validation_data == result.validation_data
        assert expected.limit_settings == result.limit_settings
        assert expected.sweep_settings == result.sweep_settings
        assert expected.fixed_parameters == result.fixed_parameters
        assert expected.search_space == result.search_space
        assert expected.featurization_settings == result.featurization_settings
        assert expected.log_verbosity == result.log_verbosity

    @pytest.mark.parametrize("run_type", ["single", "sweep"])
    def test_automl_nlp_text_classification_multilabel_from_rest_object(self, run_type):
        log_verbosity = "Debug"
        label_column = "target_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        dataset_language = "eng"

        timeout = 30
        if run_type == "sweep":
            max_concurrent_trials = 2
            max_nodes = 4
            max_trials = 2
        else:
            max_concurrent_trials = 1
            max_nodes = 1
            max_trials = 1

        identity = UserIdentityConfiguration()
        expected_job = text_classification_multilabel(
            target_column_name=label_column,
            training_data=Input(type=AssetTypes.MLTABLE, path=training_data_uri),
            validation_data=Input(type=AssetTypes.MLTABLE, path=validation_data_uri),
            log_verbosity=log_verbosity,
            # Job attributes
            compute="cpucluster",
            name="text_classification_multilabel_job",
            experiment_name="experiment",
            tags={"foo_tag": "bar"},
            identity=identity,
        )
        expected_job.set_limits(
            max_concurrent_trials=max_concurrent_trials,
            max_trials=max_trials,
            max_nodes=max_nodes,
            timeout_minutes=timeout,
        )
        expected_job.set_featurization(dataset_language=dataset_language)
        expected_job.set_training_parameters(weight_decay=0.01)

        rest_sweep = None
        rest_search_space = None
        if run_type == "sweep":
            expected_job.set_sweep(
                sampling_algorithm=SamplingAlgorithmType.GRID,
                early_termination=BanditPolicy(slack_factor=0.2, evaluation_interval=2),
            )
            expected_job.extend_search_space(
                [SearchSpace(model_name=Choice(["bert-base-cased", "distilbert-base-cased"]))]
            )
            rest_sweep = NlpSweepSettings(
                sampling_algorithm=SamplingAlgorithmType.GRID,
                early_termination=RestBanditPolicy(slack_factor=0.2, evaluation_interval=2),
            )
            rest_search_space = [NlpParameterSubspace(model_name="choice(bert-base-cased, distilbert-base-cased)")]

        task_details = TextClassificationMultilabel(
            log_verbosity=log_verbosity,
            target_column_name=label_column,
            training_data=MLTableJobInput(uri=training_data_uri),
            validation_data=MLTableJobInput(uri=validation_data_uri),
            limit_settings=NlpVerticalLimitSettings(
                max_concurrent_trials=max_concurrent_trials,
                max_trials=max_trials,
                max_nodes=max_nodes,
                timeout=to_iso_duration_format_mins(timeout),
            ),
            featurization_settings=NlpVerticalFeaturizationSettings(dataset_language=dataset_language),
            fixed_parameters=NlpFixedParameters(weight_decay=0.01),
            sweep_settings=rest_sweep,
            search_space=rest_search_space,
        )
        job_data = JobBase(properties=RestAutoMLJob(task_details=task_details, identity=identity._to_job_rest_object()))
        # Test converting REST object to Job
        converted_to_job = TextClassificationMultilabelJob._from_rest_object(job_data)
        assert converted_to_job.identity == identity
        assert isinstance(converted_to_job, TextClassificationMultilabelJob)
        assert expected_job.primary_metric == converted_to_job.primary_metric
        assert expected_job.target_column_name == converted_to_job.target_column_name
        assert expected_job.training_data == converted_to_job.training_data
        assert expected_job.validation_data == converted_to_job.validation_data
        assert expected_job.limits == converted_to_job.limits
        assert expected_job.training_parameters == converted_to_job.training_parameters
        assert expected_job.sweep == converted_to_job.sweep
        assert expected_job.search_space == converted_to_job.search_space
        assert expected_job.featurization == converted_to_job.featurization
        assert expected_job.log_verbosity == converted_to_job.log_verbosity
