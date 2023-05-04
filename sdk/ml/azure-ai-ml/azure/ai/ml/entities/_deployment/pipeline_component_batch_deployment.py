# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml.entities._component.component import Component
from azure.ai.ml._schema._deployment.batch.pipeline_component_batch_deployment_schema import (
    PipelineComponentBatchDeploymentSchema,
)  # pylint: disable=line-too-long
from azure.ai.ml.entities import Deployment, PipelineComponent
from azure.ai.ml._utils._arm_id_utils import _parse_endpoint_name_from_deployment_id
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    BatchPipelineComponentDeploymentConfiguration,
    IdAssetReference,
    BatchDeploymentProperties,
    BatchDeployment as RestBatchDeployment,
)


class PipelineComponentBatchDeployment(Deployment):
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
        component: Optional[Union[Component, str]] = None,
        settings: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.job_definition = kwargs.pop("job_definition", None)
        super().__init__(endpoint_name=endpoint_name, name=name, **kwargs)
        self.component = component
        self.settings = settings

    def _to_rest_object(self, location: str) -> "RestBatchDeployment":  # pylint: disable=arguments-differ
        if isinstance(self.component, PipelineComponent):
            id_asset_ref = IdAssetReference(asset_id=self.component.id)

            batch_pipeline_config = BatchPipelineComponentDeploymentConfiguration(
                settings=self.settings,
                tags=self.component.tags,
                description=self.component.description,
                component_id=id_asset_ref,
            )
        else:
            id_asset_ref = IdAssetReference(asset_id=self.component)
            batch_pipeline_config = BatchPipelineComponentDeploymentConfiguration(
                settings=self.settings, component_id=id_asset_ref
            )
        return RestBatchDeployment(
            location=location, properties=BatchDeploymentProperties(deployment_configuration=batch_pipeline_config)
        )

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "PipelineComponentBatchDeployment":
        data = data or {}
        params_override = params_override or []
        cls._update_params(params_override)

        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return load_from_dict(PipelineComponentBatchDeploymentSchema, data, context, **kwargs)

    @classmethod
    def _update_params(cls, params_override) -> None:
        for param in params_override:
            endpoint_name = param.get("endpoint_name")
            if isinstance(endpoint_name, str):
                param["endpoint_name"] = endpoint_name.lower()

    @classmethod
    def _from_rest_object(cls, deployment: RestBatchDeployment):  # pylint: disable=arguments-renamed
        return PipelineComponentBatchDeployment(
            name=deployment.name,
            component=deployment.properties.additional_properties["deploymentConfiguration"]["componentId"]["assetId"],
            settings=deployment.properties.additional_properties["deploymentConfiguration"]["settings"],
            endpoint_name=_parse_endpoint_name_from_deployment_id(deployment.id),
        )

    def _to_dict(self) -> Dict:
        return PipelineComponentBatchDeploymentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(
            self
        )  # pylint: disable=no-member
