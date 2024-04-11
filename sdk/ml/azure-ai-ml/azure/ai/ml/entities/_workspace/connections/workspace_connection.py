# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import warnings
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Type, Union, cast

from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    WorkspaceConnectionPropertiesV2BasicResource as RestWorkspaceConnection,
)
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ConnectionCategory,
    NoneAuthTypeWorkspaceConnectionProperties,
)
from azure.ai.ml._schema.workspace.connections.workspace_connection import WorkspaceConnectionSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import _snake_to_camel, camel_to_snake, dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, WorkspaceConnectionTypes
from azure.ai.ml.entities._credentials import (
    AccessKeyConfiguration,
    ApiKeyConfiguration,
    ManagedIdentityConfiguration,
    NoneCredentialConfiguration,
    PatTokenConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
    UsernamePasswordConfiguration,
    _BaseIdentityConfiguration,
)
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict


# Dev note: The acceptable strings for the type field are all snake_cased versions of the string constants defined
# In the rest client enum defined at _azure_machine_learning_services_enums.ConnectionCategory.
# We avoid directly referencing it in the docs to avoid restclient references.
@experimental
class WorkspaceConnection(Resource):
    """Azure ML workspace connection provides a secure way to store authentication and configuration information needed
    to connect and interact with the external resources.

    Note: For connections to OpenAI, Cognitive Search, and Cognitive Services, use the respective subclasses
    (ex: ~azure.ai.ml.entities.OpenAIWorkspaceConnection) instead of instantiating this class directly.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param type: The category of external resource for this connection.
    :type type: The type of workspace connection, possible values are: "git", "python_feed", "container_registry",
        "feature_store", "s3", "snowflake", "azure_sql_db", "azure_synapse_analytics", "azure_my_sql_db",
        "azure_postgres_db", "adls_gen_2", "azure_one_lake", "custom".
    :param credentials: The credentials for authenticating to the external resource. Note that certain connection
        types (as defined by the type input) only accept certain types of credentials.
    :type credentials: Union[
        ~azure.ai.ml.entities.PatTokenConfiguration,
        ~azure.ai.ml.entities.SasTokenConfiguration,
        ~azure.ai.ml.entities.UsernamePasswordConfiguration,
        ~azure.ai.ml.entities.ManagedIdentityConfiguration
        ~azure.ai.ml.entities.ServicePrincipalConfiguration,
        ~azure.ai.ml.entities.AccessKeyConfiguration,
        ~azure.ai.ml.entities.ApiKeyConfiguration
        ]
    :param is_shared: For connections in lean workspaces, this controls whether or not this connection
        is shared amongst other lean workspaces that are shared by the parent hub. Defaults to true.
    :type is_shared: bool
    """

    def __init__(
        self,
        *,
        target: str,
        # TODO : Check if this is okay since it shadows builtin-type type
        type: str,  # pylint: disable=redefined-builtin
        credentials: Union[
            PatTokenConfiguration,
            SasTokenConfiguration,
            UsernamePasswordConfiguration,
            ManagedIdentityConfiguration,
            ServicePrincipalConfiguration,
            AccessKeyConfiguration,
            ApiKeyConfiguration,
        ],
        is_shared: bool = True,
        **kwargs: Any,
    ):

        # Dev note: This initializer has an undocumented kwarg "from_child" to determine if this initialization
        # is from a child class.
        # This kwarg is required to allow instantiation of types that are associated with subtypes without a
        # warning printout.
        # The additional undocumented kwarg "strict_typing" turns the warning into a value error.
        from_child = kwargs.pop("from_child", False)
        strict_typing = kwargs.pop("strict_typing", False)
        correct_class = WorkspaceConnection._get_entity_class_from_type(type)
        if not from_child and correct_class != WorkspaceConnection:
            if strict_typing:
                raise ValueError(
                    f"Cannot instantiate a base WorkspaceConnection with a type of {type}. "
                    f"Please use the appropriate subclass {correct_class.__name__} instead."
                )
            warnings.warn(
                f"The workspace connection of {type} has additional fields and should not be instantiated directly "
                f"from the WorkspaceConnection class. Please use its subclass {correct_class.__name__} instead.",
            )

        super().__init__(**kwargs)

        self.type = type
        self._target = target
        self._credentials = credentials
        self._is_shared = is_shared

    @property
    def type(self) -> Optional[str]:
        """Type of the workspace connection, supported are 'git', 'python_feed' and 'container_registry'.

        :return: Type of the job.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        """Set the type of the workspace connection, supported are 'git', 'python_feed' and 'container_registry'.

        :param value: value for the type of workspace connection.
        :type: str
        """
        if not value:
            return
        self._type: Optional[str] = camel_to_snake(value)

    @property
    def target(self) -> str:
        """Target url for the workspace connection.

        :return: Target of the workspace connection.
        :rtype: str
        """
        return self._target

    @property
    def credentials(
        self,
    ) -> Union[
        PatTokenConfiguration,
        SasTokenConfiguration,
        UsernamePasswordConfiguration,
        ManagedIdentityConfiguration,
        ServicePrincipalConfiguration,
        AccessKeyConfiguration,
        ApiKeyConfiguration,
    ]:
        """Credentials for workspace connection.

        :return: Credentials for workspace connection.
        :rtype: Union[
            ~azure.ai.ml.entities.PatTokenConfiguration,
            ~azure.ai.ml.entities.SasTokenConfiguration,
            ~azure.ai.ml.entities.UsernamePasswordConfiguration,
            ~azure.ai.ml.entities.ManagedIdentityConfiguration
            ~azure.ai.ml.entities.ServicePrincipalConfiguration,
            ~azure.ai.ml.entities.AccessKeyConfiguration,
            ~azure.ai.ml.entities.ApiKeyConfiguration

        ]
        """
        return self._credentials

    @property
    def metadata(self) -> Dict[str, Any]:
        """Deprecated. Use tags.
        :return: This connection's tags.
        :rtype: Dict[str, Any]
        """
        return self.tags if self.tags is not None else {}

    @metadata.setter
    def metadata(self, value: Dict[str, Any]) -> None:
        """Deprecated. Use tags.
        :param value: The new metadata for connection.
            This completely overwrites the existing tags/metadata dictionary.
        :type value: Dict[str, Any]
        """
        if not value:
            return
        self.tags = value

    @property
    def is_shared(self) -> bool:
        """Get the Boolean describing if this connection is shared amongst its cohort within a workspace hub.
        Only applicable for connections created within a lean workspace.

        :rtype: bool
        """
        return self._is_shared

    @is_shared.setter
    def is_shared(self, value: bool) -> None:
        """Assign the is_shared property of the connection, determining if it is shared amongst other lean workspaces
        within its parent workspace hub. Only applicable for connections created within a lean workspace workspace.

        :param value: The new is_shared value.
        :type value: bool
        """
        if not value:
            return
        self._is_shared = value

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the workspace connection spec into a file in yaml format.

        :param dest: The destination to receive this workspace connection's spec.
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

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "WorkspaceConnection":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return cls._load_from_dict(data=data, context=context, **kwargs)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "WorkspaceConnection":
        conn_type = data["type"] if "type" in data else None
        schema_class = cls._get_schema_class_from_type(conn_type)
        loaded_data: WorkspaceConnection = load_from_dict(schema_class, data, context, **kwargs)
        return loaded_data

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        schema_class = WorkspaceConnection._get_schema_class_from_type(self.type)
        # Not sure what this pylint complaint was about, probably due to the polymorphic
        # tricks at play. Disabling since testing indicates no issue.
        # pylint: disable-next=missing-kwoa
        res: dict = schema_class(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspaceConnection) -> Optional["WorkspaceConnection"]:
        if not rest_obj:
            return None

        conn_cat = rest_obj.properties.category
        conn_class = cls._get_entity_class_from_type(conn_cat)

        popped_tags = conn_class._get_required_metadata_fields()

        rest_kwargs = cls._extract_kwargs_from_rest_obj(rest_obj=rest_obj, popped_tags=popped_tags)
        # Check for alternative name for custom connection type (added for client clarity).
        if rest_kwargs["type"].lower() == camel_to_snake(ConnectionCategory.CUSTOM_KEYS).lower():
            rest_kwargs["type"] = WorkspaceConnectionTypes.CUSTOM
        workspace_connection = conn_class(**rest_kwargs)
        return cast(Optional["WorkspaceConnection"], workspace_connection)

    def _validate(self) -> str:
        return str(self.name)

    def _to_rest_object(self) -> RestWorkspaceConnection:
        workspace_connection_properties_class: Any = NoneAuthTypeWorkspaceConnectionProperties
        if self._credentials:
            workspace_connection_properties_class = self._credentials._get_rest_properties_class()
        # Convert from human readable type to corresponding api enum if needed.
        conn_type = self.type
        if conn_type == WorkspaceConnectionTypes.CUSTOM:
            conn_type = ConnectionCategory.CUSTOM_KEYS

        # No credential property bag uniquely has different inputs from ALL other property bag classes.
        if workspace_connection_properties_class == NoneAuthTypeWorkspaceConnectionProperties:
            properties = workspace_connection_properties_class(
                target=self.target,
                metadata=self.tags,
                category=_snake_to_camel(conn_type),
                is_shared_to_all=self.is_shared,
            )
        else:
            properties = workspace_connection_properties_class(
                target=self.target,
                credentials=self.credentials._to_workspace_connection_rest_object() if self._credentials else None,
                metadata=self.tags,
                category=_snake_to_camel(conn_type),
                is_shared_to_all=self.is_shared,
            )

        return RestWorkspaceConnection(properties=properties)

    @classmethod
    def _extract_kwargs_from_rest_obj(cls, rest_obj: RestWorkspaceConnection, popped_tags: List[str]) -> Dict[str, str]:
        """Internal helper function with extracts all the fields needed to initialize a workspace connection object
        from its associated restful object. Pulls extra fields based on the supplied popped_tags. Returns all the
        fields as a dictionary, which is expected to then be supplied to a workspace connection initializer as kwargs.

        :param rest_obj: The rest object representation of a workspace connection
        :type rest_obj: RestWorkspaceConnection
        :param popped_tags: Tags that should be pulled from the rest object's metadata and injected as top-level
            fields into the connection's initializer. Needed for subclasses that require extra inputs compared
            to the base WorkspaceConnection class.
        :type popped_tags: List[str]

        :return: A dictionary containing all kwargs needed to construct a workspace connection.
        :rtype: Dict[str, str]
        """
        properties = rest_obj.properties
        credentials: Any = None

        credentials_class = _BaseIdentityConfiguration._get_credential_class_from_rest_type(properties.auth_type)
        if credentials_class is not NoneCredentialConfiguration:
            credentials = credentials_class._from_workspace_connection_rest_object(properties.credentials)

        tags = properties.metadata if hasattr(properties, "metadata") else None
        rest_kwargs = {
            "id": rest_obj.id,
            "name": rest_obj.name,
            "target": properties.target,
            "creation_context": SystemData._from_rest_object(rest_obj.system_data) if rest_obj.system_data else None,
            "type": camel_to_snake(properties.category),
            "credentials": credentials,
            "tags": tags,
            "is_shared": properties.is_shared_to_all if hasattr(properties, "is_shared_to_all") else True,
        }

        for name in popped_tags:
            if name in tags:
                rest_kwargs[camel_to_snake(name)] = tags[name]
        return rest_kwargs

    @classmethod
    def _get_entity_class_from_type(cls, conn_type: Optional[str]) -> Type:
        """Helper function that converts a rest client connection category into the associated
        workspace connection class or subclass. Accounts for potential snake/camel case and
        capitalization differences.

        :param conn_type: The desired connection type represented as a string. This
        should align with the 'connection_category' enum field defined in the rest client, but
        can be in snake or camel case.
        :type conn_type: str

        :return: The workspace connection class the conn_type corresponds to.
        :rtype: Type
        """
        if conn_type is None:
            return WorkspaceConnection
        # Imports are done here to avoid circular imports on load.
        from .workspace_connection_subtypes import (
            AzureAISearchWorkspaceConnection,
            AzureAIServiceWorkspaceConnection,
            AzureBlobStoreWorkspaceConnection,
            AzureOpenAIWorkspaceConnection,
        )

        # Connection categories don't perfectly follow perfect camel casing, so lower
        # case everything to avoid problems.
        CONNECTION_CATEGORY_TO_SUBCLASS_MAP = {
            ConnectionCategory.AZURE_OPEN_AI.lower(): AzureOpenAIWorkspaceConnection,
            ConnectionCategory.COGNITIVE_SEARCH.lower(): AzureAISearchWorkspaceConnection,
            ConnectionCategory.COGNITIVE_SERVICE.lower(): AzureAIServiceWorkspaceConnection,
            ConnectionCategory.AZURE_BLOB.lower(): AzureBlobStoreWorkspaceConnection,
        }
        cat = _snake_to_camel(conn_type).lower()
        return CONNECTION_CATEGORY_TO_SUBCLASS_MAP.get(cat, WorkspaceConnection)

    @classmethod
    def _get_schema_class_from_type(cls, conn_type: Optional[str]) -> Type:
        """Helper function that converts a rest client connection category into the associated
        workspace connection schema class or subclass. Accounts for potential snake/camel case and
        capitalization differences.

        :param conn_type: The connection type.
        :type conn_type: str

        :return: The workspace connection schema class the conn_type corresponds to.
        :rtype: Type
        """
        if conn_type is None:
            return WorkspaceConnectionSchema
        entity_class = cls._get_entity_class_from_type(conn_type)
        return entity_class._get_schema_class()

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        """Helper function that returns the required metadata fields for specific workspace
        connection type. This parent function returns nothing, but needs to be overwritten by child
        classes, which are created under the expectation that they have extra fields that need to be
        accounted for.

        :return: A list of the required metadata fields for the specific workspace connection type.
        :rtype: List[str]
        """
        return []

    @classmethod
    def _get_schema_class(cls) -> Type:
        """Helper function that maps this class to its associated schema class. Needs to be overridden by
        child classes to allow the base class to be polymorphic in its schema reading.

        :return: The appropriate schema class to use with this entity class.
        :rtype: Type
        """
        return WorkspaceConnectionSchema
