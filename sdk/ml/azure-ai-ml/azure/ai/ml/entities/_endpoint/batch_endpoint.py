# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_10_01.models import BatchEndpoint as BatchEndpointData
from azure.ai.ml._restclient.v2023_10_01.models import BatchEndpointProperties as RestBatchEndpoint
from azure.ai.ml._schema._endpoint import BatchEndpointSchema
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml.constants._common import AAD_TOKEN_YAML, BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._endpoint._endpoint_helpers import validate_endpoint_or_deployment_name
from azure.ai.ml.entities._util import load_from_dict

from .endpoint import Endpoint

module_logger = logging.getLogger(__name__)


class BatchEndpoint(Endpoint):
    """Batch endpoint entity.

    :param name: Name of the resource.
    :type name: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param auth_mode: Possible values include: "AMLToken", "Key", "AADToken", defaults to None
    :type auth_mode: str
    :param description: Description of the inference endpoint, defaults to None
    :type description: str
    :param location: defaults to None
    :type location: str
    :param defaults:  Traffic rules on how the traffic will be routed across deployments, defaults to {}
    :type defaults: Dict[str, str]
    :param default_deployment_name:  Equivalent to defaults.default_deployment, will be ignored if defaults is present.
    :type default_deployment_name: str
    :param scoring_uri: URI to use to perform a prediction, readonly.
    :type scoring_uri: str
    :param openapi_uri: URI to check the open API definition of the endpoint.
    :type openapi_uri: str
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        auth_mode: str = AAD_TOKEN_YAML,
        description: Optional[str] = None,
        location: Optional[str] = None,
        defaults: Optional[Dict[str, str]] = None,
        default_deployment_name: Optional[str] = None,
        scoring_uri: Optional[str] = None,
        openapi_uri: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super(BatchEndpoint, self).__init__(
            name=name,
            tags=tags,
            properties=properties,
            auth_mode=auth_mode,
            description=description,
            location=location,
            scoring_uri=scoring_uri,
            openapi_uri=openapi_uri,
            **kwargs,
        )

        self.defaults = defaults

        if not self.defaults and default_deployment_name:
            self.defaults = {}
            self.defaults["deployment_name"] = default_deployment_name

    def _to_rest_batch_endpoint(self, location: str) -> BatchEndpointData:
        validate_endpoint_or_deployment_name(self.name)
        batch_endpoint = RestBatchEndpoint(
            description=self.description,
            auth_mode=snake_to_camel(self.auth_mode),
            properties=self.properties,
            defaults=self.defaults,
        )
        return BatchEndpointData(location=location, tags=self.tags, properties=batch_endpoint)

    @classmethod
    def _from_rest_object(cls, obj: BatchEndpointData) -> "BatchEndpoint":
        return BatchEndpoint(
            id=obj.id,
            name=obj.name,
            tags=obj.tags,
            properties=obj.properties.properties,
            auth_mode=camel_to_snake(obj.properties.auth_mode),
            description=obj.properties.description,
            location=obj.location,
            defaults=obj.properties.defaults,
            provisioning_state=obj.properties.provisioning_state,
            scoring_uri=obj.properties.scoring_uri,
            openapi_uri=obj.properties.swagger_uri,
        )

    def dump(
        self,
        dest: Optional[Union[str, PathLike, IO[AnyStr]]] = None,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return BatchEndpointSchema(context=context).dump(self)  # type: ignore # pylint: disable=no-member

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "BatchEndpoint":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: BatchEndpoint = load_from_dict(BatchEndpointSchema, data, context)
        return res

    def _to_dict(self) -> Dict:
        res: dict = BatchEndpointSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member
        return res
