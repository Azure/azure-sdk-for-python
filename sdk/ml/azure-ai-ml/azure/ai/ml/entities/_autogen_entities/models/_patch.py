# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2024_04_01_preview.models import (
    EndpointDeploymentResourcePropertiesBasicResource,
    OpenAIEndpointDeploymentResourceProperties,
)

from ._models import AzureOpenAIDeployment as _AzureOpenAIDeployment, SystemData


__all__: List[str] = [
    "AzureOpenAIDeployment",
]  # Add all objects you want publicly available to users at this package level

_NULL = object()


@experimental
class AzureOpenAIDeployment(_AzureOpenAIDeployment):
    @classmethod
    def _from_rest_object(cls, obj: EndpointDeploymentResourcePropertiesBasicResource) -> "AzureOpenAIDeployment":
        properties: OpenAIEndpointDeploymentResourceProperties = obj.properties
        rest_system_data = obj.system_data
        return cls(
            name=obj.name,
            model_name=properties.model.name,
            model_version=properties.model.version,
            id=obj.id,
            system_data=SystemData(
                created_by=rest_system_data.created_by,
                created_at=rest_system_data.created_at,
                created_by_type=rest_system_data.created_by_type,
                last_modified_by=rest_system_data.last_modified_by,
                last_modified_by_type=rest_system_data.last_modified_by_type,
                last_modified_at=rest_system_data.last_modified_at,
            ),
        )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
