# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import post_load

from azure.ai.ml._schema._endpoint.batch.batch_endpoint_defaults import BatchEndpointsDefaultsSchema
from azure.ai.ml._schema._endpoint.endpoint import EndpointSchema
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

module_logger = logging.getLogger(__name__)


class BatchEndpointSchema(EndpointSchema):
    defaults = NestedField(BatchEndpointsDefaultsSchema)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import BatchEndpoint

        return BatchEndpoint(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
