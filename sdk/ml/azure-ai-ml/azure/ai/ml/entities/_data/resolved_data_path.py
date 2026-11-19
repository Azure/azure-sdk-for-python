# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, List, Optional

from azure.ai.ml._utils._experimental import experimental


@experimental
class ResolvedDataPath:
    """A storage location and, for MLTable definitions, its resolved source tree.

    A plain file or folder has a storage ``uri`` and no ``sources``. For an MLTable,
    ``uri`` identifies the definition, ``sources`` contains its resolved paths, and
    ``transformations`` preserves its read options, filters, and Delta time travel.
    Resolution does not apply transformations or grant access to the returned URIs.

    :keyword uri: Physical storage URI, without added authentication credentials.
    :paramtype uri: str
    :keyword path_type: MLTable path type (file, folder, or pattern), if known.
    :paramtype path_type: Optional[str]
    :keyword sources: Resolved MLTable sources. Nested definitions retain their own sources.
    :paramtype sources: Optional[List[~azure.ai.ml.entities.ResolvedDataPath]]
    :keyword transformations: Transformations associated with this definition.
    :paramtype transformations: Optional[List[Dict[str, Any]]]
    """

    def __init__(
        self,
        *,
        uri: str,
        path_type: Optional[str] = None,
        sources: Optional[List["ResolvedDataPath"]] = None,
        transformations: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.uri: str = uri
        self.path_type: Optional[str] = path_type
        self.sources: List["ResolvedDataPath"] = sources if sources is not None else []
        self.transformations: List[Dict[str, Any]] = transformations if transformations is not None else []
