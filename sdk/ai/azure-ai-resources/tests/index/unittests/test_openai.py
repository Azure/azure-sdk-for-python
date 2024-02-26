import logging

from azure.ai.resources._index._embeddings.openai import OpenAIEmbedder

logger = logging.getLogger(__name__)


def test_openai_embedder_adapt_batch_size():
    num_valid_requests = 0
    num_failed_requests = 0
    max_batch_size = 2

    def _embed_request(self, tokenized_texts, **kwargs) -> dict:
        nonlocal num_valid_requests
        nonlocal num_failed_requests
        nonlocal max_batch_size

        if len(tokenized_texts) > max_batch_size:
            num_failed_requests += 1
            raise Exception(f"Too many inputs {len(tokenized_texts)}. The max number of inputs is {max_batch_size}.")
        else:
            num_valid_requests += 1
            embedding = {"embedding": [3.33], "index": 0, "object": "embedding"}
            return {"data": [embedding for _ in range(len(tokenized_texts))]}

    OpenAIEmbedder._embed_request = _embed_request

    embedder = OpenAIEmbedder("api_base", "api_type")

    embedder.embedding_ctx_length = 2

    # With tiktoken encoding for `text-embedding-ada-002` token counts are: 4, 4, 12
    texts = ["This is a test", "This is another test", "This text is long enough to be split into two requests."]

    results = embedder._embed(texts)

    assert len(results) == 3
    assert num_valid_requests == 5
    assert num_failed_requests == 1

    num_valid_requests = 0
    num_failed_requests = 0
    max_batch_size = 1

    embedder.embedding_ctx_length = 8

    results = embedder._embed(texts)

    assert len(results) == 3
    assert num_valid_requests == 4
    assert num_failed_requests == 1
