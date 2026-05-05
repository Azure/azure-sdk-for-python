```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.iot.deviceprovisioning

    def azure.iot.deviceprovisioning.generate_sas_token(
            audience: str, 
            policy: str, 
            key: str, 
            expiry: int = 3600
        ) -> str: ...


    class azure.iot.deviceprovisioning.ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2021_10_01 = "2021-10-01"


    class azure.iot.deviceprovisioning.DeviceProvisioningClient(GeneratedDeviceProvisioningClient): implements ContextManager 
        device_registration_state: DeviceRegistrationStateOperations
        enrollment: EnrollmentOperations
        enrollment_group: EnrollmentGroupOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureNamedKeyCredential, AzureSasCredential], 
                *, 
                api_version: Union[str, ApiVersion] = DEFAULT_VERSION, 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                connection_string: str, 
                *, 
                api_version: Union[str, ApiVersion] = DEFAULT_VERSION, 
                **kwargs: Any
            ) -> DeviceProvisioningClient: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.iot.deviceprovisioning.aio

    class azure.iot.deviceprovisioning.aio.DeviceProvisioningClient(GeneratedDeviceProvisioningClient): implements AsyncContextManager 
        device_registration_state: DeviceRegistrationStateOperations
        enrollment: EnrollmentOperations
        enrollment_group: EnrollmentGroupOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureNamedKeyCredential, AzureSasCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, ApiVersion] = DEFAULT_VERSION, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                connection_string: str, 
                *, 
                api_version: Union[str, ApiVersion] = DEFAULT_VERSION, 
                **kwargs: Any
            ) -> DeviceProvisioningClient: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.iot.deviceprovisioning.aio.operations

    class azure.iot.deviceprovisioning.aio.operations.DeviceRegistrationStateOperations(DeviceRegistrationStateOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                id: str, 
                *, 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def query(
                self, 
                id: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...


    class azure.iot.deviceprovisioning.aio.operations.EnrollmentGroupOperations(EnrollmentGroupOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                enrollment_group: JSON, 
                *, 
                content_type: str = "application/json", 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                enrollment_group: IO, 
                *, 
                content_type: str = "application/json", 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def delete(
                self, 
                id: str, 
                *, 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_attestation_mechanism(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def query(
                self, 
                query_specification: Union[JSON, IO], 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @overload
        async def run_bulk_operation(
                self, 
                bulk_operation: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def run_bulk_operation(
                self, 
                bulk_operation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.iot.deviceprovisioning.aio.operations.EnrollmentOperations(EnrollmentOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                enrollment: JSON, 
                *, 
                content_type: str = "application/json", 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                enrollment: IO, 
                *, 
                content_type: str = "application/json", 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def delete(
                self, 
                id: str, 
                *, 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_attestation_mechanism(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def query(
                self, 
                query_specification: Union[JSON, IO], 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JSON]: ...

        @overload
        async def run_bulk_operation(
                self, 
                bulk_operation: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def run_bulk_operation(
                self, 
                bulk_operation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.iot.deviceprovisioning.operations

    class azure.iot.deviceprovisioning.operations.DeviceRegistrationStateOperations(DeviceRegistrationStateOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                id: str, 
                *, 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def query(
                self, 
                id: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...


    class azure.iot.deviceprovisioning.operations.EnrollmentGroupOperations(EnrollmentGroupOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                enrollment_group: JSON, 
                *, 
                content_type: str = "application/json", 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                enrollment_group: IO, 
                *, 
                content_type: str = "application/json", 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def delete(
                self, 
                id: str, 
                *, 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_attestation_mechanism(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def query(
                self, 
                query_specification: Union[JSON, IO], 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @overload
        def run_bulk_operation(
                self, 
                bulk_operation: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def run_bulk_operation(
                self, 
                bulk_operation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.iot.deviceprovisioning.operations.EnrollmentOperations(EnrollmentOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                enrollment: JSON, 
                *, 
                content_type: str = "application/json", 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                enrollment: IO, 
                *, 
                content_type: str = "application/json", 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def delete(
                self, 
                id: str, 
                *, 
                if_match: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_attestation_mechanism(
                self, 
                id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def query(
                self, 
                query_specification: Union[JSON, IO], 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JSON]: ...

        @overload
        def run_bulk_operation(
                self, 
                bulk_operation: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def run_bulk_operation(
                self, 
                bulk_operation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


```