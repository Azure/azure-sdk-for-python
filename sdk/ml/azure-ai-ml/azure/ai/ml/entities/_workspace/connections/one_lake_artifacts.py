# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike
from typing import Any, Optional, Dict, Union
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
)
# Dev note: Supposedly there's going to be more artifact subclasses at some point.
# If/when that comes to pass, we can worry about adding polymorphism to these classes.
# For now, this is a one-off that's needed to help match the object structure that PF uses.


# Why is this not called a "LakeHouseArtifact"?  Because despite the under-the-hood type,
# users expect this variety to be called "OneLake".
class OneLakeConnectionArtifact:
    """Artifact class used by the Connection subclass known
    as a MicrosoftOneLakeConnection. Supplying this class further
    specifies the connection as a Lake House connection.
    """

    # Note: Kwargs exist just to silently absorb type from schema.
    def __init__(self, *, name: str, **kwargs: Any):  # pylint: disable=unused-argument
        self.name = name
        self.type = "lake_house"


    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Connection":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return cls._load_from_dict(data=data, context=context, **kwargs)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "OneLakeConnectionArtifact":
        loaded_data: Connection = load_from_dict(schema_class, data, context, **kwargs)
        return loaded_data

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        from azure.ai.ml._schema.connections import OneLakeArtifactSchema
        # Not sure what this pylint complaint was about, probably due to the polymorphic
        # tricks at play. Disabling since testing indicates no issue.
        # pylint: disable-next=missing-kwoa
        res: dict = OneLakeArtifactSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
