# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
from typing import Any, Dict, Optional

from azure.core.tracing.decorator import distributed_trace

from azure.ai.resources._project_scope import OperationScope

from azure.ai.ml import MLClient

from azure.ai.resources._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin, ActivityLogger

ops_logger = ActivityLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class PFOperations():
    """Operations class for promptflow resources

    You should not instantiate this class directly. Instead, you should
    create an AIClient instance that instantiates it for you and
    attaches it as an attribute.

    :param service_client: The Azure Machine Learning client
    :type service_client: ~azure.ai.ml.MLClient
    :param scope: The scope of the operation
    :type scope: ~azure.ai.resources._project_scope.OperationScope
    """

    def __init__(self,
                 service_client: MLClient,
                 scope: OperationScope,
                 **kwargs: Any):
        
        self._service_client = service_client
        self._pf_client = None

        self._scope = scope
        ops_logger.update_info(kwargs)

    @distributed_trace
    @monitor_with_activity(logger, "PF.BatchRun", ActivityType.PUBLICAPI)
    def batch_run(self, flow: str, data: str, inputs_mapping: dict, runtime: str, connections: Optional[Dict] = None) -> Dict:
        """Run a batch flow
        
        :param flow: The flow to run
        :type flow: str
        :param data: The data to use
        :type data: str
        :param inputs_mapping: The input mappings
        :type inputs_mapping: Dict
        :param runtime: The runtime to use
        :type runtime: str
        :param connections: The connections to use
        :type connections: Optional[Dict]
        :return: The batch run details
        :rtype: Dict
        """
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

    @distributed_trace
    @monitor_with_telemetry_mixin(logger, "PF.GetRunDetails", ActivityType.PUBLICAPI)
    def get_run_details(self, run_name: str) -> "DataFrame":  # type: ignore[name-defined]
        """Get the details of a run
        
        :param run_name: The name of the run
        :type run_name: str
        :return: The run details
        :rtype: pandas.DataFrame
        """
        return self._get_pf_client().runs.get_details(run_name)
    
    def _get_pf_client(self):
        
        from promptflow.azure import PFClient

        if self._pf_client is None:
            self._pf_client = PFClient(self._service_client)

        return self._pf_client
