# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class RequestLoggingSchema(metaclass=PatchedSchemaMeta):
    capture_headers = fields.List(fields.Str())

    # pylint: disable=unused-argument
    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.request_logging import RequestLogging

        return RequestLogging(**data)
