# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional

from azure.ai.ml._schema._deployment.batch.model_batch_deployment_settings import ModelBatchDeploymentSettingsSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings


@experimental
class ModelBatchDeploymentSettings:
    """Model Batch Deployment Settings entity.

    :param mini_batch_size: Size of the mini-batch passed to each batch invocation, defaults to 10
    :type mini_batch_size: int
    :param instance_count: Number of instances the interfering will run on. Equivalent to resources.instance_count.
    :type instance_count: int
    :param output_action: Indicates how the output will be organized. Possible values include:
     "summary_only", "append_row". Defaults to "append_row"
    :type output_action: str or ~azure.ai.ml.constants._deployment.BatchDeploymentOutputAction
    :param output_file_name: Customized output file name for append_row output action, defaults to "predictions.csv"
    :type output_file_name: str
    :param max_concurrency_per_instance: Indicates maximum number of parallelism per instance, defaults to 1
    :type max_concurrency_per_instance: int
    :param retry_settings: Retry settings for a batch inference operation, defaults to None
    :type retry_settings: BatchRetrySettings
    :param environment_variables: Environment variables that will be set in deployment.
    :type environment_variables: dict
    :param error_threshold: Error threshold, if the error count for the entire input goes above
        this value,
        the batch inference will be aborted. Range is [-1, int.MaxValue]
        -1 value indicates, ignore all failures during batch inference
        For FileDataset count of file failures
        For TabularDataset, this is the count of record failures, defaults to -1
    :type error_threshold: int
    :param logging_level: Logging level for batch inference operation, defaults to "info"
    :type logging_level: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START model_batch_deployment_settings_entity_create]
            :end-before: [END model_batch_deployment_settings_entity_create]
            :language: python
            :dedent: 8
            :caption: Creating a Model Batch Deployment Settings object.
    """

    def __init__(
        self,
        *,
        mini_batch_size: Optional[int],
        instance_count: Optional[int] = None,
        max_concurrency_per_instance: Optional[int] = None,
        output_action: Optional[BatchDeploymentOutputAction] = None,
        output_file_name: Optional[str] = None,
        retry_settings: Optional[BatchRetrySettings] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        error_threshold: Optional[int] = None,
        logging_level: Optional[str] = None,
        # pylint: disable=unused-argument
        **kwargs: Any,
    ):
        self.mini_batch_size = mini_batch_size
        self.instance_count = instance_count
        self.max_concurrency_per_instance = max_concurrency_per_instance
        self.output_action = output_action
        self.output_file_name = output_file_name
        self.retry_settings = retry_settings
        self.environment_variables = environment_variables
        self.error_threshold = error_threshold
        self.logging_level = logging_level

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = ModelBatchDeploymentSettingsSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
