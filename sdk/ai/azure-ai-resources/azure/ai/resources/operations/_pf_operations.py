# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
from typing import Any

from azure.ai.resources._project_scope import OperationScope

from azure.ai.ml import MLClient



class PFOperations():
    """PFOperations.

    You should not instantiate this class directly. Instead, you should
    create an AIClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(self,
                 service_client: MLClient,
                 scope: OperationScope,
                 **kwargs: Any):

        self._service_client = service_client
        self._pf_client = None

        self._scope = scope


    def batch_run(self, flow: str, data: str, inputs_mapping: dict, runtime: str, connections: dict = None):
        from promptflow.sdk.entities import Run

        run_data = {
            "name": str(uuid.uuid4()),
            "type": "batch",
            "flow": flow,
            "data": data,
            "inputs_mapping": inputs_mapping
        }

        # remove empty fields
        run_data = {k: v for k, v in run_data.items() if v is not None}

        run = Run._load(data=run_data)


        result = self._get_pf_client().runs.create_or_update(run=run, runtime=runtime)
        return result._to_dict()

    def get_run_details(self, run_name: str):
        return self._get_pf_client().runs.get_details(run_name)

    def _get_pf_client(self):

        from promptflow.azure import PFClient

        if self._pf_client is None:
            self._pf_client = PFClient(self._service_client)

        return self._pf_client
