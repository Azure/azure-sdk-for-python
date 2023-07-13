# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from marshmallow import post_load

from azure.ai.ml._schema import PatchedSchemaMeta, StringTransformedEnum
from azure.ai.ml.constants._common import Boolean

module_logger = logging.getLogger(__name__)


class PayloadResponseSchema(metaclass=PatchedSchemaMeta):
    enabled = StringTransformedEnum(required=True, allowed_values=[Boolean.TRUE, Boolean.FALSE])

    # pylint: disable=unused-argument
    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.payload_response import PayloadResponse

        return PayloadResponse(**data)
