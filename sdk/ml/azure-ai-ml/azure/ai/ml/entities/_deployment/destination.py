# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.destination_schema import DestinationSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._deployment.event_hub import EventHub


class Destination:
    """Destination deployment entity

    :param path: Blob path for Model Data Collector file.
    :type path: str

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, path: str = None, event_hub: EventHub = None, **kwargs):
        self.path = path
        self.event_hub = event_hub

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DestinationSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
