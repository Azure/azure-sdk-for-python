# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml._schema._deployment.batch.model_batch_deployment_settings import ModelBatchDeploymentSettingsSchema


class ModelBatchDeploymentSettings:
    """Job Definition entity.

    :param type: Job definition type. Allowed value is: pipeline
    :type type: str
    :param name: Job name
    :type name: str
    :param job: Job definition
    :type job: Union[Job, str]
    :param component: Component definition
    :type component: Union[Component, str]
    :param settings: Job settings
    :type settings: Dict[str, Any]
    :param description: Job description.
    :type description: str
    :param tags: Job tags
    :type tags: Dict[str, Any]
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
        **kwargs,  # pylint: disable=unused-argument
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
    return ModelBatchDeploymentSettingsSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
