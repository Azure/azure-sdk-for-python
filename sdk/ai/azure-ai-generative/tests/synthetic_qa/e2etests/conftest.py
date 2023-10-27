# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import os

import pytest
from azure.ai.generative.synthetic.qa import QADataGenerator

API_BASE = os.environ["AI_OPENAI_API_BASE"]
API_KEY = os.environ["AI_OPENAI_API_KEY"]
DEPLOYMENT_NAME = os.environ["AI_OPENAI_COMPLETION_DEPLOYMENT_NAME"]
MODEL_NAME = os.environ["AI_OPENAI_COMPLETION_MODEL_NAME"]

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
        api_base=API_BASE,
        api_key=API_KEY,
        deployment=DEPLOYMENT_NAME,
        model=MODEL_NAME,
        max_tokens=2000,
    )
    qa_generator = QADataGenerator(model_config)
    return qa_generator
