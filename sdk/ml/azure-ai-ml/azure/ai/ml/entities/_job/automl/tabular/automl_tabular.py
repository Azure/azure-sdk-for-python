# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC
from typing import Dict, List, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    LogVerbosity,
    StackEnsembleSettings,
    TableVerticalDataSettings,
    TableVerticalValidationDataSettings,
    TestDataSettings,
    TrainingDataSettings,
    CustomNCrossValidations,
    AutoNCrossValidations,
)
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_vertical import AutoMLVertical
from azure.ai.ml.entities._job.automl.tabular.featurization_settings import (
    ColumnTransformer,
    TabularFeaturizationSettings,
)
from azure.ai.ml.entities._job.automl.tabular.limit_settings import TabularLimitSettings
from azure.ai.ml.entities._job.automl.training_settings import (
    TrainingSettings,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


class AutoMLTabular(AutoMLVertical, ABC):
    def __init__(
        self,
        *,
        task_type: str,
        data: TableVerticalDataSettings = None,
        featurization: TabularFeaturizationSettings = None,
        limits: TabularLimitSettings = None,
        training: TrainingSettings = None,
        **kwargs,
    ) -> None:
        self.log_verbosity = kwargs.pop("log_verbosity", LogVerbosity.INFO)
        super().__init__(task_type, **kwargs)

        self._data = data
        self._featurization = featurization
        self._limits = limits
        self._training = training

    @property
    def log_verbosity(self) -> LogVerbosity:
        return self._log_verbosity

    @log_verbosity.setter
    def log_verbosity(self, value: Union[str, LogVerbosity]):
        self._log_verbosity = None if value is None else LogVerbosity[camel_to_snake(value).upper()]

    @property
    def limits(self) -> TabularLimitSettings:
        return self._limits

    @limits.setter
    def limits(self, value: Union[Dict, TabularLimitSettings]) -> None:
        if isinstance(value, TabularLimitSettings):
            self._limits = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for limit settings."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_limits(**value)

    @property
    def training(self) -> TrainingSettings:
        return self._training

    @training.setter
    def training(self, value: Union[Dict, TrainingSettings]) -> None:
        if isinstance(value, TrainingSettings):
            self._training = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for training settings."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_training(**value)

    @property
    def featurization(self) -> TabularFeaturizationSettings:
        return self._featurization

    @featurization.setter
    def featurization(self, value: Union[Dict, TabularFeaturizationSettings]) -> None:
        if isinstance(value, TabularFeaturizationSettings):
            self._featurization = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a dictionary for featurization settings."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.AUTOML,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self.set_featurization(**value)

    def set_limits(
        self,
        *,
        enable_early_termination: bool = None,
        exit_score: float = None,
        max_concurrent_trials: int = None,
        max_cores_per_trial: int = None,
        max_trials: int = None,
        timeout_minutes: int = None,
        trial_timeout_minutes: int = None,
    ) -> None:
        """Set limits for the job.

        :param enable_early_termination: Whether to enable early termination if the score is not improving in the
        short term. The default is True.

        Early stopping logic:

        * No early stopping for first 20 iterations (landmarks).

        * Early stopping window starts on the 21st iteration and looks for early_stopping_n_iters iterations
            (currently set to 10). This means that the first iteration where stopping can occur is
            the 31st.

        * AutoML still schedules 2 ensemble iterations AFTER early stopping, which might result in
            higher scores.

        * Early stopping is triggered if the absolute value of best score calculated is the same for past
            early_stopping_n_iters iterations, that is, if there is no improvement in score for
            early_stopping_n_iters iterations.
        :type enable_early_termination: bool, optional
        :param exit_score: Target score for experiment. The experiment terminates after this score is reached.
        If not specified (no criteria), the experiment runs until no further progress is made
        on the primary metric. For for more information on exit criteria, see this `article
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#exit-criteria>`_.
        :type exit_score: float, optional
        :param max_concurrent_trials: Represents the maximum number of iterations that would be executed in parallel. The default value
        is 1.

        * AmlCompute clusters support one interation running per node.
          For multiple AutoML experiment parent runs executed in parallel on a single AmlCompute cluster, the
          sum of the ``max_concurrent_trials`` values for all experiments should be less
          than or equal to the maximum number of nodes. Otherwise, runs will be queued until nodes are available.

        * DSVM supports multiple iterations per node. ``max_concurrent_trials`` should
          be less than or equal to the number of cores on the DSVM. For multiple experiments
          run in parallel on a single DSVM, the sum of the ``max_concurrent_trials`` values for all
          experiments should be less than or equal to the maximum number of nodes.

        * Databricks - ``max_concurrent_trials`` should be less than or equal to the number of
          worker nodes on Databricks.

        ``max_concurrent_trials`` does not apply to local runs. Formerly, this parameter
        was named ``concurrent_iterations``.
        :type max_concurrent_trials: int, optional
        :param max_cores_per_trial: The maximum number of threads to use for a given training iteration.
        Acceptable values:

        * Greater than 1 and less than or equal to the maximum number of cores on the compute target.

        * Equal to -1, which means to use all the possible cores per iteration per child-run.

        * Equal to 1, the default.
        :type max_cores_per_trial: int, optional
        :param max_trials: he total number of different algorithm and parameter combinations to test during an
        automated ML experiment. If not specified, the default is 1000 iterations.
        :type max_trials: int, optional
        :param timeout_minutes: Maximum amount of time in minutes that all iterations combined can take before the
        experiment terminates. If not specified, the default experiment timeout is 6 days. To specify a timeout
        less than or equal to 1 hour, make sure your dataset's size is not greater than
        10,000,000 (rows times column) or an error results.
        :type timeout_minutes: int, optional
        :param trial_timeout_minutes: Maximum time in minutes that each iteration can run for before it terminates.
        If not specified, a value of 1 month or 43200 minutes is used.
        :type trial_timeout_minutes: int, optional
        """
        self._limits = self._limits or TabularLimitSettings()
        self._limits.enable_early_termination = (
            enable_early_termination if enable_early_termination is not None else self._limits.enable_early_termination
        )
        self._limits.exit_score = exit_score if exit_score is not None else self._limits.exit_score
        self._limits.max_concurrent_trials = (
            max_concurrent_trials if max_concurrent_trials is not None else self._limits.max_concurrent_trials
        )
        self._limits.max_cores_per_trial = (
            max_cores_per_trial if max_cores_per_trial is not None else self._limits.max_cores_per_trial
        )
        self._limits.max_trials = max_trials if max_trials is not None else self._limits.max_trials
        self._limits.timeout_minutes = timeout_minutes if timeout_minutes is not None else self._limits.timeout_minutes
        self._limits.trial_timeout_minutes = (
            trial_timeout_minutes if trial_timeout_minutes is not None else self._limits.trial_timeout_minutes
        )

    def set_training(
        self,
        *,
        enable_onnx_compatible_models: bool = None,
        enable_dnn_training: bool = None,
        enable_model_explainability: bool = None,
        enable_stack_ensemble: bool = None,
        enable_vote_ensemble: bool = None,
        stack_ensemble_settings: StackEnsembleSettings = None,
        ensemble_model_download_timeout: int = None,
        allowed_training_algorithms: List[str] = None,
        blocked_training_algorithms: List[str] = None,
    ) -> None:
        """Method to configure training related settings.

        :param enable_onnx_compatible_models: Whether to enable or disable enforcing the ONNX-compatible models.
        The default is False. For more information about Open Neural Network Exchange (ONNX) and Azure Machine
        Learning,see this `article <https://docs.microsoft.com/azure/machine-learning/concept-onnx>`__.,
        :type enable_onnx_compatible_models: bool, optional
        :param enable_dnn_training: Whether to include DNN based models during model selection. The default is None.
        However, the default is True for DNN NLP tasks, and it's False for all other AutoML tasks.
        :type enable_dnn_training: bool, optional
        :param enable_model_explainability: Whether to enable explaining the best AutoML model at the end of all
        AutoML training iterations. The default is True. For more information, see
        `Interpretability: model explanations in automated machine learning
        <https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`__.
        :type enable_model_explainability: bool, optional
        :param enable_stack_ensemble: Whether to enable/disable StackEnsemble iteration. The default is None.
        If `enable_onnx_compatible_models` flag is being set, then StackEnsemble iteration will be disabled.
        Similarly, for Timeseries tasks, StackEnsemble iteration will be disabled by default, to avoid risks of
        overfitting due to small training set used in fitting the meta learner.
        For more information about ensembles, see `Ensemble configuration
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`__.
        :type enable_stack_ensemble: bool, optional
        :param enable_vote_ensemble:Whether to enable/disable VotingEnsemble iteration. The default is True.
        For more information about ensembles, see `Ensemble configuration
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`__.
        :type enable_vote_ensemble: bool, optional
        :param stack_ensemble_settings: Settings for StackEnsemble iteration.
        :type stack_ensemble_settings: StackEnsembleSettings, optional
        :param ensemble_model_download_timeout: During VotingEnsemble and StackEnsemble model generation,
        multiple fitted models from the previous child runs are downloaded. Configure this parameter with a
        higher value than 300 secs, if more time is needed.
        :type ensemble_model_download_timeout: int, optional
        :param allowed_training_algorithms: A list of model names to search for an experiment. If not specified, then all models
        supported for the task are used minus any specified in ``blocked_training_algorithms`` or deprecated TensorFlow models.
        :type allowed_training_algorithms: List[str], optional
        :param blocked_training_algorithms: A list of algorithms to ignore for an experiment.
        :type blocked_training_algorithms:List(str)
        or List(azureml.train.automl.ClassificationModels) for classification task,
        or List(azure.ai.ml.automl.RegressionModels) for regression task,
        or List(azure.ai.ml.automl.ForecastingModels) for forecasting task
        """
        # get training object by calling training getter of respective tabular task
        self._training = self.training

        self._training.enable_onnx_compatible_models = (
            enable_onnx_compatible_models
            if enable_onnx_compatible_models is not None
            else self._training.enable_onnx_compatible_models
        )
        self._training.enable_dnn_training = (
            enable_dnn_training if enable_dnn_training is not None else self._training.enable_dnn_training
        )
        self._training.enable_model_explainability = (
            enable_model_explainability
            if enable_model_explainability is not None
            else self._training.enable_model_explainability
        )
        self._training.enable_stack_ensemble = (
            enable_stack_ensemble if enable_stack_ensemble is not None else self._training.enable_stack_ensemble
        )
        self._training.enable_vote_ensemble = (
            enable_vote_ensemble if enable_vote_ensemble is not None else self._training.enable_vote_ensemble
        )
        self._training.stack_ensemble_settings = (
            stack_ensemble_settings if stack_ensemble_settings is not None else self._training.stack_ensemble_settings
        )
        self._training.ensemble_model_download_timeout = (
            ensemble_model_download_timeout
            if ensemble_model_download_timeout is not None
            else self._training.ensemble_model_download_timeout
        )

        self._training.allowed_training_algorithms = allowed_training_algorithms
        self._training.blocked_training_algorithms = blocked_training_algorithms

    def set_featurization(
        self,
        *,
        blocked_transformers: List[str] = None,
        column_name_and_types: Dict[str, str] = None,
        dataset_language: str = None,
        transformer_params: Dict[str, List[ColumnTransformer]] = None,
        mode: str = None,
        enable_dnn_featurization: bool = None,
    ) -> None:
        """Define feature engineering configuration.

        :param blocked_transformers: A list of transformer names to be blocked during featurization
        :type blocked_transformers: List[str], optional
        :param column_name_and_types: A dictionary of column names and feature types used to update column purpose
        :type column_name_and_types: Dict[str, str], optional
        :param dataset_language: hree character ISO 639-3 code for the language(s) contained in the dataset.
        Languages other than English are only supported if you use GPU-enabled compute.  The language_code
        'mul' should be used if the dataset contains multiple languages. To find ISO 639-3 codes for different
        languages, please refer to https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
        :type dataset_language: str, optional
        :param transformer_params: A dictionary of transformer and corresponding customization parameters
        :type transformer_params: Dict[str, List[ColumnTransformer]], optional
        :param mode: "off", "auto", defeaults to "auto"
        :type mode: str, optional
        :param enable_dnn_featurization: Whether to include DNN based feature engineering methods
        :type enable_dnn_featurization: bool, optional
        """
        self._featurization = self._featurization or TabularFeaturizationSettings()
        self._featurization.blocked_transformers = (
            blocked_transformers if blocked_transformers is not None else self._featurization.blocked_transformers
        )
        self._featurization.column_name_and_types = (
            column_name_and_types if column_name_and_types is not None else self._featurization.column_name_and_types
        )
        self._featurization.dataset_language = (
            dataset_language if dataset_language is not None else self._featurization.dataset_language
        )
        self._featurization.transformer_params = (
            transformer_params if transformer_params is not None else self._featurization.transformer_params
        )
        self._featurization.mode = mode or self._featurization.mode
        self._featurization.enable_dnn_featurization = (
            enable_dnn_featurization
            if enable_dnn_featurization is not None
            else self._featurization.enable_dnn_featurization
        )

    def set_data(
        self,
        *,
        training_data: Input,
        target_column_name: str,
        weight_column_name: str = None,
        validation_data: Input = None,
        validation_data_size: float = None,
        n_cross_validations: Union[str, int] = None,
        cv_split_column_names: List[str] = None,
        test_data: Input = None,
        test_data_size: float = None,
    ) -> None:
        self._data = TableVerticalDataSettings(
            target_column_name=target_column_name,
            training_data=TrainingDataSettings(data=training_data),
        )

        self._data.weight_column_name = (
            weight_column_name if weight_column_name is not None else self._data.weight_column_name
        )

        self._data.validation_data = self._data.validation_data or TableVerticalValidationDataSettings()
        self._data.validation_data.data = validation_data or self._data.validation_data.data
        self._data.validation_data.validation_data_size = (
            validation_data_size
            if validation_data_size is not None
            else self._data.validation_data.validation_data_size
        )
        self._data.validation_data.n_cross_validations = (
            n_cross_validations if n_cross_validations is not None else self._data.validation_data.n_cross_validations
        )
        self._data.validation_data.cv_split_column_names = (
            cv_split_column_names
            if cv_split_column_names is not None
            else self._data.validation_data.cv_split_column_names
        )

        self._data.test_data = self._data.test_data or TestDataSettings()
        self._data.test_data.data = test_data if test_data is not None else self._data.test_data.data
        self._data.test_data.test_data_size = (
            test_data_size if test_data_size is not None else self._data.test_data.test_data_size
        )

    def _training_settings_from_rest(self, allowed_training_algorithms, blocked_training_algorithms):
        if not self._training:
            return
        self._training.allowed_training_algorithms = allowed_training_algorithms
        self._training.blocked_training_algorithms = blocked_training_algorithms

    def _validation_data_to_rest(self):
        """validation data serialization"""
        validation_data = self._data.validation_data
        if validation_data and validation_data.n_cross_validations:
            n_cross_val = self._data.validation_data.n_cross_validations
            # Convert n_cross_validations int value to CustomNCrossValidations
            if isinstance(n_cross_val, int) and n_cross_val > 1:
                self._data.validation_data.n_cross_validations = CustomNCrossValidations(value=n_cross_val)
            # Convert n_cross_validations str value to AutoNCrossValidations
            elif isinstance(n_cross_val, str):
                self._data.validation_data.n_cross_validations = AutoNCrossValidations()

    def _validation_data_from_rest(self):
        """validation data deserialization"""
        validation_data = self._data.validation_data
        if validation_data and validation_data.n_cross_validations:
            n_cross_val = self._data.validation_data.n_cross_validations
            # Convert n_cross_validations CustomNCrossValidations back into int value
            if isinstance(n_cross_val, CustomNCrossValidations):
                self._data.validation_data.n_cross_validations = n_cross_val.value
            # Convert n_cross_validations AutoNCrossValidations to str value
            elif isinstance(n_cross_val, AutoNCrossValidations):
                self._data.validation_data.n_cross_validations = AutoMLConstants.AUTO

    def __eq__(self, other):
        if not isinstance(other, AutoMLTabular):
            return NotImplemented

        return (
            self._data == other._data
            and self._featurization == other._featurization
            and self._limits == other._limits
            and self._training == other._training
        )

    def __ne__(self, other):
        return not self.__eq__(other)
