# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from devtools_testutils import AzureRecordedTestCase
from conftest import configure_async, ALL


class TestModelsAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", ALL)
    async def test_models_list(self, client_async, azure_openai_creds, api_type, **kwargs):

        models = client_async.models.list()
        async for model in models:
            assert model.id

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", ALL)
    async def test_models_retrieve(self, client_async, azure_openai_creds, api_type, **kwargs):

        model = await client_async.models.retrieve(**kwargs)
        assert model.id
