```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.containerregistry

    class azure.containerregistry.ArtifactArchitecture(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD64 = "amd64"
        ARM = "arm"
        ARM64 = "arm64"
        I386 = "386"
        MIPS = "mips"
        MIPS64 = "mips64"
        MIPS64LE = "mips64le"
        MIPSLE = "mipsle"
        PPC64 = "ppc64"
        PPC64LE = "ppc64le"
        RISCV64 = "riscv64"
        S390X = "s390x"
        WASM = "wasm"


    class azure.containerregistry.ArtifactManifestOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST_UPDATED_ON_ASCENDING = "timeasc"
        LAST_UPDATED_ON_DESCENDING = "timedesc"
        NONE = "none"


    class azure.containerregistry.ArtifactManifestProperties:
        property architecture: Optional[Union[ArtifactArchitecture, str]]    # Read-only
        property created_on: datetime    # Read-only
        property digest: str    # Read-only
        property fully_qualified_reference: str    # Read-only
        property last_updated_on: datetime    # Read-only
        property operating_system: Optional[Union[ArtifactOperatingSystem, str]]    # Read-only
        property repository_name: str    # Read-only
        property size_in_bytes: Optional[int]    # Read-only
        property tags: Optional[List[str]]    # Read-only
        can_delete: Optional[bool]
        can_list: Optional[bool]
        can_read: Optional[bool]
        can_write: Optional[bool]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.containerregistry.ArtifactOperatingSystem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AIX = "aix"
        ANDROID = "android"
        DARWIN = "darwin"
        DRAGONFLY = "dragonfly"
        FREEBSD = "freebsd"
        ILLUMOS = "illumos"
        IOS = "ios"
        JS = "js"
        LINUX = "linux"
        NETBSD = "netbsd"
        OPENBSD = "openbsd"
        PLAN9 = "plan9"
        SOLARIS = "solaris"
        WINDOWS = "windows"


    class azure.containerregistry.ArtifactTagOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST_UPDATED_ON_ASCENDING = "timeasc"
        LAST_UPDATED_ON_DESCENDING = "timedesc"
        NONE = "none"


    class azure.containerregistry.ArtifactTagProperties:
        property created_on: datetime    # Read-only
        property digest: str    # Read-only
        property last_updated_on: datetime    # Read-only
        property name: str    # Read-only
        property repository_name: str    # Read-only
        can_delete: Optional[bool]
        can_list: Optional[bool]
        can_read: Optional[bool]
        can_write: Optional[bool]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.containerregistry.ContainerRegistryClient(ContainerRegistryBaseClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Optional[TokenCredential] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: str = DEFAULT_AUDIENCE, 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def delete_blob(
                self, 
                repository: str, 
                digest: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_manifest(
                self, 
                repository: str, 
                tag_or_digest: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_repository(
                self, 
                repository: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_tag(
                self, 
                repository: str, 
                tag: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def download_blob(
                self, 
                repository: str, 
                digest: str, 
                **kwargs: Any
            ) -> DownloadBlobStream: ...

        @distributed_trace
        def get_manifest(
                self, 
                repository: str, 
                tag_or_digest: str, 
                **kwargs: Any
            ) -> GetManifestResult: ...

        @distributed_trace
        def get_manifest_properties(
                self, 
                repository: str, 
                tag_or_digest: str, 
                **kwargs: Any
            ) -> ArtifactManifestProperties: ...

        @distributed_trace
        def get_repository_properties(
                self, 
                repository: str, 
                **kwargs: Any
            ) -> RepositoryProperties: ...

        @distributed_trace
        def get_tag_properties(
                self, 
                repository: str, 
                tag: str, 
                **kwargs: Any
            ) -> ArtifactTagProperties: ...

        @distributed_trace
        def list_manifest_properties(
                self, 
                repository: str, 
                *, 
                order_by: Optional[Union[ArtifactManifestOrder, str]] = ..., 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ArtifactManifestProperties]: ...

        @distributed_trace
        def list_repository_names(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_tag_properties(
                self, 
                repository: str, 
                *, 
                order_by: Optional[Union[ArtifactTagOrder, str]] = ..., 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ArtifactTagProperties]: ...

        @distributed_trace
        def set_manifest(
                self, 
                repository: str, 
                manifest: Union[JSON, IO[bytes]], 
                *, 
                media_type: str = OCI_IMAGE_MANIFEST, 
                tag: Optional[str] = ..., 
                **kwargs: Any
            ) -> str: ...

        @overload
        def update_manifest_properties(
                self, 
                repository: str, 
                tag_or_digest: str, 
                properties: ArtifactManifestProperties, 
                **kwargs: Any
            ) -> ArtifactManifestProperties: ...

        @overload
        def update_manifest_properties(
                self, 
                repository: str, 
                tag_or_digest: str, 
                *, 
                can_delete: Optional[bool] = ..., 
                can_list: Optional[bool] = ..., 
                can_read: Optional[bool] = ..., 
                can_write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ArtifactManifestProperties: ...

        @overload
        def update_repository_properties(
                self, 
                repository: str, 
                properties: RepositoryProperties, 
                **kwargs: Any
            ) -> RepositoryProperties: ...

        @overload
        def update_repository_properties(
                self, 
                repository: str, 
                *, 
                can_delete: Optional[bool] = ..., 
                can_list: Optional[bool] = ..., 
                can_read: Optional[bool] = ..., 
                can_write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> RepositoryProperties: ...

        @overload
        def update_tag_properties(
                self, 
                repository: str, 
                tag: str, 
                properties: ArtifactTagProperties, 
                **kwargs: Any
            ) -> ArtifactTagProperties: ...

        @overload
        def update_tag_properties(
                self, 
                repository: str, 
                tag: str, 
                *, 
                can_delete: Optional[bool] = ..., 
                can_list: Optional[bool] = ..., 
                can_read: Optional[bool] = ..., 
                can_write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ArtifactTagProperties: ...

        @distributed_trace
        def upload_blob(
                self, 
                repository: str, 
                data: IO[bytes], 
                **kwargs: Any
            ) -> Tuple[str, int]: ...


    class azure.containerregistry.DigestValidationError(ValueError):
        message: str

        def __init__(self, message: str) -> None: ...


    class azure.containerregistry.DownloadBlobStream(Iterator[bytes], ContextManager[DownloadBlobStream]): implements ContextManager , Iterator 

        def __init__(
                self, 
                *, 
                blob_size: int, 
                chunk_size: int, 
                digest: str, 
                downloaded: int, 
                get_next: GetNext, 
                response: PipelineResponse[HttpRequest, HttpResponse]
            ) -> None: ...

        def close(self) -> None: ...


    class azure.containerregistry.GetManifestResult:
        digest: str
        manifest: Mapping[str, Any]
        media_type: str

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.containerregistry.RepositoryProperties:
        property created_on: Optional[datetime]    # Read-only
        property last_updated_on: Optional[datetime]    # Read-only
        property manifest_count: Optional[int]    # Read-only
        property name: Optional[str]    # Read-only
        property tag_count: Optional[int]    # Read-only
        can_delete: Optional[bool]
        can_list: Optional[bool]
        can_read: Optional[bool]
        can_write: Optional[bool]

        def __getattr__(self, name: str) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...


namespace azure.containerregistry.aio

    class azure.containerregistry.aio.AsyncDownloadBlobStream(AsyncIterator[bytes], AsyncContextManager[AsyncDownloadBlobStream]): implements AsyncContextManager , AsyncIterable , AsyncIterator 

        def __init__(
                self, 
                *, 
                blob_size: int, 
                chunk_size: int, 
                digest: str, 
                downloaded: int, 
                get_next: AsyncGetNext, 
                response: PipelineResponse[HttpRequest, AsyncHttpResponse]
            ) -> None: ...

        async def close(self) -> None: ...


    class azure.containerregistry.aio.ContainerRegistryClient(ContainerRegistryBaseClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Optional[AsyncTokenCredential] = None, 
                *, 
                api_version: Optional[str] = ..., 
                audience: str = DEFAULT_AUDIENCE, 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def delete_blob(
                self, 
                repository: str, 
                digest: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_manifest(
                self, 
                repository: str, 
                tag_or_digest: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_repository(
                self, 
                repository: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_tag(
                self, 
                repository: str, 
                tag: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def download_blob(
                self, 
                repository: str, 
                digest: str, 
                **kwargs: Any
            ) -> AsyncDownloadBlobStream: ...

        @distributed_trace_async
        async def get_manifest(
                self, 
                repository: str, 
                tag_or_digest: str, 
                **kwargs: Any
            ) -> GetManifestResult: ...

        @distributed_trace_async
        async def get_manifest_properties(
                self, 
                repository: str, 
                tag_or_digest: str, 
                **kwargs: Any
            ) -> ArtifactManifestProperties: ...

        @distributed_trace_async
        async def get_repository_properties(
                self, 
                repository: str, 
                **kwargs: Any
            ) -> RepositoryProperties: ...

        @distributed_trace_async
        async def get_tag_properties(
                self, 
                repository: str, 
                tag: str, 
                **kwargs: Any
            ) -> ArtifactTagProperties: ...

        @distributed_trace
        def list_manifest_properties(
                self, 
                repository: str, 
                *, 
                order_by: Optional[Union[ArtifactManifestOrder, str]] = ..., 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ArtifactManifestProperties]: ...

        @distributed_trace
        def list_repository_names(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_tag_properties(
                self, 
                repository: str, 
                *, 
                order_by: Optional[Union[ArtifactTagOrder, str]] = ..., 
                results_per_page: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ArtifactTagProperties]: ...

        @distributed_trace_async
        async def set_manifest(
                self, 
                repository: str, 
                manifest: Union[JSON, IO[bytes]], 
                *, 
                media_type: str = OCI_IMAGE_MANIFEST, 
                tag: Optional[str] = ..., 
                **kwargs: Any
            ) -> str: ...

        @overload
        async def update_manifest_properties(
                self, 
                repository: str, 
                tag_or_digest: str, 
                properties: ArtifactManifestProperties, 
                **kwargs: Any
            ) -> ArtifactManifestProperties: ...

        @overload
        async def update_manifest_properties(
                self, 
                repository: str, 
                tag_or_digest: str, 
                *, 
                can_delete: Optional[bool] = ..., 
                can_list: Optional[bool] = ..., 
                can_read: Optional[bool] = ..., 
                can_write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ArtifactManifestProperties: ...

        @overload
        async def update_repository_properties(
                self, 
                repository: str, 
                properties: RepositoryProperties, 
                **kwargs: Any
            ) -> RepositoryProperties: ...

        @overload
        async def update_repository_properties(
                self, 
                repository: str, 
                *, 
                can_delete: Optional[bool] = ..., 
                can_list: Optional[bool] = ..., 
                can_read: Optional[bool] = ..., 
                can_write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> RepositoryProperties: ...

        @overload
        async def update_tag_properties(
                self, 
                repository: str, 
                tag: str, 
                properties: ArtifactTagProperties, 
                **kwargs: Any
            ) -> ArtifactTagProperties: ...

        @overload
        async def update_tag_properties(
                self, 
                repository: str, 
                tag: str, 
                *, 
                can_delete: Optional[bool] = ..., 
                can_list: Optional[bool] = ..., 
                can_read: Optional[bool] = ..., 
                can_write: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ArtifactTagProperties: ...

        @distributed_trace_async
        async def upload_blob(
                self, 
                repository: str, 
                data: IO[bytes], 
                **kwargs: Any
            ) -> Tuple[str, int]: ...


```