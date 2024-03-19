# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional

from azure.ai.ml._schema._deployment.online.payload_response_schema import PayloadResponseSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class PayloadResponse:
    """Response deployment entity

    :param enabled: Is response logging enabled.
    :type enabled: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_endpoint_deployment_configs.py
            :start-after: [START payload_response_entity_create]
            :end-before: [END payload_response_entity_create]
            :language: python
            :dedent: 8
            :caption: Creating a PayloadResponse entity.

    """

    # pylint: disable=unused-argument
    def __init__(self, enabled: Optional[str] = None, **kwargs: Any):
        self.enabled = enabled

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = PayloadResponseSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
