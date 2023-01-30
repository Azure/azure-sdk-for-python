# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import List

from azure.ai.ml._restclient.dataset_dataplane import AzureMachineLearningWorkspaces as ServiceClientDatasetDataplane
from azure.ai.ml._restclient.dataset_dataplane.models import BatchDataUriResponse, BatchGetResolvedURIs
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations

module_logger = logging.getLogger(__name__)


class DatasetDataplaneOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClientDatasetDataplane,
    ):
        super().__init__(operation_scope, operation_config)
        self._operation = service_client.data_version

    def get_batch_dataset_uris(self, dataset_ids: List[str]) -> BatchDataUriResponse:
        batch_uri_request = BatchGetResolvedURIs(values=dataset_ids)
        return self._operation.batch_get_resolved_uris(
            self._operation_scope.subscription_id,
            self._operation_scope.resource_group_name,
            self._workspace_name,
            body=batch_uri_request,
        )
