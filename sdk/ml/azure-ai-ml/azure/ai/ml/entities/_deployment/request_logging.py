# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional

from azure.ai.ml._schema._deployment.online.request_logging_schema import RequestLoggingSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class RequestLogging:
    """Request Logging deployment entity

    :param capture_headers: Request payload header.
    :type capture_headers: list[str]

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, capture_headers: Optional[list] = None, **kwargs):
        self.capture_headers = capture_headers

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return RequestLoggingSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
