# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.generative.evaluate._base_handler import BaseHandler

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

    def generate_prediction_data(self):
        # TODO: Check if this is the right place for this logic
        prediction_data = []
        test_data = self.get_test_data_as_jsonl()

        import inspect
        is_asset_async = False
        if inspect.iscoroutinefunction(self.asset):
            is_asset_async = True
            import asyncio

        for d in test_data:
            prediction_data.append(
                asyncio.run(self.asset(**d)) if is_asset_async else self.asset(**d)
            )

        
        return prediction_data
