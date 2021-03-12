# Text Analytics Python Low-Level Client

## REST API Docs

Since our Low-Level clients are so close to REST API calls, you need to refer a lot to the [Text Analytics Service's REST API docs][rest_api_docs]

## Low-Level Client

Another important document for you to look at is [how to use a Python low-level client][low_level_client]

## Create and Authenticate a Low-Level [TextAnalyticsClient][text_analytics_client]

Here's a code snippet on how to create and authenticate a low-level [TextAnalyticsClient][text_analytics_client].

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

endpoint: str = "https://myEndpoint"
key: str = "myKey"

client = TextAnalyticsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)
```

## Request Preparers

Our request preparers are in the [protocol][ta_protocol] layer of our namespace. As an example, to import [prepare_sentiment][prepare_sentiment], you would import as

```python
from azure.ai.textanalytics.protocol import prepare_sentiment
```

<!-- LINKS -->

[rest_api_docs]: https://westus2.dev.cognitive.microsoft.com/docs/services/TextAnalytics-v3-1-preview-1/operations/Languages
[low_level_client]: https://github.com/iscai-msft/azure-sdk-for-python/wiki/Low-Level-Client
[text_analytics_client]: https://docsupport.blob.core.windows.net/$web/azure-ai-textanalytics/azure.ai.textanalytics.html#azure.ai.textanalytics.TextAnalyticsClient
[ta_protocol]: https://docsupport.blob.core.windows.net/$web/azure-ai-textanalytics/azure.ai.textanalytics.protocol.html
[prepare_sentiment]: https://docsupport.blob.core.windows.net/$web/azure-ai-textanalytics/azure.ai.textanalytics.protocol.html#azure.ai.textanalytics.protocol.prepare_sentiment