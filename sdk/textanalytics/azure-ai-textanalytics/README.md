# Text Analytics Python Low-Level Client

1. Since our Low-Level clients are so close to REST API calls, you need to refer a lot to the [Text Analytics Service's REST API docs][rest_api_docs]
2. Another important document for you to look at is [how to use a Python low-level client][low_level_client]
3. Here's a code snippet on how to create and authenticate a low-level `TextAnalyticsClient`.

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

4. Finally, our request preparers are in the `protocol` layer of our namespace. As an example, to import `prepare_sentiment`, you would import as

   ```python
   from azure.ai.textanalytics.protocol import prepare_sentiment
   ```

<!-- LINKS -->

[rest_api_docs]: https://westus2.dev.cognitive.microsoft.com/docs/services/TextAnalytics-v3-1-preview-1/operations/Languages
[low_level_client]: https://github.com/iscai-msft/azure-sdk-for-python/wiki/Low-Level-Client
