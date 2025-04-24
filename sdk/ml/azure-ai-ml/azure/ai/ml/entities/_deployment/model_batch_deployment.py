# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

from azure.ai.ml._restclient.v2022_05_01.models import BatchDeploymentData
from azure.ai.ml._restclient.v2022_05_01.models import BatchDeploymentDetails as RestBatchDeployment
from azure.ai.ml._restclient.v2022_05_01.models import CodeConfiguration as RestCodeConfiguration
from azure.ai.ml._restclient.v2022_05_01.models import IdAssetReference
from azure.ai.ml._schema._deployment.batch.model_batch_deployment import ModelBatchDeploymentSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets import Environment, Model
from azure.ai.ml.entities._deployment.batch_deployment import BatchDeployment
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._util import load_from_dict

from .code_configuration import CodeConfiguration
from .model_batch_deployment_settings import ModelBatchDeploymentSettings

type: Literal["model"] = "model"


class ModelBatchDeployment(BatchDeployment):
    """Model Batch Deployment entity.

    :param name: Name of the deployment resource.
    :type name: str
    :param endpoint_name: Name of the endpoint.
    :type endpoint_name: Optional[str]
    :param environment: Environment to use for deployment.
    :type environment: Optional[Union[str, Environment]]
    :param properties: The asset property dictionary.
    :type properties: Optional[Dict[str, str]]
    :param model: Model to deploy.
    :type model: Optional[Union[str, Model]]
    :param description: Deployment description.
    :type description: Optional[str]
    :param tags: Deployment tags.
    :type tags: Optional[Dict[str, Any]]
    :param settings: Deployment settings.
    :type settings: Optional[ModelBatchDeploymentSettings]
    :param resources: Resource configuration.
    :type resources: Optional[ResourceConfiguration]
    :param compute: Compute target to use.
    :type compute: Optional[str]
    :param code_configuration: Code configuration for deployment.
    :type code_configuration: Optional[CodeConfiguration]
    :param code_path: Path to the code directory.
    :type code_path: Optional[Union[str, PathLike]]
    :param scoring_script: Path to the scoring script.
    :type scoring_script: Optional[Union[str, PathLike]]
    """

    def __init__(
        self,
        *,
        name: str,
        endpoint_name: Optional[str] = None,
        environment: Optional[Union[str, Environment]] = None,
        properties: Optional[Dict[str, str]] = None,
        model: Optional[Union[str, Model]] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        settings: Optional[ModelBatchDeploymentSettings] = None,
        resources: Optional[ResourceConfiguration] = None,
        compute: Optional[str] = None,
        code_configuration: Optional[CodeConfiguration] = None,
        code_path: Optional[Union[str, PathLike]] = None,  # promoted property from code_configuration.code
        scoring_script: Optional[
            Union[str, PathLike]
        ] = None,  # promoted property from code_configuration.scoring_script
        **kwargs: Any,
    ):
        # If type not removed from kwargs, it can lead to dual type params passed to Deployment class
        # Get type from kwargs if present, otherwise use the default type defined above
        _type = kwargs.pop("type", type)
        super().__init__(
            name=name,
            _type=_type,
            endpoint_name=endpoint_name,
            properties=properties,
            code_path=code_path,
            scoring_script=scoring_script,
            environment=environment,
            model=model,
            description=description,
            tags=tags,
            code_configuration=code_configuration,
            compute=compute,
            resources=resources,
            settings=settings,
            **kwargs,
        )

    @property
    def settings(self) -> ModelBatchDeploymentSettings:
        return self._settings

    @settings.setter
    def settings(self, value: ModelBatchDeploymentSettings) -> None:
        self._settings = value

    # pylint: disable=arguments-differ
    def _to_rest_object(self, location: str) -> BatchDeploymentData:  # type: ignore[override]
        self._validate()
        code_config = (
            RestCodeConfiguration(
                code_id=self.code_configuration.code,
                scoring_script=self.code_configuration.scoring_script,
            )
            if self.code_configuration
            else None
        )
        deployment_settings = self.settings
        model = IdAssetReference(asset_id=self.model) if self.model else None
        batch_deployment = RestBatchDeployment(
            description=self.description,
            environment_id=self.environment,
            model=model,
            code_configuration=code_config,
            output_file_name=deployment_settings.output_file_name,
            output_action=BatchDeployment._yaml_output_action_to_rest_output_action(  # pylint: disable=protected-access
                deployment_settings.output_action
            ),
            error_threshold=deployment_settings.error_threshold,
            resources=self.resources._to_rest_object() if self.resources else None,  # pylint: disable=protected-access
            retry_settings=(
                deployment_settings.retry_settings._to_rest_object()  # pylint: disable=protected-access
                if deployment_settings.retry_settings
                else None
            ),
            logging_level=deployment_settings.logging_level,
            mini_batch_size=deployment_settings.mini_batch_size,
            max_concurrency_per_instance=deployment_settings.max_concurrency_per_instance,
            environment_variables=deployment_settings.environment_variables,
            compute=self.compute,
            properties=self.properties,
        )
        return BatchDeploymentData(location=location, properties=batch_deployment, tags=self.tags)

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "ModelBatchDeployment":
        data = data or {}
        params_override = params_override or []
        cls._update_params(params_override)

        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: ModelBatchDeployment = load_from_dict(ModelBatchDeploymentSchema, data, context, **kwargs)
        return res

    def _to_dict(self) -> Dict:
        res: dict = ModelBatchDeploymentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
