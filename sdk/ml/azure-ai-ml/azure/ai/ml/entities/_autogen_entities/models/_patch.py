# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import inspect
from typing import List

from ._models import ServerlessEndpoint as _ServerlessEndpoint

from azure.ai.ml._utils._experimental import experimental

from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ServerlessEndpoint as RestServerlessEndpoint,
    ServerlessEndpointProperties as RestServerlessEndpointProperties,
    ModelSettings as RestModelSettings,
    Sku as RestSku,
)

__all__: List[str] = ["ServerlessEndpoint"]  # Add all objects you want publicly available to users at this package level

_NULL = object()


class ValidationMixin():
    def _validate(self) -> None:
        # verify types
        for attr, rest_field in self._attr_to_rest_field.items():
            try:
                attr_value = self.__getitem__(attr)
                attr_type = type(attr_value)
            except KeyError:
                if rest_field._is_required:
                    raise ValueError(f"attr {attr} is a required property for {self.__class__.__name__}")
            else:
                if getattr(attr_value, "_is_model", False):
                    attr_value._validate()
                elif attr_type != rest_field._class_type:
                    raise ValueError(f"Type of attr {attr} is of type {attr_type}, not {rest_field._class_type}")
                

@experimental
class ServerlessEndpoint(_ServerlessEndpoint, ValidationMixin):

    def _to_rest_object(self) -> RestServerlessEndpoint:
        return RestServerlessEndpoint(
            properties=RestServerlessEndpointProperties(
                model_settings=RestModelSettings(model_id=self.model_id),
            ),
            tags=self.tags,
            sku=RestSku(name="Consumption"),
            location=self.location,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestServerlessEndpoint) -> "ServerlessEndpoint":
        return cls(
            name=obj.name,
            id=obj.id,
            tags=obj.tags,
            location=obj.location,
            auth_mode=obj.properties.auth_mode,
            provisioning_state=obj.properties.provisioning_state,
            model_id=obj.properties.model_settings.model_id,
        )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
