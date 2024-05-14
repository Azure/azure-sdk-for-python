# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.entities import Job
from azure.ai.ml.entities._job.base_job import _BaseJob
from azure.ai.ml.entities._system_data import SystemData

from ._restclient.index_service_apis import IndexServiceAPIs
from ._restclient.index_service_apis.models import (
    CrossRegionIndexEntitiesRequest,
    IndexEntitiesRequest,
    IndexEntitiesRequestFilter,
    IndexEntitiesRequestOrder,
    IndexEntitiesRequestOrderDirection,
    IndexEntityResponse,
)

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore


def index_entity_response_to_job(entity: IndexEntityResponse) -> Job:
    properties = entity.properties
    annotations = entity.annotations
    creation_context = SystemData(
        created_by=properties.creation_context.created_by.user_name,
        created_by_type="User",
        created_at=properties.creation_context.created_time,
    )

    return _BaseJob(
        name=properties.additional_properties["runId"],
        display_name=annotations.additional_properties["displayName"],
        description=annotations.additional_properties["description"] or "",
        tags=annotations.tags,
        properties=properties.additional_properties["userProperties"],
        experiment_name=properties.additional_properties["experimentName"],
        services={},
        status=annotations.additional_properties["status"],
        creation_context=creation_context,
        compute=(
            properties.additional_properties["compute"]["armId"]
            if "compute" in properties.additional_properties
            else None
        ),
    )


__all__ = [
    "IndexServiceAPIs",
    "CrossRegionIndexEntitiesRequest",
    "IndexEntitiesRequest",
    "IndexEntitiesRequestFilter",
    "IndexEntitiesRequestOrder",
    "IndexEntitiesRequestOrderDirection",
    "index_entity_response_to_job",
]
