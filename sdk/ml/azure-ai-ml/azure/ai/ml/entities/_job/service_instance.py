# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.runhistory.models import ServiceInstanceResult
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class ServiceInstance(RestTranslatableMixin, DictMixin):
    """Service Instance Result.

    :keyword type: The type of service.
    :paramtype type: Optional[str]
    :keyword port: The port used by the service.
    :paramtype port: Optional[int]
    :keyword status: The status of the service.
    :paramtype status: Optional[str]
    :keyword error: The error message.
    :paramtype error: Optional[str]
    :keyword endpoint: The service endpoint.
    :paramtype endpoint: Optional[str]
    :keyword properties: The service instance's properties.
    :paramtype properties: Optional[dict[str, str]]
    """

    def __init__(
        self,  # pylint: disable=unused-argument
        *,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        port: Optional[int] = None,
        status: Optional[str] = None,
        error: Optional[str] = None,
        endpoint: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        self.type = type
        self.port = port
        self.status = status
        self.error = error
        self.endpoint = endpoint
        self.properties = properties

    @classmethod
    # pylint: disable=arguments-differ
    def _from_rest_object(cls, obj: ServiceInstanceResult, node_index: int) -> "ServiceInstance":  # type: ignore
        return cls(
            type=obj.type,
            port=obj.port,
            status=obj.status,
            error=obj.error.error.message if obj.error and obj.error.error else None,
            endpoint=obj.endpoint.replace("<nodeIndex>", str(node_index)) if obj.endpoint else obj.endpoint,
            properties=obj.properties,
        )
