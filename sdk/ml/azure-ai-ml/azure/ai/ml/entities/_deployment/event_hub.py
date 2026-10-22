# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional

from azure.ai.ml._schema._deployment.online.event_hub_schema import EventHubSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._deployment.oversize_data_config import OversizeDataConfig


class EventHub:
    """Event Hub deployment entity

    :param namespace: Name space of eventhub, provided in format of "{namespace}.{name}".
    :type namespace: str
    :param oversize_data_config: Oversized payload body configurations.
    :type oversize_data_config: OversizeDataConfig

    """

    # pylint: disable=unused-argument
    def __init__(
        self, namespace: Optional[str] = None, oversize_data_config: Optional[OversizeDataConfig] = None, **kwargs: Any
    ):
        self.namespace = namespace
        self.oversize_data_config = oversize_data_config

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = EventHubSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
