---
page_type: sample
languages:
- python
products:
# Including relevant stubs from https://review.docs.microsoft.com/help/contribute/metadata-taxonomies#product
- azure
name: Azure.Analytics.Purview samples for python
description: Samples for the Azure.Analytics.Purview client library.
---

# Azure.Analytics.Purview Samples

The following are code samples that show common scenario operations with the Azure Purview client library.

* [sent_shares_examples.py](https://github.com/yamanwahsheh/azure-sdk-for-python/blob/yaman/share-v2-python-tests-and-samples/sdk/purview/azure-purview-sharing/samples/sent_shares_examples.py) - Examples of Sent Shares:
    * Create a share client
    * Create a sent share
    * Get a sent share
    * Delete a sent share
    * Get all sent shares
    * Send a user invitation
    * Send a service invitation
    * View sent invitations
    * Get a sent invitation

* [received_shares_examples.py](https://github.com/yamanwahsheh/azure-sdk-for-python/blob/yaman/share-v2-python-tests-and-samples/sdk/purview/azure-purview-sharing/samples/received_shares_examples.py) - Examples of Received Shares:
    * Create a share client
    * Get all detached received shares
    * Attach a received share
    * Get a received share
    * List attached received shares
    * Delete a received share

## Prerequisites
* Python 3.6+
* You must have an [Azure subscription](https://azure.microsoft.com/free/)

## Setup

1. Install the latest beta version of Azure Purview Sharing that the samples use:

```bash
pip install azure-purview-sharing
```

2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sent_shares_examples.py`

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-purview-sharing-ref) to learn more about
what you can do with the Azure Purview Sharing API client library.