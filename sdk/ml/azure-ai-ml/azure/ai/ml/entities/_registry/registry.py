# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, List, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import Registry as RestRegistry
from azure.ai.ml._schema.registry.registry import RegistrySchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import load_from_dict

from .registry_support_classes import RegistryRegionArmDetails


class Registry(Resource):
    def __init__(
        self,
        *,
        name: str,
        id: str,
        location: str,
        description: str = None,
        tags: Dict[str, str] = None,
        public_network_access: str = None,
        discovery_url: str = None,
        intellectual_property_publisher: str = None,
        managed_resource_group: str = None,
        mlflow_registry_uri: str = None,
        region_details: List[RegistryRegionArmDetails],
        **kwargs,
    ):

        """Azure ML registry.

        :param name: Name of the registry. Must be globally unique and is immutable.
        :type name: str
        :param tags: Tags of the registry.
        :type tags: dict
        :param id: Registry ID.
        :type id: str
        :param location: The location this registry resource is located in.
        :type location: str
        :param description: Description of the registry.
        :type description: str
        :param public_network_access: Whether to allow public endpoint connectivity.
        :type public_network_access: str
        :param intellectual_property_publisher: Intellectual property publisher.
        :type intellectual_property_publisher: str
        :param managed_resource_group: Managed resource group created for the registry.
        :type managed_resource_group: str
        :param private_link_count: Private link count.
        :type private_link_count: int
        :param region_details: Details of each region the registry is in.
        :type region_details: List[RegistryRegionArmDetails]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """

        super().__init__(name=name, description=description, tags=tags, **kwargs)

        self.id = id
        self.location = location
        self.region_details = region_details
        self.public_network_access = public_network_access
        self.intellectual_property_publisher = intellectual_property_publisher
        self.managed_resource_group = managed_resource_group
        self.private_link_count = private_link_count
        self.discovery_url = discovery_url
        self.mlflow_registry_uri = mlflow_registry_uri

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]]) -> None:
        """Dump the registry spec into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return RegistrySchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Registry":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(RegistrySchema, data, context, **kwargs)
        # TODO - ensure that top-level location, if set, exists among managed locations, throw error otherwise.
        return Registry(**loaded_schema)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestRegistry) -> "Registry":
        if not rest_obj:
            return None
        # real_registry = RestRegistry.properties
        raise NotImplementedError()
