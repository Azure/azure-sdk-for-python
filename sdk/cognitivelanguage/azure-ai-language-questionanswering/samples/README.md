.---
page_type: sample
languages:
  - python
products:
- azure
- azure-cognitive-services
- azure-qna-maker
urlFragment: languagequestionanswering-samples
---

# Samples for Language QuestionAnswering client library for Python

Question Answering is a cloud-based API service that lets you create a conversational question-and-answer layer over your existing data. Use it to build a knowledge base by extracting questions and answers from your semi-structured content, including FAQ, manuals, and documents. Answer users' questions with the best answers from the QnAs in your knowledge base—automatically. Your knowledge base gets smarter, too, as it continually learns from user behavior.

These code samples show common scenario operations with the Azure Language QuestionAnswering client library.
The async versions of the samples require Python 3.6 or later.
You can authenticate your client with a QuestionAnswering API key.

These sample programs show common scenarios for the QuestionAnswering client's offerings.

|**File Name**|**Description**|
|-------------|---------------|
|[sample_query_knowledgebase.py][query_knowledgebase] and [sample_query_knowledgebase_async.py][query_knowledgebase_async]|Ask a question from a knowledge base|
|[sample_chat.py][chat] and [sample_chat_async.py][chat_async]|Ask a follow-up question (chit-chat)|
|[sample_query_text.py][query_text] and [sample_query_text_async.py][query_text_async]|Ask a question from provided text data|


### Prerequisites

* Python 2.7, or 3.6 or later is required to use this package.
* An [Azure subscription][azure_subscription]
* An existing Question Answering resource


## Setup

1. Install the Azure QuestionAnswering client library for Python with [pip][pip]:
```bash
pip install --pre azure-ai-language-questionanswering
```
2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_chat.py`


[query_knowledgebase]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/sample_query_knowledgebase.py
[query_knowledgebase_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/async_samples/sample_query_knowledgebase_async.py
[chat]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/sample_chat.py
[chat_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/async_samples/sample_chat_async.py
[query_text]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/sample_query_text.py
[query_text_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/async_samples/sample_query_text_async.py
[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
