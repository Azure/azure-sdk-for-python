```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.purview.sharing

    class azure.purview.sharing.PurviewSharingClient: implements ContextManager 
        received_shares: ReceivedSharesOperations
        sent_shares: SentSharesOperations
        share_resources: ShareResourcesOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.purview.sharing.aio

    class azure.purview.sharing.aio.PurviewSharingClient: implements AsyncContextManager 
        received_shares: ReceivedSharesOperations
        sent_shares: SentSharesOperations
        share_resources: ShareResourcesOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.purview.sharing.aio.operations

    class azure.purview.sharing.aio.operations.ReceivedSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def activate_tenant_email_registration(
                self, 
                tenant_email_registration: JSON, 
                *, 
                content_type: str = "application/json", 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def activate_tenant_email_registration(
                self, 
                tenant_email_registration: IO, 
                *, 
                content_type: str = "application/json", 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def begin_create_or_replace(
                self, 
                received_share_id: str, 
                received_share: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                received_share_id: str, 
                received_share: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                received_share_id: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        @distributed_trace_async
        async def get(
                self, 
                received_share_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_attached(
                self, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                reference_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace
        def list_detached(
                self, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def register_tenant_email_registration(
                self, 
                *, 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.sharing.aio.operations.SentSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                sent_share_id: str, 
                sent_share: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                sent_share_id: str, 
                sent_share: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                sent_share_id: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        @distributed_trace_async
        async def begin_delete_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        @overload
        async def create_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                sent_share_invitation: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def create_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                sent_share_invitation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get(
                self, 
                sent_share_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                reference_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace
        def list_invitations(
                self, 
                sent_share_id: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace_async
        async def notify_user_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                *, 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.sharing.aio.operations.ShareResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...


namespace azure.purview.sharing.operations

    class azure.purview.sharing.operations.ReceivedSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def activate_tenant_email_registration(
                self, 
                tenant_email_registration: JSON, 
                *, 
                content_type: str = "application/json", 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def activate_tenant_email_registration(
                self, 
                tenant_email_registration: IO, 
                *, 
                content_type: str = "application/json", 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def begin_create_or_replace(
                self, 
                received_share_id: str, 
                received_share: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        @overload
        def begin_create_or_replace(
                self, 
                received_share_id: str, 
                received_share: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        @distributed_trace
        def begin_delete(
                self, 
                received_share_id: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        @distributed_trace
        def get(
                self, 
                received_share_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_attached(
                self, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                reference_name: str, 
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def list_detached(
                self, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def register_tenant_email_registration(
                self, 
                *, 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.sharing.operations.SentSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_replace(
                self, 
                sent_share_id: str, 
                sent_share: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        @overload
        def begin_create_or_replace(
                self, 
                sent_share_id: str, 
                sent_share: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        @distributed_trace
        def begin_delete(
                self, 
                sent_share_id: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        @distributed_trace
        def begin_delete_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                *, 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        @overload
        def create_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                sent_share_invitation: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def create_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                sent_share_invitation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get(
                self, 
                sent_share_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                reference_name: str, 
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def list_invitations(
                self, 
                sent_share_id: str, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def notify_user_invitation(
                self, 
                sent_share_id: str, 
                sent_share_invitation_id: str, 
                *, 
                repeatability_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.sharing.operations.ShareResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterable[JSON]: ...


```