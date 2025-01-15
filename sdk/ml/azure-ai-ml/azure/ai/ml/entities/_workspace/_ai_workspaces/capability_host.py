# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from os import PathLike
from typing import (
    List,
    Optional,
    Union,
    IO,
    Any,
    AnyStr,
    Dict,
)
from pathlib import Path
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.constants._workspace import CapabilityHostKind
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
)

from azure.ai.ml._schema.workspace.ai_workspaces.capability_host import (
    CapabilityHostSchema,
)
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._restclient.v2024_10_01_preview.models._models_py3 import (
    CapabilityHost as RestCapabilityHost,
)
from azure.ai.ml._restclient.v2024_10_01_preview.models._models_py3 import (
    CapabilityHostProperties as RestCapabilityHostProperties,
)


@experimental
class CapabilityHost(Resource):
    """Initialize a CapabilityHost instance.
    Capabilityhost management is controlled by MLClient's capabilityhosts operations.

    :param name: The name of the capability host.
    :type name: str
    :param description: The description of the capability host.
    :type description: Optional[str]
    :param vector_store_connections: A list of vector store  (AI Search) connections.
    :type vector_store_connections: Optional[List[str]]
    :param ai_services_connections: A list of OpenAI service connection.
    :type ai_services_connections: Optional[List[str]]
    :param storage_connections: A list of storage connections. Default storage connection value is
        projectname/workspaceblobstore for project workspace.
    :type storage_connections: Optional[List[str]]
    :param capability_host_kind: The kind of capability host, either as a string or CapabilityHostKind enum.
        Default is AGENTS.
    :type capability_host_kind: Union[str, CapabilityHostKind]
    :param kwargs: Additional keyword arguments.
    :type kwargs: Any

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_capability_host.py
            :start-after: [START capability_host_object_create]
            :end-before: [END capability_host_object_create]
            :language: python
            :dedent: 8
            :caption: Create a CapabilityHost object.
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        vector_store_connections: Optional[List[str]] = None,
        ai_services_connections: Optional[List[str]] = None,
        storage_connections: Optional[List[str]] = None,
        capability_host_kind: Union[str, CapabilityHostKind] = CapabilityHostKind.AGENTS,
        **kwargs: Any,
    ):
        super().__init__(name=name, description=description, **kwargs)
        self.capability_host_kind = capability_host_kind
        self.ai_services_connections = ai_services_connections
        self.storage_connections = storage_connections
        self.vector_store_connections = vector_store_connections

    def dump(
        self,
        dest: Optional[Union[str, PathLike, IO[AnyStr]]],
        **kwargs: Any,
    ) -> None:
        """Dump the CapabilityHost content into a file in yaml format.

        :param dest: The destination to receive this CapabilityHost's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        """Dump the object into a dictionary.

        :return: Dictionary representation of the object.
        :rtype: Dict
        """

        return CapabilityHostSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load(
        cls,
        data: Optional[dict] = None,
        yaml_path: Optional[Union[os.PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "CapabilityHost":
        """Load a capabilityhost object from a yaml file.

        :param cls: Indicates that this is a class method.
        :type cls: class
        :param data: Data Dictionary, defaults to None
        :type data: Dict
        :param yaml_path: YAML Path, defaults to None
        :type yaml_path: Union[PathLike, str]
        :param params_override: Fields to overwrite on top of the yaml file.
            Format is [{"field1": "value1"}, {"field2": "value2"}], defaults to None
        :type params_override: List[Dict]
        :raises Exception: An exception
        :return: Loaded CapabilityHost object.
        :rtype: ~azure.ai.ml.entities._workspace._ai_workspaces.capability_host.CapabilityHost
        """
        params_override = params_override or []
        data = data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return cls(**load_from_dict(CapabilityHostSchema, data, context, **kwargs))

    @classmethod
    def _from_rest_object(cls, rest_obj: RestCapabilityHost) -> "CapabilityHost":
        """Convert a REST object into a CapabilityHost object.

        :param cls: Indicates that this is a class method.
        :type cls: class
        :param rest_obj: The REST object to convert.
        :type rest_obj: ~azure.ai.ml._restclient.v2024_10_01_preview.models._models_py3.CapabilityHost
        :return: CapabilityHost object.
        :rtype: ~azure.ai.ml.entities._workspace._ai_workspaces.capability_host.CapabilityHost
        """
        capability_host = cls(
            name=str(rest_obj.name),
            description=(rest_obj.properties.description if rest_obj.properties else None),
            ai_services_connections=(rest_obj.properties.ai_services_connections if rest_obj.properties else None),
            storage_connections=(rest_obj.properties.storage_connections if rest_obj.properties else None),
            vector_store_connections=(rest_obj.properties.vector_store_connections if rest_obj.properties else None),
            capability_host_kind=(
                rest_obj.properties.capability_host_kind if rest_obj.properties else CapabilityHostKind.AGENTS
            ),
        )
        return capability_host

    def _to_rest_object(self) -> RestCapabilityHost:
        """
        Convert the CapabilityHost instance to a RestCapabilityHost object.

        :return: A RestCapabilityHost object representing the capability host for a Hub or Project workspace.
        :rtype: azure.ai.ml._restclient.v2024_10_01_preview.models._models_py3.CapabilityHost
        """

        properties = RestCapabilityHostProperties(
            ai_services_connections=self.ai_services_connections,
            storage_connections=self.storage_connections,
            vector_store_connections=self.vector_store_connections,
            description=self.description,
            capability_host_kind=self.capability_host_kind,
        )
        resource = RestCapabilityHost(
            properties=properties,
        )
        return resource
