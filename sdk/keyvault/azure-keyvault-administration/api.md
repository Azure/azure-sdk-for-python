```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.keyvault.administration

    class azure.keyvault.administration.ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V7_2 = "7.2"
        V7_3 = "7.3"
        V7_4 = "7.4"
        V7_5 = "7.5"
        V7_6 = "7.6"


    class azure.keyvault.administration.KeyVaultAccessControlClient(KeyVaultClientBase): implements ContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: TokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_role_assignment(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                definition_id: str, 
                principal_id: str, 
                *, 
                name: Optional[Union[str, UUID]] = ..., 
                **kwargs: Any
            ) -> KeyVaultRoleAssignment: ...

        @distributed_trace
        def delete_role_assignment(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                name: Union[str, UUID], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_role_definition(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                name: Union[str, UUID], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_role_assignment(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                name: Union[str, UUID], 
                **kwargs: Any
            ) -> KeyVaultRoleAssignment: ...

        @distributed_trace
        def get_role_definition(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                name: Union[str, UUID], 
                **kwargs: Any
            ) -> KeyVaultRoleDefinition: ...

        @distributed_trace
        def list_role_assignments(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                **kwargs: Any
            ) -> ItemPaged[KeyVaultRoleAssignment]: ...

        @distributed_trace
        def list_role_definitions(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                **kwargs: Any
            ) -> ItemPaged[KeyVaultRoleDefinition]: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def set_role_definition(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                *, 
                assignable_scopes: Optional[List[Union[str, KeyVaultRoleScope]]] = ..., 
                description: Optional[str] = ..., 
                name: Optional[Union[str, UUID]] = ..., 
                permissions: Optional[List[KeyVaultPermission]] = ..., 
                role_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> KeyVaultRoleDefinition: ...


    class azure.keyvault.administration.KeyVaultBackupClient(KeyVaultClientBase): implements ContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: TokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_backup(
                self, 
                blob_storage_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                use_managed_identity: Literal[True], 
                **kwargs: Any
            ) -> LROPoller[KeyVaultBackupResult]: ...

        @overload
        def begin_backup(
                self, 
                blob_storage_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                sas_token: str, 
                **kwargs: Any
            ) -> LROPoller[KeyVaultBackupResult]: ...

        @overload
        def begin_pre_backup(
                self, 
                blob_storage_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                use_managed_identity: Literal[True], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_backup(
                self, 
                blob_storage_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                sas_token: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_restore(
                self, 
                folder_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                use_managed_identity: Literal[True], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_restore(
                self, 
                folder_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                sas_token: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore(
                self, 
                folder_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                key_name: Optional[str] = ..., 
                use_managed_identity: Literal[True], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore(
                self, 
                folder_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                key_name: Optional[str] = ..., 
                sas_token: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.keyvault.administration.KeyVaultBackupResult:
        folder_url: str

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.keyvault.administration.KeyVaultDataAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_HSM_KEYS = "Microsoft.KeyVault/managedHsm/keys/backup/action"
        CREATE_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/create"
        DECRYPT_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/decrypt/action"
        DELETE_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/delete"
        DELETE_ROLE_ASSIGNMENT = "Microsoft.KeyVault/managedHsm/roleAssignments/delete/action"
        DELETE_ROLE_DEFINITION = "Microsoft.KeyVault/managedHsm/roleDefinitions/delete/action"
        DOWNLOAD_HSM_SECURITY_DOMAIN = "Microsoft.KeyVault/managedHsm/securitydomain/download/action"
        DOWNLOAD_HSM_SECURITY_DOMAIN_STATUS = "Microsoft.KeyVault/managedHsm/securitydomain/download/read"
        ENCRYPT_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/encrypt/action"
        EXPORT_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/export/action"
        GET_ROLE_ASSIGNMENT = "Microsoft.KeyVault/managedHsm/roleAssignments/read/action"
        IMPORT_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/import/action"
        PURGE_DELETED_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/delete"
        RANDOM_NUMBERS_GENERATE = "Microsoft.KeyVault/managedHsm/rng/action"
        READ_DELETED_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/read/action"
        READ_HSM_BACKUP_STATUS = "Microsoft.KeyVault/managedHsm/backup/status/action"
        READ_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/read/action"
        READ_HSM_RESTORE_STATUS = "Microsoft.KeyVault/managedHsm/restore/status/action"
        READ_HSM_SECURITY_DOMAIN_STATUS = "Microsoft.KeyVault/managedHsm/securitydomain/upload/read"
        READ_HSM_SECURITY_DOMAIN_TRANSFER_KEY = "Microsoft.KeyVault/managedHsm/securitydomain/transferkey/read"
        READ_ROLE_DEFINITION = "Microsoft.KeyVault/managedHsm/roleDefinitions/read/action"
        RECOVER_DELETED_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/recover/action"
        RELEASE_KEY = "Microsoft.KeyVault/managedHsm/keys/release/action"
        RESTORE_HSM_KEYS = "Microsoft.KeyVault/managedHsm/keys/restore/action"
        SIGN_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/sign/action"
        START_HSM_BACKUP = "Microsoft.KeyVault/managedHsm/backup/start/action"
        START_HSM_RESTORE = "Microsoft.KeyVault/managedHsm/restore/start/action"
        UNWRAP_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/unwrap/action"
        UPLOAD_HSM_SECURITY_DOMAIN = "Microsoft.KeyVault/managedHsm/securitydomain/upload/action"
        VERIFY_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/verify/action"
        WRAP_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/wrap/action"
        WRITE_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/write/action"
        WRITE_ROLE_ASSIGNMENT = "Microsoft.KeyVault/managedHsm/roleAssignments/write/action"
        WRITE_ROLE_DEFINITION = "Microsoft.KeyVault/managedHsm/roleDefinitions/write/action"


    class azure.keyvault.administration.KeyVaultPermission:
        actions: list[str]
        data_actions: list[str]
        not_actions: list[str]
        not_data_actions: list[str]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.keyvault.administration.KeyVaultRoleAssignment:
        name: str
        properties: KeyVaultRoleAssignmentProperties
        role_assignment_id: str
        type: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.administration.KeyVaultRoleAssignmentProperties:
        principal_id: str
        role_definition_id: str
        scope: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.administration.KeyVaultRoleDefinition:
        assignable_scopes: list[str]
        description: str
        id: str
        name: str
        permissions: list[KeyVaultPermission]
        role_name: str
        role_type: str
        type: str

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.administration.KeyVaultRoleScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "/"
        KEYS = "/keys"


    class azure.keyvault.administration.KeyVaultSetting:
        name: str
        setting_type: Union[str, KeyVaultSettingType, None]
        value: str

        def __init__(
                self, 
                name: str, 
                value: Union[str, bool], 
                setting_type: Optional[Union[str, KeyVaultSettingType]] = None, 
                **kwargs
            ) -> None: ...

        def getboolean(self) -> bool: ...


    class azure.keyvault.administration.KeyVaultSettingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "boolean"


    class azure.keyvault.administration.KeyVaultSettingsClient(KeyVaultClientBase): implements ContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: TokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_setting(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KeyVaultSetting: ...

        @distributed_trace
        def list_settings(self, **kwargs: Any) -> ItemPaged[KeyVaultSetting]: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def update_setting(
                self, 
                setting: KeyVaultSetting, 
                **kwargs: Any
            ) -> KeyVaultSetting: ...


namespace azure.keyvault.administration.aio

    class azure.keyvault.administration.aio.KeyVaultAccessControlClient(AsyncKeyVaultClientBase): implements AsyncContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_role_assignment(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                definition_id: str, 
                principal_id: str, 
                *, 
                name: Optional[Union[str, UUID]] = ..., 
                **kwargs: Any
            ) -> KeyVaultRoleAssignment: ...

        @distributed_trace_async
        async def delete_role_assignment(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                name: Union[str, UUID], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_role_definition(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                name: Union[str, UUID], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_role_assignment(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                name: Union[str, UUID], 
                **kwargs: Any
            ) -> KeyVaultRoleAssignment: ...

        @distributed_trace_async
        async def get_role_definition(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                name: Union[str, UUID], 
                **kwargs: Any
            ) -> KeyVaultRoleDefinition: ...

        @distributed_trace
        def list_role_assignments(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                **kwargs: Any
            ) -> AsyncItemPaged[KeyVaultRoleAssignment]: ...

        @distributed_trace
        def list_role_definitions(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                **kwargs: Any
            ) -> AsyncItemPaged[KeyVaultRoleDefinition]: ...

        @distributed_trace_async
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def set_role_definition(
                self, 
                scope: Union[str, KeyVaultRoleScope], 
                *, 
                assignable_scopes: Optional[List[Union[str, KeyVaultRoleScope]]] = ..., 
                description: Optional[str] = ..., 
                name: Optional[Union[str, UUID]] = ..., 
                permissions: Optional[List[KeyVaultPermission]] = ..., 
                role_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> KeyVaultRoleDefinition: ...


    class azure.keyvault.administration.aio.KeyVaultBackupClient(AsyncKeyVaultClientBase): implements AsyncContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_backup(
                self, 
                blob_storage_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                use_managed_identity: Literal[True], 
                **kwargs: Any
            ) -> AsyncLROPoller[KeyVaultBackupResult]: ...

        @overload
        async def begin_backup(
                self, 
                blob_storage_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                sas_token: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[KeyVaultBackupResult]: ...

        @overload
        async def begin_pre_backup(
                self, 
                blob_storage_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                use_managed_identity: Literal[True], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_backup(
                self, 
                blob_storage_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                sas_token: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_restore(
                self, 
                folder_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                use_managed_identity: Literal[True], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_restore(
                self, 
                folder_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                sas_token: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore(
                self, 
                folder_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                key_name: Optional[str] = ..., 
                use_managed_identity: Literal[True], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore(
                self, 
                folder_url: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                key_name: Optional[str] = ..., 
                sas_token: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.keyvault.administration.aio.KeyVaultSettingsClient(AsyncKeyVaultClientBase): implements AsyncContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_setting(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KeyVaultSetting: ...

        @distributed_trace
        def list_settings(self, **kwargs: Any) -> AsyncItemPaged[KeyVaultSetting]: ...

        @distributed_trace_async
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def update_setting(
                self, 
                setting: KeyVaultSetting, 
                **kwargs: Any
            ) -> KeyVaultSetting: ...


```