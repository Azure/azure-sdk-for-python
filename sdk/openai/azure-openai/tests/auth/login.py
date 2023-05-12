# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
from azure.identity import DefaultAzureCredential


def test_login_dac_by_env():
    # ---- test setup starts ----
    os.environ["OPENAI_API_BASE"] = os.environ["AZURE_OPENAI_ENDPOINT"]
    os.environ["OPENAI_API_TYPE"] = "azuread"
    os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
    import openai
    import azure.openai
    # ---- test setup ends ----

    azure.openai.login()
    completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")
    assert completion


def test_login_token_by_env():
    # ---- test setup starts ----
    os.environ["OPENAI_API_BASE"] = os.environ["AZURE_OPENAI_ENDPOINT"]
    os.environ["OPENAI_API_TYPE"] = "azuread"
    os.environ["OPENAI_API_KEY"] = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token
    os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
    import openai
    import azure.openai
    # ---- test setup ends ----

    azure.openai.login()
    completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")
    assert completion

    # test token rotation
    openai.api_key = "fake_token"
    with pytest.raises(openai.error.APIError):  # why isn't this an AuthenticationError?
        completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")


def test_login_key_by_env():
    # ---- test setup starts ----
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = os.environ["AZURE_OPENAI_ENDPOINT"]
    os.environ["OPENAI_API_KEY"] = os.environ["AZURE_OPENAI_KEY"]
    os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
    import openai
    import azure.openai
    # ---- test setup ends ----

    azure.openai.login()
    completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")
    assert completion

    # test key rotation
    openai.api_key = "fake_key"
    with pytest.raises(openai.error.AuthenticationError):
        completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")


def test_login_dac_kw_override():
    # ---- test setup starts ----
    os.environ["OPENAI_API_BASE"] = "https://fake.openai.azure.com/"
    os.environ["OPENAI_API_TYPE"] = ""
    os.environ["OPENAI_API_KEY"] = "fake_key"
    import openai
    import azure.openai
    # ---- test setup ends ----

    azure.openai.login(api_key=DefaultAzureCredential(), api_base=os.environ["AZURE_OPENAI_ENDPOINT"], api_version="2023-03-15-preview")
    completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")
    assert completion


def test_login_key_kw_override():
    # ---- test setup starts ----
    os.environ["OPENAI_API_BASE"] = "https://fake.openai.azure.com/"
    os.environ["OPENAI_API_TYPE"] = ""
    os.environ["OPENAI_API_KEY"] = "fake_key"
    import openai
    import azure.openai
    # ---- test setup ends ----

    azure.openai.login(api_key=os.environ["AZURE_OPENAI_KEY"], api_base=os.environ["AZURE_OPENAI_ENDPOINT"], api_type="azure", api_version="2023-03-15-preview")
    completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")
    assert completion


def test_login_context_manager():
    # ---- test setup starts ----
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = os.environ["AZURE_OPENAI_ENDPOINT"]
    os.environ["OPENAI_API_KEY"] = os.environ["AZURE_OPENAI_KEY"]
    os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
    import openai
    import azure.openai
    # ---- test setup ends ----

    with azure.openai.login():
        completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")
        assert completion


def test_login_oai_endpoint():
    # ---- test setup starts ----
    os.environ["OPENAI_API_KEY"] = os.environ["OPEN_AI_KEY"]
    import openai
    import azure.openai
    # ---- test setup ends ----

    azure.openai.login()
    completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")
    assert completion
    # test key rotation
    openai.api_key = "fake_key"
    with pytest.raises(openai.error.AuthenticationError):
        completion = openai.Completion.create(prompt="hello", deployment_id="text-davinci-003")