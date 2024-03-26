# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: skip-file

import logging
import pandas as pd

from ._base_handler import BaseHandler
from ._user_agent import USER_AGENT
from ._utils import df_to_dict_list, run_pf_flow_with_dict_list, wait_for_pf_run_to_complete


logger = logging.getLogger(__name__)


class LocalFlowHandler(BaseHandler):
    def __init__(self, asset, test_data, prediction_data=None, ground_truth=None, **kwargs):

        self.flow_parameters = kwargs.pop("flow_params", {})

        super().__init__(
            asset=asset, test_data=test_data, prediction_data=prediction_data, ground_truth=ground_truth, **kwargs
        )

    def execute_target(self):
        from promptflow import PFClient

        test_data = df_to_dict_list(self.test_data, self.params_dict)

        pf_run_result = run_pf_flow_with_dict_list(self.asset, test_data, self.flow_parameters)

        wait_for_pf_run_to_complete(pf_run_result.name)

        logger.debug("PF run results: %s", pf_run_result.properties)
        pf_client = PFClient(user_agent=USER_AGENT)
        result_df = pf_client.get_details(pf_run_result.name, all_results=True)

        # Rename inputs columns. E.g. inputs.question -> question
        input_columns = [col for col in result_df.columns if col.startswith("inputs.")]
        column_mapping = {col: col.replace("inputs.", "") for col in input_columns}

        # Rename output columns. E.g. outputs.answer -> answer
        output_columns = [col for col in result_df.columns if col.startswith("outputs.")]
        column_mapping.update({col: col.replace("outputs.", "") for col in output_columns})
        logger.debug("Renaming output columns: %s", column_mapping)
        self._input_output_data = pd.DataFrame(result_df.rename(columns=column_mapping, inplace=True))

        result_df.drop([col.replace("inputs.", "") for col in input_columns], axis=1, inplace=True)
        self._prediction_data = pd.DataFrame(result_df)
