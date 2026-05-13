```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure_postgresql_auth.core

    def azure_postgresql_auth.core.decode_jwt(token: str) -> dict[str, Any]: ...


    def azure_postgresql_auth.core.get_entra_conninfo(credential: TokenCredential) -> dict[str, str]: ...


    async def azure_postgresql_auth.core.get_entra_conninfo_async:async(credential: AsyncTokenCredential) -> dict[str, str]: ...


    def azure_postgresql_auth.core.get_entra_token(credential: TokenCredential, scope: str) -> str: ...


    async def azure_postgresql_auth.core.get_entra_token_async:async(credential: AsyncTokenCredential, scope: str) -> str: ...


    def azure_postgresql_auth.core.parse_principal_name(xms_mirid: str) -> Optional[str]: ...


    class azure_postgresql_auth.core.ScopePermissionError(AzurePgEntraError):


    class azure_postgresql_auth.core.TokenDecodeError(AzurePgEntraError):


    class azure_postgresql_auth.core.UsernameExtractionError(AzurePgEntraError):


namespace azure_postgresql_auth.errors

    class azure_postgresql_auth.errors.AzurePgEntraError(Exception):


    class azure_postgresql_auth.errors.CredentialValueError(AzurePgEntraError):


    class azure_postgresql_auth.errors.EntraConnectionValueError(AzurePgEntraError):


    class azure_postgresql_auth.errors.ScopePermissionError(AzurePgEntraError):


    class azure_postgresql_auth.errors.TokenDecodeError(AzurePgEntraError):


    class azure_postgresql_auth.errors.UsernameExtractionError(AzurePgEntraError):


namespace azure_postgresql_auth.psycopg2

    class azure_postgresql_auth.psycopg2.EntraConnection(connection):

        def __init__(
                self, 
                dsn: str, 
                *, 
                credential: TokenCredential = ..., 
                password: Union[str, None] = ..., 
                user: Union[str, None] = ..., 
                **kwargs: Any
            ) -> None: ...


namespace azure_postgresql_auth.psycopg2.entra_connection

    def azure_postgresql_auth.psycopg2.entra_connection.get_entra_conninfo(credential: TokenCredential) -> dict[str, str]: ...


    class azure_postgresql_auth.psycopg2.entra_connection.CredentialValueError(AzurePgEntraError):


    class azure_postgresql_auth.psycopg2.entra_connection.EntraConnection(connection):

        def __init__(
                self, 
                dsn: str, 
                *, 
                credential: TokenCredential = ..., 
                password: Union[str, None] = ..., 
                user: Union[str, None] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure_postgresql_auth.psycopg2.entra_connection.EntraConnectionValueError(AzurePgEntraError):


namespace azure_postgresql_auth.psycopg3

    class azure_postgresql_auth.psycopg3.AsyncEntraConnection(AsyncConnection):
        property adapters: AdaptersMap    # Read-only
        property autocommit: bool
        property broken: bool    # Read-only
        property closed: bool    # Read-only
        property connection: BaseConnection[Row]    # Read-only
        property deferrable: bool | None
        property info: ConnectionInfo    # Read-only
        property isolation_level: IsolationLevel | None
        property prepare_threshold: int | None
        property prepared_max: int | None
        property read_only: bool | None

        @classmethod
        async def connect(
                cls, 
                *args: Any, 
                **kwargs: Any
            ) -> AsyncEntraConnection: ...


    class azure_postgresql_auth.psycopg3.EntraConnection(Connection):
        property adapters: AdaptersMap    # Read-only
        property autocommit: bool
        property broken: bool    # Read-only
        property closed: bool    # Read-only
        property connection: BaseConnection[Row]    # Read-only
        property deferrable: bool | None
        property info: ConnectionInfo    # Read-only
        property isolation_level: IsolationLevel | None
        property prepare_threshold: int | None
        property prepared_max: int | None
        property read_only: bool | None

        @classmethod
        def connect(
                cls, 
                *args: Any, 
                **kwargs: Any
            ) -> EntraConnection: ...


namespace azure_postgresql_auth.psycopg3.async_entra_connection

    async def azure_postgresql_auth.psycopg3.async_entra_connection.get_entra_conninfo_async:async(credential: AsyncTokenCredential) -> dict[str, str]: ...


    class azure_postgresql_auth.psycopg3.async_entra_connection.AsyncEntraConnection(AsyncConnection):
        property adapters: AdaptersMap    # Read-only
        property autocommit: bool
        property broken: bool    # Read-only
        property closed: bool    # Read-only
        property connection: BaseConnection[Row]    # Read-only
        property deferrable: bool | None
        property info: ConnectionInfo    # Read-only
        property isolation_level: IsolationLevel | None
        property prepare_threshold: int | None
        property prepared_max: int | None
        property read_only: bool | None

        @classmethod
        async def connect(
                cls, 
                *args: Any, 
                **kwargs: Any
            ) -> AsyncEntraConnection: ...


    class azure_postgresql_auth.psycopg3.async_entra_connection.CredentialValueError(AzurePgEntraError):


    class azure_postgresql_auth.psycopg3.async_entra_connection.EntraConnectionValueError(AzurePgEntraError):


namespace azure_postgresql_auth.psycopg3.entra_connection

    def azure_postgresql_auth.psycopg3.entra_connection.get_entra_conninfo(credential: TokenCredential) -> dict[str, str]: ...


    class azure_postgresql_auth.psycopg3.entra_connection.CredentialValueError(AzurePgEntraError):


    class azure_postgresql_auth.psycopg3.entra_connection.EntraConnection(Connection):
        property adapters: AdaptersMap    # Read-only
        property autocommit: bool
        property broken: bool    # Read-only
        property closed: bool    # Read-only
        property connection: BaseConnection[Row]    # Read-only
        property deferrable: bool | None
        property info: ConnectionInfo    # Read-only
        property isolation_level: IsolationLevel | None
        property prepare_threshold: int | None
        property prepared_max: int | None
        property read_only: bool | None

        @classmethod
        def connect(
                cls, 
                *args: Any, 
                **kwargs: Any
            ) -> EntraConnection: ...


    class azure_postgresql_auth.psycopg3.entra_connection.EntraConnectionValueError(AzurePgEntraError):


namespace azure_postgresql_auth.sqlalchemy

    def azure_postgresql_auth.sqlalchemy.enable_entra_authentication(engine: Engine) -> None: ...


    def azure_postgresql_auth.sqlalchemy.enable_entra_authentication_async(engine: AsyncEngine) -> None: ...


namespace azure_postgresql_auth.sqlalchemy.async_entra_connection

    def azure_postgresql_auth.sqlalchemy.async_entra_connection.enable_entra_authentication_async(engine: AsyncEngine) -> None: ...


    def azure_postgresql_auth.sqlalchemy.async_entra_connection.get_entra_conninfo(credential: TokenCredential) -> dict[str, str]: ...


    class azure_postgresql_auth.sqlalchemy.async_entra_connection.CredentialValueError(AzurePgEntraError):


    class azure_postgresql_auth.sqlalchemy.async_entra_connection.EntraConnectionValueError(AzurePgEntraError):


namespace azure_postgresql_auth.sqlalchemy.entra_connection

    def azure_postgresql_auth.sqlalchemy.entra_connection.enable_entra_authentication(engine: Engine) -> None: ...


    def azure_postgresql_auth.sqlalchemy.entra_connection.get_entra_conninfo(credential: TokenCredential) -> dict[str, str]: ...


    class azure_postgresql_auth.sqlalchemy.entra_connection.CredentialValueError(AzurePgEntraError):


    class azure_postgresql_auth.sqlalchemy.entra_connection.EntraConnectionValueError(AzurePgEntraError):


```