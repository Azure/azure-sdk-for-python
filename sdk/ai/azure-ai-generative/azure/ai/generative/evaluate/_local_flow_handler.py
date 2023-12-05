# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os.path
import tempfile
import logging

from ._base_handler import BaseHandler
from ._utils import load_jsonl


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

        test_data = self.get_test_data_as_jsonl()
        pf_run_result = None

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, "test_data.jsonl")
            with open(tmp_path, "w") as f:
                for line in test_data:
                    f.write(json.dumps(line) + "\n")

            pf_client = PFClient()

            pf_run_result = pf_client.run(
                flow=self.asset,
                data=tmp_path,
                **self.flow_parameters
            )
            logger.debug("PF run results: %s", pf_run_result.properties)
        
        result_df = pf_client.get_details(pf_run_result.name)

        # Drop inputs columns
        input_columns = [col for col in result_df.columns if col.startswith("inputs.")]
        logger.debug("Dropping input columns: %s", input_columns)
        result_df.drop(input_columns, axis=1, inplace=True)

        # Rename output columns. E.g. output.answer -> answer
        output_columns = [col for col in result_df.columns if col.startswith("outputs.")]
        column_mapping = {col: col.replace("outputs.", "") for col in output_columns}
        logger.debug("Renaming output columns: %s", column_mapping)
        result_df.rename(columns=column_mapping, inplace=True)

        return result_df


