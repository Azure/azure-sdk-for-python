# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access

from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, List, Optional, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import ManagedServiceIdentity as RestManagedServiceIdentity
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    ManagedServiceIdentityType as RestManagedServiceIdentityType,
)
from azure.ai.ml._restclient.v2022_10_01_preview.models import Registry as RestRegistry
from azure.ai.ml._restclient.v2022_10_01_preview.models import RegistryProperties
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import load_from_dict

from .registry_support_classes import RegistryRegionDetails

CONTAINER_REGISTRY = "container_registry"
REPLICATION_LOCATIONS = "replication_locations"
INTELLECTUAL_PROPERTY = "intellectual_property"


class Registry(Resource):
    def __init__(
        self,
        *,
        name: str,
        location: str,
        identity: Optional[IdentityConfiguration] = None,
        tags: Optional[Dict[str, str]] = None,
        public_network_access: Optional[str] = None,
        discovery_url: Optional[str] = None,
        intellectual_property: Optional[IntellectualProperty] = None,
        managed_resource_group: Optional[str] = None,
        mlflow_registry_uri: Optional[str] = None,
        replication_locations: List[RegistryRegionDetails],
        **kwargs,
    ):
        """Azure ML registry.

        :param name: Name of the registry. Must be globally unique and is immutable.
        :type name: str
        :param location: The location this registry resource is located in.
        :type location: str
        :param identity: registry's System Managed Identity
        :type identity: ManagedServiceIdentity
        :param tags: Tags of the registry.
        :type tags: dict
        :param public_network_access: Whether to allow public endpoint connectivity.
        :type public_network_access: str
        :param discovery_url: Backend service base url for the registry.
        :type discovery_url: str
        :param intellectual_property_publisher: Intellectual property publisher.
        :type intellectual_property_publisher: str
        :param managed_resource_group: Managed resource group created for the registry.
        :type managed_resource_group: str
        :param mlflow_registry_uri: Ml flow tracking uri for the registry.
        :type mlflow_registry_uri: str
        :param region_details: Details of each region the registry is in.
        :type region_details: List[RegistryRegionDetails]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """

        super().__init__(name=name, tags=tags, **kwargs)

        # self.display_name = name # Do we need a top-level visible name value?
        self.location = location
        self.identity = identity
        self.replication_locations = replication_locations
        self.public_network_access = public_network_access
        self.intellectual_property = intellectual_property
        self.managed_resource_group = managed_resource_group
        self.discovery_url = discovery_url
        self.mlflow_registry_uri = mlflow_registry_uri
        self.container_registry = None

    def dump(
        self,
        dest: Union[str, PathLike, IO[AnyStr]],
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        """Dump the registry spec into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False)

    # The internal structure of the registry object is closer to how it's
    # represented by the registry API, which differs from how registries
    # are represented in YAML. This function converts those differences.
    def _to_dict(self) -> Dict:
        # JIT import to avoid experimental warnings on unrelated calls
        from azure.ai.ml._schema.registry.registry import RegistrySchema

        # pylint: disable=no-member
        schema = RegistrySchema(context={BASE_PATH_CONTEXT_KEY: "./"})

        # Grab the first acr account of the first region and set that
        # as the system-wide container registry.
        # Although support for multiple ACRs per region, as well as
        # different ACRs per region technically exist according to the
        # API schema, we do not want to surface that as an option,
        # since the use cases for variable/multiple ACRs are extremely
        # limited, and would probably just confuse most users.
        if self.replication_locations and len(self.replication_locations) > 0:
            if self.replication_locations[0].acr_config and len(self.replication_locations[0].acr_config) > 0:
                self.container_registry = self.replication_locations[0].acr_config[0]

        return schema.dump(self)

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Registry":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        # JIT import to avoid experimental warnings on unrelated calls
        from azure.ai.ml._schema.registry.registry import RegistrySchema

        loaded_schema = load_from_dict(RegistrySchema, data, context, **kwargs)
        cls._convert_yaml_dict_to_entity_input(loaded_schema)
        return Registry(**loaded_schema)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestRegistry) -> "Registry":
        if not rest_obj:
            return None
        real_registry = rest_obj.properties

        # Convert from api name region_details to user-shown name "replication locations"
        replication_locations = []
        if real_registry and real_registry.region_details:
            replication_locations = [
                RegistryRegionDetails._from_rest_object(details)
                for details in real_registry.region_details  # pylint: disable=protected-access
            ]
        identity = None
        if rest_obj.identity and isinstance(rest_obj.identity, RestManagedServiceIdentity):
            identity = IdentityConfiguration._from_rest_object(rest_obj.identity)
        return Registry(
            name=rest_obj.name,
            identity=identity,
            id=rest_obj.id,
            tags=rest_obj.tags,
            location=rest_obj.location,
            public_network_access=real_registry.public_network_access,
            discovery_url=real_registry.discovery_url,
            intellectual_property=IntellectualProperty(publisher=real_registry.intellectual_property_publisher)
            if real_registry.intellectual_property_publisher
            else None,
            managed_resource_group=real_registry.managed_resource_group,
            mlflow_registry_uri=real_registry.ml_flow_registry_uri,
            replication_locations=replication_locations,
        )

    # There are differences between what our registry validation schema
    # accepts, and how we actually represent things internally.
    # This is mostly due to the compromise required to balance
    # the actual shape of registries as they're defined by
    # autorest with how the spec wanted users to be able to
    # configure them. This function should eventually be
    @classmethod
    def _convert_yaml_dict_to_entity_input(
        cls,
        input: Dict,  # pylint: disable=redefined-builtin
    ):
        # pop container_registry value.
        global_acr_exists = False
        if CONTAINER_REGISTRY in input:
            acr_input = input.pop(CONTAINER_REGISTRY)
            global_acr_exists = True
        for region_detail in input[REPLICATION_LOCATIONS]:
            # Apply container_registry as acr_config of each region detail
            if global_acr_exists:
                if not hasattr(region_detail, "acr_details") or len(region_detail.acr_details) == 0:
                    region_detail.acr_config = [acr_input]

    def _to_rest_object(self) -> RestRegistry:
        """Build current parameterized schedule instance to a registry object before submission.

        :return: Rest registry.
        """
        identity = RestManagedServiceIdentity(type=RestManagedServiceIdentityType.SYSTEM_ASSIGNED)
        replication_locations = []
        if self.replication_locations:
            replication_locations = [details._to_rest_object() for details in self.replication_locations]
        # Notes about this construction.
        # RestRegistry.properties.tags: this property exists due to swagger inheritance
        # issues, don't actually use it, use top level RestRegistry.tags instead
        # RestRegistry.properties.managed_resource_group_tags: Registries create a
        # managed resource group to manage their internal sub-resources.
        # We always want the tags on this MRG to match those of the registry itself
        # to keep janitor policies aligned.
        return RestRegistry(
            name=self.name,
            location=self.location,
            identity=identity,
            tags=self.tags,
            properties=RegistryProperties(
                public_network_access=self.public_network_access,
                discovery_url=self.discovery_url,
                intellectual_property_publisher=(self.intellectual_property.publisher)
                if self.intellectual_property
                else None,
                managed_resource_group=self.managed_resource_group,
                ml_flow_registry_uri=self.mlflow_registry_uri,
                region_details=replication_locations,
                managed_resource_group_tags=self.tags,
            ),
        )
