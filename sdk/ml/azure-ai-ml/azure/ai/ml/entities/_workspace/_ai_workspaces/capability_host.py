# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from azure.ai.ml._utils._experimental import experimental
from typing import List, Optional, Union
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.constants._workspace import CapabilityHostKind
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, WorkspaceKind
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Union
from azure.ai.ml._schema.workspace.ai_workspaces.capability_host import CapabilityHostSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._restclient.v2024_10_01_preview.models._models_py3 import CapabilityHost as RestCapabilityHost
from azure.ai.ml._restclient.v2024_10_01_preview.models._models_py3 import CapabilityHostProperties as RestCapabilityHostProperties

@experimental
class CapabilityHost(Resource):
    """Initialize a CapabilityHost instance.
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        vector_store_connections: Optional[List[str]] = None,
        ai_services_connections: Optional[List[str]] = None,
        storage_connections: Optional[List[str]] = None,
        capability_host_kind: Optional[Union[str, CapabilityHostKind]] = CapabilityHostKind.AGENTS,
        **kwargs: Any,
    ):
        super().__init__(name=name,description=description, **kwargs)
        self.capability_host_kind = capability_host_kind
        self.ai_services_connections = ai_services_connections
        self.storage_connections = storage_connections
        self.vector_store_connections = vector_store_connections
        

    def dump(self, dest: Optional[Union[str, PathLike, IO[AnyStr]]],  **kwargs: Any,) -> None:
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        res = CapabilityHostSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
    
    @classmethod
    def _load(
        cls,
        data: Optional[dict] = None,
        yaml_path: Optional[Union[os.PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> 'CapabilityHost':
        params_override = params_override or []
        data = data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: CapabilityHost = load_from_dict(CapabilityHostSchema, data, context, **kwargs)
        return res
    
    @classmethod
    def _from_rest_object(cls, rest_obj: RestCapabilityHost) -> 'CapabilityHost':
        capability_host = CapabilityHost(
            name=str(rest_obj.name),
            description=rest_obj.properties.description if rest_obj.properties else None,
            ai_services_connections=rest_obj.properties.ai_services_connections if rest_obj.properties else [],
            storage_connections=rest_obj.properties.storage_connections if rest_obj.properties else [],
            vector_store_connections=rest_obj.properties.vector_store_connections if rest_obj.properties else [],
            capability_host_kind=rest_obj.properties.capability_host_kind if rest_obj.properties else CapabilityHostKind.AGENTS,
        )
        return capability_host
    
    def _to_rest_object_for_hub(self) -> RestCapabilityHost:
        properties = RestCapabilityHostProperties(
                description = self.description,
                capability_host_kind = self.capability_host_kind
        )
        resource = RestCapabilityHost(
            properties=properties,
        )
        return resource
    
    def _to_rest_object_for_project(self) -> RestCapabilityHost:
        properties = RestCapabilityHostProperties(
                ai_services_connections = self.ai_services_connections,
                storage_connections = self.storage_connections,
                vector_store_connections = self.vector_store_connections,
                description = self.description,
                capability_host_kind = self.capability_host_kind
        )
        resource = RestCapabilityHost(
            properties=properties,
        )
        return resource