# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Langchain + OpenAI helpers."""


def patch_openai_embedding_retries(logger, activity_logger, max_seconds_retrying=540):
    """Patch the openai embedding to retry on failure.""."""
    from datetime import datetime

    from azure.ai.generative.index._langchain.vendor.embeddings import openai as langchain_openai
    from tenacity import (
        retry,
        retry_if_exception_type,
        wait_exponential,
    )
    from tenacity.stop import stop_base

    def _log_it(retry_state) -> None:
        if retry_state.outcome.failed:
            ex = retry_state.outcome.exception()
            verb, value = "raised", f"{ex.__class__.__name__}: {ex}"
        else:
            verb, value = "returned", retry_state.outcome.result()
        logger.warning(
            f"Retrying _embed_with_retry " f"in {retry_state.next_action.sleep} seconds as it {verb} {value}.",
        )

        if "num_retries" not in activity_logger.activity_info:
            activity_logger.activity_info["num_retries"] = 0
            activity_logger.activity_info["time_spent_sleeping"] = 0
        activity_logger.activity_info["num_retries"] += 1
        activity_logger.activity_info["time_spent_sleeping"] += retry_state.idle_for

        # This is a lot of data to send to telemetry, not sending by default for now due to fears of maxxing out daily ingress cap.
        # if 'retries' not in activity_logger.activity_info:
        #     activity_logger.activity_info['retries'] = []
        #     activity_logger.activity_info['first_retry'] = datetime.utcnow()
        # activity_logger.activity_info['retries'] += [json.dumps({'idx': retry_state.attempt_number, 'timestamp': str(datetime.utcnow()), 'sleep': retry_state.next_action.sleep})]

    class stop_after_delay_that_works(stop_base):
        """Stop when the time from the first attempt >= limit."""

        def __init__(self, max_delay, activity_logger) -> None:
            self.max_delay = max_delay
            self.activity_logger = activity_logger

        def __call__(self, retry_state) -> bool:
            first_retry = self.activity_logger.activity_info.get("first_retry", None)
            if first_retry:
                return (datetime.utcnow() - first_retry).seconds >= self.max_delay
            else:
                return False

    # Copied from https://github.com/hwchase17/langchain/blob/511c12dd3985ce682226371c12f8fa70d8c9a8e1/langchain/embeddings/openai.py#L34
    def _create_retry_decorator(embeddings):
        import openai

        min_seconds = 4
        max_seconds = 10
        # Wait 2^x * 1 second between each retry starting with
        # 4 seconds, then up to 10 seconds, then 10 seconds afterwards
        return retry(
            reraise=True,
            # stop=stop_after_attempt(embeddings.max_retries),
            stop=stop_after_delay_that_works(max_seconds_retrying, activity_logger),
            wait=wait_exponential(multiplier=1, min=min_seconds, max=max_seconds),
            retry=(
                retry_if_exception_type(openai.error.Timeout)
                | retry_if_exception_type(openai.error.APIError)
                | retry_if_exception_type(openai.error.APIConnectionError)
                | retry_if_exception_type(openai.error.RateLimitError)
                | retry_if_exception_type(openai.error.ServiceUnavailableError)
            ),
            before_sleep=_log_it,
        )

    langchain_openai._create_retry_decorator = _create_retry_decorator
