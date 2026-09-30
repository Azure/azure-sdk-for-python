import json
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import load_online_endpoint, MLClient
from azure.ai.ml.entities import OnlineEndpoint, EndpointAuthKeys, EndpointAuthToken
from azure.ai.ml.entities._endpoint.online_endpoint import EndpointAadToken
from azure.ai.ml.constants._endpoint import EndpointKeyType
from azure.ai.ml.exceptions import ValidationException, MlException
from azure.core.polling import LROPoller


# Provide a minimal concrete subclass to satisfy abstract base requirements of OnlineEndpoint
class _ConcreteOnlineEndpoint(OnlineEndpoint):
    def dump(self, *args, **kwargs):
        # minimal implementation to satisfy abstract method requirements for tests
        # return a simple dict representation; not used by operations under test
        return {
            "name": getattr(self, "name", None),
            "auth_mode": getattr(self, "auth_mode", None),
        }


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestOnlineEndpointOperationsGaps(AzureRecordedTestCase):
    def test_begin_regenerate_keys_raises_for_non_key_auth(
        self, client: MLClient, rand_online_name: Callable[[str], str], tmp_path
    ) -> None:
        # Create an endpoint configured to use AAD token auth so that begin_regenerate_keys raises ValidationException
        endpoint_name = rand_online_name("endpoint_name_regen")
        try:
            # create a minimal endpoint object configured for AAD token auth
            endpoint = _ConcreteOnlineEndpoint(name=endpoint_name)
            # set auth_mode after construction to avoid instantiation issues with abstract base changes
            endpoint.auth_mode = "aad_token"
            # Create the endpoint
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            # Attempting to regenerate keys should raise ValidationException because auth_mode is not 'key'
            with pytest.raises(ValidationException):
                client.online_endpoints.begin_regenerate_keys(name=endpoint_name).result()
        finally:
            # Clean up
            client.online_endpoints.begin_delete(name=endpoint_name).result()

    def test_begin_regenerate_keys_invalid_key_type_raises(
        self, client: MLClient, rand_online_name: Callable[[str], str], tmp_path
    ) -> None:
        # Create an endpoint that uses keys so we can exercise invalid key_type validation in _regenerate_online_keys
        endpoint_name = rand_online_name("endpoint_name_invalid_key")
        try:
            endpoint = _ConcreteOnlineEndpoint(name=endpoint_name)
            endpoint.auth_mode = "key"
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            # Using an invalid key_type should raise ValidationException
            with pytest.raises(ValidationException):
                # use an invalid key string to trigger the branch that raises for non-primary/secondary
                client.online_endpoints.begin_regenerate_keys(name=endpoint_name, key_type="tertiary").result()
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()

    def test_invoke_with_nonexistent_deployment_raises(
        self, client: MLClient, rand_online_name: Callable[[str], str], tmp_path
    ) -> None:
        # Create a simple endpoint with no deployments, then attempt to invoke with a deployment_name that doesn't exist
        endpoint_name = rand_online_name("endpoint_name_invoke")
        request_file = tmp_path / "req.json"
        request_file.write_text(json.dumps({"input": [1, 2, 3]}))
        try:
            endpoint = _ConcreteOnlineEndpoint(name=endpoint_name)
            endpoint.auth_mode = "key"
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            # Invoke with a deployment name when there are no deployments should raise ValidationException
            with pytest.raises(ValidationException):
                client.online_endpoints.invoke(
                    endpoint_name=endpoint_name,
                    request_file=str(request_file),
                    deployment_name="does-not-exist",
                )
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_asset_name", "mock_component_hash")
class TestOnlineEndpointGaps(AzureRecordedTestCase):
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Key regeneration produces non-deterministic values",
    )
    def test_begin_regenerate_keys_behaves_based_on_auth_mode(
        self,
        rand_online_name: Callable[[str], str],
        client: MLClient,
    ) -> None:
        """
        Covers branches where begin_regenerate_keys either calls key regeneration for key-auth endpoints
        or raises ValidationException for non-key-auth endpoints.
        """
        # Use a name that satisfies endpoint naming validation (start with a letter, alphanumeric and '-')
        endpoint_name = rand_online_name("endpoint_name_auth")
        # Create a minimal endpoint; set auth_mode to 'key' to exercise regeneration path
        endpoint = _ConcreteOnlineEndpoint(name=endpoint_name)
        endpoint.auth_mode = "key"
        try:
            # create endpoint
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            # fetch endpoint to inspect auth mode
            get_obj = client.online_endpoints.get(name=endpoint_name)
            assert get_obj.name == endpoint_name

            # If endpoint uses key auth, regenerate secondary key should succeed and return a poller
            if getattr(get_obj, "auth_mode", "").lower() == "key":
                poller = client.online_endpoints.begin_regenerate_keys(
                    name=endpoint_name, key_type=EndpointKeyType.SECONDARY_KEY_TYPE
                )
                # Should return a poller (LROPoller); do not wait on it to avoid transient service polling errors in CI
                assert isinstance(poller, LROPoller)
                # After regeneration request initiated, fetching keys should succeed
                creds = client.online_endpoints.get_keys(name=endpoint_name)
                assert isinstance(creds, EndpointAuthKeys)
            else:
                # For non-key auth endpoints, begin_regenerate_keys should raise ValidationException
                with pytest.raises(ValidationException):
                    client.online_endpoints.begin_regenerate_keys(
                        name=endpoint_name, key_type=EndpointKeyType.PRIMARY_KEY_TYPE
                    )
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()

    def test_regenerate_keys_with_invalid_key_type_raises(
        self,
        rand_online_name: Callable[[str], str],
        client: MLClient,
    ) -> None:
        """
        Covers branch in _regenerate_online_keys that raises for invalid key_type values.
        If endpoint is not key-authenticated, the test will skip since the invalid-key-type path is only reachable
        for key-auth endpoints.
        """
        endpoint_name = rand_online_name("endpoint_name_invalid_key2")
        endpoint = _ConcreteOnlineEndpoint(name=endpoint_name)
        endpoint.auth_mode = "key"
        try:
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()
            get_obj = client.online_endpoints.get(name=endpoint_name)

            if getattr(get_obj, "auth_mode", "").lower() != "key":
                pytest.skip("Endpoint not key-authenticated; cannot test invalid key_type branch")

            # For key-auth endpoint, passing an invalid key_type should raise ValidationException
            with pytest.raises(ValidationException):
                client.online_endpoints.begin_regenerate_keys(name=endpoint_name, key_type="tertiary").result()
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()

    def test_invoke_with_nonexistent_deployment_raises_random_name(
        self,
        rand_online_name: Callable[[str], str],
        client: MLClient,
        tmp_path,
    ) -> None:
        """
        Covers validation in invoke that raises when a specified deployment_name does not exist for the endpoint.
        """
        endpoint_name = rand_online_name("endpoint_name_invoke2")
        endpoint = _ConcreteOnlineEndpoint(name=endpoint_name)
        endpoint.auth_mode = "key"
        request_file = tmp_path / "req.json"
        request_file.write_text(json.dumps({"input": [1, 2, 3]}))
        try:
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            # Pick a random deployment name that is unlikely to exist
            bad_deployment = "nonexistent-deployment"

            # Attempt to invoke with a deployment_name that does not exist should raise ValidationException
            with pytest.raises(ValidationException):
                client.online_endpoints.invoke(
                    endpoint_name=endpoint_name,
                    request_file=str(request_file),
                    deployment_name=bad_deployment,
                )
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()

    # Fixtures and additional tests merged from generated batch
    @pytest.fixture
    def endpoint_mir_yaml(self) -> str:
        return "./tests/test_configs/endpoints/online/online_endpoint_create_mir.yml"

    @pytest.fixture
    def request_file(self) -> str:
        return "./tests/test_configs/endpoints/online/data.json"

    def test_begin_create_triggers_workspace_location_and_roundtrip(
        self,
        endpoint_mir_yaml: str,
        rand_online_name: Callable[[], str],
        client: MLClient,
    ) -> None:
        """Create an endpoint to exercise internal _get_workspace_location path invoked during create_or_update.

        Covers marker lines around workspace location retrieval invoked in begin_create_or_update.
        """
        endpoint_name = rand_online_name("gaps-test-ep-")
        try:
            endpoint = load_online_endpoint(endpoint_mir_yaml)
            endpoint.name = endpoint_name
            # This will call begin_create_or_update which uses _get_workspace_location internally
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            got = client.online_endpoints.get(name=endpoint_name)
            assert got.name == endpoint_name
            assert isinstance(got, OnlineEndpoint)
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()

    def test_get_keys_returns_expected_token_or_keys(
        self,
        endpoint_mir_yaml: str,
        rand_online_name: Callable[[], str],
        client: MLClient,
    ) -> None:
        """Create an endpoint and call get_keys to exercise _get_online_credentials branches for KEY/AAD/token.

        Covers marker lines for _get_online_credentials behavior when auth_mode is key, aad_token, or other.
        """
        endpoint_name = rand_online_name("gaps-test-keys-")
        try:
            endpoint = load_online_endpoint(endpoint_mir_yaml)
            endpoint.name = endpoint_name
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            get_obj = client.online_endpoints.get(name=endpoint_name)
            assert get_obj.name == endpoint_name

            creds = client.online_endpoints.get_keys(name=endpoint_name)
            assert creds is not None
            # Depending on service-configured auth_mode, creds should be one of these types
            if isinstance(get_obj, OnlineEndpoint) and get_obj.auth_mode and get_obj.auth_mode.lower() == "key":
                assert isinstance(creds, EndpointAuthKeys)
            else:
                # service may return token types
                assert isinstance(creds, (EndpointAuthToken,))
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()

    def test_begin_regenerate_keys_with_invalid_key_type_raises(
        self,
        endpoint_mir_yaml: str,
        rand_online_name: Callable[[], str],
        client: MLClient,
    ) -> None:
        """If endpoint uses key auth, passing an invalid key_type should raise ValidationException.

        Covers branches in begin_regenerate_keys -> _regenerate_online_keys where invalid key_type raises ValidationException.
        If the endpoint is not key-authenticated in this workspace, the test will be skipped because the branch cannot be reached.
        """
        endpoint_name = rand_online_name("gaps-test-regenerate-")
        try:
            endpoint = load_online_endpoint(endpoint_mir_yaml)
            endpoint.name = endpoint_name
            client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()

            get_obj = client.online_endpoints.get(name=endpoint_name)
            if not (isinstance(get_obj, OnlineEndpoint) and get_obj.auth_mode and get_obj.auth_mode.lower() == "key"):
                pytest.skip("Endpoint not key-authenticated in this workspace; cannot exercise invalid key_type path")

            # Passing an invalid key_type should raise ValidationException
            with pytest.raises(ValidationException):
                client.online_endpoints.begin_regenerate_keys(name=endpoint_name, key_type="invalid-key-type").result()
        finally:
            client.online_endpoints.begin_delete(name=endpoint_name).result()
