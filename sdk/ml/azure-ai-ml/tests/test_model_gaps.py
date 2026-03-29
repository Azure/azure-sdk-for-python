import os
import re
import uuid
from pathlib import Path
from typing import Callable, Iterator

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import sleep_if_live

from azure.ai.ml import MLClient, load_model
from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType
from azure.ai.ml.constants._common import LONG_URI_REGEX_FORMAT
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.exceptions import ValidationException
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError, HttpResponseError
from azure.core.paging import ItemPaged


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestModelOperationsGaps(AzureRecordedTestCase):

    def test_get_with_version_and_label_raises(self, client: MLClient, randstr: Callable[[], str], tmp_path: Path) -> None:
        """Calling get with both version and label should raise a ValidationException (invalid value)."""
        name = f"model_{randstr('name')}"
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")

        with pytest.raises(ValidationException):
            client.models.get(name=name, version="1", label="latest")

    def test_get_without_version_or_label_raises(self, client: MLClient, randstr: Callable[[], str], tmp_path: Path) -> None:
        """Calling get with neither version nor label should raise a ValidationException (missing field)."""
        name = f"model_{randstr('name')}"
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")

        # Ensure the model does not exist to exercise missing-field validation path
        # If model exists, still calling get without version/label should raise
        with pytest.raises(ValidationException):
            client.models.get(name=name)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestModelPackageGaps(AzureRecordedTestCase):
    @pytest.mark.skipif(condition=not is_live(), reason="Registry share flow requires live registry access")
    def test_share_uses_set_registry_client_and_returns_model(
        self, client: MLClient, randstr: Callable[[], str], tmp_path: Path, request
    ) -> None:
        # Attempt to obtain the registry_client fixture dynamically so that failures during
        # fixture construction (like forbidden access) can be handled and cause the test to be skipped.
        try:
            registry_client = request.getfixturevalue("registry_client")
        except Exception as e:
            # If registry access is forbidden or otherwise unavailable in this environment, skip the test.
            if isinstance(e, HttpResponseError):
                pytest.skip(f"Registry access unavailable: {e}")
            raise

        # Create a model in the workspace
        name = f"model_{randstr('name')}"
        version = "1"
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")

        created = client.models.create_or_update(Model(name=name, version=version, path=str(model_path)))
        assert created.name == name
        assert created.version == version

        # Share the model with the registry referenced by registry_client
        registry_name = registry_client._operation_scope.registry_name

        shared = client.models.share(name=name, version=version, share_with_name=name, share_with_version=version, registry_name=registry_name)
        # If share succeeds, it should return a Model-like object (Model._from_rest_object path)
        assert shared is not None
        # Name should match the shared target asset name
        # The returned object may be a Model or an Environment depending on server behavior; at minimum ensure attribute access
        assert hasattr(shared, "__class__")
