# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_05_01.models import BatchDeploymentData
from azure.ai.ml._restclient.v2022_05_01.models import BatchDeploymentDetails as RestBatchDeployment
from azure.ai.ml._restclient.v2022_05_01.models import CodeConfiguration as RestCodeConfiguration
from azure.ai.ml._restclient.v2022_05_01.models import IdAssetReference
from azure.ai.ml.entities._assets import Environment, Model
from azure.ai.ml.entities import BatchDeployment
from .code_configuration import CodeConfiguration
from .model_deployment_settings import ModelDeploymentSettings
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class ModelBatchDeployment(BatchDeployment):
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
        name: Optional[str],
        endpoint_name: Optional[str] = None,
        environment: Optional[Union[str, Environment]] = None,
        model: Optional[Union[str, Model]] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        code_configuration: Optional[CodeConfiguration] = None,
        model_deployment_settings: Optional[ModelDeploymentSettings] = None,
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
        super().__init__(
            name=name,
            endpoint_name=endpoint_name,
            environment=environment,
            model=model,
            code_configuration=code_configuration,
            description=description,
            tags=tags,
            **kwargs
        )
        self.model_deployment_settings = ModelDeploymentSettings(
            mini_batch_size=mini_batch_size,
            instance_count = instance_count,
            max_concurrency_per_instance = max_concurrency_per_instance,
            output_action = output_action,
            output_file_name = output_file_name,
            retry_settings = retry_settings,
            environment_variables = environment_variables,
            error_threshold = error_threshold,
            logging_level = logging_level

        )
    
        
    def _to_rest_object(self, location: str) -> BatchDeploymentData: # pylint: disable=arguments-differ
        self._validate()
        code_config = (
            RestCodeConfiguration(
                code_id=self.code_configuration.code,
                scoring_script=self.code_configuration.scoring_script,
            )
            if self.code_configuration
            else None
        )
        deployment_settings = self.model_deployment_settings
        model = IdAssetReference(asset_id=self.model) if self.model else None
        batch_deployment = RestBatchDeployment(
            description=self.description,
            code_configuration=code_config,
            environment_id=self.environment,
            model=model,
            output_file_name=deployment_settings.output_file_name,
            output_action=BatchDeployment._yaml_output_action_to_rest_output_action(deployment_settings.output_action),
            error_threshold=deployment_settings.error_threshold,
            retry_settings=deployment_settings.retry_settings._to_rest_object() if deployment_settings.retry_settings else None,
            logging_level=deployment_settings.logging_level,
            mini_batch_size=deployment_settings.mini_batch_size,
            max_concurrency_per_instance=deployment_settings.max_concurrency_per_instance,
            environment_variables=deployment_settings.environment_variables,
        )
        return BatchDeploymentData(location=location, properties=batch_deployment, tags=self.tags)

    def _validate(self) -> None:
        self._validate_output_action()

    def _validate_output_action(self) -> None:
        if (
            self.model_deployment_settings.output_action
            and self.model_deployment_settings.output_action == BatchDeploymentOutputAction.SUMMARY_ONLY
            and self.model_deployment_settings.output_file_name
        ):
            msg = "When output_action is set to {}, the output_file_name need not to be specified."
            msg = msg.format(BatchDeploymentOutputAction.SUMMARY_ONLY)
            raise ValidationException(
                message=msg,
                target=ErrorTarget.BATCH_DEPLOYMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
    

