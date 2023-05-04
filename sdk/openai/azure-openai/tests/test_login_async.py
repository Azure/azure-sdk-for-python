# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


import os
import pytest
import asyncio


@pytest.mark.asyncio
async def test_login_dac():
    # ---- test setup starts ----
    os.environ["OPENAI_API_BASE"] = "https://openai-shared.openai.azure.com/"
    os.environ["OPENAI_API_KEY"] = "azuread"
    import openai
    from azure.openai.aio import login
    # ---- test setup ends ----

    async with login():
        completion = await openai.Completion.acreate(prompt="hello", deployment_id="text-davinci-003")
        assert completion


@pytest.mark.asyncio
async def test_login_key():

    # ---- test setup starts ----
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = "https://openai-shared.openai.azure.com/"
    os.environ["OPENAI_API_KEY"] = "real_key"
    import openai
    from azure.openai.aio import login
    # ---- test setup ends ----

    async with login():
        completion = await openai.Completion.acreate(prompt="hello", deployment_id="text-davinci-003")
        assert completion
        openai.api_key = "fake_key"
        with pytest.raises(openai.error.AuthenticationError):
            completion = await openai.Completion.acreate(prompt="hello", deployment_id="text-davinci-003")
