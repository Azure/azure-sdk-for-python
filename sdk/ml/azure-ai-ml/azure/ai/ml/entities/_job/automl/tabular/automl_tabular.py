# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from abc import ABC
from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    AutoNCrossValidations,
    BlockedTransformers,
    CustomNCrossValidations,
    LogVerbosity,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import TabularTrainingMode
from azure.ai.ml.constants._job.automl import AutoMLConstants
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.automl_vertical import AutoMLVertical
from azure.ai.ml.entities._job.automl.stack_ensemble_settings import StackEnsembleSettings
from azure.ai.ml.entities._job.automl.tabular.featurization_settings import (
    ColumnTransformer,
    TabularFeaturizationSettings,
)
from azure.ai.ml.entities._job.automl.tabular.limit_settings import TabularLimitSettings
from azure.ai.ml.entities._job.automl.training_settings import TrainingSettings
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class AutoMLTabular(AutoMLVertical, ABC):
    """Initialize an AutoML job entity for tabular data.

    Constructor for AutoMLTabular.

    :keyword task_type: The type of task to run. Possible values include: "classification", "regression"
        , "forecasting".
    :paramtype task_type: str
    :keyword featurization: featurization settings. Defaults to None.
    :paramtype featurization: typing.Optional[TabularFeaturizationSettings]
    :keyword limits: limits settings. Defaults to None.
    :paramtype limits: typing.Optional[TabularLimitSettings]
    :keyword training: training settings. Defaults to None.
    :paramtype training: typing.Optional[TrainingSettings]
    :keyword log_verbosity: Verbosity of logging. Possible values include: "debug", "info", "warning", "error",
        "critical". Defaults to "info".
    :paramtype log_verbosity: str
    :keyword target_column_name: The name of the target column. Defaults to None.
    :paramtype target_column_name: typing.Optional[str]
    :keyword weight_column_name: The name of the weight column. Defaults to None.
    :paramtype weight_column_name: typing.Optional[str]
    :keyword validation_data_size: The size of the validation data. Defaults to None.
    :paramtype validation_data_size: typing.Optional[float]
    :keyword cv_split_column_names: The names of the columns to use for cross validation. Defaults to None.
    :paramtype cv_split_column_names: typing.Optional[List[str]]
    :keyword n_cross_validations: The number of cross validations to run. Defaults to None.
    :paramtype n_cross_validations: typing.Optional[int]
    :keyword test_data_size: The size of the test data. Defaults to None.
    :paramtype test_data_size: typing.Optional[float]
    :keyword training_data: The training data. Defaults to None.
    :paramtype training_data: typing.Optional[azure.ai.ml.entities._inputs_outputs.Input]
    :keyword validation_data: The validation data. Defaults to None.
    :paramtype validation_data: typing.Optional[azure.ai.ml.entities._inputs_outputs.Input]
    :keyword test_data: The test data. Defaults to None.
    :paramtype test_data: typing.Optional[azure.ai.ml.entities._inputs_outputs.Input]
    """

    def __init__(
        self,
        *,
        task_type: str,
        featurization: Optional[TabularFeaturizationSettings] = None,
        limits: Optional[TabularLimitSettings] = None,
        training: Optional[TrainingSettings] = None,
        **kwargs,
    ) -> None:
        """Initialize an AutoML job entity for tabular data.

        Constructor for AutoMLTabular.

        :keyword task_type: The type of task to run. Possible values include: "classification", "regression"
            , "forecasting".
        :paramtype task_type: str
        :keyword featurization: featurization settings. Defaults to None.
        :paramtype featurization: typing.Optional[TabularFeaturizationSettings]
        :keyword limits: limits settings. Defaults to None.
        :paramtype limits: typing.Optional[TabularLimitSettings]
        :keyword training: training settings. Defaults to None.
        :paramtype training: typing.Optional[TrainingSettings]
        :keyword log_verbosity: Verbosity of logging. Possible values include: "debug", "info", "warning", "error",
            "critical". Defaults to "info".
        :paramtype log_verbosity: str
        :keyword target_column_name: The name of the target column. Defaults to None.
        :paramtype target_column_name: typing.Optional[str]
        :keyword weight_column_name: The name of the weight column. Defaults to None.
        :paramtype weight_column_name: typing.Optional[str]
        :keyword validation_data_size: The size of the validation data. Defaults to None.
        :paramtype validation_data_size: typing.Optional[float]
        :keyword cv_split_column_names: The names of the columns to use for cross validation. Defaults to None.
        :paramtype cv_split_column_names: typing.Optional[List[str]]
        :keyword n_cross_validations: The number of cross validations to run. Defaults to None.
        :paramtype n_cross_validations: typing.Optional[int]
        :keyword test_data_size: The size of the test data. Defaults to None.
        :paramtype test_data_size: typing.Optional[float]
        :keyword training_data: The training data. Defaults to None.
        :paramtype training_data: typing.Optional[azure.ai.ml.entities._inputs_outputs.Input]
        :keyword validation_data: The validation data. Defaults to None.
        :paramtype validation_data: typing.Optional[azure.ai.ml.entities._inputs_outputs.Input]
        :keyword test_data: The test data. Defaults to None.
        :paramtype test_data: typing.Optional[azure.ai.ml.entities._inputs_outputs.Input]
        :raises: :class:`azure.ai.ml.exceptions.ValidationException`
        """
        self.log_verbosity = kwargs.pop("log_verbosity", LogVerbosity.INFO)

        self.target_column_name = kwargs.pop("target_column_name", None)
        self.weight_column_name = kwargs.pop("weight_column_name", None)
        self.validation_data_size = kwargs.pop("validation_data_size", None)
        self.cv_split_column_names = kwargs.pop("cv_split_column_names", None)
        self.n_cross_validations = kwargs.pop("n_cross_validations", None)
        self.test_data_size = kwargs.pop("test_data_size", None)

        super().__init__(
            task_type=task_type,
            training_data=kwargs.pop("training_data", None),
            validation_data=kwargs.pop("validation_data", None),
            test_data=kwargs.pop("test_data", None),
            **kwargs,
        )

        self._featurization = featurization
        self._limits = limits
        self._training = training

    @property
    def log_verbosity(self) -> LogVerbosity:
        """Get the log verbosity for the AutoML job.

        :return: log verbosity for the AutoML job
        :rtype: LogVerbosity
        """
        return self._log_verbosity

    @log_verbosity.setter
    def log_verbosity(self, value: Union[str, LogVerbosity]):
        """Set the log verbosity for the AutoML job.

        :param value: str or LogVerbosity
        :type value: typing.Union[str, LogVerbosity]
        """
        self._log_verbosity = None if value is None else LogVerbosity[camel_to_snake(value).upper()]

    @property
    def limits(self) -> TabularLimitSettings:
        """Get the tabular limits for the AutoML job.

        :return: Tabular limits for the AutoML job
        :rtype: TabularLimitSettings
        """
        return self._limits

    @limits.setter
    def limits(self, value: Union[Dict, TabularLimitSettings]) -> None:
        """Set the limits for the AutoML job.

        :param value: typing.Dict or TabularLimitSettings
        :type value: typing.Union[typing.Dict, TabularLimitSettings]
        :raises ValidationException: Expected a dictionary for limit settings.
        """
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
        """Get the training settings for the AutoML job.

        :return: Training settings for the AutoML job.
        :rtype: TrainingSettings
        """
        return self._training

    @training.setter
    def training(self, value: Union[Dict, TrainingSettings]) -> None:
        """Set the training settings for the AutoML job.

        :param value: typing.Dict or TrainingSettings
        :type value: typing.Union[typing.Dict, TrainingSettings]
        :raises ValidationException: Expected a dictionary for training settings.
        """
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
        """Get the tabular featurization settings for the AutoML job.

        :return: Tabular featurization settings for the AutoML job
        :rtype: TabularFeaturizationSettings
        """
        return self._featurization

    @featurization.setter
    def featurization(self, value: Union[Dict, TabularFeaturizationSettings]) -> None:
        """Set the featurization settings for the AutoML job.

        :param value: typing.Dict or TabularFeaturizationSettings
        :type value: typing.Union[typing.Dict, TabularFeaturizationSettings]
        :raises ValidationException: Expected a dictionary for featurization settings
        """
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
        enable_early_termination: Optional[bool] = None,
        exit_score: Optional[float] = None,
        max_concurrent_trials: Optional[int] = None,
        max_cores_per_trial: Optional[int] = None,
        max_nodes: Optional[int] = None,
        max_trials: Optional[int] = None,
        timeout_minutes: Optional[int] = None,
        trial_timeout_minutes: Optional[int] = None,
    ) -> None:
        """Set limits for the job.

        :keyword enable_early_termination: Whether to enable early termination if the score is not improving in the
            short term, defaults to None.

            Early stopping logic:

            * No early stopping for first 20 iterations (landmarks).

            * Early stopping window starts on the 21st iteration and looks for early_stopping_n_iters iterations
                (currently set to 10). This means that the first iteration where stopping can occur is the 31st.

            * AutoML still schedules 2 ensemble iterations AFTER early stopping, which might result in higher scores.

            * Early stopping is triggered if the absolute value of best score calculated is the same for past
                early_stopping_n_iters iterations, that is, if there is no improvement in score for
                early_stopping_n_iters iterations.
        :paramtype enable_early_termination: typing.Optional[bool]
        :keyword exit_score: Target score for experiment. The experiment terminates after this score is reached.
            If not specified (no criteria), the experiment runs until no further progress is made
            on the primary metric. For for more information on exit criteria, see this `article
            <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#exit-criteria>`_
            , defaults to None
        :paramtype exit_score: typing.Optional[float]
        :keyword max_concurrent_trials: This is the maximum number of iterations that would be executed in parallel.
            The default value is 1.

            * AmlCompute clusters support one iteration running per node.
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
        :paramtype max_concurrent_trials: typing.Optional[int]
        :keyword max_cores_per_trial: The maximum number of threads to use for a given training iteration.
            Acceptable values:

            * Greater than 1 and less than or equal to the maximum number of cores on the compute target.

            * Equal to -1, which means to use all the possible cores per iteration per child-run.

            * Equal to 1, the default.
        :paramtype max_cores_per_trial: typing.Optional[int]
        :keyword max_nodes: [Experimental] The maximum number of nodes to use for distributed training.

            * For forecasting, each model is trained using max(2, int(max_nodes / max_concurrent_trials)) nodes.

            * For classification/regression, each model is trained using max_nodes nodes.

            Note- This parameter is in public preview and might change in future.
        :paramtype max_nodes: typing.Optional[int]
        :keyword max_trials: The total number of different algorithm and parameter combinations to test during an
            automated ML experiment. If not specified, the default is 1000 iterations.
        :paramtype max_trials: typing.Optional[int]
        :keyword timeout_minutes:  Maximum amount of time in minutes that all iterations combined can take before the
            experiment terminates. If not specified, the default experiment timeout is 6 days. To specify a timeout
            less than or equal to 1 hour, make sure your dataset's size is not greater than
            10,000,000 (rows times column) or an error results, defaults to None
        :paramtype timeout_minutes: typing.Optional[int]
        :keyword trial_timeout_minutes: Maximum time in minutes that each iteration can run for before it terminates.
            If not specified, a value of 1 month or 43200 minutes is used, defaults to None
        :paramtype trial_timeout_minutes: typing.Optional[int]
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
        self._limits.max_nodes = max_nodes if max_nodes is not None else self._limits.max_nodes
        self._limits.max_trials = max_trials if max_trials is not None else self._limits.max_trials
        self._limits.timeout_minutes = timeout_minutes if timeout_minutes is not None else self._limits.timeout_minutes
        self._limits.trial_timeout_minutes = (
            trial_timeout_minutes if trial_timeout_minutes is not None else self._limits.trial_timeout_minutes
        )

    def set_training(
        self,
        *,
        enable_onnx_compatible_models: Optional[bool] = None,
        enable_dnn_training: Optional[bool] = None,
        enable_model_explainability: Optional[bool] = None,
        enable_stack_ensemble: Optional[bool] = None,
        enable_vote_ensemble: Optional[bool] = None,
        stack_ensemble_settings: Optional[StackEnsembleSettings] = None,
        ensemble_model_download_timeout: Optional[int] = None,
        allowed_training_algorithms: Optional[List[str]] = None,
        blocked_training_algorithms: Optional[List[str]] = None,
        training_mode: Optional[Union[str, TabularTrainingMode]] = None,
    ) -> None:
        """The method to configure training related settings.

        :keyword enable_onnx_compatible_models: Whether to enable or disable enforcing the ONNX-compatible models.
            The default is False. For more information about Open Neural Network Exchange (ONNX) and Azure Machine
            Learning,see this `article <https://docs.microsoft.com/azure/machine-learning/concept-onnx>`__.
        :paramtype enable_onnx_compatible_models: typing.Optional[bool]
        :keyword enable_dnn_training: Whether to include DNN based models during model selection.
            However, the default is True for DNN NLP tasks, and it's False for all other AutoML tasks.
        :paramtype enable_dnn_training: typing.Optional[bool]
        :keyword enable_model_explainability: Whether to enable explaining the best AutoML model at the end of all
            AutoML training iterations. For more information, see
            `Interpretability: model explanations in automated machine learning
            <https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`__.
            , defaults to None
        :paramtype enable_model_explainability: typing.Optional[bool]
        :keyword enable_stack_ensemble: Whether to enable/disable StackEnsemble iteration.
            If `enable_onnx_compatible_models` flag is being set, then StackEnsemble iteration will be disabled.
            Similarly, for Timeseries tasks, StackEnsemble iteration will be disabled by default, to avoid risks of
            overfitting due to small training set used in fitting the meta learner.
            For more information about ensembles, see `Ensemble configuration
            <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`__
            , defaults to None
        :paramtype enable_stack_ensemble: typing.Optional[bool]
        :keyword enable_vote_ensemble: Whether to enable/disable VotingEnsemble iteration.
            For more information about ensembles, see `Ensemble configuration
            <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`__
            , defaults to None
        :paramtype enable_vote_ensemble: typing.Optional[bool]
        :keyword stack_ensemble_settings: Settings for StackEnsemble iteration, defaults to None
        :paramtype stack_ensemble_settings: typing.Optional[StackEnsembleSettings]
        :keyword ensemble_model_download_timeout: During VotingEnsemble and StackEnsemble model generation,
            multiple fitted models from the previous child runs are downloaded. Configure this parameter with a
            higher value than 300 secs, if more time is needed, defaults to None
        :paramtype ensemble_model_download_timeout: typing.Optional[int]
        :keyword allowed_training_algorithms: A list of model names to search for an experiment. If not specified,
            then all models supported for the task are used minus any specified in ``blocked_training_algorithms``
            or deprecated TensorFlow models, defaults to None
        :paramtype allowed_training_algorithms: typing.Optional[List[str]]
        :keyword blocked_training_algorithms: A list of algorithms to ignore for an experiment, defaults to None
        :paramtype blocked_training_algorithms: typing.Optional[List[str]]
        :keyword training_mode: [Experimental] The training mode to use.
            The possible values are-

            * distributed- enables distributed training for supported algorithms.

            * non_distributed- disables distributed training.

            * auto- Currently, it is same as non_distributed. In future, this might change.

            Note: This parameter is in public preview and may change in future.
        :paramtype training_mode: typing.Optional[typing.Union[str, azure.ai.ml.constants.TabularTrainingMode]]
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
        self._training.training_mode = training_mode if training_mode is not None else self._training.training_mode

    def set_featurization(
        self,
        *,
        blocked_transformers: Optional[List[Union[BlockedTransformers, str]]] = None,
        column_name_and_types: Optional[Dict[str, str]] = None,
        dataset_language: Optional[str] = None,
        transformer_params: Optional[Dict[str, List[ColumnTransformer]]] = None,
        mode: Optional[str] = None,
        enable_dnn_featurization: Optional[bool] = None,
    ) -> None:
        """Define feature engineering configuration.

        :keyword blocked_transformers: A list of transformer names to be blocked during featurization, defaults to None
        :paramtype blocked_transformers: Optional[List[Union[BlockedTransformers, str]]]
        :keyword column_name_and_types: A dictionary of column names and feature types used to update column purpose
            , defaults to None
        :paramtype column_name_and_types: Optional[Dict[str, str]]
        :keyword dataset_language: Three character ISO 639-3 code for the language(s) contained in the dataset.
            Languages other than English are only supported if you use GPU-enabled compute.  The language_code
            'mul' should be used if the dataset contains multiple languages. To find ISO 639-3 codes for different
            languages, please refer to https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes, defaults to None
        :paramtype dataset_language: Optional[str]
        :keyword transformer_params: A dictionary of transformer and corresponding customization parameters
            , defaults to None
        :paramtype transformer_params: Optional[Dict[str, List[ColumnTransformer]]]
        :keyword mode: "off", "auto", defaults to "auto", defaults to None
        :paramtype mode: Optional[str]
        :keyword enable_dnn_featurization: Whether to include DNN based feature engineering methods, defaults to None
        :paramtype enable_dnn_featurization: Optional[bool]
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
        weight_column_name: Optional[str] = None,
        validation_data: Optional[Input] = None,
        validation_data_size: Optional[float] = None,
        n_cross_validations: Optional[Union[str, int]] = None,
        cv_split_column_names: Optional[List[str]] = None,
        test_data: Optional[Input] = None,
        test_data_size: Optional[float] = None,
    ) -> None:
        """Define data configuration.

        :keyword training_data: Training data.
        :paramtype training_data: Input
        :keyword target_column_name: Column name of the target column.
        :paramtype target_column_name: str
        :keyword weight_column_name: Weight column name, defaults to None
        :paramtype weight_column_name: typing.Optional[str]
        :keyword validation_data: Validation data, defaults to None
        :paramtype validation_data: typing.Optional[Input]
        :keyword validation_data_size: Validation data size, defaults to None
        :paramtype validation_data_size: typing.Optional[float]
        :keyword n_cross_validations: n_cross_validations, defaults to None
        :paramtype n_cross_validations: typing.Optional[typing.Union[str, int]]
        :keyword cv_split_column_names: cv_split_column_names, defaults to None
        :paramtype cv_split_column_names: typing.Optional[typing.List[str]]
        :keyword test_data: Test data, defaults to None
        :paramtype test_data: typing.Optional[Input]
        :keyword test_data_size: Test data size, defaults to None
        :paramtype test_data_size: typing.Optional[float]
        """
        self.target_column_name = target_column_name if target_column_name is not None else self.target_column_name
        self.weight_column_name = weight_column_name if weight_column_name is not None else self.weight_column_name
        self.training_data = training_data if training_data is not None else self.training_data
        self.validation_data = validation_data if validation_data is not None else self.validation_data
        self.validation_data_size = (
            validation_data_size if validation_data_size is not None else self.validation_data_size
        )
        self.cv_split_column_names = (
            cv_split_column_names if cv_split_column_names is not None else self.cv_split_column_names
        )
        self.n_cross_validations = n_cross_validations if n_cross_validations is not None else self.n_cross_validations
        self.test_data = test_data if test_data is not None else self.test_data
        self.test_data_size = test_data_size if test_data_size is not None else self.test_data_size

    # pylint: disable=no-self-use
    def _validation_data_to_rest(self, rest_obj):
        """Validation data serialization.

        :param rest_obj: Serialized object
        :type rest_obj: AutoMLTabular
        """
        if rest_obj.n_cross_validations:
            n_cross_val = rest_obj.n_cross_validations
            # Convert n_cross_validations int value to CustomNCrossValidations
            if isinstance(n_cross_val, int) and n_cross_val > 1:
                rest_obj.n_cross_validations = CustomNCrossValidations(value=n_cross_val)
            # Convert n_cross_validations str value to AutoNCrossValidations
            elif isinstance(n_cross_val, str):
                rest_obj.n_cross_validations = AutoNCrossValidations()

    def _validation_data_from_rest(self):
        """Validation data deserialization."""
        if self.n_cross_validations:
            n_cross_val = self.n_cross_validations
            # Convert n_cross_validations CustomNCrossValidations back into int value
            if isinstance(n_cross_val, CustomNCrossValidations):
                self.n_cross_validations = n_cross_val.value
            # Convert n_cross_validations AutoNCrossValidations to str value
            elif isinstance(n_cross_val, AutoNCrossValidations):
                self.n_cross_validations = AutoMLConstants.AUTO

    def __eq__(self, other):
        """Return True if both instances have the same values.

        This method check instances equality and returns True if both of
            the instances have the same attributes with the same values.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        if not isinstance(other, AutoMLTabular):
            return NotImplemented

        return (
            self.target_column_name == other.target_column_name
            and self.weight_column_name == other.weight_column_name
            and self.training_data == other.training_data
            and self.validation_data == other.validation_data
            and self.validation_data_size == other.validation_data_size
            and self.cv_split_column_names == other.cv_split_column_names
            and self.n_cross_validations == other.n_cross_validations
            and self.test_data == other.test_data
            and self.test_data_size == other.test_data_size
            and self._featurization == other._featurization
            and self._limits == other._limits
            and self._training == other._training
        )

    def __ne__(self, other):
        """Check inequality between two AutoMLTabular objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)
