# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_05_01.models import BatchDeploymentData
from azure.ai.ml._restclient.v2022_05_01.models import BatchDeploymentDetails as RestBatchDeployment
from azure.ai.ml._restclient.v2022_05_01.models import BatchOutputAction
from azure.ai.ml._restclient.v2022_05_01.models import CodeConfiguration as RestCodeConfiguration
from azure.ai.ml._restclient.v2022_05_01.models import IdAssetReference
from azure.ai.ml._schema._deployment.batch.batch_deployment import BatchDeploymentSchema
from azure.ai.ml._utils._arm_id_utils import _parse_endpoint_name_from_deployment_id
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.constants._deployment import BatchDeploymentOutputAction
from azure.ai.ml.entities._assets import Environment, Model
from azure.ai.ml.entities._deployment.deployment_settings import BatchRetrySettings
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .code_configuration import CodeConfiguration
from .deployment import Deployment

module_logger = logging.getLogger(__name__)


class BatchDeployment(Deployment):  # pylint: disable=too-many-instance-attributes
    """Batch endpoint deployment entity.

    :param name: the name of the batch deployment
    :type name: str
    :param description: Description of the resource.
    :type description: str, optional
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param model: Model entity for the endpoint deployment, defaults to None
    :type model: Union[str, Model], optional
    :param code_configuration: defaults to None
    :type code_configuration: CodeConfiguration, optional
    :param environment: Environment entity for the endpoint deployment., defaults to None
    :type environment: Union[str, Environment], optional
    :param compute: Compute target for batch inference operation.
    :type compute: str
    :param output_action: Indicates how the output will be organized. Possible values include:
     "summary_only", "append_row". Defaults to "append_row"
    :type output_action: str or ~azure.ai.ml.constants._deployment.BatchDeploymentOutputAction
    :param output_file_name: Customized output file name for append_row output action, defaults to "predictions.csv"
    :type output_file_name: str
    :param max_concurrency_per_instance: Indicates maximum number of parallelism per instance, defaults to 1
    :type max_concurrency_per_instance: int
    :param error_threshold: Error threshold, if the error count for the entire input goes above
        this value,
        the batch inference will be aborted. Range is [-1, int.MaxValue]
        -1 value indicates, ignore all failures during batch inference
        For FileDataset count of file failures
        For TabularDataset, this is the count of record failures, defaults to -1
    :type error_threshold: int, optional
    :param retry_settings: Retry settings for a batch inference operation, defaults to None
    :type retry_settings: BatchRetrySettings, optional
    :param resources: Indicates compute configuration for the job.
    :type resources: ~azure.mgmt.machinelearningservices.models.ResourceConfiguration
    :param logging_level: Logging level for batch inference operation, defaults to "info"
    :type logging_level: str, optional
    :param mini_batch_size: Size of the mini-batch passed to each batch invocation, defaults to 10
    :type mini_batch_size: int, optional
    :param environment_variables: Environment variables that will be set in deployment.
    :type environment_variables: dict, optional
    :param code_path: Folder path to local code assets. Equivalent to code_configuration.code.
    :type code_path: Union[str, PathLike], optional
    :param scoring_script: Scoring script name. Equivalent to code_configuration.code.scoring_script.
    :type scoring_script: Union[str, PathLike], optional
    :param instance_count: Number of instances the interfering will run on. Equivalent to resources.instance_count.
    :type instance_count: int, optional
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if BatchDeployment cannot be successfully validated.
        Details will be provided in the error message.
    """

    def __init__(
        self,
        *,
        name: str,
        endpoint_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, str]] = None,
        model: Optional[Union[str, Model]] = None,
        code_configuration: Optional[CodeConfiguration] = None,
        environment: Optional[Union[str, Environment]] = None,
        compute: Optional[str] = None,
        resources: Optional[ResourceConfiguration] = None,
        output_file_name: Optional[str] = None,
        output_action: Optional[BatchDeploymentOutputAction] = None,
        error_threshold: Optional[int] = None,
        retry_settings: Optional[BatchRetrySettings] = None,
        logging_level: Optional[str] = None,
        mini_batch_size: Optional[int] = None,
        max_concurrency_per_instance: Optional[int] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        code_path: Optional[Union[str, PathLike]] = None,  # promoted property from code_configuration.code
        scoring_script: Optional[
            Union[str, PathLike]
        ] = None,  # promoted property from code_configuration.scoring_script
        instance_count: Optional[int] = None,  # promoted property from resources.instance_count
        **kwargs,
    ) -> None:
        self._provisioning_state = kwargs.pop("provisioning_state", None)

        super(BatchDeployment, self).__init__(
            name=name,
            endpoint_name=endpoint_name,
            properties=properties,
            tags=tags,
            description=description,
            model=model,
            code_configuration=code_configuration,
            environment=environment,
            environment_variables=environment_variables,
            code_path=code_path,
            scoring_script=scoring_script,
            **kwargs,
        )

        self.compute = compute
        self.resources = resources
        self.output_action = output_action
        self.output_file_name = output_file_name
        self.error_threshold = error_threshold
        self.retry_settings = retry_settings
        self.logging_level = logging_level
        self.mini_batch_size = mini_batch_size
        self.max_concurrency_per_instance = max_concurrency_per_instance

        if self.resources and instance_count:
            msg = "Can't set instance_count when resources is provided."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.BATCH_DEPLOYMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if not self.resources and instance_count:
            self.resources = ResourceConfiguration(instance_count=instance_count)

    @property
    def instance_count(self) -> int:
        return self.resources.instance_count if self.resources else None

    @property
    def provisioning_state(self) -> Optional[str]:
        """Batch deployment provisioning state, readonly.

        :return: Batch deployment provisioning state.
        :rtype: Optional[str]
        """
        return self._provisioning_state

    @instance_count.setter
    def instance_count(self, value: int) -> None:
        if not self.resources:
            self.resources = ResourceConfiguration()

        self.resources.instance_count = value

    def _to_dict(self) -> Dict:
        return BatchDeploymentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member

    @classmethod
    def _rest_output_action_to_yaml_output_action(cls, rest_output_action: str) -> str:
        output_switcher = {
            BatchOutputAction.APPEND_ROW: BatchDeploymentOutputAction.APPEND_ROW,
            BatchOutputAction.SUMMARY_ONLY: BatchDeploymentOutputAction.SUMMARY_ONLY,
        }

        return output_switcher.get(rest_output_action, rest_output_action)

    @classmethod
    def _yaml_output_action_to_rest_output_action(cls, yaml_output_action: str) -> str:
        output_switcher = {
            BatchDeploymentOutputAction.APPEND_ROW: BatchOutputAction.APPEND_ROW,
            BatchDeploymentOutputAction.SUMMARY_ONLY: BatchOutputAction.SUMMARY_ONLY,
        }

        return output_switcher.get(yaml_output_action, yaml_output_action)

    def _to_rest_object(self, location: str) -> BatchDeploymentData:  # pylint: disable=arguments-differ
        self._validate()
        code_config = (
            RestCodeConfiguration(
                code_id=self.code_configuration.code,
                scoring_script=self.code_configuration.scoring_script,
            )
            if self.code_configuration
            else None
        )
        model = IdAssetReference(asset_id=self.model) if self.model else None
        environment = self.environment

        batch_deployment = RestBatchDeployment(
            compute=self.compute,
            description=self.description,
            resources=self.resources._to_rest_object() if self.resources else None,
            code_configuration=code_config,
            environment_id=environment,
            model=model,
            output_file_name=self.output_file_name,
            output_action=BatchDeployment._yaml_output_action_to_rest_output_action(self.output_action),
            error_threshold=self.error_threshold,
            retry_settings=self.retry_settings._to_rest_object() if self.retry_settings else None,
            logging_level=self.logging_level,
            mini_batch_size=self.mini_batch_size,
            max_concurrency_per_instance=self.max_concurrency_per_instance,
            environment_variables=self.environment_variables,
            properties=self.properties,
        )

        return BatchDeploymentData(location=location, properties=batch_deployment, tags=self.tags)

    @classmethod
    def _from_rest_object(cls, deployment: BatchDeploymentData):  # pylint: disable=arguments-renamed
        modelId = deployment.properties.model.asset_id if deployment.properties.model else None
        code_configuration = (
            CodeConfiguration._from_rest_code_configuration(deployment.properties.code_configuration)
            if deployment.properties.code_configuration
            else None
        )
        deployment = BatchDeployment(
            name=deployment.name,
            description=deployment.properties.description,
            id=deployment.id,
            tags=deployment.tags,
            model=modelId,
            environment=deployment.properties.environment_id,
            code_configuration=code_configuration,
            output_file_name=deployment.properties.output_file_name
            if cls._rest_output_action_to_yaml_output_action(deployment.properties.output_action)
            == BatchDeploymentOutputAction.APPEND_ROW
            else None,
            output_action=cls._rest_output_action_to_yaml_output_action(deployment.properties.output_action),
            error_threshold=deployment.properties.error_threshold,
            retry_settings=BatchRetrySettings._from_rest_object(deployment.properties.retry_settings),
            logging_level=deployment.properties.logging_level,
            mini_batch_size=deployment.properties.mini_batch_size,
            compute=deployment.properties.compute,
            resources=ResourceConfiguration._from_rest_object(deployment.properties.resources),
            environment_variables=deployment.properties.environment_variables,
            max_concurrency_per_instance=deployment.properties.max_concurrency_per_instance,
            endpoint_name=_parse_endpoint_name_from_deployment_id(deployment.id),
            properties=deployment.properties.properties,
            creation_context=SystemData._from_rest_object(deployment.system_data),
            provisioning_state=deployment.properties.provisioning_state,
        )

        return deployment

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "BatchDeployment":
        data = data or {}
        params_override = params_override or []
        cls._update_params(params_override)

        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return load_from_dict(BatchDeploymentSchema, data, context, **kwargs)

    def _validate(self) -> None:
        self._validate_output_action()

    @classmethod
    def _update_params(cls, params_override) -> None:
        for param in params_override:
            endpoint_name = param.get("endpoint_name")
            if isinstance(endpoint_name, str):
                param["endpoint_name"] = endpoint_name.lower()

    def _validate_output_action(self) -> None:
        if (
            self.output_action
            and self.output_action == BatchDeploymentOutputAction.SUMMARY_ONLY
            and self.output_file_name
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
