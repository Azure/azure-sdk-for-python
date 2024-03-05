# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""OpenAI Embeddings generation and management tools."""
import os
import time
from typing import Any, Dict, List, Optional

from azure.ai.resources.constants._common import USER_AGENT_HEADER_KEY
from azure.ai.resources._user_agent import USER_AGENT
from azure.ai.resources._index._utils.logging import get_logger
from packaging import version

logger = get_logger("embeddings.openai")


class OpenAIEmbedder:
    """OpenAI Embedding client wrapper with retries."""

    def __init__(
        self,
        api_base: str,
        api_type: str,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_credential: Optional[Any] = None,
        model: str = "text-embedding-ada-002",
        deployment: Optional[str] = None,
        batch_size: Optional[int] = None,
        max_retries: Optional[int] = None,
        embedding_ctx_length: Optional[int] = None,
        show_progress_bar: bool = False,
        openai_passthrough_args: Optional[dict] = None,
    ):
        """Initialize an OpenAI Embedding client."""
        self.api_base = api_base
        self.api_type = api_type
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY") or ""
        # TODO: If azure_credential set, check api_type is azure or azure_ad and setup auth accordingly
        self.azure_credential = azure_credential

        if batch_size is None and "azure" in self.api_type:
            batch_size = 16
        elif batch_size is None:
            batch_size = 1000
        self.batch_size = int(batch_size)
        self._dynamic_batch_size: Optional[int] = None

        if max_retries is None:
            max_retries = 10
        self.max_retries = max_retries

        if model is None:
            model = "text-embedding-ada-002"
        self.model = model

        if "azure" in self.api_type and deployment is None:
            raise ValueError("Azure OpenAI requires a deployment name.")
        self.deployment = deployment

        if embedding_ctx_length is None:
            embedding_ctx_length = 8191
        self.embedding_ctx_length = embedding_ctx_length

        self.show_progress_bar = show_progress_bar
        self.openai_passthrough_args = openai_passthrough_args or {}

        try:
            import openai
        except ImportError as e:
            raise ImportError("Please install openai via `pip install openai`") from e

        if version.parse(openai.version.VERSION) >= version.parse("1.0.0"):
            self.openai_v1plus = True
            self.api_version = api_version if api_version else "2023-05-15"

            if "azure" in self.api_type:
                client = openai.AzureOpenAI(
                    api_key=self.api_key,
                    api_version=self.api_version,
                    azure_endpoint=self.api_base,
                    azure_deployment=self.deployment,
                    default_headers={USER_AGENT_HEADER_KEY: USER_AGENT},
                )
            else:
                client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base,
                    default_headers={USER_AGENT_HEADER_KEY: USER_AGENT},
                )

            self.embedding_client = client.embeddings

            self._params = {
                "model": self.model,
                **self.openai_passthrough_args,
            }
            self._retry_exceptions = [
                openai._exceptions.APIStatusError,
                openai._exceptions.APITimeoutError,
                openai._exceptions.APIError,
                openai._exceptions.APIConnectionError,
                openai._exceptions.RateLimitError,
                openai._exceptions.InternalServerError,
                openai._exceptions.APIResponseValidationError,
            ]
            self._RateLimitError = openai._exceptions.RateLimitError
        else:
            self.openai_v1plus = False
            self.api_version = api_version if api_version else "2023-03-15-preview"
            self.embedding_client = openai.Embeddings
            self._params = {
                "model": self.model,
                "api_base": self.api_base,
                "api_type": self.api_type,
                "api_version": self.api_version,
                "api_key": self.api_key,
                **self.openai_passthrough_args,
            }
            if self.deployment is not None:
                self._params["engine"] = self.deployment
            self._retry_exceptions = [
                openai.error.Timeout,
                openai.error.APIError,
                openai.error.APIConnectionError,
                openai.error.RateLimitError,
                openai.error.ServiceUnavailableError,
            ]
            self._RateLimitError = openai.error.RateLimitError

        self._statistics = {
            "num_retries": 0,
            "time_spent_sleeping": 0,
            "num_tokens": 0,
        }

    @property
    def _openai_client_params(self) -> dict:
        return self._params

    @property
    def _retryable_openai_errors(self) -> List[Exception]:
        return self._retry_exceptions

    def _dynamic_batch_size_embed_request(self, tokenized_texts: List[List[int]], **kwargs) -> dict:
        try:
            if self._dynamic_batch_size is None:
                return self._embed_request(tokenized_texts=tokenized_texts, **kwargs)
            else:
                embedding_response: Dict[str, List] = {"data": []}
                for i in range(0, len(tokenized_texts), self._dynamic_batch_size):
                    embedding_response["data"].extend(
                        self._embed_request(
                            tokenized_texts=tokenized_texts[i : i + self._dynamic_batch_size], **kwargs
                        )["data"]
                    )
        except Exception as e:
            err_msg = str(e)
            if "Too many inputs" not in err_msg:
                raise

            import re
            match = re.match(r".*The max number of inputs is ([0-9]+).*", err_msg)
            if match and match.group(1):
                try:
                    self._dynamic_batch_size = int(match.group(1))
                except Exception:
                    logger.error(
                        "Failed to parse max number of inputs from error message, falling back to batch_size=1."
                    )
                    self._dynamic_batch_size = 1
                logger.warning(f"Reducing batch_size to {self._dynamic_batch_size} and retrying.")
                embedding_response: Dict[str, List] = {"data": []}  # type: ignore[no-redef]
                for i in range(0, len(tokenized_texts), self._dynamic_batch_size):
                    embedding_response["data"].extend(
                        self._embed_request(
                            tokenized_texts=tokenized_texts[i : i + self._dynamic_batch_size], **kwargs
                        )["data"]
                    )
            else:
                raise

        return embedding_response

    def _embed_request(self, tokenized_texts: List[List[int]], **kwargs) -> dict:
        try:
            total_delay = 0
            last_exception = None
            for retry in range(self.max_retries):
                logger.info(f"Attempt {retry} to embed {len(tokenized_texts)} documents.")
                try:
                    response = self.embedding_client.create(
                        input=tokenized_texts,
                        **kwargs,
                    )
                    if self.openai_v1plus:
                        response = {"object": "list", "data": [{"object": "embedding", "embedding": d.embedding} for d in response.data]}
                    return response
                except Exception as e:
                    err_msg = str(e)
                    logger.warning(f"Error embedding: {err_msg}", exc_info=e)
                    last_exception = e
                    retrying = False
                    for retryable_error in self._retryable_openai_errors:
                        if isinstance(e, type(retryable_error)):
                            retrying = True

                            # Retry with retry-after if found in RateLimitError
                            if isinstance(e, self._RateLimitError):
                                logger.warning(f"Retrying error type {type(e)}.")
                                response_headers = e.headers if hasattr(e, "headers") else {}
                                if "Retry-After" in response_headers:
                                    delay = int(response_headers["Retry-After"])
                                    logger.warning(f"OpenAI throws RateLimitError with Retry-After {delay} seconds.")
                                else:
                                    # Wait for 1 minute as suggested by openai https://help.openai.com/en/articles/6897202-ratelimiterror
                                    logger.warning("Retry after 60 seconds.")
                                    delay = 60
                            total_delay += delay
                            logger.warning(f"Sleeping for {delay} seconds before retrying.")
                            time.sleep(delay)
                            break

                    if not retrying:
                        break
        finally:
            self._statistics["num_retries"] += retry
            self._statistics["time_spent_sleeping"] += total_delay

        err_msg = f"Failed to embed {len(tokenized_texts)} documents after {total_delay}s and {retry} retries. {last_exception}"
        logger.error(err_msg)  # TODO: Add custom dimensions
        raise RuntimeError(err_msg)

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Embed the given texts."""
        import numpy as np
        import tiktoken
        from azure.ai.resources._index._utils.tokens import tiktoken_cache_dir

        try:
            with tiktoken_cache_dir():
                encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            logger.warning("Warning: model not found. Using cl100k_base encoding.")
            model = "cl100k_base"
            encoding = tiktoken.get_encoding(model)

        tokenized_texts = []
        num_tokens = 0
        tokenized_texts_to_original_texts_indices = []
        for i, text in enumerate(texts):
            if self.model.endswith("001"):
                # Replace newlines, which can negatively affect performance.
                # See: https://github.com/openai/openai-python/issues/418#issuecomment-1525939500
                text = text.replace("\n", " ")

            tokens = encoding.encode(
                text,
                # TODO: Does this need to be configurable? Our use cases treat all text as raw data.
                disallowed_special=(),
            )
            # Text longer than a models context length can be split and the embeddings averaged to approximate full text
            # See: https://github.com/openai/openai-cookbook/blob/main/examples/Embedding_long_inputs.ipynb
            for j in range(0, len(tokens), self.embedding_ctx_length):
                tokenized_texts.append(tokens[j : j + self.embedding_ctx_length])
                num_tokens += len(tokenized_texts[-1])
                tokenized_texts_to_original_texts_indices.append(i)

        self._statistics["num_tokens"] += num_tokens

        if self.show_progress_bar:
            try:
                import tqdm

                _iter = tqdm.tqdm(range(0, len(tokenized_texts), self.batch_size))
            except ImportError:
                _iter = range(0, len(tokenized_texts), self.batch_size)
        else:
            _iter = range(0, len(tokenized_texts), self.batch_size)

        batched_embeddings: List[List[float]] = []
        for i in _iter:
            response = self._dynamic_batch_size_embed_request(
                tokenized_texts=tokenized_texts[i : i + self.batch_size],
                **self._openai_client_params,
            )
            batched_embeddings.extend(r["embedding"] for r in response["data"])

        embedding_results: List[List[List[float]]] = [[] for _ in range(len(texts))]
        num_tokens_in_batch: List[List[int]] = [[] for _ in range(len(texts))]
        for i in range(len(tokenized_texts_to_original_texts_indices)):
            embedding_results[tokenized_texts_to_original_texts_indices[i]].append(batched_embeddings[i])
            num_tokens_in_batch[tokenized_texts_to_original_texts_indices[i]].append(len(tokenized_texts[i]))

        embeddings: List[List[float]] = [[] for _ in range(len(texts))]
        for i in range(len(texts)):
            _result = embedding_results[i]
            if len(_result) == 0:
                # TODO: Bug 2875482
                average = self._embed_request(tokenized_texts="", **self._openai_client_params)["data"][0]["embedding"]  # type: ignore[arg-type]
            else:
                average = np.average(_result, axis=0, weights=num_tokens_in_batch[i])
            embeddings[i] = (average / np.linalg.norm(average)).tolist()

        return embeddings

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Batch embed documents."""
        return self._embed(documents)

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query."""
        return self.embed_documents([query])[0]

    @property
    def statistics(self) -> Dict[str, Any]:
        """Return statistics about the last embedding request."""
        return self._statistics
