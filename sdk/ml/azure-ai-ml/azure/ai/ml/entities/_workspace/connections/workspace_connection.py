# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import warnings
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Type, Union, cast


from azure.ai.ml._restclient.v2024_04_01_preview.models import (
    WorkspaceConnectionPropertiesV2BasicResource as RestWorkspaceConnection,
)
from azure.ai.ml._restclient.v2024_04_01_preview.models import (
    ConnectionCategory,
    NoneAuthTypeWorkspaceConnectionProperties,
    AADAuthTypeWorkspaceConnectionProperties,
)

from azure.ai.ml._schema.workspace.connections.workspace_connection import WorkspaceConnectionSchema
from azure.ai.ml._utils.utils import _snake_to_camel, camel_to_snake, dump_yaml_to_file
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    ConnectionTypes,
    CognitiveServiceKinds,
    CONNECTION_KIND_KEY,
    CONNECTION_RESOURCE_ID_KEY,
)
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
    AccountKeyConfiguration,
    AadCredentialConfiguration,
)
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict


CONNECTION_CATEGORY_TO_CREDENTIAL_MAP = {
    ConnectionCategory.AZURE_BLOB: [AccessKeyConfiguration, SasTokenConfiguration, AadCredentialConfiguration],
    ConnectionTypes.AZURE_DATA_LAKE_GEN_2: [
        ServicePrincipalConfiguration,
        AadCredentialConfiguration,
        ManagedIdentityConfiguration,
    ],
    ConnectionCategory.GIT: [PatTokenConfiguration, NoneCredentialConfiguration, UsernamePasswordConfiguration],
    ConnectionCategory.PYTHON_FEED: [UsernamePasswordConfiguration, PatTokenConfiguration, NoneCredentialConfiguration],
    ConnectionCategory.CONTAINER_REGISTRY: [ManagedIdentityConfiguration, UsernamePasswordConfiguration],
}

DATASTORE_CONNECTIONS = {
    ConnectionCategory.AZURE_BLOB,
    ConnectionTypes.AZURE_DATA_LAKE_GEN_2,
    ConnectionCategory.AZURE_ONE_LAKE,
}

CONNECTION_ALTERNATE_TARGET_NAMES = ["target", "api_base", "url", "azure_endpoint", "endpoint"]


