```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.storage.blob.changefeed

    class azure.storage.blob.changefeed.ChangeFeedClient:

        def __init__(
                self, 
                account_url: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: Optional[str] = ..., 
                max_chunk_get_size: Optional[int] = ..., 
                max_single_get_size: Optional[int] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                credential: Optional[Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                **kwargs: Any
            ) -> Self: ...

        @distributed_trace
        def list_changes(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                results_per_page: Optional[int] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Dict[str, Any]]: ...


```