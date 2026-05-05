```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.eventhub.extensions.checkpointstoreblob

    class azure.eventhub.extensions.checkpointstoreblob.BlobCheckpointStore(CheckpointStore): implements ContextManager 

        def __init__(
                self, 
                blob_account_url: str, 
                container_name: str, 
                credential: Optional[Union[AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: str = "2019-07-07", 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                container_name: str, 
                credential: Optional[Union[AzureNamedKeyCredential, AzureSasCredential, TokenCredential]] = None, 
                *, 
                api_version: str = "2019-07-07", 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> BlobCheckpointStore: ...

        def claim_ownership(
                self, 
                ownership_list: Iterable[Dict[str, Any]], 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        def close(self) -> None: ...

        def list_checkpoints(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        def list_ownership(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        def update_checkpoint(
                self, 
                checkpoint: Dict[str, Union[str, int]], 
                **kwargs: Any
            ) -> None: ...


```