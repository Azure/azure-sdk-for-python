# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os.path
import tempfile
import logging

from ._base_handler import BaseHandler
from ._utils import df_to_dict_list, run_pf_flow_with_dict_list


logger = logging.getLogger(__name__)


class LocalFlowHandler(BaseHandler):

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
        from promptflow import PFClient

        test_data = df_to_dict_list(self.test_data, self.params_dict)
        
        pf_run_result = run_pf_flow_with_dict_list(self.asset, test_data, self.flow_parameters)
        
        logger.debug("PF run results: %s", pf_run_result.properties)
        
        pf_client = PFClient()
        result_df = pf_client.get_details(pf_run_result.name)

        # Rename input and output columns. E.g. outputs.answer -> answer; inputs.question -> question
        output_columns = [col for col in result_df.columns if col.startswith("outputs.")]
        column_mapping = {col: col.replace("outputs.", "") for col in output_columns}
        
        input_columns = [col for col in result_df.columns if col.startswith("inputs.")]
        column_mapping.append({col: col.replace("inputs.", "") for col in input_columns})

        logger.debug("Renaming inputs and output columns: %s", column_mapping)
        result_df.rename(columns=column_mapping, inplace=True)

        return result_df


