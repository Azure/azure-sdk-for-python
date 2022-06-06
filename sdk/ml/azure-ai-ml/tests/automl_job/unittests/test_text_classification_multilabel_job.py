import pytest

from azure.ai.ml.constants import AssetTypes
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    AutoMLJob as RestAutoMLJob,
    JobBaseData,
    LogVerbosity,
    MLTableJobInput,
    NlpVerticalFeaturizationSettings,
    NlpVerticalDataSettings,
    NlpVerticalLimitSettings,
    NlpVerticalValidationDataSettings,
    TextClassificationMultilabel,
    TrainingDataSettings,
    ValidationDataSettings,
    UserIdentity,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models._azure_machine_learning_workspaces_enums import (
    ClassificationPrimaryMetrics,
)
from azure.ai.ml._utils.utils import to_iso_duration_format_mins
from azure.ai.ml.automl import text_classification_multilabel
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.nlp.text_classification_multilabel_job import TextClassificationMultilabelJob


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
        assert job._data.target_column_name == label_column
        assert job._data.training_data.data.path == training_data_uri
        assert job._data.validation_data.data.path == validation_data_uri
        assert job._limits is None
        assert job._featurization is None
        assert job.log_verbosity is None

    def test_automl_nlp_text_classification_multilabel_init(self):
        label_column = "label_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        log_verbosity = "Debug"
        max_concurrent_trials = 2
        timeout = 30
        dataset_language = "deu"
        job = text_classification_multilabel(
            log_verbosity=log_verbosity,
            target_column_name=label_column,
            training_data=Input(type=AssetTypes.MLTABLE, path=training_data_uri),
            validation_data=Input(type=AssetTypes.MLTABLE, path=validation_data_uri),
        )
        job.set_limits(max_concurrent_trials=max_concurrent_trials, timeout_minutes=timeout)
        job.set_featurization(dataset_language=dataset_language)
        assert isinstance(job, TextClassificationMultilabelJob)
        assert job.limits.max_concurrent_trials == max_concurrent_trials
        assert job.limits.timeout_minutes == timeout
        assert job.limits.max_trials == 1  # default value
        assert job.featurization.dataset_language == dataset_language
        assert job.log_verbosity == LogVerbosity.DEBUG.value

    def test_automl_nlp_text_classification_multilabel_init_with_dictionary(self):
        label_column = "label_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        log_verbosity = "Debug"
        max_concurrent_trials = 2
        timeout = 30
        dataset_language = "deu"
        job = text_classification_multilabel(
            log_verbosity=log_verbosity,
            target_column_name=label_column,
            training_data=Input(type=AssetTypes.MLTABLE, path=training_data_uri),
            validation_data=Input(type=AssetTypes.MLTABLE, path=validation_data_uri),
        )
        job.limits = {"timeout_minutes": timeout, "max_concurrent_trials": max_concurrent_trials}
        job.featurization = {"dataset_language": dataset_language}
        assert job.limits.max_concurrent_trials == max_concurrent_trials
        assert job.limits.timeout_minutes == timeout
        assert job.limits.max_trials == 1  # default value
        assert job.featurization.dataset_language == dataset_language
        assert job.log_verbosity == LogVerbosity.DEBUG.value

    def test_automl_nlp_text_classification_multilabel_to_rest_object(self):
        primary_metric = ClassificationPrimaryMetrics.ACCURACY
        log_verbosity = "Debug"
        label_column = "label_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        max_concurrent_trials = 2
        timeout = 30
        dataset_language = "eng"

        identity = UserIdentity()
        job = text_classification_multilabel(
            primary_metric=primary_metric,
            log_verbosity=log_verbosity,
            target_column_name=label_column,
            identity = identity,
            training_data=Input(type=AssetTypes.MLTABLE, path=training_data_uri),
            validation_data=Input(type=AssetTypes.MLTABLE, path=validation_data_uri),
        )
        job.set_limits(max_concurrent_trials=max_concurrent_trials, timeout_minutes=timeout)
        job.set_featurization(dataset_language=dataset_language)

        expected = TextClassificationMultilabel(
            primary_metric=primary_metric,
            log_verbosity=log_verbosity,
            data_settings=NlpVerticalDataSettings(
                target_column_name=label_column,
                training_data=TrainingDataSettings(data=MLTableJobInput(uri=training_data_uri)),
                validation_data=NlpVerticalValidationDataSettings(data=MLTableJobInput(uri=validation_data_uri)),
            ),
            limit_settings=NlpVerticalLimitSettings(
                max_concurrent_trials=max_concurrent_trials, timeout=to_iso_duration_format_mins(timeout)
            ),
            featurization_settings=NlpVerticalFeaturizationSettings(dataset_language=dataset_language),
        )

        # Test converting Job to REST object
        converted_to_rest_obj = job._to_rest_object()
        assert converted_to_rest_obj.properties.identity == identity
        assert isinstance(converted_to_rest_obj, JobBaseData)
        assert converted_to_rest_obj.properties.task_details == expected
        result = converted_to_rest_obj.properties.task_details
        assert result.task_type == "TextClassificationMultilabel"
        assert expected.task_type == result.task_type
        assert expected.primary_metric == result.primary_metric
        assert expected.data_settings == result.data_settings
        assert expected.data_settings.training_data == result.data_settings.training_data
        assert expected.data_settings.validation_data == result.data_settings.validation_data
        assert expected.limit_settings == result.limit_settings
        assert expected.featurization_settings == result.featurization_settings
        assert expected.log_verbosity == result.log_verbosity

    def test_automl_nlp_text_classification_multilabel_from_rest_object(self):
        log_verbosity = "Debug"
        label_column = "target_column"
        training_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Train"
        validation_data_uri = "azureml://datastores/workspaceblobstore/paths/NLPTextClassificationMultilabel/Valid"
        max_concurrent_trials = 2
        timeout = 30
        dataset_language = "eng"

        identity = UserIdentity()
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
            identity = identity,
        )
        expected_job.set_limits(max_concurrent_trials=max_concurrent_trials, timeout_minutes=timeout)
        expected_job.set_featurization(dataset_language=dataset_language)

        task_details = TextClassificationMultilabel(
            log_verbosity=log_verbosity,
            data_settings=NlpVerticalDataSettings(
                target_column_name=label_column,
                training_data=TrainingDataSettings(data=MLTableJobInput(uri=training_data_uri)),
                validation_data=NlpVerticalValidationDataSettings(data=MLTableJobInput(uri=validation_data_uri)),
            ),
            limit_settings=NlpVerticalLimitSettings(
                max_concurrent_trials=max_concurrent_trials, timeout=to_iso_duration_format_mins(timeout)
            ),
            featurization_settings=NlpVerticalFeaturizationSettings(dataset_language=dataset_language),
        )
        job_data = JobBaseData(properties=RestAutoMLJob(task_details=task_details, identity = identity))
        # Test converting REST object to Job
        converted_to_job = TextClassificationMultilabelJob._from_rest_object(job_data)
        assert converted_to_job.identity == identity
        assert isinstance(converted_to_job, TextClassificationMultilabelJob)
        assert expected_job.primary_metric == converted_to_job.primary_metric
        assert expected_job.target_column_name == converted_to_job.target_column_name
        assert expected_job.training_data == converted_to_job.training_data
        assert expected_job.validation_data == converted_to_job.validation_data
        assert expected_job.limits == converted_to_job.limits
        assert expected_job._data == converted_to_job._data
        assert expected_job.featurization == converted_to_job.featurization
        assert expected_job.log_verbosity == converted_to_job.log_verbosity
