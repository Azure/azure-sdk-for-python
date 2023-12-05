# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoints for creating AutoML tasks."""
from typing import List, Optional, Union

from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.tabular import (
    ClassificationJob,
    ForecastingJob,
    ForecastingSettings,
    RegressionJob,
)


@pipeline_node_decorator
def classification(
    *,
    training_data: Input,
    target_column_name: str,
    primary_metric: Optional[str] = None,
    enable_model_explainability: Optional[bool] = None,
    weight_column_name: Optional[str] = None,
    validation_data: Optional[Input] = None,
    validation_data_size: Optional[float] = None,
    n_cross_validations: Optional[Union[str, int]] = None,
    cv_split_column_names: Optional[List[str]] = None,
    test_data: Optional[Input] = None,
    test_data_size: Optional[float] = None,
    **kwargs,
) -> ClassificationJob:
    """Function to create a ClassificationJob.

    A classification job is used to train a model that best predict the class of a data sample.
    Various models are trained using the training data. The model with the best performance on the validation data
    based on the primary metric is selected as the final model.

    :keyword training_data: The training data to be used within the experiment.
            It should contain both training features and a label column (optionally a sample weights column).
    :paramtype training_data: Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data``, ``validation_data`` and ``test_data`` parameters
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: accuracy, AUC_weighted, norm_macro_recall, average_precision_score_weighted,
            and precision_score_weighted
            Defaults to accuracy
    :type primary_metric: str
    :keyword enable_model_explainability: Whether to enable explaining the best AutoML model at the end of all AutoML
            training iterations.
            The default is None. For more information, see
            `Interpretability: model explanations in automated machine learning
            <https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`__.
    :paramtype enable_model_explainability: bool
    :keyword weight_column_name: The name of the sample weight column. Automated ML supports a weighted column
            as an input, causing rows in the data to be weighted up or down.
            If the input data is from a pandas.DataFrame which doesn't have column names,
            column indices can be used instead, expressed as integers.

            This parameter is applicable to ``training_data`` and ``validation_data`` parameters
    :paramtype weight_column_name: str
    :keyword validation_data: The validation data to be used within the experiment.
            It should contain both training features and label column (optionally a sample weights column).

            Defaults to None
    :paramtype validation_data: Input
    :keyword validation_data_size: What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
            ``validation_data_size`` to extract validation data out of the specified training data.
            For custom cross validation fold, use ``cv_split_column_names``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.

            Defaults to None
    :paramtype validation_data_size: float
    :keyword n_cross_validations: How many cross validations to perform when user validation data is not specified.

            Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
            ``validation_data_size`` to extract validation data out of the specified training data.
            For custom cross validation fold, use ``cv_split_column_names``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.

            Defaults to None
    :paramtype n_cross_validations: Union[str, int]
    :keyword cv_split_column_names: List of names of the columns that contain custom cross validation split.
            Each of the CV split columns represents one CV split where each row are either marked
            1 for training or 0 for validation.

            Defaults to None
    :paramtype cv_split_column_names: List[str]
    :keyword test_data: The Model Test feature using test datasets or test data splits is a feature in
            Preview state and might change at any time.
            The test data to be used for a test run that will automatically be started after
            model training is complete. The test run will get predictions using the best model
            and will compute metrics given these predictions.

            If this parameter or the ``test_data_size`` parameter are not specified then
            no test run will be executed automatically after model training is completed.
            Test data should contain both features and label column.
            If ``test_data`` is specified then the ``target_column_name`` parameter must be specified.

            Defaults to None
    :paramtype test_data: Input
    :keyword test_data_size: The Model Test feature using test datasets or test data splits is a feature in
            Preview state and might change at any time.
            What fraction of the training data to hold out for test data for a test run that will
            automatically be started after model training is complete. The test run will get
            predictions using the best model and will compute metrics given these predictions.

            This should be between 0.0 and 1.0 non-inclusive.
            If ``test_data_size`` is specified at the same time as ``validation_data_size``,
            then the test data is split from ``training_data`` before the validation data is split.
            For example, if ``validation_data_size=0.1``, ``test_data_size=0.1`` and the original training data has
            1000 rows, then the test data will have 100 rows, the validation data will contain 90 rows and the
            training data will have 810 rows.

            For regression based tasks, random sampling is used. For classification tasks, stratified sampling
            is used. Forecasting does not currently support specifying a test dataset using a train/test split.

            If this parameter or the ``test_data`` parameter are not specified then
            no test run will be executed automatically after model training is completed.

            Defaults to None
    :paramtype test_data_size: float
    :return: A job object that can be submitted to an Azure ML compute for execution.
    :rtype: ClassificationJob
    """
    classification_job = ClassificationJob(primary_metric=primary_metric, **kwargs)

    classification_job.set_data(
        training_data=training_data,
        target_column_name=target_column_name,
        weight_column_name=weight_column_name,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
        n_cross_validations=n_cross_validations,
        cv_split_column_names=cv_split_column_names,
        test_data=test_data,
        test_data_size=test_data_size,
    )
    classification_job.set_training(enable_model_explainability=enable_model_explainability)

    return classification_job


