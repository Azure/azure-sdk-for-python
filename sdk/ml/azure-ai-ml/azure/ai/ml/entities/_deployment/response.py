# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict
from azure.ai.ml._schema._deployment.online.response_schema import ResponseSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class Response:
    """Response deployment entity

    :param enabled: Is response logging enabled.
    :type enabled: str, optional

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, enabled: str = None, **kwargs):
        self.endabled = enabled

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return ResponseSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
