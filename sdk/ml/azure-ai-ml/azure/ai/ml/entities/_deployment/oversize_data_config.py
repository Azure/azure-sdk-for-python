# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.oversize_data_config_schema import OversizeDataConfigSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class OversizeDataConfig:
    """Oversize Data Config deployment entity

    :param client_id: Client id of System/User Assigned Identity.
    :type client_id: str
    :param path: Blob path for Model Data Collector file.
    :type path: str

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, path: str = None, client_id: str = None, **kwargs):
        self.path = (path,)
        self.client_id = client_id

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return OversizeDataConfigSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