@pipeline_node_decorator
def regression(
    *,
    training_data: Input,
    target_column_name: str,
    primary_metric: Optional[str] = None,
    enable_model_explainability: Optional[bool] = None,
    weight_column_name: Optional[str] = None,
    validation_data: Optional[Input] = None,
    validation_data_size: Optional[float] = None,
    n_cross_validations: Optional[Union[str, int]] = None,
    cv_split_column_names: Optional[List[str]] = None,
    test_data: Optional[Input] = None,
    test_data_size: Optional[float] = None,
    **kwargs,
) -> RegressionJob:
    """Function to create a Regression Job.

    A regression job is used to train a model to predict continuous values of a target variable from a dataset.
    Various models are trained using the training data. The model with the best performance on the validation data
    based on the primary metric is selected as the final model.


    :keyword training_data: The training data to be used within the experiment.
            It should contain both training features and a label column (optionally a sample weights column).
    :paramtype training_data: Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data``, ``validation_data`` and ``test_data`` parameters
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: spearman_correlation, r2_score, normalized_mean_absolute_error,
            normalized_root_mean_squared_error.
            Defaults to normalized_root_mean_squared_error
    :type primary_metric: str
    :keyword enable_model_explainability: Whether to enable explaining the best AutoML model at the end of all AutoML
            training iterations.
            The default is None. For more information, see
            `Interpretability: model explanations in automated machine learning
            <https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`__.
    :paramtype enable_model_explainability: bool
    :keyword weight_column_name: The name of the sample weight column. Automated ML supports a weighted column
            as an input, causing rows in the data to be weighted up or down.
            If the input data is from a pandas.DataFrame which doesn't have column names,
            column indices can be used instead, expressed as integers.

            This parameter is applicable to ``training_data`` and ``validation_data`` parameters
    :paramtype weight_column_name: str
    :keyword validation_data: The validation data to be used within the experiment.
            It should contain both training features and label column (optionally a sample weights column).

            Defaults to None
    :paramtype validation_data: Input
    :keyword validation_data_size: What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
            ``validation_data_size`` to extract validation data out of the specified training data.
            For custom cross validation fold, use ``cv_split_column_names``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.

            Defaults to None
    :paramtype validation_data_size: float
    :keyword n_cross_validations: How many cross validations to perform when user validation data is not specified.

            Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
            ``validation_data_size`` to extract validation data out of the specified training data.
            For custom cross validation fold, use ``cv_split_column_names``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.

            Defaults to None
    :paramtype n_cross_validations: Union[str, int]
    :keyword cv_split_column_names: List of names of the columns that contain custom cross validation split.
            Each of the CV split columns represents one CV split where each row are either marked
            1 for training or 0 for validation.

            Defaults to None
    :paramtype cv_split_column_names: List[str]
    :keyword test_data: The Model Test feature using test datasets or test data splits is a feature in
            Preview state and might change at any time.
            The test data to be used for a test run that will automatically be started after
            model training is complete. The test run will get predictions using the best model
            and will compute metrics given these predictions.

            If this parameter or the ``test_data_size`` parameter are not specified then
            no test run will be executed automatically after model training is completed.
            Test data should contain both features and label column.
            If ``test_data`` is specified then the ``target_column_name`` parameter must be specified.

            Defaults to None
    :paramtype test_data: Input
    :keyword test_data_size: The Model Test feature using test datasets or test data splits is a feature in
            Preview state and might change at any time.
            What fraction of the training data to hold out for test data for a test run that will
            automatically be started after model training is complete. The test run will get
            predictions using the best model and will compute metrics given these predictions.

            This should be between 0.0 and 1.0 non-inclusive.
            If ``test_data_size`` is specified at the same time as ``validation_data_size``,
            then the test data is split from ``training_data`` before the validation data is split.
            For example, if ``validation_data_size=0.1``, ``test_data_size=0.1`` and the original training data has
            1000 rows, then the test data will have 100 rows, the validation data will contain 90 rows
            and the training data will have 810 rows.

            For regression based tasks, random sampling is used. For classification
            tasks, stratified sampling is used. Forecasting does not currently
            support specifying a test dataset using a train/test split.

            If this parameter or the ``test_data`` parameter are not specified then
            no test run will be executed automatically after model training is completed.

            Defaults to None
    :paramtype test_data_size: float
    :return: A job object that can be submitted to an Azure ML compute for execution.
    :rtype: RegressionJob
    """
    regression_job = RegressionJob(primary_metric=primary_metric, **kwargs)
    regression_job.set_data(
        training_data=training_data,
        target_column_name=target_column_name,
        weight_column_name=weight_column_name,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
        n_cross_validations=n_cross_validations,
        cv_split_column_names=cv_split_column_names,
        test_data=test_data,
        test_data_size=test_data_size,
    )
    regression_job.set_training(enable_model_explainability=enable_model_explainability)

    return regression_job


