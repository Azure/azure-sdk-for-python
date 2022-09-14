# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.destination_schema import DestinationSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class Destination:
    """Destination deployment entity

    :param path: Blob path for Model Data Collector file.
    :type path: string

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, path: str = None, **kwargs):
        self.path = path

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DestinationSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