# Dev note: The acceptable strings for the type field are all snake_cased versions of the string constants defined
# In the rest client enum defined at _azure_machine_learning_services_enums.ConnectionCategory.
# We avoid directly referencing it in the docs to avoid restclient references.
class WorkspaceConnection(Resource):
    """Azure ML connection provides a secure way to store authentication and configuration information needed
    to connect and interact with the external resources.

    Note: For connections to OpenAI, Cognitive Search, and Cognitive Services, use the respective subclasses
    (ex: ~azure.ai.ml.entities.OpenAIConnection) instead of instantiating this class directly.

    :param name: Name of the connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param metadata: Metadata dictionary.
    :type metadata: Optional[Dict[str, Any]]
    :param type: The category of external resource for this connection.
    :type type: The type of connection, possible values are: "git", "python_feed", "container_registry",
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
        ~azure.ai.ml.entities.ApiKeyConfiguration,
        ~azure.ai.ml.entities.NoneCredentialConfiguration
        ~azure.ai.ml.entities.AccountKeyConfiguration,
        ~azure.ai.ml.entities.AadCredentialConfiguration,
        None
        ]
    :param is_shared: For connections in project, this controls whether or not this connection
        is shared amongst other projects that are shared by the parent hub. Defaults to true.
    :type is_shared: bool
    """

    def __init__(
        self,
        *,
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
            NoneCredentialConfiguration,
            AccountKeyConfiguration,
            AadCredentialConfiguration,
        ],
        is_shared: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
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
                    f"Cannot instantiate a base Connection with a type of {type}. "
                    f"Please use the appropriate subclass {correct_class.__name__} instead."
                )
            warnings.warn(
                f"The connection of {type} has additional fields and should not be instantiated directly "
                f"from the Connection class. Please use its subclass {correct_class.__name__} instead.",
            )
        # This disgusting code allows for a variety of inputs names to technically all
        # act like the target field, while still maintaining the aggregate field as required.
        target = None
        for target_name in CONNECTION_ALTERNATE_TARGET_NAMES:
            target = kwargs.pop(target_name, target)
        if target is None and type not in {ConnectionCategory.SERP, ConnectionCategory.Open_AI}:
            raise ValueError("target is a required field for Connection.")

        tags = kwargs.pop("tags", None)
        if tags is not None:
            if metadata is not None:
                # Update tags updated with metadata to make sure metadata values are preserved in case of conflicts.
                tags.update(metadata)
                metadata = tags
                warnings.warn(
                    "Tags are a deprecated field for connections, use metadata instead. Since both "
                    + "metadata and tags are assigned, metadata values will take precedence in the event of conflicts."
                )
            else:
                metadata = tags
                warnings.warn("Tags are a deprecated field for connections, use metadata instead.")

        super().__init__(**kwargs)

        self.type = type
        self._target = target
        self._credentials = credentials
        self._is_shared = is_shared
        self._metadata = metadata
        self._validate_cred_for_conn_cat()

    def _validate_cred_for_conn_cat(self) -> None:
        """Given a connection type, ensure that the given credentials are valid for that connection type.
        Does not validate the actual data of the inputted credential, just that they are of the right class
        type.

        """
        # Convert none credentials to AAD credentials for datastore connection types.
        # The backend stores datastore aad creds as none, unlike other connection types with aad,
        # which actually list them as aad. This IS distinct from regular none credentials, or so I've been told,
        # so I will endeavor to smooth over that inconsistency here.
        converted_type = _snake_to_camel(self.type).lower()
        if self._credentials == NoneCredentialConfiguration() and any(
            converted_type == _snake_to_camel(item).lower() for item in DATASTORE_CONNECTIONS
        ):
            self._credentials = AadCredentialConfiguration()

        if self.type in CONNECTION_CATEGORY_TO_CREDENTIAL_MAP:
            allowed_credentials = CONNECTION_CATEGORY_TO_CREDENTIAL_MAP[self.type]
            if self.credentials is None and NoneCredentialConfiguration not in allowed_credentials:
                raise ValueError(
                    f"Cannot instantiate a Connection with a type of {self.type} and no credentials."
                    f"Please supply credentials from one of the following types: {allowed_credentials}."
                )
            cred_type = type(self.credentials)
            if cred_type not in allowed_credentials:
                raise ValueError(
                    f"Cannot instantiate a Connection with a type of {self.type} and credentials of type"
                    f" {cred_type}. Please supply credentials from one of the following types: {allowed_credentials}."
                )
        # For unknown types, just let the user do whatever they want.

    @property
    def type(self) -> Optional[str]:
        """Type of the connection, supported are 'git', 'python_feed' and 'container_registry'.

        :return: Type of the job.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        """Set the type of the connection, supported are 'git', 'python_feed' and 'container_registry'.

        :param value: value for the type of connection.
        :type: str
        """
        if not value:
            return
        self._type: Optional[str] = camel_to_snake(value)

    @property
    def target(self) -> Optional[str]:
        """Target url for the connection.

        :return: Target of the connection.
        :rtype: Optional[str]
        """
        return self._target

    @property
    def endpoint(self) -> Optional[str]:
        """Alternate name for the target of the connection,
        which is used by some connection subclasses.

        :return: The target of the connection.
        :rtype: str
        """
        return self.target

    @property
    def azure_endpoint(self) -> Optional[str]:
        """Alternate name for the target of the connection,
        which is used by some connection subclasses.

        :return: The target of the connection.
        :rtype: str
        """
        return self.target

    @property
    def url(self) -> Optional[str]:
        """Alternate name for the target of the connection,
        which is used by some connection subclasses.

        :return: The target of the connection.
        :rtype: str
        """
        return self.target

    @property
    def api_base(self) -> Optional[str]:
        """Alternate name for the target of the connection,
        which is used by some connection subclasses.

        :return: The target of the connection.
        :rtype: str
        """
        return self.target

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
        NoneCredentialConfiguration,
        AccountKeyConfiguration,
        AadCredentialConfiguration,
    ]:
        """Credentials for connection.

        :return: Credentials for connection.
        :rtype: Union[
            ~azure.ai.ml.entities.PatTokenConfiguration,
            ~azure.ai.ml.entities.SasTokenConfiguration,
            ~azure.ai.ml.entities.UsernamePasswordConfiguration,
            ~azure.ai.ml.entities.ManagedIdentityConfiguration
            ~azure.ai.ml.entities.ServicePrincipalConfiguration,
            ~azure.ai.ml.entities.AccessKeyConfiguration,
            ~azure.ai.ml.entities.ApiKeyConfiguration
            ~azure.ai.ml.entities.NoneCredentialConfiguration,
            ~azure.ai.ml.entities.AccountKeyConfiguration,
            ~azure.ai.ml.entities.AadCredentialConfiguration,
            ]
        """
        return self._credentials

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """The connection's metadata dictionary.
        :return: This connection's metadata.
        :rtype: Optional[Dict[str, Any]]
        """
        return self._metadata if self._metadata is not None else {}

    @metadata.setter
    def metadata(self, value: Optional[Dict[str, Any]]) -> None:
        """Set the metadata for the connection. Be warned that setting this will override
        ALL metadata values, including those implicitly set by certain connection types to manage their
        extra data. Usually, you should probably access the metadata dictionary, then add or remove values
        individually as needed.
        :param value: The new metadata for connection.
            This completely overwrites the existing metadata dictionary.
        :type value: Optional[Dict[str, Any]]
        """
        if not value:
            return
        self._metadata = value

    @property
    def tags(self) -> Optional[Dict[str, Any]]:
        """Deprecated. Use metadata instead.
        :return: This connection's metadata.
        :rtype: Optional[Dict[str, Any]]
        """
        return self._metadata if self._metadata is not None else {}

    @tags.setter
    def tags(self, value: Optional[Dict[str, Any]]) -> None:
        """Deprecated use metadata instead
        :param value: The new metadata for connection.
            This completely overwrites the existing metadata dictionary.
        :type value: Optional[Dict[str, Any]]
        """
        if not value:
            return
        self._metadata = value

    @property
    def is_shared(self) -> bool:
        """Get the Boolean describing if this connection is shared amongst its cohort within a hub.
        Only applicable for connections created within a project.

        :rtype: bool
        """
        return self._is_shared

    @is_shared.setter
    def is_shared(self, value: bool) -> None:
        """Assign the is_shared property of the connection, determining if it is shared amongst other projects
        within its parent hub. Only applicable for connections created within a project.

        :param value: The new is_shared value.
        :type value: bool
        """
        if not value:
            return
        self._is_shared = value

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the connection spec into a file in yaml format.

        :param dest: The destination to receive this connection's spec.
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
    def _from_rest_object(cls, rest_obj: RestWorkspaceConnection) -> "WorkspaceConnection":
        conn_class = cls._get_entity_class_from_rest_obj(rest_obj)

        popped_metadata = conn_class._get_required_metadata_fields()

        rest_kwargs = cls._extract_kwargs_from_rest_obj(rest_obj=rest_obj, popped_metadata=popped_metadata)
        # Check for alternative name for custom connection type (added for client clarity).
        if rest_kwargs["type"].lower() == camel_to_snake(ConnectionCategory.CUSTOM_KEYS).lower():
            rest_kwargs["type"] = ConnectionTypes.CUSTOM
        if rest_kwargs["type"].lower() == camel_to_snake(ConnectionCategory.ADLS_GEN2).lower():
            rest_kwargs["type"] = ConnectionTypes.AZURE_DATA_LAKE_GEN_2
        target = rest_kwargs.get("target", "")
        # This dumb code accomplishes 2 things.
        # It ensures that sub-classes properly input their target, regardless of which
        # arbitrary name they replace it with, while also still allowing our official
        # client specs to list those inputs as 'required'
        for target_name in CONNECTION_ALTERNATE_TARGET_NAMES:
            rest_kwargs[target_name] = target
        if rest_obj.properties.category == ConnectionCategory.AZURE_ONE_LAKE:
            # The microsoft one lake connection uniquely has client-only inputs
            # that aren't just an alternate name for the target.
            # This sets those inputs, that way the initializer can still
            # required those fields for users.
            rest_kwargs["artifact"] = ""
            rest_kwargs["one_lake_workspace_name"] = ""
        if rest_obj.properties.category == ConnectionTypes.AI_SERVICES_REST_PLACEHOLDER:
            # AI Services renames it's metadata field when surfaced to users and inputted
            # into it's initializer for clarity. ResourceId doesn't really tell much on its own.
            # No default in pop, this should fail if we somehow don't get a resource ID
            rest_kwargs["ai_services_resource_id"] = rest_kwargs.pop(camel_to_snake(CONNECTION_RESOURCE_ID_KEY))
        connection = conn_class(**rest_kwargs)
        return cast(WorkspaceConnection, connection)

    def _validate(self) -> str:
        return str(self.name)

    def _to_rest_object(self) -> RestWorkspaceConnection:
        connection_properties_class: Any = NoneAuthTypeWorkspaceConnectionProperties
        if self._credentials:
            connection_properties_class = self._credentials._get_rest_properties_class()
        # Convert from human readable type to corresponding api enum if needed.
        conn_type = self.type
        if conn_type == ConnectionTypes.CUSTOM:
            conn_type = ConnectionCategory.CUSTOM_KEYS
        elif conn_type == ConnectionTypes.AZURE_DATA_LAKE_GEN_2:
            conn_type = ConnectionCategory.ADLS_GEN2
        elif conn_type in {
            ConnectionTypes.AZURE_CONTENT_SAFETY,
            ConnectionTypes.AZURE_SPEECH_SERVICES,
        }:
            conn_type = ConnectionCategory.COGNITIVE_SERVICE
        elif conn_type == ConnectionTypes.AZURE_SEARCH:
            conn_type = ConnectionCategory.COGNITIVE_SEARCH
        elif conn_type == ConnectionTypes.AZURE_AI_SERVICES:
            # ConnectionCategory.AI_SERVICES category accidentally unpublished
            conn_type = ConnectionTypes.AI_SERVICES_REST_PLACEHOLDER
        # Some credential property bags have no credential input.
        if connection_properties_class in {
            NoneAuthTypeWorkspaceConnectionProperties,
            AADAuthTypeWorkspaceConnectionProperties,
        }:
            properties = connection_properties_class(
                target=self.target,
                metadata=self.metadata,
                category=_snake_to_camel(conn_type),
                is_shared_to_all=self.is_shared,
            )
        else:
            properties = connection_properties_class(
                target=self.target,
                credentials=self.credentials._to_workspace_connection_rest_object() if self._credentials else None,
                metadata=self.metadata,
                category=_snake_to_camel(conn_type),
                is_shared_to_all=self.is_shared,
            )

        return RestWorkspaceConnection(properties=properties)

    @classmethod
    def _extract_kwargs_from_rest_obj(
        cls, rest_obj: RestWorkspaceConnection, popped_metadata: List[str]
    ) -> Dict[str, str]:
        """Internal helper function with extracts all the fields needed to initialize a connection object
        from its associated restful object. Pulls extra fields based on the supplied `popped_metadata` input.
        Returns all the fields as a dictionary, which is expected to then be supplied to a
        connection initializer as kwargs.

        :param rest_obj: The rest object representation of a connection
        :type rest_obj: RestWorkspaceConnection
        :param popped_metadata: Key names that should be pulled from the rest object's metadata and
            injected as top-level fields into the client connection's initializer.
            This is needed for subclasses that require extra inputs compared to the base Connection class.
        :type popped_metadata: List[str]

        :return: A dictionary containing all kwargs needed to construct a connection.
        :rtype: Dict[str, str]
        """
        properties = rest_obj.properties
        credentials: Any = NoneCredentialConfiguration()

        credentials_class = _BaseIdentityConfiguration._get_credential_class_from_rest_type(properties.auth_type)
        # None and AAD auth types have a property bag class, but no credentials inside that.
        # Thankfully they both have no inputs.

        if credentials_class is AadCredentialConfiguration:
            credentials = AadCredentialConfiguration()
        elif credentials_class is not NoneCredentialConfiguration:
            credentials = credentials_class._from_workspace_connection_rest_object(properties.credentials)

        metadata = properties.metadata if hasattr(properties, "metadata") else {}
        rest_kwargs = {
            "id": rest_obj.id,
            "name": rest_obj.name,
            "target": properties.target,
            "creation_context": SystemData._from_rest_object(rest_obj.system_data) if rest_obj.system_data else None,
            "type": camel_to_snake(properties.category),
            "credentials": credentials,
            "metadata": metadata,
            "is_shared": properties.is_shared_to_all if hasattr(properties, "is_shared_to_all") else True,
        }

        for name in popped_metadata:
            if name in metadata:
                rest_kwargs[camel_to_snake(name)] = metadata[name]
        return rest_kwargs

    @classmethod
    def _get_entity_class_from_type(cls, type: str) -> Type:
        """Helper function that derives the correct connection class given the client or server type.
        Differs slightly from the rest object version in that it doesn't need to account for
        rest object metadata.

        This reason there are two functions at all is due to certain API connection types that
        are obfuscated with different names when presented to the client. These types are
        accounted for in the ConnectionTypes class in the constants file.

        :param type: The type string describing the connection.
        :type type: str

        :return: Theconnection class the conn_type corresponds to.
        :rtype: Type
        """
        from .connection_subtypes import (
            AzureBlobStoreConnection,
            MicrosoftOneLakeConnection,
            AzureOpenAIConnection,
            AzureAIServicesConnection,
            AzureAISearchConnection,
            AzureContentSafetyConnection,
            AzureSpeechServicesConnection,
            APIKeyConnection,
            OpenAIConnection,
            SerpConnection,
            ServerlessConnection,
        )

        conn_type = _snake_to_camel(type).lower()
        if conn_type is None:
            return WorkspaceConnection

        # Connection categories don't perfectly follow perfect camel casing, so lower
        # case everything to avoid problems.
        CONNECTION_CATEGORY_TO_SUBCLASS_MAP = {
            ConnectionCategory.AZURE_OPEN_AI.lower(): AzureOpenAIConnection,
            ConnectionCategory.AZURE_BLOB.lower(): AzureBlobStoreConnection,
            ConnectionCategory.AZURE_ONE_LAKE.lower(): MicrosoftOneLakeConnection,
            ConnectionCategory.API_KEY.lower(): APIKeyConnection,
            ConnectionCategory.OPEN_AI.lower(): OpenAIConnection,
            ConnectionCategory.SERP.lower(): SerpConnection,
            ConnectionCategory.SERVERLESS.lower(): ServerlessConnection,
            _snake_to_camel(ConnectionTypes.AZURE_CONTENT_SAFETY).lower(): AzureContentSafetyConnection,
            _snake_to_camel(ConnectionTypes.AZURE_SPEECH_SERVICES).lower(): AzureSpeechServicesConnection,
            ConnectionCategory.COGNITIVE_SEARCH.lower(): AzureAISearchConnection,
            _snake_to_camel(ConnectionTypes.AZURE_SEARCH).lower(): AzureAISearchConnection,
            _snake_to_camel(ConnectionTypes.AZURE_AI_SERVICES).lower(): AzureAIServicesConnection,
            ConnectionTypes.AI_SERVICES_REST_PLACEHOLDER.lower(): AzureAIServicesConnection,
        }
        return CONNECTION_CATEGORY_TO_SUBCLASS_MAP.get(conn_type, WorkspaceConnection)

    @classmethod
    def _get_entity_class_from_rest_obj(cls, rest_obj: RestWorkspaceConnection) -> Type:
        """Helper function that converts a restful connection into the associated
         connection class or subclass. Accounts for potential snake/camel case and
        capitalization differences in the type, and sub-typing derived from metadata.

        :param rest_obj: The rest object representation of the connection to derive a class from.
        :type rest_obj: RestWorkspaceConnection

        :return: The  connection class the conn_type corresponds to.
        :rtype: Type
        """
        conn_type = rest_obj.properties.category
        conn_type = _snake_to_camel(conn_type).lower()
        if conn_type is None:
            return WorkspaceConnection

        # Imports are done here to avoid circular imports on load.
        from .connection_subtypes import (
            AzureContentSafetyConnection,
            AzureSpeechServicesConnection,
        )

        # Cognitive search connections have further subdivisions based on the kind of service.
        if (
            conn_type == ConnectionCategory.COGNITIVE_SERVICE.lower()
            and hasattr(rest_obj.properties, "metadata")
            and rest_obj.properties.metadata is not None
        ):
            kind = rest_obj.properties.metadata.get(CONNECTION_KIND_KEY, "").lower()
            if kind == CognitiveServiceKinds.CONTENT_SAFETY.lower():
                return AzureContentSafetyConnection
            if kind == CognitiveServiceKinds.SPEECH.lower():
                return AzureSpeechServicesConnection
            return WorkspaceConnection

        return cls._get_entity_class_from_type(type=conn_type)

    @classmethod
    def _get_schema_class_from_type(cls, conn_type: Optional[str]) -> Type:
        """Helper function that converts a rest client connection category into the associated
        connection schema class or subclass. Accounts for potential snake/camel case and
        capitalization differences.

        :param conn_type: The connection type.
        :type conn_type: str

        :return: The  connection schema class the conn_type corresponds to.
        :rtype: Type
        """
        if conn_type is None:
            return WorkspaceConnectionSchema
        entity_class = cls._get_entity_class_from_type(conn_type)
        return entity_class._get_schema_class()

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        """Helper function that returns the required metadata fields for specific
        connection type. This parent function returns nothing, but needs to be overwritten by child
        classes, which are created under the expectation that they have extra fields that need to be
        accounted for.

        :return: A list of the required metadata fields for the specific connection type.
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
