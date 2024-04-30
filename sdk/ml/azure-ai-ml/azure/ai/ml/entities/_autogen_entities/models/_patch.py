# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Dict, List, Optional

from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2024_04_01_preview.models import (
    EndpointDeploymentResourcePropertiesBasicResource,
    OpenAIEndpointDeploymentResourceProperties,
)

from ._models import AzureOpenAIDeployment as _AzureOpenAIDeployment
from .._model_base import rest_field


__all__: List[str] = [
    "AzureOpenAIDeployment",
]  # Add all objects you want publicly available to users at this package level

_NULL = object()


@experimental
class AzureOpenAIDeployment(_AzureOpenAIDeployment):

    system_data: Optional[SystemData] = rest_field(visibility=["read"])
    """System data of the endpoint."""

    @classmethod
    def _from_rest_object(cls, obj: EndpointDeploymentResourcePropertiesBasicResource) -> "AzureOpenAIDeployment":
        properties: OpenAIEndpointDeploymentResourceProperties = obj.properties
        return cls(
            name=obj.name,
            model_name=properties.model.name,
            model_version=properties.model.version,
            id=obj.id,
            system_data=SystemData._from_rest_object(obj.system_data),
        )

    def as_dict(self, *, exclude_readonly: bool = False) -> Dict[str, Any]:
        d = super().as_dict(exclude_readonly=exclude_readonly)
        d["system_data"] = json.loads(json.dumps(self.system_data._to_dict()))  # type: ignore
        return d


AzureOpenAIDeployment.__doc__ += (
    _AzureOpenAIDeployment.__doc__.strip()  # type: ignore
    + """
    :ivar system_data: System data of the deployment.
    :vartype system_data: ~azure.ai.ml.entities.SystemData
"""
)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
