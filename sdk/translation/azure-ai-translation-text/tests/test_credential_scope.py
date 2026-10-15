# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.ai.translation.text import TextTranslationClient
from azure.ai.translation.text.aio import TextTranslationClient as TextTranslationClientAsync

AUDIENCE_TO_SCOPE = [
    (None, "https://cognitiveservices.azure.com/.default"),
    ("api://translationhub-live", "api://translationhub-live/.default"),
    ("api://translationhub-live/", "api://translationhub-live/.default"),
    ("api://translationhub-live/.default", "api://translationhub-live/.default"),
    ("https://cognitiveservices.azure.com", "https://cognitiveservices.azure.com/.default"),
]


class _TokenRequested(Exception):
    pass


class _ScopeCapturingCredential:
    def __init__(self):
        self.scopes = None

    def get_token(self, *scopes, **kwargs):
        self.scopes = scopes
        raise _TokenRequested()


class _AsyncScopeCapturingCredential:
    def __init__(self):
        self.scopes = None

    async def get_token(self, *scopes, **kwargs):
        self.scopes = scopes
        raise _TokenRequested()

    async def close(self):
        pass


class TestCredentialScope:
    @pytest.mark.parametrize("audience,expected_scope", AUDIENCE_TO_SCOPE)
    def test_audience_to_scope(self, audience, expected_scope):
        credential = _ScopeCapturingCredential()
        client = TextTranslationClient(credential=credential, audience=audience)
        with client:
            with pytest.raises(_TokenRequested):
                client.get_supported_languages()

        assert credential.scopes == (expected_scope,)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("audience,expected_scope", AUDIENCE_TO_SCOPE)
    async def test_audience_to_scope_async(self, audience, expected_scope):
        credential = _AsyncScopeCapturingCredential()
        client = TextTranslationClientAsync(credential=credential, audience=audience)
        async with client:
            with pytest.raises(_TokenRequested):
                await client.get_supported_languages()

        assert credential.scopes == (expected_scope,)
