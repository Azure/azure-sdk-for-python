# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.iot.modelsrepository._client import (
    ModelsRepositoryClient,
    DEPENDENCY_MODE_TRY_FROM_EXPANDED,
    DEPENDENCY_MODE_ENABLED,
    DEPENDENCY_MODE_DISABLED,
)
from azure.iot.modelsrepository._resolver import HttpFetcher, FilesystemFetcher


@pytest.mark.describe("ModelsRepositoryClient - Instantiation")
class TestModelsRepositoryClientInstantiation(object):
    @pytest.mark.it(
        "Defaults to using 'https://devicemodels.azure.com' as the repository location if one is not provided"
    )
    def test_default_repository_location(self):
        client = ModelsRepositoryClient()
        assert client.fetcher.base_url == "https://devicemodels.azure.com"

    @pytest.mark.it(
        "Is configured for HTTP/HTTPS REST operations if provided a repository location in URL format"
    )
    @pytest.mark.parametrize(
        "url",
        [
            pytest.param("http://myfakerepository.com/", id="HTTP URL, with trailing '/'"),
            pytest.param("http://myfakerepository.com", id="HTTP URL, no trailing '/'"),
            pytest.param("https://myfakerepository.com/", id="HTTPS URL, with trailing '/'"),
            pytest.param("https://myfakerepository.com", id="HTTPS URL, no trailing '/'"),
            pytest.param(
                "myfakerepository.com/", id="Web URL, no protocol specified, with trailing '/'"
            ),
            pytest.param(
                "myfakerepository.com", id="Web URL, no protocol specified, no trailing '/'"
            ),
        ],
    )
    def test_repository_location_remote(self, url):
        client = ModelsRepositoryClient(repository_location=url)
        assert isinstance(client.fetcher, HttpFetcher)

    @pytest.mark.it(
        "Is configured for local filesystem operations if provided a repository location in filesystem format"
    )
    @pytest.mark.parametrize(
        "path",
        [
            pytest.param(
                "F:/repos/myrepo/",
                id="Drive letter filesystem path, '/' separators, with trailing '/'",
            ),
            pytest.param(
                "F:/repos/myrepo",
                id="Drive letter filesystem path, '/' separators, no trailing '/'",
            ),
            pytest.param(
                "F:\\repos\\myrepo\\",
                id="Drive letter filesystem path, '\\' separators, with trailing '\\'",
            ),
            pytest.param(
                "F:\\repos\\myrepo",
                id="Drive letter filesystem path, '\\' separators, no trailing '\\'",
            ),
            pytest.param(
                "F:\\repos/myrepo/",
                id="Drive letter filesystem path, mixed separators, with trailing separator",
            ),
            pytest.param(
                "F:\\repos/myrepo",
                id="Drive letter filesystem path, mixed separators, no trailing separator",
            ),
            pytest.param("/repos/myrepo/", id="POSIX filesystem path, with trailing '/'"),
            pytest.param("/repos/myrepo", id="POSIX filesystem path, no trailing '/'"),
            pytest.param(
                "file:///f:/repos/myrepo/",
                id="URI scheme, drive letter filesystem path, with trailing '/'",
            ),
            pytest.param(
                "file:///f:/repos/myrepo",
                id="URI scheme, drive letter filesystem path, no trailing '/'",
            ),
            pytest.param(
                "file:///repos/myrepo/", id="URI scheme, POSIX filesystem path, with trailing '/'"
            ),
            pytest.param(
                "file:///repos/myrepo", id="URI schem, POSIX filesystem path, no trailing '/'"
            ),
        ],
    )
    def test_repository_location_local(self, path):
        client = ModelsRepositoryClient(repository_location=path)
        assert isinstance(client.fetcher, FilesystemFetcher)

    @pytest.mark.it("Raises ValueError if provided a repository location that cannot be identified")
    def test_invalid_repository_location(self):
        with pytest.raises(ValueError):
            ModelsRepositoryClient(repository_location="not a location")

    @pytest.mark.it(
        "Defaults to using 'tryFromExpanded' as the dependency resolution mode if one is not specified while using the default repository location"
    )
    def test_default_dependency_resolution_mode_default_location(self):
        client = ModelsRepositoryClient()
        assert client.resolution_mode == DEPENDENCY_MODE_TRY_FROM_EXPANDED

    @pytest.mark.it(
        "Defaults to using 'enabled' as the dependency resolution mode if one is not specified while using a custom repository location"
    )
    @pytest.mark.parametrize(
        "location",
        [
            pytest.param("https://myfakerepository.com", id="Remote repository location"),
            pytest.param("/repos/myrepo", id="Local repository location"),
        ],
    )
    def test_default_dependency_resolution_mode_custom_location(self, location):
        client = ModelsRepositoryClient(repository_location=location)
        assert client.resolution_mode == DEPENDENCY_MODE_ENABLED

    @pytest.mark.it(
        "Is configured with the provided dependency resolution mode if one is specified"
    )
    @pytest.mark.parametrize(
        "dependency_mode",
        [DEPENDENCY_MODE_ENABLED, DEPENDENCY_MODE_DISABLED, DEPENDENCY_MODE_TRY_FROM_EXPANDED],
    )
    def test_dependency_mode(self, dependency_mode):
        client = ModelsRepositoryClient(dependency_resolution=dependency_mode)
        assert client.resolution_mode == dependency_mode

    @pytest.mark.it("Raises ValueError if provided an unrecognized dependency resolution mode")
    def test_invalid_dependency_mode(self):
        with pytest.raises(ValueError):
            ModelsRepositoryClient(dependency_resolution="not a mode")
