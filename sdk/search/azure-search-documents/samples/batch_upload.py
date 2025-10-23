from azure.search.documents import SearchClient
from azure.identity import AzureCliCredential

client = SearchClient(
    endpoint="https://vector-search-test.search.windows.net",
    index_name="batch-test",
    credential=AzureCliCredential(),
)
documents = [{"id": str(i), "content": " " * 10000} for i in range(10000)]
client.upload_documents(documents=documents)
