# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2024_01_01_preview.models import BatchDeployment as RestBatchDeployment
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    BatchDeploymentProperties,
    BatchPipelineComponentDeploymentConfiguration,
    IdAssetReference,
)
from azure.ai.ml._schema._deployment.batch.pipeline_component_batch_deployment_schema import (  # pylint: disable=line-too-long
    PipelineComponentBatchDeploymentSchema,
)
from azure.ai.ml._utils._arm_id_utils import _parse_endpoint_name_from_deployment_id
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities import PipelineComponent
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import load_from_dict


@experimental
class PipelineComponentBatchDeployment(Resource):
    """Pipeline Component Batch Deployment entity.

    :param type: Job definition type. Allowed value: "pipeline"
    :type type: Optional[str]
    :param name: Name of the deployment resource.
    :type name: Optional[str]
    :param description: Description of the deployment resource.
    :type description: Optional[str]
    :param component: Component definition.
    :type component: Optional[Union[Component, str]]
    :param settings: Run-time settings for the pipeline job.
    :type settings: Optional[Dict[str, Any]]
    :param tags: A set of tags. The tags which will be applied to the job.
    :type tags: Optional[Dict[str, Any]]
    :param job_definition: Arm ID or PipelineJob entity of an existing pipeline job.
    :type job_definition: Optional[Dict[str, ~azure.ai.ml.entities._builders.BaseNode]]
    :param endpoint_name: Name of the Endpoint resource, defaults to None.
    :type endpoint_name: Optional[str]
    """

    def __init__(
        self,
        *,
        name: Optional[str],
        endpoint_name: Optional[str] = None,
        component: Optional[Union[Component, str]] = None,
        settings: Optional[Dict[str, str]] = None,
        job_definition: Optional[Dict[str, BaseNode]] = None,
        tags: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs: Any,  # pylint: disable=unused-argument
    ):
        self._type = kwargs.pop("type", None)
        super().__init__(name=name, tags=tags, description=description, **kwargs)
        self.component = component
        self.endpoint_name = endpoint_name
        self.settings = settings
        self.job_definition = job_definition

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
            location=location,
            tags=self.tags,
            properties=BatchDeploymentProperties(
                deployment_configuration=batch_pipeline_config,
                description=self.description,
            ),
        )

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "PipelineComponentBatchDeployment":
        data = data or {}
        params_override = params_override or []
        cls._update_params(params_override)

        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: PipelineComponentBatchDeployment = load_from_dict(
            PipelineComponentBatchDeploymentSchema, data, context, **kwargs
        )
        return res

    @classmethod
    def _update_params(cls, params_override: Any) -> None:
        for param in params_override:
            endpoint_name = param.get("endpoint_name")
            if isinstance(endpoint_name, str):
                param["endpoint_name"] = endpoint_name.lower()

    @classmethod
    def _from_rest_object(  # pylint: disable=arguments-renamed
        cls, deployment: RestBatchDeployment
    ) -> "PipelineComponentBatchDeployment":
        return PipelineComponentBatchDeployment(
            name=deployment.name,
            tags=deployment.tags,
            component=deployment.properties.additional_properties["deploymentConfiguration"]["componentId"]["assetId"],
            settings=deployment.properties.additional_properties["deploymentConfiguration"]["settings"],
            endpoint_name=_parse_endpoint_name_from_deployment_id(deployment.id),
        )

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the deployment content into a file in yaml format.

        :param dest: The destination to receive this deployment's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: typing.Union[os.PathLike, str, typing.IO[typing.AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        res: dict = PipelineComponentBatchDeploymentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(
            self
        )  # pylint: disable=no-member

        return res
