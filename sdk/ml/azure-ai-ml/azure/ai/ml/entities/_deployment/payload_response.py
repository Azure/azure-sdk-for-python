# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict
from azure.ai.ml._schema._deployment.online.payload_response_schema import PayloadResponseSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class PayloadResponse:
    """Response deployment entity

    :param enabled: Is response logging enabled.
    :type enabled: str, optional

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, enabled: str = None, **kwargs):
        self.enabled = enabled

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return PayloadResponseSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
