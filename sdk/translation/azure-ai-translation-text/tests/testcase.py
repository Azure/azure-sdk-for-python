# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from devtools_testutils.fake_credentials_async import AsyncFakeCredential
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase
from azure.ai.translation.text import TextTranslationClient

from static_access_token_credential import StaticAccessTokenCredential


class TextTranslationTest(AzureRecordedTestCase):
    def create_getlanguage_client(self, endpoint):
        client = TextTranslationClient(endpoint=endpoint, credential=None)
        return client

    def create_client(self, endpoint, apikey, region):
        credential = AzureKeyCredential(apikey)
        client = TextTranslationClient(endpoint=endpoint, credential=credential, region=region)
        return client

    def create_client_token(self, endpoint, apikey, region):
        credential = StaticAccessTokenCredential(apikey, region)
        client = TextTranslationClient(endpoint=endpoint, credential=credential)
        return client

    def create_text_translation_client_with_aad(self, innerCredential, aadRegion, aadResourceId):
        text_translator = TextTranslationClient(credential=innerCredential, resource_id=aadResourceId, region=aadRegion)
        return text_translator

    def create_async_getlanguage_client(self, endpoint):
        from azure.ai.translation.text.aio import TextTranslationClient as TextTranslationClientAsync

        client = TextTranslationClientAsync(endpoint=endpoint, credential=None)
        return client

    def create_async_client(self, endpoint, apikey, region):
        credential = AzureKeyCredential(apikey)
        from azure.ai.translation.text.aio import TextTranslationClient as TextTranslationClientAsync

        client = TextTranslationClientAsync(endpoint=endpoint, credential=credential, region=region)
        return client

    def create_async_client_token(self, endpoint, apikey, region):
        credential = StaticAccessTokenCredential(apikey, region)
        from azure.ai.translation.text.aio import TextTranslationClient as TextTranslationClientAsync

        client = TextTranslationClientAsync(endpoint=endpoint, credential=credential)
        return client

    def create_async_text_translation_client_with_aad(self, innerCredential, aadRegion, aadResourceId):
        from azure.ai.translation.text.aio import TextTranslationClient as TextTranslationClientAsync

        text_translator = TextTranslationClientAsync(
            credential=innerCredential, resource_id=aadResourceId, region=aadRegion
        )
        return text_translator

    def get_mt_credential(self, is_async, **kwargs):
        # Return live credentials only in live mode
        if self.is_live:
            from azure.identity import ClientSecretCredential

            if is_async:
                from azure.identity.aio import ClientSecretCredential

            tenant_id = os.environ.get("AZURE_TENANT_ID", getattr(os.environ, "TENANT_ID", None))
            client_id = os.environ.get("AZURE_CLIENT_ID", getattr(os.environ, "CLIENT_ID", None))
            secret = os.environ.get("AZURE_CLIENT_SECRET", getattr(os.environ, "CLIENT_SECRET", None))
            return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=secret)

        # For playback tests, return credentials that will accept playback `get_token` calls
        else:
            if is_async:
                return AsyncFakeCredential()
            else:
                return self.settings.get_azure_core_credentials()
