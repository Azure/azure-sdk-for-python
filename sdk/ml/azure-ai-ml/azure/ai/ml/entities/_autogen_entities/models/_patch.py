# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import inspect
from typing import List

from ._models import ServerlessEndpoint as _ServerlessEndpoint, MarketplaceSubscription as _MarketplaceSubscription, MarketplacePlan

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import SystemData

from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ServerlessEndpoint as RestServerlessEndpoint,
    ServerlessEndpointProperties as RestServerlessEndpointProperties,
    ModelSettings as RestModelSettings,
    Sku as RestSku,
    MarketplaceSubscription as RestMarketplaceSubscription,
    MarketplaceSubscriptionProperties as RestMarketplaceSubscriptionProperties,
)

__all__: List[str] = ["ServerlessEndpoint", "MarketplaceSubscription"]  # Add all objects you want publicly available to users at this package level

_NULL = object()

func_to_attr_type = {
    "_deserialize_dict": dict,
    "_deserialize_sequence": list,
}

def _get_rest_field_type(rest_field):
    if hasattr(rest_field, "_type"):
        if rest_field._type.func.__name__ == "_deserialize_default":
            return rest_field._type.args[0]
        if func_to_attr_type.get(rest_field._type.func.__name__):
            return func_to_attr_type[rest_field._type.func.__name__]
        return _get_rest_field_type(rest_field._type.args[0])
    if hasattr(rest_field, "func" ) and func_to_attr_type.get(rest_field.func.__name__):
        return func_to_attr_type[rest_field.func.__name__]
    if hasattr(rest_field, "args"):
        return _get_rest_field_type(rest_field.args[0])
    return rest_field

class ValidationMixin():
    def _validate(self) -> None:
        # verify types
        for attr, rest_field in self._attr_to_rest_field.items():
            try:
                attr_value = self.__getitem__(attr)
                attr_type = type(attr_value)
            except KeyError:
                if rest_field._visibility and "read" in rest_field._visibility:
                    # read-only field, no need to validate
                    continue
                if rest_field._type.func.__name__ != "_deserialize_with_optional":
                    # i'm required
                    raise ValueError(f"attr {attr} is a required property for {self.__class__.__name__}")
            else:
                if getattr(attr_value, "_is_model", False):
                    return attr_value._validate()
                rest_field_type = _get_rest_field_type(rest_field)
                if attr_type != rest_field_type:
                    raise ValueError(f"Type of attr {attr} is of type {attr_type}, not {rest_field_type}")
                

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
            provisioning_state=camel_to_snake(obj.properties.provisioning_state),
            model_id=obj.properties.model_settings.model_id,
            system_data=SystemData._from_rest_object(obj.system_data),
        )

@experimental
class MarketPlacesubscription(_MarketplaceSubscription, ValidationMixin):

    def _to_rest_object(self) -> RestMarketplaceSubscription:
        return RestMarketplaceSubscription(
            properties=RestMarketplaceSubscriptionProperties(model_id=self.model_id)
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMarketplaceSubscription) -> "ServerlessEndpoint":
        properties = obj.properties
        return cls(
            name=obj.name,
            id=obj.id,
            model_id=properties.model_id,
            marketplace_plan=MarketplacePlan(
                properties.marketplace_plan,
            ),
            status=camel_to_snake(properties.marketplace_subscription_status),
            provisioning_state=camel_to_snake(properties.provisioning_state),
            system_data=SystemData._from_rest_object(obj.system_data),
        )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
