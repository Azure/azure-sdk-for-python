```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.eventhub.extensions.checkpointstoreblobaio

    class azure.eventhub.extensions.checkpointstoreblobaio.BlobCheckpointStore(CheckpointStore): implements AsyncContextManager 

        def __init__(
                self, 
                blob_account_url: str, 
                container_name: str, 
                *, 
                api_version: str = "2019-07-07", 
                credential: Optional[Union[AsyncTokenCredential, AzureNamedKeyCredential, AzureSasCredential]] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                container_name: str, 
                *, 
                api_version: str = "2019-07-07", 
                credential: Optional[Union[AsyncTokenCredential, AzureNamedKeyCredential, AzureSasCredential]] = ..., 
                secondary_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> BlobCheckpointStore: ...

        async def claim_ownership(
                self, 
                ownership_list: Iterable[Dict[str, Any]], 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        async def close(self) -> None: ...

        async def list_checkpoints(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        async def list_ownership(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        async def update_checkpoint(
                self, 
                checkpoint: Dict[str, Any], 
                **kwargs: Any
            ) -> None: ...


```