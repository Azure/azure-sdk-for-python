# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live, recorded tests for ``project_client.beta.models``.

These tests exercise the generated ``BetaModelsOperations`` (``list``,
``list_versions``, ``get``, ``pending_upload``, ``get_credentials``, ``delete``)
and the patched ``models_create`` end-to-end helper. They follow the same
"upload + record" pattern used by ``test_datasets.py``.

``create_or_update`` is intentionally not tested here. The Foundry data plane
currently returns ``404 Not Found`` for that route even when ``GET`` for the
same name/version succeeds. The cell will be re-enabled once the service-side
issue is fixed.
"""

import os

import pytest
from devtools_testutils import (
    add_general_regex_sanitizer,
    is_live,
    is_live_and_not_recording,
    recorded_by_proxy,
)
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from test_base import TestBase, servicePreparer

# Construct the path to the data folder used in this test
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "../test_data/models"))


@pytest.mark.skipif(
    not is_live_and_not_recording(),
    reason="Skipped when using recordings due to flakiness of recording blob storage calls",
)
class TestModels(TestBase):

    # cls & pytest tests\models\test_models.py::TestModels::test_models_models_create -s
    @servicePreparer()
    @recorded_by_proxy
    def test_models_models_create(self, **kwargs):
        """End-to-end: pending_upload -> azcopy -> create_async -> get/list/delete."""
        model_name = self.test_models_params["model_name_1"]
        model_version = self.test_models_params["model_version"]
        expected_model_name = model_name if is_live() else "sanitized-model-name"
        add_general_regex_sanitizer(regex=r"test-model-name-\d{5}", value="sanitized-model-name", function_scoped=True)

        with self.create_client(**kwargs) as project_client:

            print(f"[test_models_models_create] models_create {model_name}@{model_version}")
            registered = project_client.beta.models.models_create(
                name=model_name,
                version=model_version,
                source=data_folder,
                weight_type="FullWeight",
                description="Registered by test_models_models_create",
                tags={"source": "test_models.py"},
            )
            assert registered is not None
            assert registered.name == expected_model_name
            assert registered.version == model_version
            assert registered.blob_uri, "blob_uri should be populated after models_create"

            print(f"[test_models_models_create] get {model_name}@{model_version}")
            fetched = project_client.beta.models.get(name=model_name, version=model_version)
            assert fetched.id == registered.id
            assert fetched.name == expected_model_name
            assert fetched.version == model_version

            print(f"[test_models_models_create] list_versions({model_name!r})")
            versions = list(project_client.beta.models.list_versions(name=model_name))
            assert any(
                mv.version == model_version for mv in versions
            ), f"version {model_version!r} not found in list_versions"

            print("[test_models_models_create] list (latest of every model)")
            empty = True
            for mv in project_client.beta.models.list():
                empty = False
                assert mv.name and mv.version
            assert not empty, "list() returned no models even though we just registered one"

            print(f"[test_models_models_create] get_credentials {model_name}@{model_version}")
            from azure.ai.projects.models import ModelCredentialRequest

            creds = project_client.beta.models.get_credentials(
                name=model_name,
                version=model_version,
                body=ModelCredentialRequest(blob_uri=registered.blob_uri),
            )
            blob_ref = getattr(creds, "blob_reference_for_consumption", None) or getattr(creds, "blob_reference", None)
            assert blob_ref is not None, f"no blob reference in credentials response: {creds!r}"
            assert blob_ref.blob_uri
            assert blob_ref.credential is not None
            assert blob_ref.credential.sas_uri

            print(f"[test_models_models_create] delete {model_name}@{model_version}")
            try:
                project_client.beta.models.delete(name=model_name, version=model_version)
            except HttpResponseError as ex:
                # The service currently returns 200 OK for a successful DELETE while
                # the generated operation only allow-lists 204. Tolerate that here.
                if ex.status_code != 200:
                    raise

            print(f"[test_models_models_create] get on deleted {model_name}@{model_version} should 404")
            with pytest.raises((ResourceNotFoundError, HttpResponseError)):
                project_client.beta.models.get(name=model_name, version=model_version)

    # cls & pytest tests\models\test_models.py::TestModels::test_models_pending_upload -s
    @servicePreparer()
    @recorded_by_proxy
    def test_models_pending_upload(self, **kwargs):
        """Lower-level: ``pending_upload`` returns a usable SAS URI."""
        from azure.ai.projects.models import ModelPendingUploadRequest, PendingUploadType

        model_name = self.test_models_params["model_name_2"]
        model_version = self.test_models_params["model_version"]
        add_general_regex_sanitizer(regex=r"test-model-name-\d{5}", value="sanitized-model-name", function_scoped=True)

        with self.create_client(**kwargs) as project_client:

            print(f"[test_models_pending_upload] pending_upload {model_name}@{model_version}")
            pending = project_client.beta.models.pending_upload(
                name=model_name,
                version=model_version,
                body=ModelPendingUploadRequest(
                    pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE,
                ),
            )
            payload = pending.as_dict() if hasattr(pending, "as_dict") else dict(pending)
            blob_ref = payload.get("blobReferenceForConsumption") or payload.get("blobReference") or {}
            assert (blob_ref.get("credential") or {}).get(
                "sasUri"
            ), f"pending_upload response missing SAS URI: {payload!r}"
            assert blob_ref.get("blobUri"), f"pending_upload response missing blobUri: {payload!r}"
