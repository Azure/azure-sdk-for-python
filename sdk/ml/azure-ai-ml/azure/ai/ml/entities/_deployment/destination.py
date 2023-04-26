# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional

from azure.ai.ml._schema._deployment.online.destination_schema import DestinationSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._deployment.event_hub import EventHub


class Destination:
    """Destination deployment entity.

    :param path: Blob path for Model Data Collector file.
    :type path: str
    :param event_hub: Azure Event Hub location where payload logging will be stored.
    :type event_hub: EventHub
    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, path: Optional[str] = None, event_hub: Optional[EventHub] = None, **kwargs):
        self.path = path
        self.event_hub = event_hub

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DestinationSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
