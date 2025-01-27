# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
from typing import Any, Dict, List, Optional

from azure.ai.ml._restclient.v2024_01_01_preview.models import MarketplaceSubscription as RestMarketplaceSubscription
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    MarketplaceSubscriptionProperties as RestMarketplaceSubscriptionProperties,
)
from azure.ai.ml._restclient.v2024_01_01_preview.models import ModelSettings as RestModelSettings
from azure.ai.ml._restclient.v2024_01_01_preview.models import ServerlessEndpoint as RestServerlessEndpoint
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ServerlessEndpointProperties as RestServerlessEndpointProperties,
)
from azure.ai.ml._restclient.v2024_01_01_preview.models import Sku as RestSku
from azure.ai.ml._restclient.v2024_04_01_preview.models import (
    EndpointDeploymentResourcePropertiesBasicResource,
    OpenAIEndpointDeploymentResourceProperties,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._system_data import SystemData

from .._model_base import rest_field
from ._models import AzureOpenAIDeployment as _AzureOpenAIDeployment
from ._models import MarketplacePlan as _MarketplacePlan
from ._models import MarketplaceSubscription as _MarketplaceSubscription
from ._models import ServerlessEndpoint as _ServerlessEndpoint

__all__: List[str] = [
    "AzureOpenAIDeployment",
    "ServerlessEndpoint",
    "MarketplaceSubscription",
    "MarketplacePlan",
]  # Add all objects you want publicly available to users at this package level

_NULL = object()


func_to_attr_type = {
    "_deserialize_dict": dict,
    "_deserialize_sequence": list,
}


def _get_rest_field_type(field):
    if hasattr(field, "_type"):
        if field._type.func.__name__ == "_deserialize_default":
            return field._type.args[0]
        if func_to_attr_type.get(field._type.func.__name__):
            return func_to_attr_type[field._type.func.__name__]
        return _get_rest_field_type(field._type.args[0])
    if hasattr(field, "func") and func_to_attr_type.get(field.func.__name__):
        return func_to_attr_type[field.func.__name__]
    if hasattr(field, "args"):
        return _get_rest_field_type(field.args[0])
    return field


class ValidationMixin:
    def _validate(self) -> None:
        # verify types
        for attr, field in self._attr_to_rest_field.items():  # type: ignore
            try:
                attr_value = self.__getitem__(attr)  # type: ignore
                attr_type = type(attr_value)
            except KeyError as exc:
                if field._visibility and "read" in field._visibility:
                    # read-only field, no need to validate
                    continue
                if field._type.func.__name__ != "_deserialize_with_optional":
                    # i'm required
                    raise ValueError(f"attr {attr} is a required property for {self.__class__.__name__}") from exc
            else:
                if getattr(attr_value, "_is_model", False):
                    attr_value._validate()
                rest_field_type = _get_rest_field_type(field)
                if attr_type != rest_field_type:
                    raise ValueError(f"Type of attr {attr} is of type {attr_type}, not {rest_field_type}")


@experimental
class AzureOpenAIDeployment(_AzureOpenAIDeployment):

    system_data: Optional[SystemData] = rest_field(visibility=["read"])
    """System data of the deployment."""

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


@experimental
class MarketplacePlan(_MarketplacePlan):
    pass


@experimental
class ServerlessEndpoint(_ServerlessEndpoint, ValidationMixin):

    system_data: Optional[SystemData] = rest_field(visibility=["read"])
    """System data of the endpoint."""

    def _to_rest_object(self) -> RestServerlessEndpoint:
        return RestServerlessEndpoint(
            properties=RestServerlessEndpointProperties(
                model_settings=RestModelSettings(model_id=self.model_id),
            ),
            auth_mode="key",  # only key is supported for now
            tags=self.tags,
            sku=RestSku(name="Consumption"),
            location=self.location,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestServerlessEndpoint) -> "ServerlessEndpoint":
        return cls(  # type: ignore
            name=obj.name,
            id=obj.id,
            tags=obj.tags,
            location=obj.location,
            auth_mode=obj.properties.auth_mode,
            provisioning_state=camel_to_snake(obj.properties.provisioning_state),
            model_id=obj.properties.model_settings.model_id if obj.properties.model_settings else None,
            scoring_uri=obj.properties.inference_endpoint.uri if obj.properties.inference_endpoint else None,
            system_data=SystemData._from_rest_object(obj.system_data) if obj.system_data else None,
            headers=obj.properties.inference_endpoint.headers if obj.properties.inference_endpoint else None,
        )

    def as_dict(self, *, exclude_readonly: bool = False) -> Dict[str, Any]:
        d = super().as_dict(exclude_readonly=exclude_readonly)
        d["system_data"] = json.loads(json.dumps(self.system_data._to_dict()))  # type: ignore
        return d


ServerlessEndpoint.__doc__ += (
    _ServerlessEndpoint.__doc__.strip()  # type: ignore
    + """
    :ivar system_data: System data of the endpoint.
    :vartype system_data: ~azure.ai.ml.entities.SystemData
"""
)


@experimental
class MarketplaceSubscription(_MarketplaceSubscription, ValidationMixin):

    system_data: Optional[SystemData] = rest_field(visibility=["read"])
    """System data of the endpoint."""

    def _to_rest_object(self) -> RestMarketplaceSubscription:
        return RestMarketplaceSubscription(properties=RestMarketplaceSubscriptionProperties(model_id=self.model_id))

    @classmethod
    def _from_rest_object(cls, obj: RestMarketplaceSubscription) -> "MarketplaceSubscription":
        properties = obj.properties
        return cls(  # type: ignore
            name=obj.name,
            id=obj.id,
            model_id=properties.model_id,
            marketplace_plan=MarketplacePlan(
                publisher_id=properties.marketplace_plan.publisher_id,
                offer_id=properties.marketplace_plan.offer_id,
                plan_id=properties.marketplace_plan.plan_id,
            ),
            status=camel_to_snake(properties.marketplace_subscription_status),
            provisioning_state=camel_to_snake(properties.provisioning_state),
            system_data=SystemData._from_rest_object(obj.system_data) if obj.system_data else None,
        )

    def as_dict(self, *, exclude_readonly: bool = False) -> Dict[str, Any]:
        d = super().as_dict(exclude_readonly=exclude_readonly)
        if self.system_data:
            d["system_data"] = json.loads(json.dumps(self.system_data._to_dict()))
        return d


MarketplaceSubscription.__doc__ = (
    _MarketplaceSubscription.__doc__.strip()  # type: ignore
    + """
    :ivar system_data: System data of the marketplace subscription.
    :vartype system_data: ~azure.ai.ml.entities.SystemData
"""
)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
