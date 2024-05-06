# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any

from azure.ai.ml._restclient.v2022_10_01.models import SystemData as RestSystemData
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class SystemData(RestTranslatableMixin):
    """Metadata related to the creation and most recent modification of a resource.

    :ivar created_by: The identity that created the resource.
    :vartype created_by: str
    :ivar created_by_type: The type of identity that created the resource. Possible values include:
        "User", "Application", "ManagedIdentity", "Key".
    :vartype created_by_type: str or ~azure.ai.ml.entities.CreatedByType
    :ivar created_at: The timestamp of resource creation (UTC).
    :vartype created_at: ~datetime.datetime
    :ivar last_modified_by: The identity that last modified the resource.
    :vartype last_modified_by: str
    :ivar last_modified_by_type: The type of identity that last modified the resource. Possible
        values include: "User", "Application", "ManagedIdentity", "Key".
    :vartype last_modified_by_type: str or ~azure.ai.ml.entities.CreatedByType
    :ivar last_modified_at: The timestamp of resource last modification (UTC).
    :vartype last_modified_at: ~datetime.datetime
    :keyword created_by: The identity that created the resource.
    :paramtype created_by: str
    :keyword created_by_type: The type of identity that created the resource. Accepted values are
        "User", "Application", "ManagedIdentity", "Key".
    :paramtype created_by_type: Union[str, ~azure.ai.ml.entities.CreatedByType]
    :keyword created_at: The timestamp of resource creation (UTC).
    :paramtype created_at: datetime
    :keyword last_modified_by: The identity that last modified the resource.
    :paramtype last_modified_by: str
    :keyword last_modified_by_type: The type of identity that last modified the resource. Accepted values are
        "User", "Application", "ManagedIdentity", "Key".
    :paramtype last_modified_by_type: Union[str, ~azure.ai.ml.entities.CreatedByType]
    :keyword last_modified_at: The timestamp of resource last modification in UTC.
    :paramtype last_modified_at: datetime
    """

    def __init__(self, **kwargs: Any) -> None:
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

    def _to_dict(self) -> dict:
        from azure.ai.ml._schema.job.creation_context import CreationContextSchema

        return CreationContextSchema().dump(self)  # pylint: disable=no-member
