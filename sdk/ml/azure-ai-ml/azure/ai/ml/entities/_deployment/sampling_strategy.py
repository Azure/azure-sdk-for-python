# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.sampling_strategy_schema import SamplingStrategySchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class SamplingStrategy:
    """Sampling strategy deployment entity

    :param random_sample_percentage: Random sample percent of traffic.
    :type random_sample_percentage: int, optional

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, random_sample_percentage: int = None, **kwargs):
        self.random_sample_percentage = random_sample_percentage

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return SamplingStrategySchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