@pipeline_node_decorator
def forecasting(
    *,
    training_data: Input,
    target_column_name: str,
    primary_metric: Optional[str] = None,
    enable_model_explainability: Optional[bool] = None,
    weight_column_name: Optional[str] = None,
    validation_data: Optional[Input] = None,
    validation_data_size: Optional[float] = None,
    n_cross_validations: Optional[Union[str, int]] = None,
    cv_split_column_names: Optional[List[str]] = None,
    test_data: Optional[Input] = None,
    test_data_size: Optional[float] = None,
    forecasting_settings: Optional[ForecastingSettings] = None,
    **kwargs,
) -> ForecastingJob:
    """Function to create a Forecasting job.

    A forecasting task is used to predict target values for a future time period based on the historical data.
    Various models are trained using the training data. The model with the best performance on the validation data
    based on the primary metric is selected as the final model.

    :keyword training_data: The training data to be used within the experiment.
            It should contain both training features and a label column (optionally a sample weights column).
    :paramtype training_data: Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data``, ``validation_data`` and ``test_data`` parameters
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: r2_score, normalized_mean_absolute_error, normalized_root_mean_squared_error
            Defaults to normalized_root_mean_squared_error
    :type primary_metric: str
    :keyword enable_model_explainability: Whether to enable explaining the best AutoML model at the end of all AutoML
            training iterations.
            The default is None. For more information, see
            `Interpretability: model explanations in automated machine learning
            <https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`__.
    :paramtype enable_model_explainability: bool
    :keyword weight_column_name: The name of the sample weight column. Automated ML supports a weighted column
            as an input, causing rows in the data to be weighted up or down.
            If the input data is from a pandas.DataFrame which doesn't have column names,
            column indices can be used instead, expressed as integers.

            This parameter is applicable to ``training_data`` and ``validation_data`` parameters
    :paramtype weight_column_name: str
    :keyword validation_data: The validation data to be used within the experiment.
            It should contain both training features and label column (optionally a sample weights column).

            Defaults to None
    :paramtype validation_data: Input
    :keyword validation_data_size: What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
            ``validation_data_size`` to extract validation data out of the specified training data.
            For custom cross validation fold, use ``cv_split_column_names``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.

            Defaults to None
    :paramtype validation_data_size: float
    :keyword n_cross_validations: How many cross validations to perform when user validation data is not specified.

            Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
            ``validation_data_size`` to extract validation data out of the specified training data.
            For custom cross validation fold, use ``cv_split_column_names``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.

            Defaults to None
    :paramtype n_cross_validations: Union[str, int]
    :keyword cv_split_column_names: List of names of the columns that contain custom cross validation split.
            Each of the CV split columns represents one CV split where each row are either marked
            1 for training or 0 for validation.

            Defaults to None
    :paramtype cv_split_column_names: List[str]
    :keyword test_data: The Model Test feature using test datasets or test data splits is a feature in
            Preview state and might change at any time.
            The test data to be used for a test run that will automatically be started after
            model training is complete. The test run will get predictions using the best model
            and will compute metrics given these predictions.

            If this parameter or the ``test_data_size`` parameter are not specified then
            no test run will be executed automatically after model training is completed.
            Test data should contain both features and label column.
            If ``test_data`` is specified then the ``target_column_name`` parameter must be specified.

            Defaults to None
    :paramtype test_data: Input
    :keyword test_data_size: The Model Test feature using test datasets or test data splits is a feature in
            Preview state and might change at any time.
            What fraction of the training data to hold out for test data for a test run that will
            automatically be started after model training is complete. The test run will get
            predictions using the best model and will compute metrics given these predictions.

            This should be between 0.0 and 1.0 non-inclusive.
            If ``test_data_size`` is specified at the same time as ``validation_data_size``,
            then the test data is split from ``training_data`` before the validation data is split.
            For example, if ``validation_data_size=0.1``, ``test_data_size=0.1`` and the original training data
            has 1000 rows, then the test data will have 100 rows, the validation data will contain 90 rows
            and the training data will have 810 rows.

            For regression based tasks, random sampling is used. For classification
            tasks, stratified sampling is used. Forecasting does not currently
            support specifying a test dataset using a train/test split.

            If this parameter or the ``test_data`` parameter are not specified then
            no test run will be executed automatically after model training is completed.

            Defaults to None
    :paramtype test_data_size: float
    :keyword forecasting_settings: The settings for the forecasting task
    :paramtype forecasting_settings: ForecastingSettings
    :return: A job object that can be submitted to an Azure ML compute for execution.
    :rtype: ForecastingJob
    """
    forecast_job = ForecastingJob(
        primary_metric=primary_metric,
        forecasting_settings=forecasting_settings,
        **kwargs,
    )
    forecast_job.set_data(
        training_data=training_data,
        target_column_name=target_column_name,
        weight_column_name=weight_column_name,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
        n_cross_validations=n_cross_validations,
        cv_split_column_names=cv_split_column_names,
        test_data=test_data,
        test_data_size=test_data_size,
    )
    forecast_job.set_training(enable_model_explainability=enable_model_explainability)

    return forecast_job
