---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-personalizer
---

# Samples for Azure Personalizer client library for Python

## Prerequisites
* Python 3.7 or later is required to use this package
* You must have an [Azure subscription][azure_subscription] and an
[Azure Personalizer account][personalizer] to run these samples.

## Setup

1. Install the Azure Personalizer client library for Python with pip:

```commandline
pip install azure-ai-personalizer
```

2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python rank_actions_and_reward_events.py`

## Next steps

Check out the [API reference documentation][python-personalizer-ref-docs] to learn more about
what you can do with the Azure Personalizer client library.

| File                                                                                                                                                    | Description                                                                |
|---------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| [rank_actions_and_reward_events.py][rank_actions_and_reward_events] and [rank_actions_and_reward_events_async.py][rank_actions_and_reward_events_async] | demos sending rank and reward to personalizer in single-slot configuration |
| [multi_slot_rank_actions_and_reward_events.py][multi_slot_rank_actions_and_reward_events] and [multi_slot_rank_actions_and_reward_events_async.py][multi_slot_rank_actions_and_reward_events_async]                                             | demos sending rank and reward to personalizer in multi-slot configuration  |

<!-- LINKS -->
[azure_subscription]: https://azure.microsoft.com/free/
[personalizer]: https://azure.microsoft.com/products/cognitive-services/personalizer/
[python-personalizer-ref-docs]: https://aka.ms/azsdk/python/personalizer/docs
[rank_actions_and_reward_events]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/personalizer/azure-ai-personalizer/samples/rank_actions_and_reward_events.py
[rank_actions_and_reward_events_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/personalizer/azure-ai-personalizer/samples/async_samples/rank_actions_and_reward_events_async.py
[multi_slot_rank_actions_and_reward_events]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/personalizer/azure-ai-personalizer/samples/multi_slot_rank_actions_and_reward_events.py
[multi_slot_rank_actions_and_reward_events_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/personalizer/azure-ai-personalizer/samples/async_samples/multi_slot_rank_actions_and_reward_events_async.py
