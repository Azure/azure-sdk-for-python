# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import pandas as pd

from azure.ai.generative.evaluate._base_handler import BaseHandler
from ._utils import df_to_dict_list

logger = logging.getLogger(__name__)


class LocalCodeHandler(BaseHandler):

    def __init__(self, asset, test_data, prediction_data=None, ground_truth=None, **kwargs):
        self.flow_parameters = kwargs.pop("flow_params", {})

        super().__init__(
            asset=asset,
            test_data=test_data,
            prediction_data=prediction_data,
            ground_truth=ground_truth,
            **kwargs
        )

    def execute_target(self):
        prediction_data = []
        input_output_data = []
        test_data = df_to_dict_list(self.test_data, self.params_dict)

        import inspect
        is_asset_async = False
        if inspect.iscoroutinefunction(self.asset):
            is_asset_async = True
            import asyncio

        for input in test_data:
            # The assumption here is target function returns a dict with output keys
            fn_output = asyncio.run(self.asset(**input)) if is_asset_async else self.asset(**input) 
            
            prediction_data.append(fn_output)
            # When input and output have a common key, value in output overrides value in input
            input_output = dict(input)
            input_output.update(fn_output)
            input_output_data.append(input_output)


        self._prediction_data = pd.DataFrame(prediction_data)
        self._input_output_data = pd.DataFrame(input_output_data)
