# Azure Personalizer client library for Python

[Azure Personalizer][personalizer_doc]
is a cloud-based service that helps your applications choose the best content item to show your users. You can use the Personalizer service to determine what product to suggest to shoppers or to figure out the optimal position for an advertisement. After the content is shown to the user, your application monitors the user's reaction and reports a reward score back to the Personalizer service. This ensures continuous improvement of the machine learning model, and Personalizer's ability to select the best content item based on the contextual information it receives.

## Getting started

### Prerequisites
* Python 3.7 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and a
[Personalizer resource][personalizer_account] to use this package.

### Install the package
Install the Azure Personalizer client library for Python with [pip][pip]:

```bash
pip install azure-ai-personalizer
```

> Note: This version of the client library defaults to the `2022-09-01-preview` version of the service.

This table shows the relationship between SDK versions and supported API versions of the service:

|SDK version|Supported API version of service
|-|-
|1.0.0b1| 2022-09-01-preview

## Key concepts

### PersonalizerClient
The [synchronous PersonalizerClient][personalizer_sync_client] and
[asynchronous PersonalizerClient][personalizer_async_client] provide synchronous and asynchronous operations to:
- Manage the machine learning model and learning settings for the Personalizer service.
- Manage the properties of the Personalizer service such as the [learning mode][learning_mode], [exploration percentage][exploration].
- Run counterfactual evaluations on prior historical event data.
- Rank a set of actions, then activate and reward the event. 
- Use [multi-slot personalization][multi_slot] when there are more than one slots.
- Manage the properties of the Personalizer service.
- Run counterfactual evaluations on prior historical event data.


## Examples
The following examples outline the main scenarios when using personalizer in single-slot and multi-slot configurations.

* [Send rank and reward when using a single slot](#send-rank-and-reward "Send rank and reward")
* [Send rank and reward when using multiple slots](#send-multi-slot-rank-and-reward "Send multi-slot rank and reward")

### Send rank and reward

```python
from azure.ai.personalizer import PersonalizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<my-personalizer-instance>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

client = PersonalizerClient(endpoint, credential)

# The list of actions to be ranked with metadata associated for each action.
actions = [
    {
        "id": "Video1",
        "features": [
            {"videoType": "documentary", "videoLength": 35, "director": "CarlSagan"},
            {"mostWatchedByAge": "50-55"},
        ],
    },
    {
        "id": "Video2",
        "features": [
            {"videoType": "movie", "videoLength": 120, "director": "StevenSpielberg"},
            {"mostWatchedByAge": "40-45"},
        ],
    },
]

# Context of the user to which the action must be presented.
context_features = [
    {"currentContext": {"day": "tuesday", "time": "night", "weather": "rainy"}},
    {
        "userContext": {
            "payingUser": True,
            "favoriteGenre": "documentary",
            "hoursOnSite": 0.12,
            "lastWatchedType": "movie",
        },
    },
]

request = {
    "actions": actions,
    "contextFeatures": context_features,
}

rank_response = client.rank(request)
print("Sending reward event")
client.reward(rank_response.get("eventId"), {"value": 1.0})
```

### Send multi-slot rank and reward

```python
from azure.ai.personalizer import PersonalizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<my-personalizer-instance>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

client = PersonalizerClient(endpoint, credential)

# We want to rank the actions for two slots.
slots = [
    {
        "id": "Main Article",
        "baselineAction": "NewsArticle",
        "positionFeatures": [{"Size": "Large", "Position": "Top Middle"}],
    },
    {
        "id": "Side Bar",
        "baselineAction": "SportsArticle",
        "positionFeatures": [{"Size": "Small", "Position": "Bottom Right"}],
    },
]

# The list of actions to be ranked with metadata associated for each action.
actions = [
    {"id": "NewsArticle", "features": [{"type": "News"}]},
    {"id": "SportsArticle", "features": [{"type": "Sports"}]},
    {"id": "EntertainmentArticle", "features": [{"type": "Entertainment"}]},
]

# Context of the user to which the action must be presented.
context_features = [
    {"user": {"profileType": "AnonymousUser", "latLong": "47.6,-122.1"}},
    {"environment": {"dayOfMonth": "28", "monthOfYear": "8", "weather": "Sunny"}},
    {"device": {"mobile": True, "windows": True}},
    {"recentActivity": {"itemsInCart": 3}},
]

request = {
    "slots": slots,
    "actions": actions,
    "contextFeatures": context_features,
}
rank_response = client.rank_multi_slot(request)
print("Sending reward event for Main Article slot")
client.reward_multi_slot(
    rank_response.get("eventId"),
    {"reward": [{"slotId": "Main Article", "value": 1.0}]})
```

## Troubleshooting

### General
Personalizer client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Logging
This library uses the standard [logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Next steps

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->
[personalizer_doc]: https://docs.microsoft.com/azure/cognitive-services/personalizer/
[azure_subscription]: https://azure.microsoft.com/free
[personalizer_account]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[personalizer_sync_client]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/personalizer/azure-ai-personalizer/azure/ai/personalizer/_client.py
[personalizer_async_client]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/personalizer/azure-ai-personalizer/azure/ai/personalizer/aio/_client.py
[learning_mode]: https://docs.microsoft.com/azure/cognitive-services/personalizer/what-is-personalizer#learning-modes
[exploration]: https://docs.microsoft.com/azure/cognitive-services/personalizer/concepts-exploration
[multi_slot]: https://docs.microsoft.com/azure/cognitive-services/personalizer/concept-multi-slot-personalization
[examples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/personalizer/azure-ai-personalizer/samples
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
