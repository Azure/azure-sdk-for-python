# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from devtools_testutils import AzureRecordedTestCase
from conftest import configure, ALL


class TestModels(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize("api_type", ALL)
    def test_models_list(self, client, azure_openai_creds, api_type, **kwargs):

        models = client.models.list()
        for model in models:
            assert model.id

    @configure
    @pytest.mark.parametrize("api_type", ALL)
    def test_models_retrieve(self, client, azure_openai_creds, api_type, **kwargs):

        model = client.models.retrieve(**kwargs)
        assert model.id
