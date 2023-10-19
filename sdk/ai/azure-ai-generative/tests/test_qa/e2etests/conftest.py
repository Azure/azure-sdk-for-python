# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import os

import pytest
from azure.ai.generative.synthetic.qa import QADataGenerator


@pytest.fixture
def event_loop():
    # this function needed to fix a windows-only issue
    # https://github.com/pytest-dev/pytest-asyncio/issues/371#issuecomment-1161462430
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    res = policy.new_event_loop()
    asyncio.set_event_loop(res)
    res._close = res.close
    res.close = lambda: None
    yield res
    res._close()


@pytest.fixture
def qa_generator():
    model_config = dict(
        api_base=os.environ["OPENAI_API_BASE"],
        api_key=os.environ["OPENAI_API_KEY"],
        deployment=os.environ.get("MODEL_NAME", "gpt-4"),
        model=os.environ.get("DEPLOYMENT_NAME", "gpt-4"),
        max_tokens=2000,
    )
    qa_generator = QADataGenerator(model_config)
    return qa_generator
