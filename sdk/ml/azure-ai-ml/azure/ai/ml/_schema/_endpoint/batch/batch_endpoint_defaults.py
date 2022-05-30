# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any
from marshmallow import post_load, fields
from azure.ai.ml._schema import PatchedSchemaMeta

from azure.ai.ml._restclient.v2022_05_01.models import (
    BatchEndpointDefaults,
)

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY

module_logger = logging.getLogger(__name__)


class BatchEndpointsDefaultsSchema(metaclass=PatchedSchemaMeta):
    deployment_name = fields.Str(
        metadata={
            "description": "Name of the deployment that will be default for the endpoint. This deployment will end up getting 100% traffic when the endpoint scoring URL is invoked."
        }
    )

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        return BatchEndpointDefaults(**data)
