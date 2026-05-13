```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.sms

    class azure.communication.sms.SmsClient:

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs
            ) -> SmsClient: ...

        @distributed_trace
        def send(
                self, 
                from_: str, 
                to: Union[str, List[str]], 
                message: str, 
                *, 
                enable_delivery_report: bool = False, 
                tag: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[SmsSendResult]: ...


    class azure.communication.sms.SmsSendResult(Model):

        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                http_status_code: int, 
                message_id: Optional[str] = ..., 
                successful: bool, 
                to: str, 
                **kwargs
            ): ...


namespace azure.communication.sms.aio

    class azure.communication.sms.aio.SmsClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> SmsClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def send(
                self, 
                from_: str, 
                to: Union[str, List[str]], 
                message: str, 
                *, 
                enable_delivery_report: bool = False, 
                tag: Optional[str] = ..., 
                **kwargs: Any
            ) -> List[SmsSendResult]: ...


```