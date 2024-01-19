# Q&A Evaluation:

The Q&A evaluation flow will evaluate the Q&A systems by leveraging the state-of-the-art Large Language Models (LLM) to measure the quality and safety of your responses. Utilizing GPT and GPT embedding model to assist with measurements aims to achieve a high agreement with human evaluations compared to traditional mathematical measurements.

## What you will learn

The Q&A evaluation flow allows you to assess and evaluate your model with the LLM-assisted metrics and f1_score:


* __gpt_coherence__: Measures the quality of all sentences in a model's predicted answer and how they fit together naturally.

Coherence is scored on a scale of 1 to 5, with 1 being the worst and 5 being the best.

* __gpt_relevance__: Measures how relevant the model's predicted answers are to the questions asked. 

Relevance metric is scored on a scale of 1 to 5, with 1 being the worst and 5 being the best.

* __gpt_fluency__: Measures how grammatically and linguistically correct the model's predicted answer is.

Fluency is scored on a scale of 1 to 5, with 1 being the worst and 5 being the best

* __gpt_similarity__: Measures similarity between user-provided ground truth answers and the model predicted answer.

Similarity is scored on a scale of 1 to 5, with 1 being the worst and 5 being the best.

* __gpt_groundedness__ (against context)**: Measures how grounded the model's predicted answers are against the context. Even if LLM’s responses are true, if not verifiable against context, then such responses are considered ungrounded.

Groundedness metric is scored on a scale of 1 to 5, with 1 being the worst and 5 being the best. 

* __ada_similarity__: Measures the cosine similarity of ada embeddings of the model prediction and the ground truth.

ada_similarity is a value in the range [0, 1]. 

* __F1-score__: Compute the f1-Score based on the tokens in the predicted answer and the ground truth.

The f1-score evaluation flow allows you to determine the f1-score metric using number of common tokens between the normalized version of the ground truth and the predicted answer.

 F1-score is a value in the range [0, 1]. 


## Prerequisites

- Connection: Azure OpenAI or OpenAI connection.
- Data input: Evaluating the Coherence metric requires you to provide data inputs including a question, an answer, a ground truth, and a context. 

## Tools used in this flow
- LLM tool
- Python tool
- Embedding tool