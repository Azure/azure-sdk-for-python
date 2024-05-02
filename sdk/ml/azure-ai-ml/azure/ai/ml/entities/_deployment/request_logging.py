# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, List, Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import RequestLogging as RestRequestLogging
from azure.ai.ml._schema._deployment.online.request_logging_schema import RequestLoggingSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


@experimental
class RequestLogging:
    """Request Logging deployment entity.

    :param capture_headers: Request payload header.
    :type capture_headers: list[str]
    """

    def __init__(
        self,
        *,
        capture_headers: Optional[List[str]] = None,
        **kwargs: Any,
    ):  # pylint: disable=unused-argument
        self.capture_headers = capture_headers

    @classmethod
    def _from_rest_object(cls, rest_obj: RestRequestLogging) -> "RequestLogging":
        return RequestLogging(capture_headers=rest_obj.capture_headers)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = RequestLoggingSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    def _to_rest_object(self) -> RestRequestLogging:
        return RestRequestLogging(capture_headers=self.capture_headers)
