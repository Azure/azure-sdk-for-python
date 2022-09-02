# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_05_01.models import BatchEndpointDefaults
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class BatchEndpointsDefaultsSchema(metaclass=PatchedSchemaMeta):
    deployment_name = fields.Str(
        metadata={
            "description": """Name of the deployment that will be default for the endpoint.
             This deployment will end up getting 100% traffic when the endpoint scoring URL is invoked."""
        }
    )

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        return BatchEndpointDefaults(**data)
