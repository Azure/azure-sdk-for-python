# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_10_01.models import SystemData as RestSystemData
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class SystemData(RestTranslatableMixin):
    """Metadata related to the creation and most recent modification of a resource.

    :keyword created_by: The identity that created the resource.
    :type created_by: str
    :keyword created_by_type: The type of identity that created the resource. Accepted values are
        "User", "Application", "ManagedIdentity", "Key".
    :type created_by_type: Union[str, ~azure.ai.ml.entities.CreatedByType]
    :keyword created_at: The timestamp of resource creation (UTC).
    :type created_at: datetime
    :keyword last_modified_by: The identity that last modified the resource.
    :type last_modified_by: str
    :keyword last_modified_by_type: The type of identity that last modified the resource. Accepted values are
        "User", "Application", "ManagedIdentity", "Key".
    :type last_modified_by_type: Union[str, ~azure.ai.ml.entities.CreatedByType]
    :keyword last_modified_at: The timestamp of resource last modification in UTC.
    :type last_modified_at: datetime
    """

    def __init__(self, **kwargs) -> None:
        self.created_by = kwargs.get("created_by", None)
        self.created_by_type = kwargs.get("created_by_type", None)
        self.created_at = kwargs.get("created_at", None)
        self.last_modified_by = kwargs.get("last_modified_by", None)
        self.last_modified_by_type = kwargs.get("last_modified_by_type", None)
        self.last_modified_at = kwargs.get("last_modified_at", None)

    @classmethod
    def _from_rest_object(cls, obj: RestSystemData) -> "SystemData":
        return cls(
            created_by=obj.created_by,
            created_at=obj.created_at,
            created_by_type=obj.created_by_type,
            last_modified_by=obj.last_modified_by,
            last_modified_by_type=obj.last_modified_by_type,
            last_modified_at=obj.last_modified_at,
        )

    def _to_rest_object(self) -> RestSystemData:
        return RestSystemData(
            created_by=self.created_by,
            created_at=self.created_at,
            created_by_type=self.created_by_type,
            last_modified_by=self.last_modified_by,
            last_modified_by_type=self.last_modified_by_type,
            last_modified_at=self.last_modified_at,
        )
