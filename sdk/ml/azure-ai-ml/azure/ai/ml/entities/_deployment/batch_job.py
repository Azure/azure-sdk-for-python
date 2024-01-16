# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict

from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import BatchJobResource


class BatchJob(object):
    """Batch jobs that are created with batch deployments/endpoints invocation.

    This class shouldn't be instantiated directly. Instead, it is used as the return type of batch deployment/endpoint
    invocation and job listing.
    """

    def __init__(self, **kwargs: Any):
        self.id = kwargs.get("id", None)
        self.name = kwargs.get("name", None)
        self.type = kwargs.get("type", None)
        self.status = kwargs.get("status", None)

    def _to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
        }

    @classmethod
    def _from_rest_object(cls, obj: BatchJobResource) -> "BatchJob":
        return cls(
            id=obj.id,
            name=obj.name,
            type=obj.type,
            status=obj.properties.status,
        )
