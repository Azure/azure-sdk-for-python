# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional

from azure.ai.ml._schema._deployment.online.oversize_data_config_schema import OversizeDataConfigSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class OversizeDataConfig:
    """Oversize Data Config deployment entity.

    :param path: Blob path for Model Data Collector file.
    :type path: str
    """

    # pylint: disable=unused-argument
    def __init__(self, path: Optional[str] = None, **kwargs: Any):
        self.path = path

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = OversizeDataConfigSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
