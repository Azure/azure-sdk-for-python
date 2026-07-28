# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict


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
    def _from_rest_object(cls, obj: Dict[str, Any]) -> "BatchJob":
        # ``BatchJobResource`` is not modeled on arm_ml_service; read the camelCase wire dict directly.
        properties = obj.get("properties") or {}
        return cls(
            id=obj.get("id"),
            name=obj.get("name"),
            type=obj.get("type"),
            status=properties.get("status"),
        )
