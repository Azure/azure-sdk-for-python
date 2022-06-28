# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List
import logging
from azure.ai.ml._restclient.model_dataplane import (
    AzureMachineLearningWorkspaces as ServiceClientModelDataplane,
)
from azure.ai.ml._restclient.model_dataplane.models import BatchGetResolvedUrisDto, BatchModelPathResponseDto
from azure.ai.ml._scope_dependent_operations import _ScopeDependentOperations, OperationScope

module_logger = logging.getLogger(__name__)


class ModelDataplaneOperations(_ScopeDependentOperations):
    def __init__(self, operation_scope: OperationScope, service_client: ServiceClientModelDataplane):
        super().__init__(operation_scope)
        self._operation = service_client.models

    def get_batch_model_uris(self, model_ids: List[str]) -> BatchModelPathResponseDto:
        batch_uri_request = BatchGetResolvedUrisDto(values=model_ids)
        return self._operation.batch_get_resolved_uris(
            self._operation_scope.subscription_id,
            self._operation_scope.resource_group_name,
            self._workspace_name,
            body=batch_uri_request,
        )
