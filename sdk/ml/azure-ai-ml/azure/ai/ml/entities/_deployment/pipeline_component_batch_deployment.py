# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Literal, Optional, Union

from azure.ai.ml._restclient.arm_ml_service.models import (
    BatchDeployment as RestBatchDeployment,
)
from azure.ai.ml._restclient.arm_ml_service.models import (
    BatchDeploymentProperties,
    BatchPipelineComponentDeploymentConfiguration,
    IdAssetReference,
)
from azure.ai.ml._schema._deployment.batch.pipeline_component_batch_deployment_schema import (
    PipelineComponentBatchDeploymentSchema,
)
from azure.ai.ml._utils._arm_id_utils import _parse_endpoint_name_from_deployment_id
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities import PipelineComponent
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._deployment.batch_deployment import BatchDeployment
from azure.ai.ml.entities._util import load_from_dict

type: Literal["pipeline"] = "pipeline"


class PipelineComponentBatchDeployment(BatchDeployment):
    """Pipeline Component Batch Deployment entity.

    :keyword name: Name of the deployment resource.
    :paramtype name: str
    :keyword description: Description of the deployment resource.
    :paramtype description: Optional[str]
    :keyword component: Component definition.
    :paramtype component: Optional[Union[Component, str]]
    :keyword settings: Run-time settings for the pipeline job.
    :paramtype settings: Optional[Dict[str, Any]]
    :keyword tags: A set of tags. The tags which will be applied to the job.
    :paramtype tags: Optional[Dict[str, Any]]
    :keyword job_definition: Arm ID or PipelineJob entity of an existing pipeline job.
    :paramtype job_definition: Optional[Dict[str, ~azure.ai.ml.entities._builders.BaseNode]]
    :keyword endpoint_name: Name of the Endpoint resource, defaults to None.
    :paramtype endpoint_name: Optional[str]
    """

    def __init__(
        self,
        *,
        name: str,
        endpoint_name: Optional[str] = None,
        component: Optional[Union[Component, str]] = None,
        settings: Optional[Dict[str, str]] = None,
        job_definition: Optional[Dict[str, BaseNode]] = None,
        tags: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ):
        # If type not removed from kwargs, it can lead to dual type params passed to Deployment class
        # Get type from kwargs if present, otherwise use the default type defined above
        _type = kwargs.pop("type", type)
        super().__init__(
            name=name,
            _type=_type,
            endpoint_name=endpoint_name,
            tags=tags,
            description=description,
            **kwargs,
        )
        self.component = component
        self.settings = settings
        self.job_definition = job_definition

    def _to_rest_object(self, location: str) -> "RestBatchDeployment":  # type: ignore[override]
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
                # The v2024_01 msrest BatchDeploymentProperties model defaulted these fields and always
                # emitted them on the wire even when unset here. The shared arm_ml_service model does not
                # default them, so set them explicitly to the same values to keep the body byte-identical.
                error_threshold=-1,
                max_concurrency_per_instance=1,
                mini_batch_size=10,
                output_file_name="predictions.csv",
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
    def _from_rest_object(cls, deployment: RestBatchDeployment) -> "PipelineComponentBatchDeployment":
        # The arm_ml_service model is a MutableMapping and exposes untyped wire keys via ``.get``; the
        # legacy msrest model exposed the same extra keys via ``additional_properties``.
        deployment_config = (
            deployment.properties.additional_properties.get("deploymentConfiguration", {})
            if hasattr(deployment.properties, "additional_properties")
            else deployment.properties.get("deploymentConfiguration", {})
        )
        return PipelineComponentBatchDeployment(
            name=deployment.name,
            tags=deployment.tags,
            component=deployment_config["componentId"]["assetId"],
            settings=deployment_config["settings"],
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
        res: dict = PipelineComponentBatchDeploymentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

        return res
