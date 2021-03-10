# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import logging
from azure.iot.modelsrepository import ModelsRepositoryClient, DEPENDENCY_MODE_ENABLED, DEPENDENCY_MODE_TRY_FROM_EXPANDED
from azure.iot.modelsrepository import resolver

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.describe("ModelsRepositoryClient -- Instantiation (Remote Repository)")
class TestModelsRepositoryClientInstantiation(object):
    @pytest.fixture
    def location(self):
        return "https://my.fake.respository.com"

    @pytest.mark.it("Instantiates a PipelineClient that uses the provided repository location")
    @pytest.mark.parametrize("location, expected_pl_base_url", [
        pytest.param("http://repository.mydomain.com/", "http://repository.mydomain.com/", id="HTTP URL"),
        pytest.param("https://repository.mydomain.com/", "https://repository.mydomain.com/", id="HTTPS URL"),
        pytest.param("repository.mydomain.com", "https://repository.mydomain.com", id="No protocol specified on URL (defaults to HTTPS)"),
        pytest.param("https://repository.mydomain.com", "https://repository.mydomain.com", id="No trailing '/' on URL")
    ])
    def test_pipeline_client(self, location, expected_pl_base_url):
        client = ModelsRepositoryClient(repository_location=location)
        assert client.fetcher.client._base_url == expected_pl_base_url

    @pytest.mark.it("Configures the PipelineClient ")

    # @pytest.mark.it("Instantiates a DtmiResolver from an HttpFetcher if the client is being created from a remote repository location")
    # def test_resolver_fetcher(self):
    #     location = "https://my.fake.respository.com"
    #     client = ModelsRepositoryClient(repository_location=location)

    #     assert isinstance(client.resolver, resolver.DtmiResolver)
    #     assert isinstance(client.fetcher, resolver.HttpFetcher)
    #     assert client.resolver.fetcher is client.fetcher
    #     assert client.fetcher.client._base_url == location

    # @pytest.mark.it("Instantiates a PseudoParser from the DtmiResolver")