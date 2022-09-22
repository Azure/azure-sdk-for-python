# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, List, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import ManagedServiceIdentity as RestManagedServiceIdentity
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    ManagedServiceIdentityType as RestManagedServiceIdentityType,
)
from azure.ai.ml._restclient.v2022_10_01_preview.models import Registry as RestRegistry
from azure.ai.ml._restclient.v2022_10_01_preview.models import RegistryProperties
from azure.ai.ml._schema.registry.registry import RegistrySchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._registry.identity import ManagedServiceIdentity
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import load_from_dict

from .registry_support_classes import RegistryRegionArmDetails

YAML_REGION_DETAILS = "replication_locations"
YAML_SINGLE_ACR_DETAIL = "container_registry"
CLASS_REGION_DETAILS = "region_details"


class Registry(Resource):
    def __init__(
        self,
        *,
        name: str,
        location: str,
        identity: ManagedServiceIdentity = None,
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
        :param region_details: Details of each region the registry is in.
        :type region_details: List[RegistryRegionArmDetails]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """

        super().__init__(name=name, description=description, tags=tags, **kwargs)

        # self.display_name = name # Do we need a top-level visible name value?
        self.location = location
        self.identity = identity
        self.region_details = region_details
        self.public_network_access = public_network_access
        self.intellectual_property_publisher = intellectual_property_publisher
        self.managed_resource_group = managed_resource_group
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
        cls._convert_yaml_dict_to_entity_input(loaded_schema)
        # https://dev.azure.com/msdata/Vienna/_workitems/edit/1971490/
        # TODO - ensure that top-level location, if set, exists among managed locations, throw error otherwise.
        return Registry(**loaded_schema)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestRegistry) -> "Registry":
        if not rest_obj:
            return None
        real_registry = rest_obj.properties

        region_details = []
        if real_registry.region_details:
            region_details = [
                RegistryRegionArmDetails._from_rest_object(details) for details in real_registry.region_details
            ]
        identity = None
        if rest_obj.identity and isinstance(rest_obj.identity, RestManagedServiceIdentity):
            identity = ManagedServiceIdentity._from_rest_object(rest_obj.identity)
        return Registry(
            name=rest_obj.name,
            description=real_registry.description,
            identity=identity,
            tags=real_registry.tags,
            location=rest_obj.location,
            public_network_access=real_registry.public_network_access,
            discovery_url=real_registry.discovery_url,
            intellectual_property_publisher=real_registry.intellectual_property_publisher,
            managed_resource_group=real_registry.managed_resource_group,
            mlflow_registry_uri=real_registry.ml_flow_registry_uri,
            region_details=region_details,
        )

    # There are differences between what our registry validation schema
    # accepts, and how we actually represent things internally.
    # This is mostly due to the compromise required to balance
    # the actual shape of registries as they're defined by
    # autorest with how the spec wanted users to be able to
    # configure them
    @classmethod
    def _convert_yaml_dict_to_entity_input(cls, input: Dict):
        # change replication_locations to region_details
        global_acr_exists = False
        if YAML_REGION_DETAILS in input:
            input[CLASS_REGION_DETAILS] = input.pop(YAML_REGION_DETAILS)
        if YAML_SINGLE_ACR_DETAIL in input:
            acr_input = input.pop(YAML_SINGLE_ACR_DETAIL)
            global_acr_exists = True
        for region_detail in input[CLASS_REGION_DETAILS]:
            if global_acr_exists:
                if not hasattr(region_detail, "acr_details") or len(region_detail.acr_details) == 0:
                    region_detail.acr_config = [acr_input]

    def _to_rest_object(self) -> RestRegistry:
        """Build current parameterized schedule instance to a registry object before submission.

        :return: Rest registry.
        """
        identity = RestManagedServiceIdentity(type=RestManagedServiceIdentityType.SYSTEM_ASSIGNED)
        region_details = []
        if self.region_details:
            region_details = [details._to_rest_object() for details in self.region_details]
        return RestRegistry(
            name=self.name,
            location=self.location,
            identity=identity,
            properties=RegistryProperties(
                description=self.description,
                tags=self.tags,
                public_network_access=self.public_network_access,
                discovery_url=self.discovery_url,
                intellectual_property_publisher=self.intellectual_property_publisher,
                managed_resource_group=self.managed_resource_group,
                ml_flow_registry_uri=self.mlflow_registry_uri,
                region_details=region_details,
            ),
        )
