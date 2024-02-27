# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import KEY
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ServerlessEndpoint as RestServerlessEndpoint,
    ServerlessEndpointProperties as RestServerlessEndpointProperties,
    ModelSettings as RestModelSettings,
    Sku as RestSku,
)

from .endpoint import Endpoint


@experimental
class ServerlessEndpoint(Endpoint):
    def __init__(
        self,
        name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        location: Optional[str] = None,
        auth_mode: str = KEY,
        provisioning_state: Optional[str] = None,
        model_id: str = None,
        **kwargs: Any,
    ):
        self.marketplace_subscription_id = kwargs.pop("marketplace_subscription_id", None)
        super().__init__(
            name=name,
            tags=tags,
            location=location,
            auth_mode=auth_mode,
            provisioning_state=provisioning_state,
            **kwargs,
        )
        self.model_id = model_id

    def _to_rest_object(self) -> RestServerlessEndpoint:
        return RestServerlessEndpoint(
            properties=RestServerlessEndpointProperties(
                model_settings=RestModelSettings(model_id=self.model_id),
            ),
            tags=self.tags,
            sku=RestSku(name="Consumption"),
            location=self.location
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
            marketplace_subscription=obj.properties.marketplace_subscription_id
        )