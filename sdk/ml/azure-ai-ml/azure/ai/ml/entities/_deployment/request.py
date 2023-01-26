# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.request_schema import RequestSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class Request:
    """Request deployment entity

    :param enabled: Is request logging enabled.
    :type enabled: str, optional

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, enabled: str = None, **kwargs):
        self.enabled = enabled

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return RequestSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
